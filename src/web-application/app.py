from flask import Flask, render_template, request, jsonify
import json
import subprocess
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Load JSON data from file
def load_config():
    with open('anl-master-config.json', 'r') as f:
        return json.load(f)

# Save JSON data to file
def save_config(data):
    with open('anl-master-config.json', 'w') as f:
        json.dump(data, f, indent=4)

# Check if form data contains any Simulation signals
def form_contains_simulation_signals(form_data):
    simulation_signals = load_config()['FlexILUDPSignals']['Simulation']
    for signal_name in simulation_signals:
        if f'Simulation_signal_{signal_name}' in form_data:
            return True
    return False

# Check if form data contains any Mabx signals
def form_contains_mabx_signals(form_data):
    mabx_signals = load_config()['FlexILUDPSignals']['Mabx']
    for signal_name in mabx_signals:
        if f'Mabx_signal_{signal_name}' in form_data:
            return True
    return False

# Check if form data contains any Facilities signals
def form_contains_facilities_signals(form_data):
    facilities_signals = load_config()['FlexILUDPSignals']['Facilities']
    for signal_name in facilities_signals:
        if f'Facilities_signal_{signal_name}' in form_data:
            return True
    return False

# Check if form data contains any Test signals
def form_contains_test_signals(form_data):
    test_signals = load_config()['FlexILUDPSignals']['Test']
    for signal_name in test_signals:
        if f'Test_signal_{signal_name}' in form_data:
            return True
    return False

@app.route('/')
def index():
    config_data = load_config()
    # Generate IP status
    ip_status = {}
    for device, ip in config_data["IPAddress"].items():
        ip_status[device] = ping_ip(ip)

    return render_template('index.html', config_data=config_data, ip_status=ip_status)

@app.route('/update', methods=['POST'])
def update_config():
    if request.method == 'POST':
        config_data = load_config()
        form_data = request.form

        # Update IPAddress section
        ip_addresses = form_data.getlist('ip_address')
        for device, new_ip in zip(config_data['IPAddress'], ip_addresses):
            config_data['IPAddress'][device] = new_ip

        # Update PortNumber section
        port_numbers = form_data.getlist('port_number')
        for component, new_port in zip(config_data['PortNumber'], port_numbers):
            config_data['PortNumber'][component] = int(new_port)

        # Check if form data contains Simulation signals
        if form_contains_simulation_signals(form_data):
            # Set all Simulation signals to False by default
            for signal_name in config_data['FlexILUDPSignals']['Simulation']:
                config_data['FlexILUDPSignals']['Simulation'][signal_name] = False

            # Update FlexILUDPSignals section for Simulation based on form data
            for signal_name in config_data['FlexILUDPSignals']['Simulation']:
                if f'Simulation_signal_{signal_name}' in form_data:
                    config_data['FlexILUDPSignals']['Simulation'][signal_name] = form_data.get(f'Simulation_signal_{signal_name}') == 'on'

        # Check if form data contains Mabx signals
        if form_contains_mabx_signals(form_data):
            # Set all Mabx signals to False by default
            for signal_name in config_data['FlexILUDPSignals']['Mabx']:
                config_data['FlexILUDPSignals']['Mabx'][signal_name] = False

            # Update FlexILUDPSignals section for Mabx based on form data
            for signal_name in config_data['FlexILUDPSignals']['Mabx']:
                if f'Mabx_signal_{signal_name}' in form_data:
                    config_data['FlexILUDPSignals']['Mabx'][signal_name] = form_data.get(f'Mabx_signal_{signal_name}') == 'on'
                    
        # Check if form data contains Facilities signals
        if form_contains_facilities_signals(form_data):
            # Set all Facilities signals to False by default
            for signal_name in config_data['FlexILUDPSignals']['Facilities']:
                config_data['FlexILUDPSignals']['Facilities'][signal_name] = False

            # Update FlexILUDPSignals section for Facilities based on form data
            for signal_name in config_data['FlexILUDPSignals']['Facilities']:
                if f'Facilities_signal_{signal_name}' in form_data:
                    config_data['FlexILUDPSignals']['Facilities'][signal_name] = form_data.get(f'Facilities_signal_{signal_name}') == 'on'   
                    
        # # Check if form data contains Test signals
        # if form_contains_test_signals(form_data):
        #     # Set all Test signals to False by default
        #     for signal_name in config_data['FlexILUDPSignals']['Test']:
        #         config_data['FlexILUDPSignals']['Test'][signal_name] = False

        #     # Update FlexILUDPSignals section for Test based on form data
        #     for signal_name in config_data['FlexILUDPSignals']['Test']:
        #         if f'Test_signal_{signal_name}' in form_data:
        #             config_data['FlexILUDPSignals']['Test'][signal_name] = form_data.get(f'Test_signal_{signal_name}') == 'on'            
        
        # Save updated JSON data back to file
        save_config(config_data)

        # Debugging statements
        # print(json.dumps(config_data, indent=4))

        # Return success response
        return jsonify({'status': 'success'})

    return jsonify({'status': 'error', 'message': 'Invalid request method'})

@app.route('/performance-data')
def performance_data():
    # Load the CSV data
    # df = pd.read_csv('performance-data-log.csv')
    df = pd.read_csv('log/msg_count_log_.csv')
    
    # Split the data into transmitted and received messages
    transmitted = df[df['Type'] == 'Transmitted']
    received = df[df['Type'] == 'Received']
    
    # Get the current time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return render_template('performance_data.html', transmitted=transmitted, received=received, current_time=current_time)



def ping_ip(ip):
    try:
        output = subprocess.check_output(['ping', '-c', '1', ip], stderr=subprocess.STDOUT, universal_newlines=True)
        if '1 received' in output:
            return 'successful'
        else:
            return 'unsuccessful'
    except subprocess.CalledProcessError:
        return 'unsuccessful'

if __name__ == '__main__':
    app.run(debug=True)
