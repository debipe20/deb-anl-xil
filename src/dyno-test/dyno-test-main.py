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

    hostVehicleLat, hostVehicleLon, hostVehicleSpeed = 42.2994845, -83.6992433, 0.0
    leadVehicleLat, leadVehicleLon, leadVehicleSpeed = 0.0, 0.0, 0.0

    receivedTime = time.time()

    counter = 0.0
    # logfile = open("log-data.log", "w")
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
        # # print("Received data length: ", len(data))

        if dataLength == SpeedDataLength:
            # decoded_data = struct.unpack("d", data)[0]
            decodedCounter, decodedSpeed = struct.unpack("dd", data)
            # print("Decoded data is: ", decodedSpeed)
            print(
                "Decoded data is: ", decodedSpeed, " and counter is: ", decodedCounter
            )
            hostVehicleLat, hostVehicleLon, hostVehicleSpeed, bsmJsonString = (
                bsmGenerator.getBsmJsonString(decodedSpeed)
            )
            encodedBsm = v2x.MessageFrame.from_json(bsmJsonString)
            # print("Encoded BSM is Following:\n", encodedBsm)

            dynoTestDataManagerSocket.sendto(encodedBsm, MessageReceiverAddress)

            # msg = (
            #     "\n["
            #     + str(round(time.time(),4))
            #     + "]: ***Follwing Data is received*** \nCounter: "
            #     + str(counter)
            #     + "\nDecoded Speed: "
            #     + str(round(decodedSpeed, 2))
            #     + "\n"
            # )
            # logfile.write(msg)
            csvrow = (str(round(time.time(), 4)) + "," 
                      + str(round(counter, 0)) + "," 
                      + str(round(decodedSpeed, 2)) + "\n")
            hostVehicleLogFile.write(csvrow)

            # decoded_data_length = struct.calcsize("!d")
            # print("Length of decoded data:", decoded_data_length)

        else:

            hexPacket = binascii.hexlify(data)
            # print("Hexed Data:\n ", hexPacket)
            packetString = str(hexPacket, encoding="utf-8")
            bsmIdentifier = packetString.find("0014")

            if bsmIdentifier >= 0:
                timeGap = time.time() - receivedTime
                receivedTime = time.time()
                leadVehicleLat, leadVehicleLon, leadVehicleSpeed = (
                    leadVehicleDataManager.getLeadVehicleInformation(data)
                )
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

                print(
                    "Sending relative distance & speed, counter, and speed:\n ",
                    relativeDistance,
                    relativeSpeed,
                    counter,
                    leadVehicleSpeed,
                    hostVehicleSpeed,
                )

                sendingData = (
                    encodedDistance
                    + encodedSpeed
                    + encodedCounter
                    + encodedSpeedOriginal
                )
                dynoTestDataManagerSocket.sendto(sendingData, vehicleControllerAddress)

                # msg = (
                #     "\n["
                #     + str(time.time())
                #     + "]: ***Follwing Data is sent*** \nRelative Distance: "
                #     + str(relativeDistance)
                #     + "\nRelative Speed: "
                #     + str(relativeSpeed)
                #     + "\nCounter: "
                #     + str(counter)
                #     + "\nCurrent Speed: "
                #     + str(leadVehicleSpeed)
                #     + "\n"
                # )
                # logfile.write(msg)

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
    # logfile.close()
    hostVehicleLogFile.close()
    leadVehicleLogFile.close()


if __name__ == "__main__":
    main()
