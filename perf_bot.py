import requests
import logging
import paramiko
import re
import sys
import datetime
import time
from prettytable import PrettyTable 
from collections import defaultdict
import numpy as np
import json



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
private_key_path = config['PRIVATE_KEY_PATH']
passphrase = config['PASSPHRASE']
sort_column_index = config['SORT_COLUMN_INDEX']
sort_order = config['SORT_ORDER']
threshold = config['THRESHOLD']


# Define the log filter class
class LogFilter(logging.Filter):
    def filter(self, record):
        unwanted_messages = [
            "Connected (version 2.0, client OpenSSH_8.2p1)",
            "Auth banner: b'Welcome to vast.ai.",
            "Authentication (publickey) successful!",
            "Authentication (publickey) failed."
        ]
        return not any(msg in record.getMessage() for msg in unwanted_messages)

# Logging Configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
log_filter = LogFilter()
for handler in logging.getLogger().handlers:
    handler.addFilter(log_filter)


# Load API Key
api_key = API_KEY


def instance_list():
    """Function to list instances and get SSH information."""
    url = f'https://console.vast.ai/api/v0/instances/?api_key={api_key}'
    headers = {'Accept': 'application/json'}
    ssh_info_list = []
    total_dph_running_machines = 0  # Initialized at the start
    total_gpus_running = 0  # Counter for total GPUs of running instances

    for attempt in range(3):  # Retrying up to 3 times
        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                response_json = response.json()

                if 'instances' not in response_json:
                    logging.error("'instances' key not found in response. Please check the API documentation for the correct structure.")
                    return ssh_info_list, total_dph_running_machines
                instances = response_json['instances']

                for instance in instances:
                    instance_id = instance.get('id', 'N/A')
                    gpu_name = instance.get('gpu_name', 'N/A')
                    dph_total = instance.get('dph_total', 'N/A')
                    ssh_host = instance.get('ssh_host', 'N/A')
                    ssh_port = instance.get('ssh_port', 'N/A')
                    num_gpus = instance.get('num_gpus', 'N/A')
                    gpu_util = instance.get('gpu_util', 'N/A')
                    disk_util = instance.get('disk_util', 'N/A')
                    disk_space = instance.get('disk_space', 'N/A')
                    cpu_util = instance.get('cpu_util', 'N/A')
                    label = instance.get('label', 'N/A')
                    actual_status = instance.get('actual_status', 'N/A')
                    if actual_status.lower() == 'running':
                        total_dph_running_machines += float(dph_total)
                        total_gpus_running += int(num_gpus) 

                    ssh_info = {
                        'instance_id': instance_id,
                        'gpu_name': gpu_name,
                        'dph_total': dph_total,
                        'ssh_host': ssh_host,
                        'ssh_port': ssh_port,
                        'num_gpus': num_gpus,
                        'gpu_util': gpu_util,
                        'actual_status': actual_status,
                        'label': label,
                        'disk_util': disk_util,
                        'disk_space': disk_space,
                        'cpu_util': cpu_util
                    }
                    ssh_info_list.append(ssh_info)
                break

            elif response.status_code == 429:
                logging.error("Too many requests, retrying in 10 seconds...")
                if attempt < 2:  # Wait only if we have retries left
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

    return ssh_info_list, total_dph_running_machines, total_gpus_running, 

# Function to remove ANSI escape codes
def clean_ansi_codes(input_string):
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]', re.IGNORECASE)
    return ansi_escape.sub('', input_string)


instances_perf = []
def get_log_info(ssh_host, ssh_port, username, private_key_path, passphrase=None):
    # Create an SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Attempt to load the private key with the provided passphrase
        try:
            key = paramiko.Ed25519Key(filename=private_key_path, password=passphrase)
        except paramiko.ssh_exception.PasswordRequiredException:
            logging.error("Private key file is encrypted and requires a passphrase.")
            return None, None, None, None, None, None, None, None
        except paramiko.ssh_exception.SSHException as e:
            logging.error("Failed to decrypt private key with provided passphrase: %s", e)
            return None, None, None, None, None, None, None, None

        ssh.connect(ssh_host, port=ssh_port, username=username, pkey=key)
        ssh_link = f"ssh -p {ssh_port} root@{ssh_host} -L 8080:localhost:8080"
        
        # Determine the log file path
        log_file_path = '/root/XENGPUMiner/miner.log'  # Default path
        _, stdout, _ = ssh.exec_command('if [ -f /root/miner.log ]; then echo "/root/miner.log"; else echo "/root/XENGPUMiner/miner.log"; fi')
        file_path = stdout.read().decode().strip()
        if file_path == "/root/miner.log":
            log_file_path = file_path

        # Execute the command to get the log information
        _, stdout, _ = ssh.exec_command(f'tail -n 1 {log_file_path}')
        last_line = stdout.read().decode().strip()
        #logging.info(f"Last line from log: {last_line}")
        
        # Clean ANSI codes from the log line
        last_line = clean_ansi_codes(last_line)
        
        # Define patterns based on log file location
        if log_file_path == "/root/XENGPUMiner/miner.log":
            pattern = re.compile(r'Mining:.*\[(?:(\d+):)?(\d+):(\d+)(?:\.\d+)?,.*?(?:Details=(?:(?:super:(\d+)\s)?normal:(\d+)|xuni:(\d+)).*?)?HashRate:(\d+\.\d+).*Difficulty=(\d+)')
        else:
            pattern = re.compile(r'Mining: \d+ Hashes \[\s*(?:(\d+):)?(\d+):(\d+)(?:\.\d+)?,\s*\d+ GPUs,\s*(?:super:(\d+),\s*)?(?:normal:(\d+),\s*)?(?:xuni:(\d+),\s*)?([\d.]+) Hashes/s,\s*Difficulty=(\d+)\]')

        match = pattern.search(last_line)
        if match:
            # Extracting the running time and blocks information
            hours, minutes, seconds, super_blocks, normal_blocks, xuni_blocks, hash_rate, difficulty = match.groups()
            
            hours = int(hours) if hours is not None else 0
            minutes = int(minutes)
            seconds = int(seconds)
            super_blocks = int(super_blocks) if super_blocks is not None else 0
            normal_blocks = int(normal_blocks) if normal_blocks is not None else 0
            xuni_blocks = int(xuni_blocks) if xuni_blocks is not None else 0
            hash_rate = float(hash_rate)
            difficulty = int(difficulty)
            logging.info(f"Successfully collected data for Instance ID {instance_id}!")
            instances_perf.append({
                'ssh_link': ssh_link,
                'super_blocks': super_blocks,
                'normal_blocks': normal_blocks,
                'xuni_blocks': xuni_blocks,
                'hash_rate': hash_rate,
                'difficulty': difficulty
            })
            return hours, minutes, seconds, super_blocks, normal_blocks, xuni_blocks, hash_rate, difficulty
        else:
            logging.error("Failed to parse the log line: %s", last_line)
            return None, None, None, None, None, None, None, None
        
    except Exception as e:
        logging.error(f"Failed to connect to Instance {instance_id} or miner.log file is missing! Check if SSH Key Path is correct in the settings or repeat STEP 3 in the Configuration Wizard then click COMPLETE in STEP4 to save changes. If miner.log file is missing rebuild your instance.")
        return None, None, None, None, None, None, None, None
    
    finally:
        ssh.close()


     
def print_table(data, mean_difficulty, average_dollars_per_normal_block, total_dph_running_machines, usd_per_gpu, hash_rate_per_gpu, hash_rate_per_usd, label, disk_util, disk_space, cpu_util, sum_normal_block_per_hour, total_hash_rate, total_gpus_running, text_output_file='table_output.txt', html_output_file='table_output.html'):
    if not data:  # If data list is empty, do not proceed.
        print("No data to print.")
        return

    # Define the table and its columns for text output
    text_table = PrettyTable()
    text_table.field_names = ["Instance ID", "GPU Name", "GPU's", "Util.%", "USD/h", "USD/GPU", "Inst.H/s", "GPU H/s", "XNM", "XUNI", "X.BLK", "Runtime", "Block/h", "H/s/USD", "USD/Block", "Label", "CPU %", "HDD %"]

    # Get current timestamp and other information
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    difficulty = int(mean_difficulty) if mean_difficulty is not None else "N/A"
    total_hash_rate_str = f"{total_hash_rate:.2f} h/s" if total_hash_rate is not None else "N/A"
    total_dph_running_machines_str = f"{total_dph_running_machines:.4f}$" if total_dph_running_machines is not None else "N/A"
    average_dollars_per_normal_block_str = f"{average_dollars_per_normal_block:.4f}$" if average_dollars_per_normal_block is not None else "N/A"
    sum_normal_block_per_hour_str = f"{sum_normal_block_per_hour:.2f}" if sum_normal_block_per_hour is not None else "N/A"

    # Process data for text table
    for row in data:
        text_table.add_row(row)

    # Write the text table and timestamp to a text file
    with open(text_output_file, 'a') as f:
        f.write(f"Timestamp: {timestamp}, GPU's: {total_gpus_running}, Difficulty: {difficulty}, Total Hash: {total_hash_rate_str}, Total DPH: {total_dph_running_machines_str}, Avg_$/Block: {average_dollars_per_normal_block_str}, Total Blocks/h: {sum_normal_block_per_hour_str}\n{text_table}\n")
    #print(f"Table also written to {text_output_file}\n")

    # HTML table setup with header information
    html_table = f"""
    <h3>Performance summary: </h3>
    <table border="1" style="font-size: 18px">
    <tr>
        <th>Timestamp</th>
        <th>GPU's</th>
        <th>Difficulty</th>
        <th>Total Hash</th>
        <th>Hour cost</th>
        <th>XNM Block cost</th>
        <th>XNM Blocks/h</th>
    </tr>
    <tr>
        <td>{timestamp}</td>
        <td>{total_gpus_running}</td>
        <td>{difficulty}</td>
        <td>{total_hash_rate_str}</td>
        <td>{total_dph_running_machines_str}</td>
        <td>{average_dollars_per_normal_block_str}</td>
        <td>{sum_normal_block_per_hour_str}</td>
    </tr>
    </table>

    <br>
    <h3>Performance details: </h3>
    <table border="1">
      <tr>
        <th>Instance ID</th>
        <th>GPU Name</th>
        <th>GPU's</th>
        <th>Util.%</th>
        <th>USD/h</th>
        <th>USD/GPU</th>
        <th>Inst.H/s</th>
        <th>GPU H/s</th>
        <th>XNM</th>
        <th>XUNI</th>
        <th>X.BLK</th>        
        <th>Runtime</th>
        <th>XNM/h</th>
        <th>H/s/USD</th>
        <th>USD/XNM</th>
        <th>Label</th>
        <th>CPU %</th>
        <th>HDD %</th>
      </tr>
    """

    # Process data for HTML table
    for row in data:
        html_table += '<tr>' + ''.join(f'<td>{col}</td>' for col in row) + '</tr>'

    # Close the table tag
    html_table += '</table><br>'

    # Write the HTML table to a HTML file
    with open(html_output_file, 'w') as f:
        f.write(html_table)



# List Instances and Get SSH Information
ssh_info_list, total_dph_running_machines, total_gpus_running = instance_list()
username = "root"

# Initialize Data Storage
gpu_hash_rates = defaultdict(list)
dph_values = []
difficulties = []
hash_rates = []
dollars_per_normal_block_values = []
sum_normal_block_per_hour = 0
table_data = []
mean_difficulty = None
average_dollars_per_normal_block = None
usd_per_gpu = None
hash_rate_per_gpu = None
hash_rate_per_usd = None
label = None
disk_util = None
disk_space = None
cpu_util = None
total_hash_rate = sum(hash_rates)
gpu_util = None
gpu_util_warnings_set = set()
# Fetch Log Information for Each Instance
for ssh_info in ssh_info_list:
    instance_id = ssh_info['instance_id']
    gpu_name = ssh_info['gpu_name']
    num_gpus = ssh_info['num_gpus']
    gpu_util = ssh_info['gpu_util']
    actual_status = ssh_info['actual_status']
    label = ssh_info['label'] if ssh_info['label'] is not None else ''  
    cpu_util = ssh_info['cpu_util']
    disk_util = ssh_info['disk_util'] 
    disk_space = ssh_info['disk_space']    
    dph_total = float(ssh_info['dph_total'])  # Convert DPH to float for calculations
    dph_values.append(dph_total)
    ssh_host = ssh_info['ssh_host']
    ssh_port = ssh_info['ssh_port']

    hours, minutes, seconds, super_blocks, normal_blocks, xuni_blocks, hash_rate, difficulty = get_log_info(ssh_host, ssh_port, username, private_key_path, passphrase)

    # Warning if instance is running but GPU not fully utilized
    if actual_status == "running" and gpu_util is not None and gpu_util < 85:  # Check if gpu_util is below 85%
        warning_message = f"GPU Utilization for instance {instance_id} is at {gpu_util:.2f}% - Make sure miner is working!"
        if warning_message not in gpu_util_warnings_set:
            gpu_util_warnings_set.add(warning_message)

    if num_gpus != 'N/A' and dph_total != 'N/A':
        usd_per_gpu = round(dph_total / float(num_gpus), 4)
    else:
        usd_per_gpu = 'N/A'
    if dph_total != 'N/A' and hash_rate is not None:
        hash_rate_per_usd = round(hash_rate / dph_total, 2)
    else:
        hash_rate_per_usd = 'N/A'        
   
    if difficulty is not None and difficulty != 0:
        difficulties.append(difficulty)
    if hash_rate is not None and hash_rate != 0:
        hash_rates.append(hash_rate)        
    
    if normal_blocks is not None and xuni_blocks is not None:
        runtime_hours = hours + minutes / 60 + seconds / 3600

        # Calculate Block/h, sum it and handle the case when runtime is zero
        if runtime_hours != 0:
            normal_block_per_hour = normal_blocks / runtime_hours
            # Update sum
            sum_normal_block_per_hour += normal_block_per_hour
        else:
            normal_block_per_hour = 0

        # Calculate $/Blocks and handle the case when the number of blocks is zero
        if normal_blocks != 0:
            dollars_per_normal_block = (runtime_hours * dph_total) / normal_blocks
            dollars_per_normal_block_values.append(dollars_per_normal_block)
        else:
            dollars_per_normal_block = 0
        
        hdd_utilization_percent = (disk_util / disk_space) * 100
        hash_rate_per_gpu = hash_rate / float(num_gpus) if num_gpus != 'N/A' and hash_rate is not None else 'N/A'
        
        if hash_rate is not None and hash_rate != 0 and num_gpus != 'N/A':
            hash_rate_per_gpu = hash_rate / float(num_gpus)
            gpu_hash_rates[gpu_name].append(hash_rate_per_gpu)
        else:
            hash_rate_per_gpu = 'N/A'
        
        table_data.append([instance_id, gpu_name, num_gpus, round(gpu_util, 2), round(dph_total, 4), round(usd_per_gpu, 4), hash_rate, hash_rate_per_gpu, normal_blocks, xuni_blocks, super_blocks, round(runtime_hours, 2), round(normal_block_per_hour, 2), round(hash_rate_per_usd, 2), round(dollars_per_normal_block, 2), label, round(cpu_util, 2), round(hdd_utilization_percent, 2)])        
    else:
        pass


    if difficulties:
        mean_difficulty = sum(difficulties) / len(difficulties)
    if hash_rates:
        total_hash_rate = sum(hash_rates)
    if dph_values:
        total_dph = sum(dph_values)
    if dollars_per_normal_block_values:
        average_dollars_per_normal_block = sum(dollars_per_normal_block_values) / len(dollars_per_normal_block_values)
    else:
        average_dollars_per_normal_block = None



# Sort the data by "<column_name>" in asc or desc order
    if not table_data:
        print("Error: table_data is empty!")
    elif sort_column_index < 0 or (table_data and sort_column_index >= len(table_data[0])):
        print("Invalid sort_column_index: {}. Must be between 0 and {}.".format(sort_column_index, len(table_data[0])-1 if table_data else 'N/A'))
    else:
        # Ensure all rows have the same number of columns
        num_columns = len(table_data[0])
        if all(len(row) == num_columns for row in table_data):
            try:
                # Convert the sort column to float if possible for proper numeric sorting
                table_data.sort(key=lambda x: (float(x[sort_column_index]) if x[sort_column_index] not in (None, 'N/A') else float('-inf'), x), 
                                reverse=(sort_order == 'descending'))
            except ValueError:
                # Fallback to string sorting if conversion to float is not possible
                table_data.sort(key=lambda x: (x[sort_column_index] if x[sort_column_index] not in (None, 'N/A') else '', x), 
                                reverse=(sort_order == 'descending'))
        else:
            print("Error: Not all rows have the same number of columns.")


# Print the table
print_table(table_data, mean_difficulty, average_dollars_per_normal_block, total_dph_running_machines, usd_per_gpu, hash_rate_per_gpu, hash_rate_per_usd, label, cpu_util, disk_util, disk_space, sum_normal_block_per_hour, total_hash_rate, total_gpus_running)
   
    
# Calculate Outliers
html_output = ""
outliers = defaultdict(list)
performances = defaultdict(lambda: {'bottom': []})
highlighted_outliers = defaultdict(list)

# Calculating mean and standard deviation for each GPU type
stats = {}

instance_gpu_mapping = {row[0]: (row[1], row[6]) for row in table_data}
for gpu_type, hash_rates in gpu_hash_rates.items():
    if len(hash_rates) > 1:
        average_hash_rate = np.mean(hash_rates)
        std_dev_hash_rate = np.std(hash_rates, ddof=1)  # Set 'ddof=1' for sample standard deviation
        stats[gpu_type] = {"mean": average_hash_rate, "std_dev": std_dev_hash_rate}

        # Calculate outliers and performances based on actual data per GPU type
        for instance_id, (instance_gpu_type, instance_hash_rate) in instance_gpu_mapping.items():
            if instance_gpu_type == gpu_type and instance_hash_rate != 'N/A':
                instance_hash_rate = float(instance_hash_rate)
                z_score = (instance_hash_rate - average_hash_rate) / std_dev_hash_rate
                if z_score < -threshold:
                    highlighted_outliers[gpu_type].append((instance_id, instance_hash_rate, z_score))


# Print Warnings if GPU not fully utilized
for warning in gpu_util_warnings_set:
    html_output += f"<p style='color: red;'><u>{warning}</u></p>"
  

# Print Outliers and Stats
insufficient_data_messages = []  # List to store messages for insufficient data
for gpu_type in gpu_hash_rates.keys():  # Iterate through all GPU types

    if gpu_type in stats:
        mean = stats[gpu_type]["mean"]
        std_dev = stats[gpu_type]["std_dev"]
        html_output += f"<br><h5>{gpu_type} Performance Stats:</h5>"
        html_output += f"<p>- Average hash rate: <b>{mean:.2f} H/s</b>, Standard deviation: <b>{std_dev:.2f} H/s</b></p>"

        if gpu_type in highlighted_outliers and highlighted_outliers[gpu_type]:
            # Sort the highlighted outliers by Z-Score from lowest to highest (worst to best)
            sorted_outliers = sorted(highlighted_outliers[gpu_type], key=lambda x: x[2])
            
            html_output += "<p><u>Some instances are below the average hash rate:</u></p>"
            for ID, h_rate, z_score in sorted_outliers:
                percent_from_mean = (mean - h_rate) / mean * 100  # Calculate the percentage from the mean here
                html_output += f"<p>- Instance ID {ID} with <b>{h_rate:.2f}H/s</b> is <b>{percent_from_mean:.2f}%</b> below average, <b>Variance</b>: {z_score:.2f} Z-Score</p>"
        else:
            if std_dev > 100:
                html_output += f"<p style='color: orange;'>- Warning: Alarming deviation for {gpu_type} above <b>100 H/s</b> detected! Lower the Z-Score threshold and reload for more details.</p>"
            else:
                # This message will only print if there are no highlighted outliers and the standard deviation is not greater than 100
                html_output += f"<p>- <b>GOOD NEWS!</b> All {gpu_type} instances are performing within the expected range.</p>"
    else:
        insufficient_data_messages.append(f"** {gpu_type}: ** Not enough data to compare performance stats.")


# Print messages for insufficient data at the end
html_output += f"<br><hr>"
for message in insufficient_data_messages:
    html_output += f"<p>{message}</p>"
 
# Write the HTML output to an external file
with open("table_output.html", "a") as html_file:
    html_file.write("<br><h3>Performance analysis:</h3>")
    html_file.write(html_output)
with open('table_perf.json', 'w') as file:
    if not instances_perf:  
        json.dump([], file, indent=4)  
    else:
        json.dump(instances_perf, file, indent=4)  

# Exit the script
logging.info("Script finished execution.")
sys.exit()
