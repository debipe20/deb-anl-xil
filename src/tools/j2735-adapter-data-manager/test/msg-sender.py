import socket
import json
import time
import binascii
fileName = "sample-raw-message.txt"

# Read a config file into a json object:
configFile = open("/nojournal/bin/anl-master-config.json", 'r')
config = (json.load(configFile))
configFile.close()

hostIp = config["IPAddress"]["HostIp"]
port = config["PortNumber"]["VehicleStatusManager"]
msgSenderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
msgSenderSocket.bind((hostIp,port))

clientPort = config["PortNumber"]["LeadVehicleDataManager"]
communicationInfo = (hostIp, clientPort)
msgSendingTime = 0.0

f = open(fileName, 'r')
data = f.read()
# data = binascii.unhexlify(data)
msgSenderSocket.sendto(data.encode(),communicationInfo)

# while True:
#     if time.time()-msgSendingTime >=1.0:
#         f = open(fileName, 'r')
#         data = f.read()
#         msgSenderSocket.sendto(data.encode(),communicationInfo)
#         mapSendingTime = time.time()
#         print("sent Map at time", time.time())

f.close()
msgSenderSocket.close()