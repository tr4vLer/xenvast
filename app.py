from flask import Flask, render_template, jsonify, request, flash, redirect, url_for, Response, send_file
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
from instance_rebuilder import reboot_instance, update_onstart_script
from dust_removal import destroy_instance
import subprocess
import requests
import threading
import json
import logging
import os

app = Flask(__name__)
Bootstrap(app)

# Welcome banner

print("""
__  __          ____  _            _        __  __ _                 
\\ \\/ /___ _ __ | __ )| | ___   ___| | _____|  \\/  (_)_ __   ___ _ __ 
 \\  // _ \\ '_ \\|  _ \\| |/ _ \\ / __| |/ / __| |\\/| | | '_ \\ / _ \\ '__|
 /  \\  __/ | | | |_) | | (_) | (__|   <\\__ \\ |  | | | | | |  __/ |   
/_/\\_\\___|_| |_|____/|_|\\___/ \\___|_|\\_\\___/_|  |_|_|_| |_|\\___|_|   
""")
print("""
 _             _        _  _        _             _          ___   ____  
| |__  _   _  | |_ _ __| || |__   _| | ___ _ __  | | __   __/ _ \\ |___ \\ 
| '_ \\| | | | | __| '__| || |\\ \\ / / |/ _ \\ '__| | | \\ \\ / / | | |  __) |
| |_) | |_| | | |_| |  |__   _\\ V /| |  __/ |    | |  \\ V /| |_| | / __/ 
|_.__/ \\__, |  \\__|_|     |_|  \\_/ |_|\\___|_|    |_|   \\_/  \\___(_)_____|
       |___/                                     |_|                     
""")


app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
script_process = None
market_gpu_process = None 
xuni_farming = None
instance_rebuilder_process = None
dust_removal = None
perf_bot_running = False
instances_cache = None
last_modified_time = 0

# Function to load instances from instances.json
def load_instances():
    global instances_cache, last_modified_time
    try:
        current_modified_time = os.path.getmtime('instances.json')
    except FileNotFoundError:
        current_modified_time = 0

    if current_modified_time > last_modified_time:
        try:
            with open('instances.json', 'r') as f:
                instances_cache = json.load(f)
                last_modified_time = current_modified_time
        except FileNotFoundError:
            instances_cache = []
    
    return instances_cache


# Get instances 
def get_instances():
    get_instance_update()
    return load_instances()


# Load configuration
def load_config():
    with open('config.json', 'r') as file:
        return json.load(file)

# Save configuration
def save_config(config):
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)

def background_script():
    global script_process
    script_process = subprocess.Popen(['python3', 'app_bot3.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in iter(script_process.stdout.readline, ''):
        socketio.emit('script_output', {'data': line.strip()})
    script_process.stdout.close()
    
def background_market_gpu_script():
    global market_gpu_process
    market_gpu_process = subprocess.Popen(['python3', 'market_gpu.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in iter(market_gpu_process.stdout.readline, ''):
        socketio.emit('market_gpu_output', {'data': line.strip()})
    market_gpu_process.stdout.close()   

def background_xuni_farming():
    global xuni_farming
    xuni_farming = subprocess.Popen(['python3', 'xuni_farming.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in iter(xuni_farming.stdout.readline, ''):
        socketio.emit('xuni_farming_output', {'data': line.strip()})
    xuni_farming.stdout.close()        
    
def background_instance_rebuilder():
    global instance_rebuilder_process
    instance_rebuilder_process = subprocess.Popen(['python3', 'instance_rebuilder.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in iter(instance_rebuilder_process.stdout.readline, ''):
        socketio.emit('instance_rebuilder_output', {'data': line.strip()})
    instance_rebuilder_process.stdout.close()
    instance_rebuilder_process.wait()

def background_dust_removal():
    global dust_removal
    dust_removal = subprocess.Popen(['python3', 'dust_removal.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in iter(dust_removal.stdout.readline, ''):
        socketio.emit('dust_removal_output', {'data': line.strip()})
    dust_removal.stdout.close()
    dust_removal.wait()
    reset_config_values()

# transfer_credit function here
def transfer_credit(api_key, from_account, to_account, amount):
    url = "https://console.vast.ai/api/v0/commands/transfer_credit/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "sender": from_account,
        "recipient": to_account,
        "amount": amount
    }
    response = requests.put(url, json=data, headers=headers) 
    if response.status_code == 200:
        return response.json()
    else:
        return None

@app.route('/')
def index():
    config = load_config()
    gpu_dph_rates = config.get('GPU_DPH_RATES', {})
    dark_theme = config.get('DARK_THEME', False)
    CURRENT_MARKET_DPH = config.get('CURRENT_MARKET_DPH', {})
    instances = get_instances()  # Get the instances data
    return render_template('index.html', config=config, gpu_dph_rates=gpu_dph_rates, dark_theme=dark_theme, CURRENT_MARKET_DPH=CURRENT_MARKET_DPH, instances=instances)


@app.route('/get-balance-info')
def get_balance_info():
    try:
        output = subprocess.check_output(['python3', 'balance_info.py'], stderr=subprocess.STDOUT, text=True)
        return jsonify({'status': 'success', 'output': output})
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'output': e.output})
        
@app.route('/get-instance-update')
def get_instance_update():
    try:
        output = subprocess.check_output(['python3', 'instances.py'], stderr=subprocess.STDOUT, text=True)
        return jsonify({'status': 'success', 'output': output})
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'output': e.output})    

@app.route('/get-instances-data')
def get_instances_data():
    instances = get_instances()  # Get the instances data
    return jsonify(instances=instances)        
        
@app.route('/get-mining-stats')
def get_mining_stats():
    file_path = 'mining_data.html'
    try:
        # You can still run your script to update the HTML file
        subprocess.check_output(['python3', 'mining_stats.py'], stderr=subprocess.STDOUT, text=True)
        return send_file(file_path, mimetype='text/html')
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'output': e.output})     
        
@app.route('/get-current-dph')
def get_current_dph():
    try:
        output = subprocess.check_output(['python3', 'market_price_check.py'], stderr=subprocess.STDOUT, text=True)
        return jsonify({'status': 'success', 'output': output})
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'output': e.output})        


@app.route('/update-settings', methods=['POST'])
def update_settings():
    config = load_config()
    api_key = request.form.get('api_key')
    eth_address = request.form.get('eth_address')
    ssh_key_path = request.form.get('ssh_key_path')  # Get the SSH Key path
    passphrase = request.form.get('passphrase')  # Get the Passphrase
    
    # Debugging
    print("Received API Key:", api_key)
    print("Received ETH Address:", eth_address)
    print("Received SSH Key Path:", ssh_key_path)
    print("Received Passphrase:", passphrase)

    if api_key is not None:
        config['API_KEY'] = api_key
    if eth_address is not None:
        config['ETH_ADDRESS'] = eth_address
    if ssh_key_path is not None:
        config['PRIVATE_KEY_PATH'] = ssh_key_path  # Update the SSH Key path
    if passphrase is not None:
        config['PASSPHRASE'] = passphrase  # Update the Passphrase
    
    save_config(config)
    return jsonify({'status': 'Settings updated'})



@app.route('/update-gpu-deals', methods=['POST'])
def update_gpu_deals():
    config = load_config()
    config['MAX_ORDERS'] = int(request.form['max_orders'])

    gpu_names = request.form.getlist('gpu_name[]')
    dph_rates = request.form.getlist('dph_rate[]')

    gpu_dph_rates = {}

    for i in range(len(gpu_names)):
        gpu_name = gpu_names[i].strip()
        dph_rate = float(dph_rates[i])

        if gpu_name and dph_rate:
            gpu_dph_rates[gpu_name] = dph_rate

    config['GPU_DPH_RATES'] = gpu_dph_rates

    save_config(config)
    return Response(status=204)  # Return a 204 No Content response

@app.route('/start-script', methods=['POST'])
def start_script():
    global script_process
    if script_process is None or script_process.poll() is not None:
        threading.Thread(target=background_script, daemon=True).start()
        return 'Limit order script started'
    else:
        return 'Limit order Script is already running'

@app.route('/stop-script', methods=['POST'])
def stop_script():
    global script_process
    if script_process and script_process.poll() is None:
        script_process.terminate()
        return 'Limit order script stopped'
    else:
        return 'No running script to stop'    

@app.route('/script-status', methods=['GET'])
def script_status():
    global script_process
    if script_process and script_process.poll() is None:
        return jsonify({'status': 'running'})
    else:
        return jsonify({'status': 'stopped'})

@app.route('/start-market-gpu-script', methods=['POST'])
def start_market_gpu_script():
    global market_gpu_process
    if market_gpu_process is None or market_gpu_process.poll() is not None:
        threading.Thread(target=background_market_gpu_script, daemon=True).start()
        return 'Market GPU script started'
    else:
        return 'Market GPU script is already running'

        
@app.route('/stop-market-gpu-script', methods=['POST'])
def stop_market_gpu_script():
    global market_gpu_process
    if market_gpu_process and market_gpu_process.poll() is None:
        market_gpu_process.terminate()
        return 'Market GPU script stopped'
    else:
        return 'No running script to stop'        
        
@app.route('/market-gpu-status', methods=['GET'])
def market_gpu_status():
    global market_gpu_process
    if market_gpu_process and market_gpu_process.poll() is None:
        return jsonify({'status': 'running'})
    else:
        return jsonify({'status': 'stopped'})      

@app.route('/start-xuni-farming', methods=['POST'])
def start_xuni_farming():
    global xuni_farming
    if xuni_farming is None or xuni_farming.poll() is not None:
        threading.Thread(target=background_xuni_farming, daemon=True).start()
        return 'XUNI Farming script started'
    else:
        return 'XUNI Farming script is already running'

@app.route('/stop-xuni-farming', methods=['POST'])
def stop_xuni_farming():
    global xuni_farming
    if xuni_farming and xuni_farming.poll() is None:
        xuni_farming.terminate()
        return 'XUNI Farming script stopped'
    else:
        return 'No running script to stop'

@app.route('/xuni-farming-status', methods=['GET'])
def xuni_farming_status():
    global xuni_farming
    if xuni_farming and xuni_farming.poll() is None:
        return jsonify({'status': 'running'})
    else:
        return jsonify({'status': 'stopped'})          
        
        
@app.route('/start-perf-bot', methods=['POST'])
def start_perf_bot():
    global perf_bot_running
    silent = request.args.get('silent', 'false') == 'true'
    if not perf_bot_running:
        perf_bot_process = subprocess.Popen(['python3', 'perf_bot.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        perf_bot_running = True
        socketio.emit('perf_bot_status', {'data': 'Performance bot started'})

        def emit_perf_bot_output():
            for line in iter(perf_bot_process.stdout.readline, ''):
                socketio.emit('perf_bot_output', {'data': line.strip()})
            perf_bot_process.stdout.close()

        # Start a thread to emit perf_bot_output
        emit_thread = threading.Thread(target=emit_perf_bot_output)
        emit_thread.start()

        # Wait for the perf_bot_process to complete in a separate thread to avoid blocking
        def wait_for_process():
            perf_bot_process.wait()
            emit_thread.join()  # Ensure all output has been emitted
            global perf_bot_running
            perf_bot_running = False
            # Call emit_perf_bot_table_output after the bot completes its execution
            with app.app_context():  # Ensure access to Flask application context
                socketio.emit('perf_bot_status', {'data': 'Performance bot completed'})
                emit_perf_bot_table_output()

        process_thread = threading.Thread(target=wait_for_process)
        process_thread.start()

        return 'Performance bot started'
    else:
        return 'Performance bot is already running'


@app.route('/emit-perf-bot-table-output')
def emit_perf_bot_table_output():
    try:
        with open('table_output.html', 'r') as file:
            html_content = file.read()
            socketio.emit('perf_bot_html', {'html': html_content})
            return jsonify({'status': 'success'})
    except FileNotFoundError:
        return jsonify({'status': 'error', 'message': 'table_output.html not found'}), 404



@app.route('/start-instance-rebuilder', methods=['POST'])
def start_instance_rebuilder():
    global instance_rebuilder_process

    if instance_rebuilder_process is None or instance_rebuilder_process.poll() is not None:
        threading.Thread(target=background_instance_rebuilder, daemon=True).start()
        return 'Instance rebuilder script started'
    else:
        return 'Instance rebuilder script is already running'
        
@app.route('/start-dust-removal', methods=['POST'])
def start_dust_removal():
    global dust_removal

    if dust_removal is None or dust_removal.poll() is not None:
        threading.Thread(target=background_dust_removal, daemon=True).start()
        return 'Dust cleaner script started'
    else:
        return 'Dust cleaner script is already running'

@app.route('/dust-removal-config', methods=['POST'])
def dust_removal_config():
    config = load_config()
    
    remove_scheduling = request.form.get('remove_scheduling', 'off') == 'on'
    remove_inactive = request.form.get('remove_inactive', 'off') == 'on'
    remove_offline = request.form.get('remove_offline', 'off') == 'on'

    config['REMOVE_SCHEDULING'] = remove_scheduling
    config['REMOVE_INACTIVE'] = remove_inactive
    config['REMOVE_OFFLINE'] = remove_offline
    save_config(config)   
    return Response(status=204)
    
def reset_config_values():
    config = load_config()
    config['REMOVE_SCHEDULING'] = False
    config['REMOVE_INACTIVE'] = False
    config['REMOVE_OFFLINE'] = False
    save_config(config)    

@app.route('/update-config', methods=['POST'])
def update_config():
    config = load_config()
    
    # Get values from the form
    api_key = request.form.get('api_key')
    eth_address = request.form.get('eth_address')
    ssh_key_path = request.form.get('ssh_key_path')
    
    # Update the configuration with the received values
    config['API_KEY'] = api_key
    config['ETH_ADDRESS'] = eth_address
    config['PRIVATE_KEY_PATH'] = ssh_key_path

    # Set CONFIG_WIZARD to True once updates are successful
    config['CONFIG_WIZARD'] = True
    
    # Save the updated configuration
    save_config(config)
    
    return jsonify({'status': 'Configuration updated'})
    
@app.route('/market-gpu-config', methods=['POST'])
def market_gpu_config():
    config = load_config()
    
    # Get values from the form
    max_gpu_str = request.form.get('max_gpu')
    
    try:
        max_gpu = int(max_gpu_str)  # Convert to an integer
    except ValueError:
        return jsonify({'status': 'Invalid input for max_gpu'})

    gpu_market = request.form.get('gpu_market')
    
    # Update the configuration with the received values
    config['MAX_GPU'] = max_gpu
    config['GPU_MARKET'] = gpu_market

    save_config(config)
    return Response(status=204)
    
@app.route('/xuni-farming-config', methods=['POST'])
def xuni_farming_config():
    config = load_config()
    
    # Get values from the form
    xuni_max_gpu_str = request.form.get('xuni_max_gpu')
    
    try:
        xuni_max_gpu = int(xuni_max_gpu_str)  # Convert to an integer
    except ValueError:
        return jsonify({'status': 'Invalid input for xuni_max_gpu'})

    xuni_gpu_market = request.form.get('xuni_gpu_market')
    
    # Update the configuration with the received values
    config['XUNI_MAX_GPU'] = xuni_max_gpu
    config['XUNI_GPU_MARKET'] = xuni_gpu_market

    save_config(config)
    return Response(status=204)    
    
    
@app.route('/perf-bot-config', methods=['POST'])
def perf_bot_config():
    config = load_config()
    
    # Get values from the form and convert numerical values appropriately
    sort_column_index = request.form.get('sort_column_index', type=int)  # Convert to int
    threshold = request.form.get('threshold', type=float)  # Convert to float
    sort_order = request.form.get('sort_order')
    
    # Update the configuration with the received and converted values
    config['SORT_COLUMN_INDEX'] = sort_column_index
    config['THRESHOLD'] = threshold
    config['SORT_ORDER'] = sort_order

    save_config(config)   
    return Response(status=204)


@app.route('/generate-ssh-key', methods=['GET'])
def generate_ssh_key():
    try:
        output = subprocess.check_output(['python3', 'ssh_keygen.py'], stderr=subprocess.STDOUT)
        return jsonify({'status': 'success', 'output': output.decode('utf-8')})
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'output': e.output.decode('utf-8')})

@app.route('/donate', methods=['POST'])
def handle_donation():
    config = load_config()
    api_key = config.get('API_KEY')
    amount = request.form.get('donation_amount', type=float)
    
    response = transfer_credit(api_key, "me", "stania92@gmail.com", amount)

    if response:
        return jsonify({'status': 'success', 'message': 'Donation successful! Thank you for your support!'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Donation failed. Please try again or contact support.'}), 400


@app.route('/toggle-theme', methods=['POST'])
def toggle_theme():
    data = request.get_json()
    config = load_config()
    config['DARK_THEME'] = data['darkTheme']
    save_config(config)
    return jsonify({'success': True})
    

@app.route('/destroy_instance', methods=['POST'])
def flask_destroy_instance():
    instance_id = request.form.get('instance_id_destroy')
    config = load_config()
    api_key = config.get('API_KEY')

    if not instance_id or not api_key:
        return jsonify({'error': 'Missing instance_id or api_key'}), 400

    if destroy_instance(instance_id, api_key):
        return jsonify({'message': f'Successfully destroyed instance {instance_id}.'}), 200
        time.sleep(10)
        instances = get_instances() 
    else:
        return jsonify({'error': f'Failed to destroy instance {instance_id}.'}), 500


@app.route('/reboot_instance', methods=['POST'])
def handle_reboot_route():
    instance_id = request.form.get('instance_id_reboot')
    success = handle_reboot_core(instance_id)
    if success:
        return jsonify({'message': f'Instance {instance_id} rebooted successfully!'}), 200
    else:
        return jsonify({'error': f'Failed to reboot instance {instance_id}.'}), 400

def handle_reboot_core(instance_id):
    # Core logic for rebooting an instance
    config = load_config()
    api_key = config.get('API_KEY')
    return reboot_instance(api_key, instance_id)


@app.route('/rebuild_link', methods=['POST'])
def rebuild_link():
    instance_id_str = request.form.get('instance_id_rebuild')
    try:
        instance_id = int(instance_id_str)
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Invalid instance ID format.'}), 400
    
    config = load_config()
    api_key = config.get('API_KEY')
    passphrase = config.get('PASSPHRASE')
    private_key_path = config.get('PRIVATE_KEY_PATH')
    username = "root"
    instances = get_instances()

    if not instances:
        return jsonify({'status': 'error', 'message': 'Failed to retrieve instances.'}), 404

    instance = next((instance for instance in instances if instance['instance_id'] == instance_id), None)
    if not instance:
        return jsonify({'status': 'error', 'message': 'Instance not found.'}), 404

    ssh_host = instance['ssh_host']
    ssh_port = instance['ssh_port']

    success = update_onstart_script(ssh_host, ssh_port, username, private_key_path, instance_id, passphrase)
    if success:
        reboot_success = handle_reboot_core(instance_id)
        if reboot_success:
            return jsonify({'message': f'Instance {instance_id} has been rebuilt successfully! Rebooting now.'}), 200
        else:
            return jsonify({'warning': f'Instance {instance_id} rebuilt, but reboot failed.'}), 206
    else:
        return jsonify({'error': f'Failed to rebuild instance {instance_id}.'}), 400




if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=4999, debug=True, allow_unsafe_werkzeug=True)

