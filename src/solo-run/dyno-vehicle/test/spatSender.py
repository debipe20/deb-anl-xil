
import socket
import json
import time
import binascii

def main():
    configFile = open("/nojournal/bin/anl-master-config.json", 'r')
    config = (json.load(configFile))
    configFile.close()

    hostIp = config["IPAddress"]["HostIp"]
    port = config["PortNumber"]["MessageDecoder"]
    hostAddress = (hostIp, port)

    clientIp = config["IPAddress"]["HostIp"]
    clientPort = config["PortNumber"]["HostVehicleDatamanager"]
    clientAddress = (clientIp, clientPort)
    
    spatSenderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    spatSenderSocket.bind(hostAddress)
    

    while True:

        spatPayload = '00134c4247bc0180000000408247bcac910700204342b52ab52802022a159f559f401810d0ad4aad4a01008a8567d567d00904342b52c650005021a159f6328002c10d0ad4b19400180868567d8ca0'
        sendingData =  binascii.unhexlify(spatPayload)
        # sendingData = spatPayload.encode()
        spatSenderSocket.sendto(sendingData, clientAddress)
        print("sent spat at time ", time.time())

        time.sleep(0.0998)

    spatSenderSocket.close()

if __name__ == '__main__':
    main()