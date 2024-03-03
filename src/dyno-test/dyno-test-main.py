import socket
import json
import binascii
import struct
import haversine
import time
from osys import v2x
from BsmGenerator import BsmGenerator
from LeadVehicleDataManager import LeadVehicleDataManager

SpeedDataLength = 16

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

    # vehicleControllerIp = config["IPAddress"]["VehicleControllerIp"]
    vehicleControllerIp = config["IPAddress"]["HostIp"]
    vehicleControllerPort = config["PortNumber"]["VehicleController"]
    vehicleControllerAddress = (vehicleControllerIp, vehicleControllerPort)
    
    dynoTestDataManagerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dynoTestDataManagerSocket.bind(hostAddress)
    
    bsmGenerator = BsmGenerator(config)
    leadVehicleDataManager = LeadVehicleDataManager(config)

    hostVehicleLat, hostVehicleLon, hostVehicleSpeed = 42.2994845, -83.6992433, 0.0
    leadVehicleLat, leadVehicleLon, leadVehicleSpeed = 0.0, 0.0, 0.0

    receivedTime = time.time()

    counter = 0.0
    # sendingTime = time.time()
    # while True:
    #     timeGap = time.time() - sendingTime
    #     if timeGap >=0.1:
    #         relativeDistance = 9.5
    #         relativeSpeed = 1.5
    #         counter = counter + 1.0

    #         encodedDistance = struct.pack("d", relativeDistance)
    #         encodedSpeed = struct.pack("d", relativeSpeed)
    #         encodedCounter = struct.pack("d", counter)

    #         sendingData = encodedDistance + encodedSpeed + encodedCounter
    #         dynoTestDataManagerSocket.sendto(sendingData, vehicleControllerAddress)
    #         print("Send Data No: ", counter, "at time gap: ", timeGap)
    #         # print("Send Data No: ", counter)
    #         sendingTime = time.time()


    while True:
        data, address = dynoTestDataManagerSocket.recvfrom(2048)
        # print("Received data is following:\n", data)
        
        dataLength = len(data)
        # # print("Received data length: ", len(data))

        if dataLength == SpeedDataLength:
            # decoded_data = struct.unpack("d", data)[0]
            decodedCounter, decodedSpeed = struct.unpack("dd", data)
            # print("Decoded data is: ", decodedSpeed)
            print("Decoded data is: ", decodedSpeed, " and counter is: ", decodedCounter)
            hostVehicleLat, hostVehicleLon, hostVehicleSpeed , bsmJsonString =  bsmGenerator.getBsmJsonString(decodedSpeed)
            encodedBsm = v2x.MessageFrame.from_json(bsmJsonString)
            print("Encoded BSM is Following:\n", encodedBsm)

            dynoTestDataManagerSocket.sendto(encodedBsm, MessageReceiverAddress)

            # print(decoded_data)
            # decoded_data_length = struct.calcsize("!d")
            # print("Length of decoded data:", decoded_data_length)

        else:
        
            hexPacket = binascii.hexlify(data)
            # print("Hexed Data:\n ", hexPacket)
            packetString = str(hexPacket, encoding='utf-8')
            bsmIdentifier = packetString.find('0014')

            if bsmIdentifier >= 0:
                timeGap = time.time() - receivedTime
                receivedTime = time.time()
                leadVehicleLat, leadVehicleLon, leadVehicleSpeed = leadVehicleDataManager.getLeadVehicleInformation(data)
                relativeDistance = haversine.haversine((leadVehicleLat, leadVehicleLon),(hostVehicleLat, hostVehicleLon), unit=haversine.Unit.METERS)
                relativeSpeed = leadVehicleSpeed - hostVehicleSpeed 
                counter = counter + 1.0
                encodedDistance = struct.pack("d", relativeDistance)
                encodedSpeed = struct.pack("d", relativeSpeed)
                encodedCounter = struct.pack("d", counter)
                encodedSpeedOriginal = struct.pack("d", leadVehicleSpeed)
                print("Lat and Lon is following:", hostVehicleLat, hostVehicleLon, leadVehicleLat, leadVehicleLon)
                print("Sending relative distance & speed, counter, and speed:\n ", relativeDistance, relativeSpeed, counter, leadVehicleSpeed, hostVehicleSpeed)
                print("Time Gap is: ", timeGap)
                sendingData = encodedDistance + encodedSpeed + encodedCounter + encodedSpeedOriginal
                dynoTestDataManagerSocket.sendto(sendingData, vehicleControllerAddress)

            else: continue

    dynoTestDataManagerSocket.close()

if __name__ == '__main__':
    main()