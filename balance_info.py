import requests
import json
import sys
import logging
import time

# Initialize logging
logging.basicConfig(level=logging.INFO)

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

# Load API Key
api_key = API_KEY

def instance_list(api_key):
    url = f'https://console.vast.ai/api/v0/instances/?api_key={api_key}'
    headers = {'Accept': 'application/json'}
    total_dph_running_machines = 0 
    total_disk_cost = 0
    disk_cost_saving = 0
    
    for attempt in range(3):  # Retrying up to 3 times
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                response_json = response.json()
                if 'instances' not in response_json:
                    logging.error("Something went wrong. Check if API key provided is valid.")
                    return total_dph_running_machines, total_disk_cost, disk_cost_saving
                
                instances = response_json['instances']
                for instance in instances:
                    dph_base = instance.get('dph_base', 0)  # Assume 0 if not available
                    credit_discount = instance.get('credit_discount', 0)  # Assume 0 discount if not available
                    actual_status = instance.get('actual_status', 'N/A')
                    storage_total_cost = instance.get('storage_total_cost', 0)  # Assume 0 if not available

                    # Apply discount to dph_base if any
                    if credit_discount is not None and credit_discount != 'N/A':
                        discounted_dph = float(dph_base) * (1 - float(credit_discount))
                    else:
                        discounted_dph = float(dph_base)

                    if actual_status.lower() == 'running':
                        total_dph_running_machines += round(discounted_dph, 3)
                    
                    if actual_status.lower() != 'offline':
                        total_disk_cost += round(float(storage_total_cost), 3)
                    
                    if actual_status.lower() != 'offline' and actual_status.lower() != 'running':
                        disk_cost_saving += round(float(storage_total_cost), 3)                       
                break  # Break the loop on successful response
            elif response.status_code == 429:
                if attempt < 2:  # Wait only if we have retries left
                    time.sleep(10)
            else:
                logging.error("ERROR! Setup your API key!")
                break
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            break

    return total_dph_running_machines, total_disk_cost, disk_cost_saving

# Function to calculate time covered by balance
def calculate_time_covered_by_balance(balance, total_dph_running_machines, total_disk_cost, hourly_cost):
    if total_dph_running_machines == 0:
        return 0, 0, 0  # Return zeros if total_dph is zero to avoid division by zero
    days_covered = balance / (hourly_cost * 24)
    whole_days = int(days_covered)
    remaining_hours = (days_covered - whole_days) * 24
    whole_hours = int(remaining_hours)
    remaining_minutes = (remaining_hours - whole_hours) * 60
    whole_minutes = int(remaining_minutes)
    return whole_days, whole_hours, whole_minutes


# Function to check Vast.ai balance
def check_vastai_balance(api_key, total_dph_running_machines, total_disk_cost, hourly_cost, disk_cost_saving):
    url = f'https://console.vast.ai/api/v0/users/current?api_key={api_key}'
    headers = {'Accept': 'application/json'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        balance = data.get('credit', None)
        if balance is not None:
            balance = float(balance)  # Ensure the balance is a float
            daily_cost_with_fee = hourly_cost * 24
            daily_disk_cost = total_disk_cost * 24
            daily_gpu_cost = total_dph_running_machines * 24
            daily_disk_cost_saving = disk_cost_saving * 24
            # Display the balance and estimated spend rate
            print(f"Vast.ai credit: ${balance:.2f}")
            print(f"Your daily spend rate: ${daily_cost_with_fee:.3f}/day")
            days, hours, minutes = calculate_time_covered_by_balance(balance, total_dph_running_machines, total_disk_cost, hourly_cost)
            print(f"\nTime left with current spend rate:\n {days} days, {hours} hours, and {minutes} minutes.")
            print(f"\nSpend rate supplements:")
            print(f"GPU cost: ${daily_gpu_cost:.3f}/day")
            print(f"Disk space cost: ${daily_disk_cost:.3f}/day")
            if disk_cost_saving > 0:
                print(f"\nSaving opportunity recognized!\n NOT running instances cost you: {daily_disk_cost_saving:.3f}$/day!\n You may want to consider terminating these machines manually or using the DUST CLEANER script from the TOOLS tab.")
        else:
            print("Balance information was not available in the response.")
    else:
        print(f"Failed to retrieve data: {response.status_code}")
       


total_dph_running_machines, total_disk_cost, disk_cost_saving = instance_list(API_KEY)
hourly_cost = total_dph_running_machines + total_disk_cost
check_vastai_balance(API_KEY, total_dph_running_machines, total_disk_cost, hourly_cost, disk_cost_saving)


# Exit the script
sys.exit()
