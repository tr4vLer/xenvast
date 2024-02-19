import requests
import logging
import time
import json
import sys

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

config = load_config()
if config is not None:
    API_KEY = config.get('API_KEY')
    REMOVE_SCHEDULING = config.get('REMOVE_SCHEDULING')
    REMOVE_INACTIVE = config.get('REMOVE_INACTIVE')
    REMOVE_OFFLINE = config.get('REMOVE_OFFLINE')
else:
    API_KEY = None
    REMOVE_SCHEDULING = False  
    REMOVE_INACTIVE = False  
    REMOVE_OFFLINE = False 

# Logging Configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define status lists in a higher scope
status_scheduling = []
status_inactive = []
status_offline = []

def instance_list():
    url = f'https://console.vast.ai/api/v0/instances/?api_key={api_key}'
    headers = {'Accept': 'application/json'}

    for attempt in range(3):  # Retrying up to 3 times
        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                response_json = response.json()

                if 'instances' not in response_json:
                    logging.error("'instances' key not found in response. Please check the API documentation for the correct structure.")
                    return 
                instances = response_json['instances']
                for instance in instances:
                    instance_id = instance.get('id', 'N/A')
                    actual_status = instance.get('actual_status', 'N/A')
                    if actual_status.lower() == 'exited':
                        status_scheduling.append(instance_id)
                    if actual_status.lower() == 'created':
                        status_inactive.append(instance_id)                        
                    if actual_status.lower() == 'offline':
                        status_offline.append(instance_id)                        
                break

        except requests.exceptions.RequestException as e:
            logging.error("A requests exception occurred: %s", str(e))
            break  # Exit loop if a request-related exception occurs

        except Exception as e:
            logging.error("An unexpected error occurred: %s", str(e))
            break  # Exit loop for any other exception

    return 

def destroy_instance(instance_id, api_key):
    url = f"https://console.vast.ai/api/v0/instances/{instance_id}/?api_key={api_key}"
    headers = {'Accept': 'application/json'}
  
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()  

        if response.json().get('success') == True:
            logging.info(f"Successfully destroyed instance {instance_id}.")
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

# Main loop
def main_loop():
    while True:
        removed_instances = []  
        instance_list() 

        if REMOVE_SCHEDULING:
            print("Instances with SCHEDULING status:", status_scheduling)
            for instance_id in list(status_scheduling):  
                success = destroy_instance(instance_id, api_key)
                if success:
                    status_scheduling.remove(instance_id)
                    removed_instances.append(instance_id)
            if not status_scheduling:
                print("No SCHEDULING instances to be removed.")

        if REMOVE_INACTIVE:
            print("Instances with INACTIVE/STARTING status:", status_inactive)
            for instance_id in list(status_inactive):
                success = destroy_instance(instance_id, api_key)
                if success:
                    status_inactive.remove(instance_id)
                    removed_instances.append(instance_id)  
            if not status_inactive:
                print("No INACTIVE instances to be removed.")
        
        if REMOVE_OFFLINE:
            print("Instances with OFFLINE status:", status_offline)
            for instance_id in list(status_offline):
                success = destroy_instance(instance_id, api_key)  # Define success correctly
                if success:
                    status_offline.remove(instance_id)
                    removed_instances.append(instance_id)  
            if not status_offline:
                print("No OFFLINE instances to be removed.")

        if not (REMOVE_SCHEDULING or REMOVE_INACTIVE or REMOVE_OFFLINE):
            print("No status types were selected for removal!")
            break
        else:
            print("Removed instances:", removed_instances)
            break

    print("\n\nScript finished execution.")
    sys.exit()

if __name__ == "__main__":
    main_loop()
