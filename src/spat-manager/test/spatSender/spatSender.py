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
clientPort = config["PortNumber"]["SpatManager"]
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((hostIp,clientPort))


communicationInfo = (hostIp, port)

data = "00136D00385A6C3D3D3CA0A9979F44127774CBCB9E5C7D34EFDC0001020008D0A612B881600208607B5F00204343DB0BDB080B02181ED7C00C10C0F6BE00808687CE77CE701804303DAF80282181ED7C01810D0F6C2F6C203408607B5F00704303DAF804021A1F39DF39C07010C0F6BE"
s.sendto(data.encode(),communicationInfo)
print("sent spat at time ", time.time())
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

# while True:

#     f = open(fileName3, 'r')
#     for line in f:
#         data = line.strip()
#         s.sendto(data.encode(),communicationInfo)
#         print("sent spat at time ", time.time())

#         time.sleep(0.0998)
    

f.close()
s.close()