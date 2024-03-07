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
    configFile = open("/nojournal/bin/anl-master-config.json", "r")
    config = json.load(configFile)
    configFile.close()

    hostIp = config["IPAddress"]["HostIp"]
    port = config["PortNumber"]["LeadVehicleDataManager"]
    hostAddress = (hostIp, port)

    MessageReceiverIp = config["IPAddress"]["V2XHubIp"]
    MessageReceiverPort = config["PortNumber"]["MessageReceiver"]
    MessageReceiverAddress = (MessageReceiverIp, MessageReceiverPort)

    vehicleControllerIp = config["IPAddress"]["VehicleControllerIp"]
    # vehicleControllerIp = config["IPAddress"]["HostIp"]
    vehicleControllerPort = config["PortNumber"]["VehicleController"]
    vehicleControllerAddress = (vehicleControllerIp, vehicleControllerPort)

    dynoTestDataManagerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dynoTestDataManagerSocket.bind(hostAddress)

    bsmGenerator = BsmGenerator(config)
    leadVehicleDataManager = LeadVehicleDataManager(config)

    hostVehicleLat, hostVehicleLon, hostVehicleSpeed = 0.0, 0.0, 0.0
    leadVehicleLat, leadVehicleLon, leadVehicleSpeed = 0.0, 0.0, 0.0
    counter = 0.0

    hostVehicleLogFile = open("host-vehicle-log.csv", "w")
    leadVehicleLogFile = open("lead-vehicle-log.csv", "w")

    hostHeader = ("TimeStamp, Counter, HostVehicleSpeed\n")
    leadHeader = ("TimeStamp, Counter, RelativeDistance, RelativeSpeed, LeadVehicleSpeed\n")

    hostVehicleLogFile.write(hostHeader)
    leadVehicleLogFile.write(leadHeader)

    while True:
        data, address = dynoTestDataManagerSocket.recvfrom(2048)
        # print("Received data is following:\n", data)

        dataLength = len(data)

        if dataLength == SpeedDataLength:
            decodedCounter, decodedSpeed = struct.unpack("dd", data)
            print("Decoded data is: ", decodedSpeed, " and counter is: ", decodedCounter)
            
            hostVehicleLat, hostVehicleLon, hostVehicleSpeed, bsmJsonString = (bsmGenerator.getBsmJsonString(decodedSpeed))
            
            encodedBsm = v2x.MessageFrame.from_json(bsmJsonString)
            dynoTestDataManagerSocket.sendto(encodedBsm, MessageReceiverAddress)

            csvrow = (str(round(time.time(), 4)) + "," 
                      + str(round(counter, 0)) + "," 
                      + str(round(decodedSpeed, 2)) + "\n")
            hostVehicleLogFile.write(csvrow)

        else:

            hexPacket = binascii.hexlify(data)
            packetString = str(hexPacket, encoding="utf-8")
            bsmIdentifier = packetString.find("0014")

            if bsmIdentifier >= 0:
                leadVehicleInformationStatus, leadVehicleLat, leadVehicleLon, leadVehicleSpeed = (leadVehicleDataManager.getLeadVehicleInformation(data))
                
                if leadVehicleInformationStatus == True:
                    relativeDistance = haversine.haversine(
                        (leadVehicleLat, leadVehicleLon),
                        (hostVehicleLat, hostVehicleLon),
                        unit=haversine.Unit.METERS,
                    )
                    relativeSpeed = leadVehicleSpeed - hostVehicleSpeed
                    counter = counter + 1.0
                    encodedDistance = struct.pack("d", relativeDistance)
                    encodedSpeed = struct.pack("d", relativeSpeed)
                    encodedCounter = struct.pack("d", counter)
                    encodedSpeedOriginal = struct.pack("d", leadVehicleSpeed)

                    print("Sending relative distance & speed, counter, and lead and host vehicle speed:\n ",
                        relativeDistance, relativeSpeed, counter, leadVehicleSpeed,hostVehicleSpeed,)

                    sendingData = (
                        encodedDistance
                        + encodedSpeed
                        + encodedCounter
                        + encodedSpeedOriginal
                    )
                    dynoTestDataManagerSocket.sendto(sendingData, vehicleControllerAddress)

                    csvrow = (
                        str(round(time.time(), 4))
                        + ","
                        + str(round(counter, 0))
                        + ","
                        + str(round(relativeDistance, 3))
                        + ","
                        + str(round(relativeSpeed, 2))
                        + ","
                        + str(round(leadVehicleSpeed, 2))
                        + "\n"
                    )
                    leadVehicleLogFile.write(csvrow)

            else:
                continue

    dynoTestDataManagerSocket.close()
    hostVehicleLogFile.close()
    leadVehicleLogFile.close()


if __name__ == "__main__":
    main()
