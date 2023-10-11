import socket
import json
import datetime
import time

fileName = "map.json"
fileName2 = "map2.json"
fileName3 = "map3.json"

# Read a config file into a json object:
configFile = open("/nojournal/bin/anl-master-config.json", 'r')
config = (json.load(configFile))
configFile.close()

hostIp = config["HostIp"]
port = config["PortNumber"]["MessageDecoder"]
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((hostIp,port))

priorityRequestGeneratorPort = config["PortNumber"]["MapManager"]
communicationInfo = (hostIp, priorityRequestGeneratorPort)

mapNo = 1

while True:

    f = open(fileName, 'r')
    data = f.read()
    s.sendto(data.encode(),communicationInfo)
    print("sent Map ", mapNo," at time", time.time())
    mapNo = mapNo + 1
    time.sleep(0.998)
    
    f = open(fileName2, 'r')
    data = f.read()
    s.sendto(data.encode(),communicationInfo)
    print("sent Map ", mapNo," at time", time.time())
    mapNo = mapNo + 1
    time.sleep(0.998)
    
    f = open(fileName3, 'r')
    data = f.read()
    s.sendto(data.encode(),communicationInfo)
    print("sent Map ", mapNo," at time", time.time())
    mapNo = 1
    time.sleep(0.998)

f.close()
s.close()