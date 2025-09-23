import socket
import json
import time
import os
import platform
import argparse

# Argument parser
parser = argparse.ArgumentParser()
parser.add_argument("--once", action="store_true", help="Send SPaT only once")
args = parser.parse_args()

fileName = "spat.json"

# Determine config file path based on OS
current_os = platform.system()
if current_os == "Linux":
    config_file_path = os.path.join(os.path.expanduser("~"), "Desktop", "deb-anl-xil", "config", "anl-master-config.json")
elif current_os == "Windows":
    config_file_path = os.path.join("C:\\", "Users", "ddas", "deb-anl-xil", "config", "anl-master-config.json")
else:
    raise OSError(f"Unsupported operating system: {current_os}")

# Load config
with open(config_file_path, 'r') as configFile:
    config = json.load(configFile)

hostIp = config["IPAddress"]["HostIp"]
port = 5001
spat_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
spat_sender_socket.bind((hostIp, port))

vehicleStatusManagerPort = config["PortNumber"]["VehicleStatusManager"]
client_address = (hostIp, vehicleStatusManagerPort)

spatSendingTime = 0.0

def send_spat():
    with open(fileName, 'r') as f:
        data = f.read()
    spat_sender_socket.sendto(data.encode(), client_address)
    print("Sent SPaT at time", time.time())

if args.once:
    send_spat()  # Send only once
else:
    # Send continuously every 0.1 seconds
    while True:
        if time.time() - spatSendingTime >= 0.1:
            send_spat()
            spatSendingTime = time.time()

spat_sender_socket.close()
