import socket
import json
import time

fileName = "spat-json-string.json"
fileName1 = "spat.txt"
fileName2 = "spat2.txt"

fileName3 = "SPaT-Payload.txt"

# Read a config file into a json object:
configFile = open("/nojournal/bin/anl-master-config.json", 'r')
config = (json.load(configFile))
configFile.close()

hostIp = config["HostIp"]
port = config["PortNumber"]["MessageDecoder"]
clientPort = config["PortNumber"]["SpatManager"]


communicationInfo = (hostIp, port)
clientInfo = (hostIp, clientPort)

spatSenderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
spatSenderSocket.bind((communicationInfo))


f = open(fileName, 'r')
data = f.read()
spatSenderSocket.sendto(data.encode(),clientInfo)
print("sent following spat at time ", time.time(), data)
f.close()

# f = open(fileName1, 'r')
# data = f.read()
# spatSenderSocket.sendto(data.encode(),clientInfo)
# print("sent spat at time ", time.time())
# f.close()

# f = open(fileName2, 'r')
# data = f.read()
# spatSenderSocket.sendto(data.encode(),clientInfo)
# print("sent spat at time ", time.time())

# while True:

#     f = open(fileName, 'r')
#     data = f.read()
#     spatSenderSocket.sendto(data.encode(),clientInfo)
#     print("sent spat at time ", time.time())

#     time.sleep(0.0998)

# while True:

#     f = open(fileName3, 'r')
#     for line in f:
#         data = line.strip()
#         spatSenderSocket.sendto(data.encode(),clientInfo)
#         print("sent spat at time ", time.time())

#         time.sleep(0.0998)
    

f.close()
spatSenderSocket.close()