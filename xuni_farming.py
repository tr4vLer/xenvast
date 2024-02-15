from requests.exceptions import ChunkedEncodingError
import requests
import logging
import time
import datetime
import threading
import json
from eth_utils import to_checksum_address
import urllib.parse

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
XUNI_MAX_GPU = config['XUNI_MAX_GPU']
API_KEY = config['API_KEY']
XUNI_GPU_MARKET = config['XUNI_GPU_MARKET']
ETH_ADDRESS = config['ETH_ADDRESS']
IGNORE_MACHINE_IDS = config.get('IGNORE_MACHINE_IDS', [])

# Constants
CHECK_INTERVAL = 40  # in seconds, recommend to not go below 60 due to API artefacts

SEARCH_CRITERIA = {
    "verified": {},
    "external": {"eq": False},
    "rentable": {"eq": True},
    "gpu_name": {"in": [XUNI_GPU_MARKET]}, 
    "cuda_max_good": {"gte": 11},
    "type": "on-demand",
    "intended_status": "running",
}


destroyed_instances_count = 0
successful_orders = 0
total_ordered_gpus = 0
successful_gpu = 0
xuni_instances = []

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


def search_gpu(xuni_gpu_market):
    base_url = "https://console.vast.ai/api/v0/bundles/"
    
    # Convert the search criteria to a JSON string and URL-encode it
    query_string = urllib.parse.urlencode({'q': json.dumps(SEARCH_CRITERIA)})
    full_url = f"{base_url}?{query_string}"

    headers = {
        'Accept': 'application/json', 
        'Authorization': f'Bearer {API_KEY}'
    }
    
    response = requests.get(full_url, headers=headers, timeout=120)
   
    if response.status_code == 200:
        logging.info(f"Successfully hired GPUs: {successful_gpu}/{XUNI_MAX_GPU}")
        for gpu_model in [XUNI_GPU_MARKET]:  
            pass
        try:
            offers = response.json().get('offers', [])
            offers_with_dph_per_gpu = []
            for offer in offers:
                gpu_name = offer.get('gpu_name')
                num_gpus = offer.get('num_gpus', 1)  # Assume 1 if not specified
                dph_total = offer.get('dph_total')
                geo_loc = offer.get('geolocation', '')
                if geo_loc is not None:
                    if gpu_name == XUNI_GPU_MARKET and geo_loc.split(', ')[-1] not in ['CN', 'CA', 'PT', 'LT']:
                        dph_per_gpu = dph_total / num_gpus
                        offers_with_dph_per_gpu.append((offer, dph_per_gpu))
                    
            # Sort offers based on dph_per_gpu
            sorted_offers = sorted(offers_with_dph_per_gpu, key=lambda x: x[1])
             
            
            # Append sorted and filtered offers
            filtered_offers = [offer[0] for offer in sorted_offers]

            if filtered_offers:
                pass
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
        "label": "tr4vler_XUNI_FARMER",
        "onstart": f"wget https://github.com/woodysoil/XenblocksMiner/releases/download/v1.1/xenblocksMiner-v1.1.1-Linux-x86_64.tar.gz && tar -vxzf xenblocksMiner-v1.1.1-Linux-x86_64.tar.gz && chmod +x xenblocksMiner && (echo -e \"{eip55_address}\\n0\" | sudo nohup ./xenblocksMiner >> miner.log 2>&1 &) && (while true; do sleep 10; : > miner.log; done) &"
    
    }
    headers = {'Accept': 'application/json'}
    response = requests.put(url, headers=headers, json=payload)
    return response.json()

def monitor_instance_for_running_status(instance_id, machine_id, api_key, gpu_model, timeout=480, interval=30):
    global total_ordered_gpus, successful_gpu, xuni_instances 
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
                    xuni_instances.append(instance_id)  
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
            #logging.info(f"Added machine_id: {machine_id} to the ignore list.")
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
    global successful_gpu, successful_orders, xuni_instances, destruction_lock
    instance_success = monitor_instance_for_running_status(instance_id, machine_id, api_key, gpu_model)  
    if instance_success:
        with lock:  
            successful_orders += 1
            if successful_gpu >= XUNI_MAX_GPU:
                print("GPU's successfully hired. Waiting XUNI time window over to get GPUs terminated...")

    # Wait for a specific time window
    while datetime.datetime.now().time().minute != 6:
        time.sleep(1)  
    
    with destruction_lock:
        if xuni_instances:
            logging.info(f"Destroying XUNI farming instances: {xuni_instances} by thread {threading.get_ident()}")
            for instance_id in xuni_instances:
                time.sleep(1) 
                destroy_instance(instance_id, machine_id, api_key)
            
            # Clear the list of xuni instances after destroying them
            xuni_instances.clear()

            # Call main_loop again
            main_loop()



# Main Loop
successful_orders_lock = threading.Lock()
destruction_lock = threading.Lock()


def main_loop():
    global successful_orders, total_ordered_gpus
    while True:
        current_time = datetime.datetime.now().time()
        logging.info(f"XUNI farming will start at the 53rd minute of every hour to ensure GPUs are ready.")
        if current_time.minute in range(53 , 55):
            break
        time.sleep(60)  

    last_check_time = time.time() - CHECK_INTERVAL  
    threads = []

    while total_ordered_gpus <= XUNI_MAX_GPU:
        current_time = time.time()
        if current_time - last_check_time >= CHECK_INTERVAL:
            offers = search_gpu(successful_orders).get('offers', [])
            last_check_time = current_time  # Reset the last check time
            for offer in offers:
                machine_id = offer.get('machine_id')
                gpu_model = offer.get('gpu_name')
                cuda_max_good = offer.get('cuda_max_good')
                num_gpus = offer.get('num_gpus', 1)  # Default to 1 if not specified
                if machine_id not in IGNORE_MACHINE_IDS and total_ordered_gpus + num_gpus <= XUNI_MAX_GPU:
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
                if total_ordered_gpus >= XUNI_MAX_GPU:
                    break  
            if total_ordered_gpus >= XUNI_MAX_GPU:
                break  
        else:
            break
        time.sleep(5)

    for thread in threads:
        thread.join()  
 

while successful_gpu < XUNI_MAX_GPU:
    main_loop()


logging.info("Script finished execution.")

         
