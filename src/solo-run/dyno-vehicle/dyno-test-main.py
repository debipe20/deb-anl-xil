import socket
import json
import binascii
import struct
import haversine
import time
from osys import v2x
from BsmGenerator import BsmGenerator
from SpatManager import SpatManager
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


def getMessageType(string):
    messageType = ""

    if (string[:4]) == "0012":
        messageType = "MAP"

    elif (string[:4]) == "0013":
        messageType = "SPaT"

    elif (string[:4]) == "0014":
        messageType = "BSM"

    return messageType

def main():
    configFile = open("/nojournal/bin/anl-master-config.json", "r")
    config = json.load(configFile)
    configFile.close()

    hostIp = config["IPAddress"]["HostIp"]
    port = config["PortNumber"]["HostVehicleDatamanager"]
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
    spatManager = SpatManager()
    leadVehicleDataManager = LeadVehicleDataManager(config)

    hostVehicleLat, hostVehicleLon, hostVehicleSpeed = 0.0, 0.0, 0.0
    leadVehicleLat, leadVehicleLon, leadVehicleSpeed = 0.0, 0.0, 0.0
    relativeDistance, relativeSpeed, counter = 200.0, 0.0, 0.0
    leadVehicleDataReceivedTime = time.time()

    while True:
        data, address = dynoTestDataManagerSocket.recvfrom(2048)
        # print("Received data is following:\n", data)

        dataLength = len(data)

        if dataLength == SpeedDataLength:
            decodedCounter, decodedSpeed = struct.unpack("dd", data)            
            hostVehicleLat, hostVehicleLon, hostVehicleSpeed, bsmJsonString = (bsmGenerator.getBsmJsonString(decodedSpeed))
            
            encodedBsm = v2x.MessageFrame.from_json(bsmJsonString)
            dynoTestDataManagerSocket.sendto(encodedBsm, MessageReceiverAddress)
            
            logHostVehicleData(decodedCounter, decodedSpeed)
            print("Decoded data is: ", decodedSpeed, " and counter is: ", decodedCounter)
            
            if time.time() - leadVehicleDataReceivedTime > 1.0:
                while relativeDistance > 10:
                    relativeDistance, relativeSpeed, counter, leadVehicleSpeed = getSafeDynoOperationData(counter, relativeDistance)
                    sendingData =  struct.pack("dddd", relativeDistance, relativeSpeed, counter, leadVehicleSpeed)

                    dynoTestDataManagerSocket.sendto(sendingData, vehicleControllerAddress)
                    
                    logLeadVehicleData(counter, relativeDistance, relativeSpeed, leadVehicleSpeed)
                    print("Sending relative distance & speed, counter, and lead and host vehicle speed for safe operation:\n ", relativeDistance, relativeSpeed, counter, leadVehicleSpeed, hostVehicleSpeed)

        else:

            hexPacket = binascii.hexlify(data)
            packetString = str(hexPacket, encoding="utf-8")
            print("Hexed packet is following:\n", hexPacket)
            # bsmIdentifier = packetString.find("0014")
            
            msgIdentifier = packetString.find('001')
            payload = packetString[msgIdentifier:].strip()
            msgType = getMessageType(payload)

            # if bsmIdentifier >= 0:
            if msgType == "BSM":
                pass
                # leadVehicleInformationStatus, leadVehicleLat, leadVehicleLon, leadVehicleSpeed = (leadVehicleDataManager.getLeadVehicleInformation(payload))
                
                # if leadVehicleInformationStatus == True:
                #     relativeDistance = haversine.haversine((leadVehicleLat, leadVehicleLon), (hostVehicleLat, hostVehicleLon), unit=haversine.Unit.METERS)
 
                #     leadVehicleDataReceivedTime = time.time()
                #     relativeSpeed = leadVehicleSpeed - hostVehicleSpeed
                #     counter = counter + 1.0
                #     sendingData =  struct.pack("dddd", relativeDistance, relativeSpeed, counter, leadVehicleSpeed)
                    
                #     dynoTestDataManagerSocket.sendto(sendingData, vehicleControllerAddress)
                #     logLeadVehicleData(counter, relativeDistance, relativeSpeed, leadVehicleSpeed)
                #     print("Sending relative distance & speed, counter, and lead and host vehicle speed:\n ",
                #         relativeDistance, relativeSpeed, counter, leadVehicleSpeed, hostVehicleSpeed)

            elif msgType == "SPaT":
                spatManager.manageSpatData(payload)

        dynoTestDataManagerSocket.close()
        hostVehicleLogFile.close()
        leadVehicleLogFile.close()


if __name__ == "__main__":
    main()
