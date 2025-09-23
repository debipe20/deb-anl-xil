import socket
import json
import datetime
import time
import os
import platform

fileName = "map.json"

# Read a config file into a json object:
current_os = platform.system()
    
if current_os == "Linux":
    config_file_path = os.path.join(os.path.expanduser("~"), "Desktop", "deb-anl-xil", "config", "anl-master-config.json")
    
# configFile = open("/nojournal/bin/mmitss-phase3-master-config.json", 'r')
configFile = open(config_file_path, 'r')
config = (json.load(configFile))
configFile.close()

hostIp = config["IPAddress"]["HostIp"]
port = config["PortNumber"]["MessageDecoder"]
map_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
map_sender_socket.bind((hostIp,port))

vehicleStatusManagerPort = config["PortNumber"]["VehicleStatusManager"]
client_address = (hostIp, vehicleStatusManagerPort)
mapSendingTime = 0.0

while True:
    if time.time()-mapSendingTime >=1.0:
        f = open(fileName, 'r')
        data = f.read()
        map_sender_socket.sendto(data.encode(),client_address)
        mapSendingTime = time.time()
        print("sent Map at time", time.time())

f.close()
map_sender_socket.close()