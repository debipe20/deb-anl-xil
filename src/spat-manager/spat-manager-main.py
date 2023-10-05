import socket
import json
import binascii
from osys import v2x


def main():

    configFile = open("/nojournal/bin/anl-master-config.json", 'r')
    config = (json.load(configFile))
    configFile.close()
    
    hostIp = config["HostIp"]
    port = config["PortNumber"]["SpatManager"]
    com_info = (hostIp, port)
    
    spatManagerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    spatManagerSocket.bind(com_info)

    while True:
        bsmBytes = binascii.unhexlify(bsmPayload)
        receivedJsonString = v2x.MessageFrame.to_json(bsmBytes, len(bsmBytes))
        receivedJsonString = json.loads(receivedJsonString)


    spatManagerSocket.close()

if __name__ == '__main__':
    main()