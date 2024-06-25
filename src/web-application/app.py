from flask import Flask, render_template, request, jsonify
import json
import subprocess

app = Flask(__name__)

# Load JSON data from file
with open('anl-master-config.json', 'r') as f:
    config_data = json.load(f)

@app.route('/')
def index():
    # Generate IP status
    ip_status = {}
    for device, ip in config_data["IPAddress"].items():
        ip_status[device] = ping_ip(ip)

    return render_template('index.html', config_data=config_data, ip_status=ip_status)

@app.route('/update', methods=['POST'])
def update_config():
    if request.method == 'POST':
        # Process form submission and update JSON data
        ip_addresses = request.form.getlist('ip_address')
        port_numbers = request.form.getlist('port_number')

        # Update IPAddress section
        for device, new_ip in zip(config_data['IPAddress'], ip_addresses):
            config_data['IPAddress'][device] = new_ip

        # Update PortNumber section
        for component, new_port in zip(config_data['PortNumber'], port_numbers):
            config_data['PortNumber'][component] = int(new_port)

        # Save updated JSON data back to file
        with open('anl-master-config.json', 'w') as f:
            json.dump(config_data, f, indent=4)

        # Return success response
        return jsonify({'status': 'success'})

    # If not a POST request, return error response
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
