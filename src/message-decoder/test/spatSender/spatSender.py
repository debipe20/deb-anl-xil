import socket
import json
import time

# Read a config file into a json object:
configFile = open("/nojournal/bin/anl-master-config.json", 'r')
config = (json.load(configFile))
configFile.close()

hostIp = config["HostIp"]
port = 2000
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((hostIp,port))

clientPort = config["PortNumber"]["MessageDecoder"]
communicationInfo = (hostIp, clientPort)

# fileName = "spat.txt"
fileName = "SPaT-Payload.txt"

f = open(fileName, 'r')

while True:

    for line in f:
        data = line.strip()
        s.sendto(data.encode(),communicationInfo)
        print("sent spat at time ", time.time())

        time.sleep(0.0998)
    
    f.close()
    break

s.close()