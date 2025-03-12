import socket
import json
import binascii
import struct
import haversine
import time
import atexit
from osys import v2x
from BsmGenerator import BsmGenerator
from LeadVehicleDataManager import LeadVehicleDataManager
from Logger import Logger

SpeedDataLength = 16

def getSafeDynoOperationData(counter, relativeDistance):
    
    relativeDistance = relativeDistance - 5.0
    relativeSpeed, leadVehicleSpeed = 0.0, 0.0
    counter = counter + 1.0        
    
    return relativeDistance, relativeSpeed, counter, leadVehicleSpeed

def destruct_logger(logger:Logger):
    logger.consoleDisplay("Shutting down now!")
    del logger

def main():
    configFile = open("../../config/anl-master-config.json", "r")
    config = json.load(configFile)
    configFile.close()

    hostIp = config["IPAddress"]["HostIp"]
    port = config["PortNumber"]["HostVehicleDataManager"]
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

    # Get logging and console output variables
    consoleStatus = config["GeneralInformation"]["ConsoleOutput"]
    loggingStatus = config["GeneralInformation"]["Logging"]
    debugStatus =  config["GeneralInformation"]["Debug"]
    
    logger = Logger(consoleStatus, loggingStatus, debugStatus)
    atexit.register(lambda: destruct_logger(logger))
    bsmGenerator = BsmGenerator(config, logger)
    leadVehicleDataManager = LeadVehicleDataManager(config, logger)

    hostVehicleLat, hostVehicleLon, hostVehicleSpeed = 0.0, 0.0, 0.0
    leadVehicleLat, leadVehicleLon, leadVehicleSpeed = 0.0, 0.0, 0.0
    relativeDistance, relativeSpeed, counter = 10.0, 0.0, 0.0
    leadVehicleDataReceivedTime = time.time()
    
    sendingData =  struct.pack("dddd", relativeDistance, relativeSpeed, counter, leadVehicleSpeed)


    while True:
        data, address = dynoTestDataManagerSocket.recvfrom(2048)
        # logger.consoleDisplay("Received data is following:\n" + str(data))

        dataLength = len(data)

        if dataLength == SpeedDataLength:
            decodedCounter, decodedSpeed = struct.unpack("dd", data)            
            hostVehicleLat, hostVehicleLon, hostVehicleSpeed, bsmJsonString = (bsmGenerator.getBsmJsonString(decodedSpeed))
            
            encodedBsm = v2x.MessageFrame.from_json(bsmJsonString)
            dynoTestDataManagerSocket.sendto(encodedBsm, MessageReceiverAddress)
            
            hostBsmHex = binascii.hexlify(encodedBsm)
            logger.logHostBsmHexData(hostBsmHex)
            logger.logHostVehicleData(decodedCounter, decodedSpeed)
            logger.consoleDisplay("Decoded data is: " + str(decodedSpeed) + " and counter is: " + str(decodedCounter))
            
            
            if time.time() - leadVehicleDataReceivedTime > 1.0:
                while relativeDistance > 10:
                    relativeDistance, relativeSpeed, counter, leadVehicleSpeed = getSafeDynoOperationData(counter, relativeDistance)
                    sendingData =  struct.pack("dddd", relativeDistance, relativeSpeed, counter, leadVehicleSpeed)

                    dynoTestDataManagerSocket.sendto(sendingData, vehicleControllerAddress)
                    
                    logger.consoleDisplay("Sending relative distance & speed, counter, and lead & host vehicle speed for safe operation: " +
                                          str(relativeDistance) + ", " + str(relativeSpeed) + ", " + str(counter) + ", " + str(leadVehicleSpeed) + ", " + str(hostVehicleSpeed))
                    
        else:

            hexPacket = binascii.hexlify(data)
            packetString = str(hexPacket, encoding="utf-8")
            bsmIdentifier = packetString.find("0014")

            if bsmIdentifier >= 0:
                logger.logLeadBsmHexData(hexPacket)
                leadVehicleInformationStatus, leadVehicleLat, leadVehicleLon, leadVehicleSpeed = leadVehicleDataManager.getLeadVehicleInformation(data)
                
                if leadVehicleInformationStatus == True:
                    relativeDistance = haversine.haversine((leadVehicleLat, leadVehicleLon), (hostVehicleLat, hostVehicleLon), unit=haversine.Unit.METERS)
                    
                    if relativeDistance >= 80.0:
                        relativeDistance = 10.0
                        
                    leadVehicleDataReceivedTime = time.time()
                    relativeSpeed = leadVehicleSpeed - hostVehicleSpeed
                    counter = counter + 1.0
                    
                    sendingData =  struct.pack("dddd", relativeDistance, relativeSpeed, counter, leadVehicleSpeed)
                    
                    dynoTestDataManagerSocket.sendto(sendingData, vehicleControllerAddress)
                    logger.logLeadVehicleData(counter, relativeDistance, relativeSpeed, leadVehicleSpeed, hostVehicleSpeed)
                    logger.consoleDisplay("Sending relative distance & speed, counter, and lead & host vehicle speed: " + 
                                          str(relativeDistance) + ", " + str(relativeSpeed) + ", " + str(counter) + ", " + str(leadVehicleSpeed) + ", " + str(hostVehicleSpeed))
                    
    dynoTestDataManagerSocket.close()

if __name__ == "__main__":
    main()
