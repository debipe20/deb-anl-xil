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

hostVehicleLogFile = open("host-vehicle-log.csv", "w")
leadVehicleLogFile = open("lead-vehicle-log.csv", "w")

hostHeader = ("TimeStamp, Counter, HostVehicleSpeed\n")
leadHeader = ("TimeStamp, Counter, RelativeDistance, RelativeSpeed, LeadVehicleSpeed\n")

hostVehicleLogFile.write(hostHeader)
leadVehicleLogFile.write(leadHeader)

def logLeadVehicleData(counter, relativeDistance, relativeSpeed, leadVehicleSpeed):
    csvrow = (
            str(round(time.time(), 4)) + ","
            + str(round(counter, 0))  + ","
            + str(round(relativeDistance, 3)) + ","
            + str(round(relativeSpeed, 2)) + ","
            + str(round(leadVehicleSpeed, 2)) + "\n")
    leadVehicleLogFile.write(csvrow)
    
def logHostVehicleData(counter, decodedSpeed):
    csvrow = (str(round(time.time(), 4)) + "," 
            + str(round(counter, 0)) + "," 
            + str(round(decodedSpeed, 2)) + "\n")
    hostVehicleLogFile.write(csvrow)
    
def getSafeDynoOperationData(counter, relativeDistance):
    
    relativeDistance = relativeDistance - 5.0
    relativeSpeed, leadVehicleSpeed = 0.0, 0.0
    counter = counter + 1.0        
    
    
    return relativeDistance, relativeSpeed, counter, leadVehicleSpeed

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
    dynoTestDataManagerSocket.settimeout(1.0)

    bsmGenerator = BsmGenerator(config)
    leadVehicleDataManager = LeadVehicleDataManager(config)

    hostVehicleLat, hostVehicleLon, hostVehicleSpeed = 0.0, 0.0, 0.0
    leadVehicleLat, leadVehicleLon, leadVehicleSpeed = 0.0, 0.0, 0.0
    relativeDistance, relativeSpeed, counter = 200.0, 0.0, 0.0
   
    try:
        while True:
            try:
                data, address = dynoTestDataManagerSocket.recvfrom(2048)
                # print("Received data is following:\n", data)

                dataLength = len(data)

                if dataLength == SpeedDataLength:
                    decodedCounter, decodedSpeed = struct.unpack("dd", data)
                    # print("Decoded data is: ", decodedSpeed, " and counter is: ", decodedCounter)
                    
                    hostVehicleLat, hostVehicleLon, hostVehicleSpeed, bsmJsonString = (bsmGenerator.getBsmJsonString(decodedSpeed))
                    
                    encodedBsm = v2x.MessageFrame.from_json(bsmJsonString)
                    dynoTestDataManagerSocket.sendto(encodedBsm, MessageReceiverAddress)

                    # csvrow = (str(round(time.time(), 4)) + "," 
                    #         + str(round(counter, 0)) + "," 
                    #         + str(round(decodedSpeed, 2)) + "\n")
                    # hostVehicleLogFile.write(csvrow)
                    print("Decoded data is: ", decodedSpeed, " and counter is: ", decodedCounter)
                    
                    logHostVehicleData(counter, decodedSpeed)

                else:

                    hexPacket = binascii.hexlify(data)
                    packetString = str(hexPacket, encoding="utf-8")
                    bsmIdentifier = packetString.find("0014")

                    if bsmIdentifier >= 0:
                        leadVehicleInformationStatus, leadVehicleLat, leadVehicleLon, leadVehicleSpeed = (leadVehicleDataManager.getLeadVehicleInformation(data))
                        
                        if leadVehicleInformationStatus == True:
                            relativeDistance = haversine.haversine((leadVehicleLat, leadVehicleLon),(hostVehicleLat, hostVehicleLon),unit=haversine.Unit.METERS)
                            # if relativeDistance >= 50.0:
                            #     relativeDistance = 30.0
                            relativeSpeed = leadVehicleSpeed - hostVehicleSpeed
                            counter = counter + 1.0
                            encodedDistance = struct.pack("d", relativeDistance)
                            encodedSpeed = struct.pack("d", relativeSpeed)
                            encodedCounter = struct.pack("d", counter)
                            encodedSpeedOriginal = struct.pack("d", leadVehicleSpeed)

                            print("Sending relative distance & speed, counter, and lead and host vehicle speed:\n ",
                                relativeDistance, relativeSpeed, counter, leadVehicleSpeed, hostVehicleSpeed)

                            sendingData = (
                                encodedDistance
                                + encodedSpeed
                                + encodedCounter
                                + encodedSpeedOriginal
                            )
                            dynoTestDataManagerSocket.sendto(sendingData, vehicleControllerAddress)

                            # csvrow = (
                            #     str(round(time.time(), 4)) + ","
                            #     + str(round(counter, 0))  + ","
                            #     + str(round(relativeDistance, 3)) + ","
                            #     + str(round(relativeSpeed, 2)) + ","
                            #     + str(round(leadVehicleSpeed, 2)) + "\n"
                            # )
                            # leadVehicleLogFile.write(csvrow)
                            logLeadVehicleData(counter, relativeDistance, relativeSpeed, leadVehicleSpeed)

                    else:
                        continue
            
            except:
                # if (time.time() - leadVehicleDataReceivedTime) >= 2.0 :
                    # leadVehicleDataReceivedTime = time.time()
                    # counter = counter + 1.0
                    # relativeDistance, relativeSpeed, leadVehicleSpeed = 5.0, 0.0, 0.0
                while relativeDistance > 10:
                    relativeDistance, relativeSpeed, counter, leadVehicleSpeed = getSafeDynoOperationData(counter, relativeDistance)
                  
                    encodedDistance = struct.pack("d", relativeDistance)
                    encodedSpeed = struct.pack("d", relativeSpeed)
                    encodedCounter = struct.pack("d", counter)
                    encodedSpeedOriginal = struct.pack("d", leadVehicleSpeed)

                    print("Sending relative distance & speed, counter, and lead and host vehicle speed for safe operation:\n ", relativeDistance, relativeSpeed, counter, leadVehicleSpeed, hostVehicleSpeed)
                    
                    sendingData = (encodedDistance + encodedSpeed + encodedCounter + encodedSpeedOriginal)
                    # sendingData = struct.pack("dddd", 5.0, 0.0, 1.0, 0.0)
                    dynoTestDataManagerSocket.sendto(sendingData, vehicleControllerAddress)
                    logLeadVehicleData(counter, relativeDistance, relativeSpeed, leadVehicleSpeed)
                    time.sleep(0.099)
                      
    except KeyboardInterrupt:
        print("Finished with ctrl+c")
        
    dynoTestDataManagerSocket.close()
    hostVehicleLogFile.close()
    leadVehicleLogFile.close()


if __name__ == "__main__":
    main()
