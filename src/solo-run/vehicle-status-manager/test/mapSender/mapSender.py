import socket
import json
import datetime
import time

fileName = "mcity-state-liberty.json"
fileName1 = "map.json"
fileName2 = "map2.json"
fileName3 = "map3.json"

# Read a config file into a json object:
configFile = open("/nojournal/bin/anl-master-config.json", 'r')
config = (json.load(configFile))
configFile.close()

hostIp = config["IPAddress"]["HostIp"]
# port = config["PortNumber"]["MessageDecoder"]
port = 2010
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((hostIp,port))

vehicleStatusManagerPort = config["PortNumber"]["VehicleStatusManager"]
communicationInfo = (hostIp, vehicleStatusManagerPort)

mapNo = 1

f = open(fileName, 'r')
data = f.read()
s.sendto(data.encode(),communicationInfo)
print("sent Map ", mapNo," at time", time.time())
mapNo = mapNo + 1
f.close()
time.sleep(0.998)
# while True:

#     f = open(fileName, 'r')
#     data = f.read()
#     s.sendto(data.encode(),communicationInfo)
#     print("sent Map ", mapNo," at time", time.time())
#     mapNo = mapNo + 1
#     f.close()
#     time.sleep(0.998)

    # f = open(fileName1, 'r')
    # data = f.read()
    # s.sendto(data.encode(),communicationInfo)
    # print("sent Map ", mapNo," at time", time.time())
    # mapNo = mapNo + 1
    # f.close()
    # time.sleep(0.998)
    
    # f = open(fileName2, 'r')
    # data = f.read()
    # s.sendto(data.encode(),communicationInfo)
    # print("sent Map ", mapNo," at time", time.time())
    # mapNo = mapNo + 1
    # f.close()
    # time.sleep(0.998)
    
    # f = open(fileName3, 'r')
    # data = f.read()
    # s.sendto(data.encode(),communicationInfo)
    # print("sent Map ", mapNo," at time", time.time())
    # mapNo = 1
    # f.close()
    # time.sleep(0.998)
    
s.close()
