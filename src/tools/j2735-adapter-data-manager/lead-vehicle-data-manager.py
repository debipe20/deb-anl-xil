import socket
import json
import binascii
from osys import v2x

def main():
    configFile = open("/nojournal/bin/anl-master-config.json", 'r')
    config = (json.load(configFile))
    configFile.close()

    hostIp = config["IPAddress"]["HostIp"]
    port = config["PortNumber"]["LeadVehicleDataManager"]
    clientIp = config["IPAddress"]["VehicleControllerIp"]
    clientPort = config["PortNumber"]["VehicleController"]
    com_info = (hostIp, port)
    clientAddress = (clientIp, clientPort)
    
    leadVehicleDataManagerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    leadVehicleDataManagerSocket.bind(com_info)

    # data = b'\x00\x14%\x00<\x0e\xb5\x89$"\'m\xcc\xc1\x9c\xb3L!\x0c\xb0\x00\x00\x00\x00 \x007\xe8~}\x07\xd0\x7f\x7f\xff\x80\x00\x01\x80\x08'

    # encodedBsm = binascii.hexlify(data)
    # print(encodedBsm)
    # receivedJsonString = v2x.MessageFrame.to_json(data, len(data))
    # print(receivedJsonString)


    while True:
        data, address = leadVehicleDataManagerSocket.recvfrom(2048)
        print("Received data:", data)
        encodedBsm = binascii.hexlify(data)
        print("Enocoded Bsm is following: \n", encodedBsm)
        receivedJsonString = v2x.MessageFrame.to_json(data, len(data))
        print(receivedJsonString)

    leadVehicleDataManagerSocket.close()

if __name__ == '__main__':
    main()