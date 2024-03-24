import socket
import json
import datetime
import time

fileName = "bsm.json"

# Read a config file into a json object:
configFile = open("/nojournal/bin/anl-master-config.json", 'r')
config = (json.load(configFile))
configFile.close()

hostIp = config["IPAddress"]["HostIp"]
# port = config["PortNumber"]["BsmGenerator"]
port = 4001
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((hostIp,port))

vehicleStatusManagerPort = config["PortNumber"]["VehicleStatusManager"]
communicationInfo = (hostIp, vehicleStatusManagerPort)


bsmSendingTime = 0.0
f = open(fileName, 'r')
data = f.read() 
s.sendto(data.encode(),communicationInfo)
bsmSendingTime = time.time()
# print (time.time())
# print(data.encode())
print("sent BSM at time", time.time())
# while True:
#     if time.time()-bsmSendingTime >= 0.1:
#         f = open(fileName, 'r')
#         data = f.read() 
#         s.sendto(data.encode(),communicationInfo)
#         bsmSendingTime = time.time()
#         # print (time.time())
#         # print(data.encode())
#         print("sent BSM at time", time.time())

f.close()
s.close()