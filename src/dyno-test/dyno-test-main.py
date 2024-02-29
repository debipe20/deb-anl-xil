import socket
import json
import binascii
import struct
import haversine
from osys import v2x
from BsmGenerator import BsmGenerator
from LeadVehicleDataManager import LeadVehicleDataManager

SpeedDataLength = 8

def main():
    configFile = open("/nojournal/bin/anl-master-config.json", 'r')
    config = (json.load(configFile))
    configFile.close()

    hostIp = config["IPAddress"]["HostIp"]
    port = config["PortNumber"]["LeadVehicleDataManager"]
    hostAddress = (hostIp, port)

    MessageReceiverIp = config["IPAddress"]["V2XHubIp"]
    MessageReceiverPort = config["PortNumber"]["MessageReceiver"]
    MessageReceiverAddress = (MessageReceiverIp, MessageReceiverPort)

    vehicleControllerIp = config["IPAddress"]["VehicleControllerIp"]
    vehicleControllerPort = config["PortNumber"]["VehicleController"]
    vehicleControllerAddress = (vehicleControllerIp, vehicleControllerPort)
    
    dynoTestDataManagerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dynoTestDataManagerSocket.bind(hostAddress)
    
    bsmGenerator = BsmGenerator(config)
    leadVehicleDataManager = LeadVehicleDataManager(config)

    hostVehicleLat, hostVehicleLon, hostVehicleSpeed = 42.2994845, -83.6992433, 5.0
    leadVehicleLat, leadVehicleLon, leadVehicleSpeed = 0.0, 0.0, 0.0

    while True:
        data, address = dynoTestDataManagerSocket.recvfrom(2048)
        # print("Received data is following:\n", data)
        
        dataLength = len(data)
        print("Received data length: ", len(data))

        if dataLength == SpeedDataLength:
            deocded_data = struct.unpack("!d", data)[0]
            hostVehicleLat, hostVehicleLon, bsmJsonString =  bsmGenerator.getBsmJsonString(deocded_data)
            encodedBsm = v2x.MessageFrame.from_json(bsmJsonString)
            print("Encoded BSM is Following:\n", encodedBsm)

            dynoTestDataManagerSocket.sendto(encodedBsm, MessageReceiverAddress)

            # print(deocded_data)
            # decoded_data_length = struct.calcsize("!d")
            # print("Length of decoded data:", decoded_data_length)

        else:
            hexPacket = binascii.hexlify(data)
            print("Hexed Data:\n ", hexPacket)
            packetString = str(hexPacket, encoding='utf-8')
            bsmIdentifier = packetString.find('0014')

            if bsmIdentifier >= 0:
                leadVehicleLat, leadVehicleLon, leadVehicleSpeed = leadVehicleDataManager.getLeadVehicleInformation(data)
                relativeDistance = haversine.haversine((hostVehicleLat, hostVehicleLon), (leadVehicleLat, leadVehicleLon), unit=haversine.Unit.METERS)
                relativeSpeed = hostVehicleSpeed - leadVehicleSpeed
                encoded_data = struct.pack("!d", relativeSpeed)
                sendingData = str(relativeSpeed).encode()
                dynoTestDataManagerSocket.sendto(sendingData, vehicleControllerAddress)

            else: continue

    dynoTestDataManagerSocket.close()

if __name__ == '__main__':
    main()