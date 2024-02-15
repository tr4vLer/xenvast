from requests.exceptions import ChunkedEncodingError
import requests
import logging
import time
import threading
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



# Main Script
config = load_config()
API_KEY = config['API_KEY']
CURRENT_MARKET_DPH = config['CURRENT_MARKET_DPH']

SEARCH_CRITERIA = {
    "verified": {},
    "external": {"eq": False},
    "rentable": {"eq": True},
    "gpu_name": {"in": list(CURRENT_MARKET_DPH.keys())}, 
    "cuda_max_good": {"gte": 11},
    "type": "on-demand",
    "intended_status": "running"
}


# Logging Configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])


# Load API Key
api_key = API_KEY


def search_gpu():
    url = "https://console.vast.ai/api/v0/bundles/"
    headers = {'Accept': 'application/json'}
    try:
        response = requests.post(url, headers=headers, json=SEARCH_CRITERIA, timeout=240)
        response.raise_for_status()  

        if response.status_code == 200:
            offers = response.json().get('offers', [])
            # Group offers by GPU name
            gpu_offers = {}
            for offer in offers:
                gpu_name = offer.get('gpu_name')
                if gpu_name in gpu_offers:
                    gpu_offers[gpu_name].append(offer)
                else:
                    gpu_offers[gpu_name] = [offer]

            # Calculate DPH per unit and sort offers for each GPU
            sorted_offers = {}
            for gpu_name, offers in gpu_offers.items():
                sorted_offers[gpu_name] = sorted(offers, key=lambda x: x.get('dph_total', 0) / x.get('num_gpus', 1))

            # Find the cheapest offer for each GPU name in GPU_DPH_RATES
            for gpu_name, dph_rate in CURRENT_MARKET_DPH.items():
                if gpu_name in sorted_offers:
                    cheapest_offer = sorted_offers[gpu_name][0]
                    dph_per_unit = cheapest_offer.get('dph_total', 0) / cheapest_offer.get('num_gpus', 1)
                    rounded_dph_per_unit = round(dph_per_unit, 3)  # Round to 3 decimal places
                    print(f"{gpu_name}: {rounded_dph_per_unit:.3f}")

                    # Update the CURRENT_MARKET_DPH dictionary
                    config['CURRENT_MARKET_DPH'][gpu_name] = rounded_dph_per_unit
            
            # Write the updated config back to config.json
            #with open('config.json', 'w') as config_file:
            #    json.dump(config, config_file, indent=4)
                
        else:
            logging.error(f"Offers check failed. Status code: {response.status_code}. Response: {response.text}")

    except ChunkedEncodingError as ce:
        logging.error(f"ChunkedEncodingError occurred during the API request: {ce}")
    except requests.exceptions.RequestException as re:
        logging.error(f"RequestException occurred during the API request: {re}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


offers = search_gpu()
# Exit the script
sys.exit()