import requests
import logging
import time
import json
import paramiko
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


# Main Script
config = load_config()
API_KEY = config['API_KEY']
ETH_ADDRESS = config['ETH_ADDRESS']
private_key_path = config['PRIVATE_KEY_PATH']
DEV = config['DEV']
passphrase = config['PASSPHRASE']

# Logging Configuration

class LogFilter(logging.Filter):
    def filter(self, record):
        unwanted_messages = [
            "Connected (version 2.0, client OpenSSH_8.2p1)",
            "Auth banner: b'Welcome to vast.ai.",
            "Authentication (publickey) successful!"
        ]
        return not any(msg in record.getMessage() for msg in unwanted_messages)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
log_filter = LogFilter()
for handler in logging.getLogger().handlers:
    handler.addFilter(log_filter)

# Load API Key
api_key = API_KEY


# Define Functions
def eip55_encode(address):
    if not address:
        return None
    return to_checksum_address(address)

erc20_address = ETH_ADDRESS
eip55_address = eip55_encode(erc20_address)
dev_fee = DEV

def instance_list(api_key):
    url = f'https://console.vast.ai/api/v0/instances/?api_key={api_key}'
    headers = {'Accept': 'application/json'}
    instance_ids = []
    ssh_info_list = []

    for attempt in range(3):  # Retrying up to 3 times
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                response_json = response.json()
                if 'instances' not in response_json:
                    logging.error("'instances' key not found in response. Please check the API documentation for the correct structure.")
                    return ssh_info_list
                instances = response_json['instances']
                logging.info("Updating your instances now!")
                for instance in instances:
                    instance_id = instance.get('id', 'N/A')
                    instance_ids.append(instance_id)  
                    ssh_host = instance.get('ssh_host', 'N/A')
                    ssh_port = instance.get('ssh_port', 'N/A')
                    
                    ssh_info = {
                        'instance_id': instance_id,
                        'ssh_host': ssh_host,
                        'ssh_port': ssh_port,
                    }
                    ssh_info_list.append(ssh_info)
                    
                break  # Break out of the retry loop upon success
            elif response.status_code == 429:
                logging.error("Too many requests, retrying in 10 seconds...")
                if attempt < 2:  # Wait only if we have retries left
                    time.sleep(10)
                else:
                    logging.error("Maximum retries reached. Please try again later.")
            elif response.status_code == 401:
                # Handle Unauthorized error
                logging.error("Failed to retrieve instances. Status code: 401. Response: %s", response.text)
                logging.error("This action requires a valid login. Please make sure that you provided correct API key.")
                break  # No need to retry, authorization issues cannot be solved by retrying
            else:
                logging.error("Failed to retrieve instances. Status code: %s. Response: %s", response.status_code, response.text)
                break  # Exit loop if an unrelated error occurs
        except requests.exceptions.RequestException as e:
            logging.error("A requests exception occurred: %s", str(e))
            break  # Exit loop if a request-related exception occurs
        except Exception as e:
            logging.error("An unexpected error occurred: %s", str(e))
            break  # Exit loop for any other exception
    return instance_ids, ssh_info_list  # Return the collected instance IDs

def rebuild_instance(api_key, instance_id):
    url = f"https://console.vast.ai/api/v0/instances/{instance_id}/"  
    onstart_script = f"wget https://github.com/woodysoil/XenblocksMiner/releases/download/v1.1.3/xenblocksMiner-v1.1.3-Linux-x86_64.tar.gz && tar -vxzf xenblocksMiner-v1.1.3-Linux-x86_64.tar.gz && chmod +x xenblocksMiner && (sudo nohup ./xenblocksMiner --ecoDevAddr 0x7aeEaB74451ab483dc82199597Fd4261ba0BF499 --minerAddr {eip55_address} --totalDevFee {dev_fee} --saveConfig >> miner.log 2>&1 &) && (while true; do sleep 10; : > miner.log; done) &"
    payload = {
        "label": "tr4vler_REBUILDER",
    }
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}',  
        'Content-Type': 'application/json'
    }
    response = requests.put(url, headers=headers, json=payload)
    if response.status_code == 200:
        pass
    else:
        logging.error(f"Failed to update instance {instance_id}. Status code: {response.status_code}. Response: {response.text}")
        logging.error(f"Response body: {response.text}")
        
        
def update_onstart_script(ssh_host, ssh_port, username, private_key_path, instance_id, passphrase=None):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        try:
            key = paramiko.Ed25519Key(filename=private_key_path, password=passphrase)
        except paramiko.ssh_exception.PasswordRequiredException:
            print("Private key file is encrypted and requires a passphrase.")
            return False
        except paramiko.ssh_exception.SSHException as e:
            print(f"Failed to decrypt private key with provided passphrase: {e}")
            return False

        ssh.connect(ssh_host, port=ssh_port, username=username, pkey=key)
        update_command = f'echo "wget https://github.com/woodysoil/XenblocksMiner/releases/download/v1.1.3/xenblocksMiner-v1.1.3-Linux-x86_64.tar.gz && tar -vxzf xenblocksMiner-v1.1.3-Linux-x86_64.tar.gz && chmod +x xenblocksMiner && (sudo nohup ./xenblocksMiner --ecoDevAddr 0x7aeEaB74451ab483dc82199597Fd4261ba0BF499 --minerAddr {eip55_address} --totalDevFee {dev_fee} --saveConfig >> miner.log 2>&1 &) && (while true; do sleep 10; : > miner.log; done) &" > /root/onstart.sh'
        ssh.exec_command(update_command)
        return True

    except Exception as e:
        print(f"Failed to connect instance {instance_id}: {e}")
        return False

    finally:
        ssh.close()
        
def reboot_instance(api_key, instance_id):
    url = f'https://console.vast.ai/api/v0/instances/reboot/{instance_id}/'
    params = {'api_key': api_key}
    headers = {'Accept': 'application/json'}
    
    response = requests.put(url, headers=headers, params=params)

    if response.status_code == 200:
        # Optionally, check response body for success confirmation
        response_data = response.json()
        if 'success' in response_data and response_data['success']:
            return True
        else:
            return False
    else:
        return False


      


# Main Loop
username = "root"
if __name__ == "__main__":
    instance_ids, ssh_info_list = instance_list(API_KEY) 
    for ssh_info in ssh_info_list:
        instance_id = ssh_info['instance_id']
        ssh_host = ssh_info['ssh_host']
        ssh_port = ssh_info['ssh_port']

        rebuild_instance(API_KEY, instance_id)

        update_success = update_onstart_script(ssh_host, ssh_port, username, private_key_path, instance_id, passphrase) 
        if update_success:
            logging.info(f"Instance {instance_id} updated successfully. Rebooting now.")
            reboot_instance(API_KEY, instance_id)
        else:
            pass
logging.info("Script finished execution.")