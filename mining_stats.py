import requests
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
        
config = load_config()
ETH_ADDRESS = config['ETH_ADDRESS']       


def fetch_json_data(url):
    """Fetch JSON data from a given URL."""
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError as e:
            print(f"Error parsing JSON: {e}")
            return None
    else:
        print(f"Failed to fetch data: HTTP {response.status_code}")
        return None

def generate_html_table(data_dict, title, exclude_keys=None):
    """Generate an HTML table from a dictionary, excluding specified keys."""
    if exclude_keys is None:
        exclude_keys = []
    html = f"<h2>{title}</h2>"
    html += "<table border='1'>"
    # Table rows
    for key, value in data_dict.items():
        if key not in exclude_keys:  # Skip excluded keys
            html += f"<tr><td>{key.replace('_', ' ').title()}</td><td>{value}</td></tr>"
    html += "</table>"
    return html

def find_account_data(accounts_data, account_address, exclude_keys=None):
    """Find and generate an HTML table for a specific account address within the 'data' list in the dictionary, excluding specified keys."""
    accounts_list = accounts_data.get('data')  
    if accounts_list:
        for account in accounts_list:
            if account.get("account") == account_address:
                return generate_html_table(account, f"Miner Account<br><p class='custom-p'>{account_address}</p>", exclude_keys)
    return f"No data found for account {account_address}<br>"

def save_html(content, filename):
    """Save HTML content to a file."""
    with open(filename, 'w') as file:
        file.write(content)

# URLs to fetch data from
network_stats_url = "https://raw.githubusercontent.com/TreeCityWes/HashHead/main/network_stats.json"
accounts_url = "https://raw.githubusercontent.com/TreeCityWes/HashHead/main/accounts.json"

# Fetch and process account data
accounts_data = fetch_json_data(accounts_url)
exclude_keys_account = ['account', 'daily_blocks', 'total_hashes_per_second']
your_account_address = ETH_ADDRESS  
account_data_html = ""
if accounts_data:
    account_data_html = find_account_data(accounts_data, your_account_address, exclude_keys_account)

# Fetch and process network stats
network_stats = fetch_json_data(network_stats_url)
network_stats_html = ""
if network_stats:
    network_stats_html = generate_html_table(network_stats, "Network Info")
    
# Corrected and formatted HTML content for the text with link
text_with_link_html = f"<div class='mining-info'>Data fetched from <a href='https://hashhead.io'>hashhead.io</a> thanks to <a href='https://github.com/TreeCityWes/HashHead'>TreeCityWes</a>. For more sophisticated data, visit <a href='https://xen.pub/xblocks.php?addr={your_account_address}'>XEN.pub</a>.</div>"

# Combine HTML content and save to file
html_content = f"<html><body>{account_data_html}<br>{network_stats_html}<br>{text_with_link_html}</body></html>"
save_html(html_content, "mining_data.html")
