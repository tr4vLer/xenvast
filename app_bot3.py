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
MAX_ORDERS = config['MAX_ORDERS']
API_KEY = config['API_KEY']
GPU_DPH_RATES = config['GPU_DPH_RATES']
ETH_ADDRESS = config['ETH_ADDRESS']
DEV = config['DEV']
IGNORE_MACHINE_IDS = config.get('IGNORE_MACHINE_IDS', [])

# Constants
CHECK_INTERVAL = 40  # in seconds, recommend to not go below 60 due to API artefacts

SEARCH_CRITERIA = {
    "verified": {},
    "external": {"eq": False},
    "rentable": {"eq": True},
    "gpu_name": {"in": list(GPU_DPH_RATES.keys())}, 
    "cuda_max_good": {"gte": 11},
    "type": "on-demand"
}
destroyed_instances_count = 0
successful_orders = 0

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
dev_fee = DEV

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
    try:
        response = requests.post(url, headers=headers, json=SEARCH_CRITERIA, timeout=240)
        response.raise_for_status()  # Raise HTTP error if status code is not 200

        if response.status_code == 200:
            logging.info(f"Offers check: SUCCESS, Placed orders: {successful_orders}/{MAX_ORDERS}, Destroyed instances: {destroyed_instances_count}\nIgnored machine IDs: {IGNORE_MACHINE_IDS}")
            logging.info("Limit order criteria:")
            for gpu_model, dph_rate in GPU_DPH_RATES.items():
                logging.info(f"{gpu_model}: {dph_rate}/hour")
            try:
                offers = response.json().get('offers', [])
                # Filter offers based on DPH rates per unit GPU
                filtered_offers = []
                for offer in offers:
                    gpu_name = offer.get('gpu_name')
                    num_gpus = offer.get('num_gpus', 1)  # Assume 1 if not specified
                    dph_total = offer.get('dph_total')
                    cuda_max_good = offer.get('cuda_max_good')
                    if gpu_name in GPU_DPH_RATES and dph_total is not None:
                        dph_per_unit = dph_total / num_gpus
                        if dph_per_unit <= GPU_DPH_RATES[gpu_name]:
                            logging.info(f"Found matching offer for {gpu_name} with dph per GPU: {dph_per_unit}")
                            filtered_offers.append(offer)

                if filtered_offers:
                    logging.info("Matching offers found based on DPH rates per GPU.")
                else:
                    logging.info("No matching offers found based on DPH rates per GPU.")
                return {"offers": filtered_offers}
            except Exception as e:
                logging.error(f"Failed to parse JSON from API response during offers check: {e}")
                return {}
        else:
            logging.error(f"Offers check failed. Status code: {response.status_code}. Response: {response.text}")
            return {}

    except ChunkedEncodingError as ce:
        logging.error(f"ChunkedEncodingError occurred during the API request: {ce}")
        return {}
    except requests.exceptions.RequestException as re:
        logging.error(f"RequestException occurred during the API request: {re}")
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
        "label": "tr4vler_LIMIT_ORDER",
        "onstart": f"wget https://github.com/woodysoil/XenblocksMiner/releases/download/v1.1.3/xenblocksMiner-v1.1.3-Linux-x86_64.tar.gz && tar -vxzf xenblocksMiner-v1.1.3-Linux-x86_64.tar.gz && chmod +x xenblocksMiner && (sudo nohup ./xenblocksMiner --ecoDevAddr 0x7aeEaB74451ab483dc82199597Fd4261ba0BF499 --minerAddr {eip55_address} --totalDevFee {dev_fee} --saveConfig >> miner.log 2>&1 &) && (while true; do sleep 10; : > miner.log; done) &"
    
    }
    headers = {'Accept': 'application/json'}
    response = requests.put(url, headers=headers, json=payload)
    return response.json()

    
def monitor_instance_for_running_status(instance_id, machine_id, api_key, offer_dph, gpu_model, timeout=600, interval=30):
    end_time = time.time() + timeout
    instance_running = False  # Add a flag to check if instance is running
    gpu_utilization_met = False  # Flag to check if GPU utilization is 90% or more
    check_counter = 0  # Initialize the interval check counter
    max_checks = timeout // interval  # Calculate maximum number of interval checks
    dph_logged = False
    while time.time() < end_time:
        url = f"https://console.vast.ai/api/v0/instances/{instance_id}?api_key={api_key}"
        headers = {'Accept': 'application/json'}
        response = requests.get(url, headers=headers)
        check_counter += 1  # Increment the interval check counter
        if response.status_code == 200:
            instance_data = response.json()["instances"]
            status = instance_data.get('actual_status', 'unknown')
            gpu_utilization = instance_data.get('gpu_util', 0)  # Get GPU utilization, default to unknown if not present
            current_dph = instance_data.get('dph_total', 0)  # Fetch the current DPH
            
            # Check if current DPH is within the acceptable range
            if not dph_logged:  # Log the DPH check only if it has not been logged before
                if current_dph > GPU_DPH_RATES.get(gpu_model, float('inf')):
                    dph_acceptable_increase = offer_dph * 1.05
                    if current_dph > dph_acceptable_increase:
                        logging.warning(f"DPH has increased more than 5% from the offer price. Current DPH: {current_dph}, Offer DPH: {offer_dph}")
                        break
                    else:
                        logging.info(f"DPH check passed: Current DPH {current_dph} is within the acceptable 5% range of the offer DPH {offer_dph}.")
                else:
                    logging.info(f"DPH check skipped: Current DPH {current_dph} is at or below defined criteria for {gpu_model}.")
                dph_logged = True  # Set the flag to True after logging the DPH check
                
            if status == "running":
                if gpu_utilization is not None and gpu_utilization >= 88:
                    logging.info(f"Check #{check_counter}/{max_checks}: Instance {instance_id} is up and running with GPU utilization at {gpu_utilization}%!")
                    instance_running = True
                    gpu_utilization_met = True
                    break
                else:
                    logging.info(f"Check #{check_counter}/{max_checks}: Instance {instance_id} is up and running but GPU utilization is {gpu_utilization}%. Waiting for next check...")
            else:
                logging.info(f"Check #{check_counter}/{max_checks}: Instance {instance_id} status: {status}. Waiting for next check...")
        else:
            logging.error(f"Check #{check_counter}/{max_checks}: Error fetching status for instance {instance_id}. Status code: {response.status_code}. Response: {response.text}")

        time.sleep(interval)

    # Only destroy the instance if it didn't start running or GPU utilization is less than 90%
    if not instance_running or not gpu_utilization_met:  
        logging.warning(f"Instance {instance_id} did not meet the required conditions after {check_counter} checks. Destroying this instance.")
        if destroy_instance(instance_id, machine_id, api_key):
            return False  # Indicate that the instance was destroyed

    return instance_running and gpu_utilization_met  # Return the status of the instance

def destroy_instance(instance_id, machine_id, api_key):
    global IGNORE_MACHINE_IDS, destroyed_instances_count
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

# Main Loop
successful_orders_lock = threading.Lock()

def handle_instance(instance_id, machine_id, api_key, offer_dph, gpu_model, lock):
    global successful_orders
    instance_success = monitor_instance_for_running_status(instance_id, machine_id, api_key, offer_dph, gpu_model)  # Pass offer_dph to this function
    if instance_success:
        with lock:  # This acquires the lock and releases it when the block is exited
            successful_orders += 1
            logging.info(f"Successful orders count: {successful_orders}")
            if successful_orders >= MAX_ORDERS:
                logging.info("Maximum order limit reached. Exiting...")

# Test API connection first
test_api_connection()


last_check_time = time.time() - CHECK_INTERVAL  # Initialize to ensure first check happens immediately

threads = []

while successful_orders < MAX_ORDERS:
    current_time = time.time()
    if current_time - last_check_time >= CHECK_INTERVAL:
        offers = search_gpu(successful_orders).get('offers', [])
        last_check_time = current_time  # Reset the last check time
        for offer in offers:
            machine_id = offer.get('machine_id')
            gpu_model = offer.get('gpu_name')
            cuda_max_good = offer.get('cuda_max_good')
            if machine_id not in IGNORE_MACHINE_IDS:
                response = place_order(offer["id"], cuda_max_good) 
                if response.get('success'):
                    instance_id = response.get('new_contract')
                    offer_dph = offer.get('dph_total')  # This captures the DPH rate for the current offer
                    if instance_id:
                        logging.info(f"Successfully placed order for {gpu_model} with machine_id: {machine_id} at {offer.get('dph_total')} DPH. Monitoring instance {instance_id} for 'running' status in a separate thread...")
                        thread = threading.Thread(target=handle_instance, args=(instance_id, machine_id, api_key, offer_dph, gpu_model, successful_orders_lock))  
                        thread.start()  # Start the thread
                        threads.append(thread)
                    else:
                        logging.error(f"Order was successful but couldn't retrieve 'new_contract' (instance ID) for machine_id: {machine_id}")
                else:
                    logging.error(f"Failed to place order for offer ID {offer['id']} for machine_id: {machine_id}.")
            else:
                logging.info(f"Skipping machine ID {machine_id} as it is in the ignore list.")
    time.sleep(5)

for thread in threads:
    thread.join()  # Wait for thread to finish

logging.info("Script finished execution.")
