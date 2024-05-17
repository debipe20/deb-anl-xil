import socket
import json
import binascii
import struct
from osys import v2x
from LeadVehicleDataManager import LeadVehicleDataManager

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
    
    leadVehicleDataManager = LeadVehicleDataManager(config)

    while True:
        data, address = leadVehicleDataManagerSocket.recvfrom(2048)
        # print("Received data is following:\n", data)
        # print("Received data type is following:\n", type(data))
        # deocded_data = struct.unpack("!d", data)[0]
        # print("Data length type1 is:",len(data))
        # print(deocded_data)
        # decoded_data_length = struct.calcsize("!d")
        # print("Length of decoded data:", decoded_data_length)
        
        hexPacket = binascii.hexlify(data)
        print("Hexed Data:\n ", hexPacket)
        packetString = str(hexPacket, encoding='utf-8')
        bsmIdentifier = packetString.find('0014')
        # print("BsmIdentifier: ", bsmIdentifier)
        if bsmIdentifier >=0:
            leadVehicleSpeed = leadVehicleDataManager.getLeadVehicleInformation(data)
        
            sendingData = str(leadVehicleSpeed).encode()
            leadVehicleDataManagerSocket.sendto(sendingData, clientAddress)
        else: continue

    leadVehicleDataManagerSocket.close()

if __name__ == '__main__':
    main()