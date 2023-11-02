import socket
import json
import time

# Read a config file into a json object:
configFile = open("/nojournal/bin/anl-master-config.json", 'r')
config = (json.load(configFile))
configFile.close()

hostIp = config["HostIp"]
port = config["PortNumber"]["VehicleStatusManager"]
clientPort = config["PortNumber"]["SpatManager"]

communicationInfo = (hostIp, port)
clientInfo = (hostIp,clientPort)

requestSenderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
requestSenderSocket.bind(communicationInfo)

sendingJsonString = json.dumps(
    {
        "MsgType":"SignalGroupDataRequest",
        "IntersectionId": 1,
        "SignalGroup": 2
    }
)
requestSenderSocket.sendto(sendingJsonString.encode(),clientInfo)
print("Message sent  at time ", time.time())


requestSenderSocket.close()