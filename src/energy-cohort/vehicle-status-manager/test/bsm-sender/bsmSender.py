import socket
import json
import datetime
import time
import os
import platform

fileName = "bsm.json"

# Read a config file into a json object:
current_os = platform.system()
    
if current_os == "Linux":
    config_file_path = os.path.join(os.path.expanduser("~"), "Desktop", "deb-anl-xil", "config", "anl-master-config.json")
    
# Read a config file into a json object:
# configFile = open("/nojournal/bin/mmitss-phase3-master-config.json", 'r')
configFile = open(config_file_path, 'r')
config = (json.load(configFile))
configFile.close()

hostIp = config["IPAddress"]["HostIp"]
port = config["PortNumber"]["EgoVehicleDataManager"]
bsm_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
bsm_sender_socket.bind((hostIp,port))

vehicleStatusManagerPort = config["PortNumber"]["VehicleStatusManager"]
client_address = (hostIp, vehicleStatusManagerPort)

bsmSendingTime = 0.0

while True:
    if time.time()-bsmSendingTime >= 0.1:
        f = open(fileName, 'r')
        data = f.read() 
        bsm_sender_socket.sendto(data.encode(),client_address)
        bsmSendingTime = time.time()
        # print (time.time())
        # print(data.encode())
        print("sent BSM at time", time.time())

f.close()
bsm_sender_socket.close()