import socket
import json
import binascii
import socket

def main():
    configFile = open("/nojournal/bin/anl-master-config.json", 'r')
    config = (json.load(configFile))
    configFile.close()

    hostIp = config["HostIp"]
    port = config["PortNumber"]["DataConverter"]
    clientIp = config["V2XHubIp"]
    clientPort = config["PortNumber"]["MessageReceiver"]
    com_info = (hostIp, port)
    clientAddress = (clientIp, clientPort)

    dataConverterSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dataConverterSocket.bind(com_info)

    while True:
        data, address = dataConverterSocket.recvfrom(1024)
        encodedBsm = binascii.unhexlify(data)
        # print("Encoded BSM is Following:\n", encodedBsm)
        dataConverterSocket.sendto(encodedBsm, clientAddress)
        
    dataConverterSocket.close()

if __name__ == '__main__':
    main()