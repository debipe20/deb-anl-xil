import socket
import json
import binascii
from osys import v2x


def main():

    configFile = open("/nojournal/bin/anl-master-config.json", 'r')
    config = (json.load(configFile))
    configFile.close()
    
    hostIp = config["HostIp"]
    port = config["PortNumber"]["MessageDecoder"]
    com_info = (hostIp, port)
    
    spatManagerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    spatManagerSocket.bind(com_info)

    spatManagerSocket.close()

if __name__ == '__main__':
    main()