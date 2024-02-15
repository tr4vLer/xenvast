from requests.exceptions import ChunkedEncodingError
import requests
import logging
import time
import threading
import json
from eth_utils import to_checksum_address

# Load Configuration
def load_config():
    try:
        with open('config.json', 'r') as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        # Handle missing config file
        pass
    except json.JSONDecodeError:
        # Handle invalid JSON
        pass
def save_config(config):
    try:
        with open('config.json', 'w') as file:
            json.dump(config, file, indent=4)
    except Exception as e:
        logging.error(f"Failed to save config: {e}")


# Main Script
config = load_config()
MAX_GPU = config['MAX_GPU']
API_KEY = config['API_KEY']
GPU_MARKET = config['GPU_MARKET']
ETH_ADDRESS = config['ETH_ADDRESS']
IGNORE_MACHINE_IDS = config.get('IGNORE_MACHINE_IDS', [])

# Constants
CHECK_INTERVAL = 40  # in seconds, recommend to not go below 60 due to API artefacts

SEARCH_CRITERIA = {
    "verified": {},
    "external": {"eq": False},
    "rentable": {"eq": True},
    "gpu_name": {"in": [GPU_MARKET]}, 
    "cuda_max_good": {"gte": 11},
    "type": "on-demand",
    "intended_status": "running"
}
destroyed_instances_count = 0
successful_orders = 0
total_ordered_gpus = 0
successful_gpu = 0

# Logging Configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])


# Load API Key
api_key = API_KEY


# Define Functions
def eip55_encode(address):
    return to_checksum_address(address)

erc20_address = ETH_ADDRESS
eip55_address = eip55_encode(erc20_address)


def test_api_connection():
    """Function to test the API connection."""
    test_url = "https://console.vast.ai/api/v0/"
    try:
        response = requests.get(test_url, headers={"Accept": "application/json"})
        if response.status_code == 200:
            logging.info("Connection with API established and working fine.")
        else:
            logging.error(f"Error connecting to API. Status code: {response.status_code}. Response: {response.text}")
    except Exception as e:
        logging.error(f"Error connecting to API: {e}")


def search_gpu(successful_orders):
    url = "https://console.vast.ai/api/v0/bundles/"
    headers = {'Accept': 'application/json'}
    response = requests.post(url, headers=headers, json=SEARCH_CRITERIA, timeout=120)
    if response.status_code == 200:
        logging.info(f"Offers check: SUCCESS\nSuccessfully hired GPUs: {successful_gpu}/{MAX_GPU}\nDestroyed instances: {destroyed_instances_count}\nIgnored machine IDs: {IGNORE_MACHINE_IDS}")
        for gpu_model in [GPU_MARKET]:  
            logging.info(f"Placing market GPU orders for: {gpu_model}")

        try:
            offers = response.json().get('offers', [])
            
            # Calculate dph_per_gpu and sort offers
            offers_with_dph_per_gpu = []
            for offer in offers:
                gpu_name = offer.get('gpu_name')
                num_gpus = offer.get('num_gpus', 1)  # Assume 1 if not specified
                dph_total = offer.get('dph_total')
                if gpu_name == GPU_MARKET:
                    dph_per_gpu = dph_total / num_gpus
                    offers_with_dph_per_gpu.append((offer, dph_per_gpu))
                    
            # Sort offers based on dph_per_gpu
            sorted_offers = sorted(offers_with_dph_per_gpu, key=lambda x: x[1])
            
            # Append sorted and filtered offers
            filtered_offers = [offer[0] for offer in sorted_offers]

            if filtered_offers:
                logging.info("Matching offers found for selected GPU.")
            else:
                logging.info("No matching offers found for selected GPU.")
            return {"offers": filtered_offers}
        except ChunkedEncodingError as ce:
            logging.error(f"ChunkedEncodingError occurred during the API request: {ce}")
            return {}
        except requests.exceptions.RequestException as re:
            logging.error(f"RequestException occurred during the API request: {re}")
            return {}
        except Exception as e:
            logging.error(f"Failed to parse JSON from API response during offers check: {e}")
            return {}
    else:
        logging.error(f"Offers check failed. Status code: {response.status_code}. Response: {response.text}")
        return {}

def place_order(offer_id, cuda_max_good):
    url = f"https://console.vast.ai/api/v0/asks/{offer_id}/?api_key={api_key}"
    if cuda_max_good >= 12:
        image = "nvidia/cuda:12.0.1-devel-ubuntu20.04"
    else:
        image = "nvidia/cuda:11.1.1-devel-ubuntu20.04"

    payload = {
        "client_id": "me",
        "image": image,
        "disk": 3,
        "label": "tr4vler_MARKET_ORDER",
        "onstart": f"wget https://github.com/woodysoil/XenblocksMiner/releases/download/v1.1/xenblocksMiner-v1.1.1-Linux-x86_64.tar.gz && tar -vxzf xenblocksMiner-v1.1.1-Linux-x86_64.tar.gz && chmod +x xenblocksMiner && (echo -e \"{eip55_address}\\n0\" | sudo nohup ./xenblocksMiner >> miner.log 2>&1 &) && (while true; do sleep 10; : > miner.log; done) &"
    
    }
    headers = {'Accept': 'application/json'}
    response = requests.put(url, headers=headers, json=payload)
    return response.json()


    
def monitor_instance_for_running_status(instance_id, machine_id, api_key, gpu_model, timeout=600, interval=30):
    global total_ordered_gpus, successful_gpu  
    end_time = time.time() + timeout
    instance_running = False
    gpu_utilization_met = False
    check_counter = 0
    max_checks = timeout // interval
    while time.time() < end_time:
        url = f"https://console.vast.ai/api/v0/instances/{instance_id}?api_key={api_key}"
        headers = {'Accept': 'application/json'}
        response = requests.get(url, headers=headers)
        check_counter += 1
        if response.status_code == 200:
            instance_data = response.json()["instances"]
            status = instance_data.get('actual_status', 'unknown')
            gpu_utilization = instance_data.get('gpu_util', 0) or 0
            amnt_gpus = instance_data.get('num_gpus', 1)  
            if status == "running":
                if gpu_utilization >= 90:
                    logging.info(f"Check #{check_counter}/{max_checks}: Instance {instance_id} ({amnt_gpus}xGPU) is up and running with GPU utilization at {gpu_utilization}%!")
                    instance_running = True
                    gpu_utilization_met = True
                    successful_gpu += amnt_gpus
                    logging.info(f"Successfuly hired GPUs: {successful_gpu}")
                    break
                else:
                    logging.info(f"Check #{check_counter}/{max_checks}: Instance {instance_id} ({amnt_gpus}xGPU) is up but GPU utilization is {gpu_utilization}%. Waiting for next check...")
            else:
                logging.info(f"Check #{check_counter}/{max_checks}: Instance {instance_id} ({amnt_gpus}xGPU) status: {status}. Waiting for next check...")
        else:
            logging.error(f"Check #{check_counter}/{max_checks}: Error fetching status for instance {instance_id}. Status code: {response.status_code}. Response: {response.text}")
        time.sleep(interval)

    if not instance_running or not gpu_utilization_met:
        logging.warning(f"Instance {instance_id} did not meet required conditions after {check_counter} checks. Destroying this instance.")
        if destroy_instance(instance_id, machine_id, api_key):
            total_ordered_gpus -= amnt_gpus  # Decrement total_ordered_gpus by the number of GPUs from the destroyed instance
            logging.info(f"Decremented total rented GPUs by {amnt_gpus}. New total: {total_ordered_gpus}")
            return False

    return instance_running and gpu_utilization_met


def destroy_instance(instance_id, machine_id, api_key):
    global IGNORE_MACHINE_IDS, destroyed_instances_count, total_ordered_gpus
    url = f"https://console.vast.ai/api/v0/instances/{instance_id}/?api_key={api_key}"
    headers = {'Accept': 'application/json'}
  
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code

        if response.json().get('success') == True:
            logging.info(f"Successfully destroyed instance {instance_id}.")
            config['IGNORE_MACHINE_IDS'].append(machine_id)
            logging.info(f"Added machine_id: {machine_id} to the ignore list.")
            save_config(config)  # Save changes to config.json
            destroyed_instances_count += 1  # Increment the counter
            return True
        else:
            logging.error(f"Failed to destroy instance {instance_id}. API did not return a success status. Response: {response.text}")
            return False

    except requests.HTTPError as e:
        logging.error(f"HTTP error occurred while trying to destroy instance {instance_id}: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred while trying to destroy instance {instance_id}: {e}")
        return False


def handle_instance(instance_id, machine_id, api_key, gpu_model, lock):
    global successful_gpu, successful_orders
    instance_success = monitor_instance_for_running_status(instance_id, machine_id, api_key, gpu_model)  # Pass to this function
    if instance_success:
        with lock:  # This acquires the lock and releases it when the block is exited
            successful_orders += 1
            if successful_gpu >= MAX_GPU:
                logging.info("Maximum order limit reached. Exiting...")


# Main Loop
successful_orders_lock = threading.Lock()

# Test API connection first
test_api_connection()

def main_loop():
    global successful_orders, total_ordered_gpus
    last_check_time = time.time() - CHECK_INTERVAL  # Initialize to ensure first check happens immediately
    threads = []

    # Update loop condition to also check total_ordered_gpus against MAX_GPU
    while total_ordered_gpus <= MAX_GPU:
        current_time = time.time()
        if current_time - last_check_time >= CHECK_INTERVAL:
            offers = search_gpu(successful_orders).get('offers', [])
            last_check_time = current_time  # Reset the last check time
            for offer in offers:
                machine_id = offer.get('machine_id')
                gpu_model = offer.get('gpu_name')
                cuda_max_good = offer.get('cuda_max_good')
                num_gpus = offer.get('num_gpus', 1)  # Default to 1 if not specified
                if machine_id not in IGNORE_MACHINE_IDS and total_ordered_gpus + num_gpus <= MAX_GPU:
                    response = place_order(offer["id"], cuda_max_good)
                    if 'new_contract' in response:
                        instance_id = response.get('new_contract')
                        if instance_id:
                            logging.info(f"Successfully placed order for {gpu_model} with machine_id: {machine_id}. Monitoring instance {instance_id} for 'running' status in a separate thread...")
                            thread = threading.Thread(target=handle_instance, args=(instance_id, machine_id, api_key, gpu_model, successful_orders_lock))
                            thread.start()  # Start the thread
                            threads.append(thread)
                            total_ordered_gpus += num_gpus  # Increment the total ordered GPUs count
                            logging.info(f"Total rented GPUs: {total_ordered_gpus}")
                            time.sleep(1)
                        else:
                            logging.error(f"Order was successful but couldn't retrieve 'new_contract' (instance ID) for machine_id: {machine_id}")
                    else:
                        logging.warning(f"Failed to place order for offer ID {offer['id']} for machine_id: {machine_id}.")
                if total_ordered_gpus >= MAX_GPU:
                    break  # Exit the loop if MAX_GPU is reached
            if total_ordered_gpus >= MAX_GPU:
                break  # Exit the loop if MAX_GPU is reached
        else:
            break
        time.sleep(5)

    for thread in threads:
        thread.join()  # Wait for all threads to finish


while successful_gpu < MAX_GPU:
    main_loop() 

logging.info("Script finished execution.")

         
