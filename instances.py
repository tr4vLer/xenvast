import requests
import logging
import datetime
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
        pass
    except json.JSONDecodeError:
        pass
        
# Main Script
config = load_config()
API_KEY = config['API_KEY']       
private_key_path = config['PRIVATE_KEY_PATH']
passphrase = config['PASSPHRASE']


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load API Key
api_key = API_KEY

current_date = datetime.datetime.now()

# Load table_perf.json
def load_table_perf():
    try:
        with open('table_perf.json', 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return []

# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return super().default(o)

total_super_blocks = 0
total_normal_blocks = 0
total_xuni_blocks = 0
total_hash_rate = 0 
def instance_list():
    global total_super_blocks, total_normal_blocks, total_xuni_blocks, total_hash_rate
    """Function to list instances and get SSH information."""
    url = f'https://console.vast.ai/api/v0/instances/?api_key={api_key}'
    headers = {'Accept': 'application/json'}
    instances = [] 
    table_perf_data = load_table_perf()
 
    
    for attempt in range(3):  # Retrying up to 3 times
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                response_json = response.json()
                if 'instances' not in response_json:
                    logging.error("'instances' key not found in response. Please check the API documentation for the correct structure.")
                    return 
                instances_data = response_json['instances']
                 
                for instance_data in instances_data:
                    ssh_link = f"ssh -p {instance_data.get('ssh_port', 'N/A')} root@{instance_data.get('ssh_host', 'N/A')} -L 8080:localhost:8080"
                    matching_entry = next((item for item in table_perf_data if item.get('ssh_link', 'N/A') == ssh_link), None)
                    if matching_entry:
                        total_super_blocks += int(matching_entry.get('super_blocks', 0))
                        total_normal_blocks += int(matching_entry.get('normal_blocks', 0))
                        total_xuni_blocks += int(matching_entry.get('xuni_blocks', 0))
                        total_hash_rate += float(matching_entry.get('hash_rate', 0.0))   
                        total_hash_rate = round(total_hash_rate, 2)

                    
                    actual_status = instance_data.get('actual_status', 'N/A')
                    if actual_status != 'running':
                        gpu_util = 'N/A'
                        cpu_util = 'N/A'
                    else:
                        gpu_util_value = instance_data.get('gpu_util', 'N/A')
                        if isinstance(gpu_util_value, (int, float)):
                            gpu_util = round(gpu_util_value, 2)  
                        else:
                            gpu_util = 'N/A'  
                        cpu_util_value = instance_data.get('cpu_util', 'N/A')
                        if isinstance(cpu_util_value, (int, float)):
                            cpu_util = round(cpu_util_value, 2)  
                        else:
                            cpu_util = 'N/A'  

                    disk_util = instance_data.get('disk_util', 'N/A')
                    disk_space = instance_data.get('disk_space', 'N/A') 
                    if disk_util is None or disk_util == 'N/A' or disk_util == -1:
                        disk_util = 0.01
                    gpu_ram_mb = instance_data.get('gpu_ram', 'N/A')
                    
                    end_timestamp = instance_data.get('end_date', 'N/A')
                    duration = instance_data.get('duration')
                    start_timestamp = instance_data.get('start_date', 'N/A')
                    start_date_str = str(start_timestamp) if start_timestamp else 'N/A'
                    end_date_str = str(end_timestamp) if end_timestamp else 'N/A'
                    start_date = datetime.datetime.utcfromtimestamp(float(start_timestamp)) if start_timestamp else None
                    end_date = datetime.datetime.utcfromtimestamp(float(end_timestamp)) if end_timestamp else None
                    current_date = datetime.datetime.utcnow()
                    instance_id_reboot = instance_data.get('id', 'N/A')
                    instance_id_rebuild = instance_data.get('id', 'N/A')
                    instance_id_destroy = instance_data.get('id', 'N/A')
                    num_gpus = instance_data.get('num_gpus', 'N/A')

                    # Calculate age with days, hours, minutes, and seconds
                    if start_date:
                        age_timedelta = current_date - start_date
                        days = age_timedelta.days
                        hours, remainder = divmod(age_timedelta.seconds, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        age = f"{days}d {hours}h {minutes}m"
                    else:
                        age = 'N/A'
                    
                    # Before calculating hdd_usage
                    if disk_space == 'N/A' or not isinstance(disk_space, (int, float)):
                        disk_space = 1.0  # Default value to avoid division by zero or errors
                    
                    if disk_util == 'N/A' or not isinstance(disk_util, (int, float)):
                        disk_util = 0.01  # Default value to ensure some minimal disk utilization
                    
                    # Now, disk_space and disk_util are guaranteed to be numeric, and the division will not raise an error
                    hdd_usage = round((disk_util / max(disk_space, 1)) * 100, 2)
                    gpu_ram_gb = 'N/A'
                    if gpu_ram_mb != 'N/A' and isinstance(gpu_ram_mb, (int, float)):
                        gpu_ram_gb = round(gpu_ram_mb / 1024, 2) * num_gpus
                    else:
                        gpu_ram_gb = 0.0 
                    gpu_ram_used_gb = 'N/A'
                    if gpu_util != 'N/A' and isinstance(gpu_util, (int, float)) and isinstance(gpu_ram_gb, (int, float)):
                        gpu_ram_used_gb = round((gpu_util / 100) * gpu_ram_gb, 2)
                    else:
                        gpu_ram_used_gb = 0.0
                    start_datetime = 'N/A'
                    end_datetime = 'N/A'
                    inst_age = 'N/A'
                    if start_timestamp is not None:
                        start_datetime = datetime.datetime.utcfromtimestamp(float(start_timestamp))
                    if end_timestamp is not None:
                        end_datetime = datetime.datetime.utcfromtimestamp(float(end_timestamp))
                    if isinstance(duration, tuple):
                        logging.error("Duration is a tuple instead of a single value.")
                    elif duration is not None:
                        inst_age_timedelta = datetime.timedelta(seconds=float(duration))
                        inst_age_days = inst_age_timedelta.days
                        inst_age_hours, inst_age_remainder = divmod(inst_age_timedelta.seconds, 3600)
                        inst_age_minutes, inst_age_seconds = divmod(inst_age_remainder, 60)
                        inst_age = f"{inst_age_days}d {inst_age_hours}h {inst_age_minutes}m"
                    
 
                    if isinstance(cpu_util, (int, float)):  # Ensure it's a number
                        cpu_util = round(cpu_util, 2)
                    else:
                        cpu_util = 'N/A'  # Keep as 'N/A' if it's not a number
                    
                    # For 'dph_total'
                    dph_total = instance_data.get('dph_total', 0)  # Default to 0 if not found
                    if isinstance(dph_total, (int, float)):  # Ensure it's a number
                        dph_total = round(dph_total, 3)
                    else:
                        dph_total = 'N/A'  # Keep as 'N/A' if it's not a number
                    

   
                    instance = {
                        'instance_id': instance_data.get('id', 'N/A'),
                        'instance_id_reboot': instance_id_reboot,
                        'instance_id_rebuild': instance_id_rebuild,
                        'instance_id_destroy': instance_id_destroy,
                        'machine_id': instance_data.get('machine_id', 'N/A'),
                        'host_id': instance_data.get('host_id', 'N/A'),
                        'verification': instance_data.get('verification', 'N/A'),
                        'geolocation': instance_data.get('geolocation', 'N/A'),
                        'start_date': start_date_str,
                        'age': str(age),
                        'end_date': end_datetime,
                        'duration': inst_age,
                        'gpu_name': instance_data.get('gpu_name', 'N/A'),
                        'num_gpus': num_gpus,
                        'gpu_util': gpu_util,
                        'cpu_util': cpu_util,
                        'disk_space': disk_space,
                        'disk_util': disk_util,
                        'gpu_ram_gb': gpu_ram_gb,
                        'gpu_ram_used_gb': gpu_ram_used_gb,
                        'hdd_usage': hdd_usage,
                        'dph_total': dph_total,
                        'actual_status': actual_status,
                        'status_msg': instance_data.get('status_msg', 'N/A'),
                        'label': instance_data.get('label', 'N/A'),
                        'ssh_port': instance_data.get('ssh_port', 'N/A'),
                        'ssh_host': instance_data.get('ssh_host', 'N/A'),
                        'ssh_link': ssh_link,
                        'super_blocks': matching_entry.get('super_blocks', 'N/A') if matching_entry else 'N/A',
                        'normal_blocks': matching_entry.get('normal_blocks', 'N/A') if matching_entry else 'N/A',
                        'xuni_blocks': matching_entry.get('xuni_blocks', 'N/A') if matching_entry else 'N/A',
                        'hash_rate': matching_entry.get('hash_rate', 'N/A') if matching_entry else 'N/A',
                        'difficulty':  matching_entry.get('difficulty', 0) if matching_entry else 0,
                        'total_super_blocks': total_super_blocks,
                        'total_normal_blocks': total_normal_blocks,
                        'total_xuni_blocks': total_xuni_blocks,
                        'total_hash_rate': total_hash_rate,
                    }
                    
                    instances.append(instance)

                return instances

            elif response.status_code == 429:
                logging.error("Too many requests, retrying in 10 seconds...")
                if attempt < 2:
                    time.sleep(10)
                else:
                    logging.error("Maximum retries reached. Please try again later.")
            elif response.status_code == 401:
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

    return instances

if __name__ == "__main__":
    instances = instance_list()
    print(f"Stats: {total_hash_rate}h/s, normal:{total_normal_blocks}, super:{total_super_blocks}, xuni:{total_xuni_blocks} ")
    if instances:
        for instance in instances:
            print("Instance ID:", instance['instance_id'])
        
        # Save instances data to JSON file using custom encoder
        with open('instances.json', 'w') as f:
            json.dump(instances, f, cls=DateTimeEncoder, indent=4)

        sys.exit()  
    else:
        print("Failed to retrieve instances.")
        # Write empty list to JSON file
        with open('instances.json', 'w') as f:
            json.dump([], f)