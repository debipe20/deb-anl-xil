from flask import Flask, render_template, request, jsonify
import json
import subprocess

app = Flask(__name__)

# Load JSON data from file
def load_config():
    with open('anl-master-config.json', 'r') as f:
        return json.load(f)

# Save JSON data to file
def save_config(data):
    with open('anl-master-config.json', 'w') as f:
        json.dump(data, f, indent=4)

# Check if form data contains any SimPC signals
def form_contains_simpc_signals(form_data):
    simpc_signals = load_config()['FlexILUDPSignals']['SimPC']
    for signal_name in simpc_signals:
        if f'SimPC_signal_{signal_name}' in form_data:
            return True
    return False

# Check if form data contains any Mabx signals
def form_contains_mabx_signals(form_data):
    mabx_signals = load_config()['FlexILUDPSignals']['Mabx']
    for signal_name in mabx_signals:
        if f'Mabx_signal_{signal_name}' in form_data:
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

        # Check if form data contains SimPC signals
        if form_contains_simpc_signals(form_data):
            # Set all SimPC signals to False by default
            for signal_name in config_data['FlexILUDPSignals']['SimPC']:
                config_data['FlexILUDPSignals']['SimPC'][signal_name] = False

            # Update FlexILUDPSignals section for SimPC based on form data
            for signal_name in config_data['FlexILUDPSignals']['SimPC']:
                if f'SimPC_signal_{signal_name}' in form_data:
                    config_data['FlexILUDPSignals']['SimPC'][signal_name] = form_data.get(f'SimPC_signal_{signal_name}') == 'on'

        # Check if form data contains Mabx signals
        if form_contains_mabx_signals(form_data):
            # Set all Mabx signals to False by default
            for signal_name in config_data['FlexILUDPSignals']['Mabx']:
                config_data['FlexILUDPSignals']['Mabx'][signal_name] = False

            # Update FlexILUDPSignals section for Mabx based on form data
            for signal_name in config_data['FlexILUDPSignals']['Mabx']:
                if f'Mabx_signal_{signal_name}' in form_data:
                    config_data['FlexILUDPSignals']['Mabx'][signal_name] = form_data.get(f'Mabx_signal_{signal_name}') == 'on'

        # Save updated JSON data back to file
        save_config(config_data)

        # Debugging statements
        print(json.dumps(config_data, indent=4))

        # Return success response
        return jsonify({'status': 'success'})

    return jsonify({'status': 'error', 'message': 'Invalid request method'})

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
