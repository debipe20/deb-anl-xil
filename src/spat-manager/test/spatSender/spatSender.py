import socket
import json
import time

fileName = "spat.txt"
fileName2 = "spat2.txt"

fileName3 = "SPaT-Payload.txt"

# Read a config file into a json object:
configFile = open("/nojournal/bin/anl-master-config.json", 'r')
config = (json.load(configFile))
configFile.close()

hostIp = config["HostIp"]
port = config["PortNumber"]["MessageDecoder"]
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((hostIp,port))

clientPort = config["PortNumber"]["SpatManager"]
communicationInfo = (hostIp, clientPort)

# f = open(fileName, 'r')
# data = f.read()
# s.sendto(data.encode(),communicationInfo)
# print("sent spat at time ", time.time())
# f.close()

# f = open(fileName2, 'r')
# data = f.read()
# s.sendto(data.encode(),communicationInfo)
# print("sent spat at time ", time.time())

# while True:

#     f = open(fileName, 'r')
#     data = f.read()
#     s.sendto(data.encode(),communicationInfo)
#     print("sent spat at time ", time.time())

#     time.sleep(0.0998)

while True:

    f = open(fileName3, 'r')
    for line in f:
        data = line.strip()
        s.sendto(data.encode(),communicationInfo)
        print("sent spat at time ", time.time())

        time.sleep(0.0998)
    

f.close()
s.close()