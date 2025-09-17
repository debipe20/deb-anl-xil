"""
**********************************************************************************

dyno-vehicle-data-manager.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************
  
Description:
------------
  1. This script contains API of BSMGenerator and SpatManager class to generate ego vehicle's BSM and feed required information to vehicle controller.
"""

import socket
import json
import binascii
import struct
import haversine
import time
import atexit
from osys import v2x
from BsmGenerator import BsmGenerator
from SpatManager import SpatManager
from Logger import Logger

SpeedDataLength = 16
LEAD_VEHICLE_DATA_LENGTH = 24

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
        
    else: messageType = "Unknown"

    return messageType

def destruct_logger(logger:Logger):
    logger.consoleDisplay("Shutting down now!")
    del logger

def main():
    configFile = open("../../../config/anl-master-config.json", "r")
    config = json.load(configFile)
    configFile.close()

    hostIp = config["IPAddress"]["HostIp"]
    port = config["PortNumber"]["EgoVehicleDataManager"]
    hostAddress = (hostIp, port)

    messageReceiverIp = config["IPAddress"]["V2XHubIp"]
    messageReceiverPort = config["PortNumber"]["MessageReceiver"]
    messageReceiverAddress = (messageReceiverIp, messageReceiverPort)

    # vehicleControllerIp = config["IPAddress"]["VehicleControllerIp"]
    vehicleControllerIp = config["IPAddress"]["HostIp"]
    vehicleControllerPort = config["PortNumber"]["VehicleController"]
    vehicleControllerAddress = (vehicleControllerIp, vehicleControllerPort)
    
    leadVehicleDataManagerPort = config["PortNumber"]["LeadVehicleDataManager"]
    leadVehicleDataManagerAddress = (hostIp, leadVehicleDataManagerPort)

    egoVehicleDataManagerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    egoVehicleDataManagerSocket.bind(hostAddress)
    
    # Get logging and console output variables
    consoleStatus = config["GeneralInformation"]["ConsoleOutput"]
    loggingStatus = config["GeneralInformation"]["Logging"]
    debugStatus =  config["GeneralInformation"]["Debug"]
    
    logger = Logger(consoleStatus, loggingStatus, debugStatus)
    atexit.register(lambda: destruct_logger(logger))
    bsmGenerator = BsmGenerator(config, logger)
    spatManager = SpatManager(config, logger)

    egoVehicleLat, egoVehicleLon, egoVehicleSpeed = 42.3025391192385, -83.69779345760013, 0.0
    leadVehicleLat, leadVehicleLon, leadVehicleSpeed = 42.30245402283134, -83.69784540965374, 0.0
    relativeDistance, relativeSpeed, counter = 10.0, 0.0, 0.0
    leadVehicleDataReceivedTime = time.time()

    while True:
        data, address = egoVehicleDataManagerSocket.recvfrom(2048)
        # logger.consoleDisplay("Received data is following:\n" + str(data))

        dataLength = len(data)

        if dataLength == SpeedDataLength:
            decodedCounter, decodedSpeed = struct.unpack("dd", data)            
            egoVehicleLat, egoVehicleLon, egoVehicleSpeed, bsmJsonString = (bsmGenerator.getBsmJsonString(decodedSpeed))
            
            encodedBsm = v2x.MessageFrame.from_json(bsmJsonString)

            # egoVehicleDataManagerSocket.sendto(encodedBsm, messageReceiverAddress)
            
            # egoBsmHex = binascii.hexlify(encodedBsm)
            egoBsmHex = encodedBsm.hex()            
            logger.logEgoBsmHexData(egoBsmHex)
            logger.consoleDisplay("Encoded Hexlify BSM is: \n" + str(egoBsmHex))

            logger.logEgoVehicleData(decodedCounter, decodedSpeed)
            logger.consoleDisplay("Decoded data is: " + str(decodedSpeed) + " and counter is: " + str(decodedCounter))
            
            if time.time() - leadVehicleDataReceivedTime > 1.0:
                while relativeDistance > 10:
                    relativeDistance, relativeSpeed, counter, leadVehicleSpeed = getSafeDynoOperationData(counter, relativeDistance)
                    sendingData =  struct.pack("dddd", relativeDistance, relativeSpeed, counter, leadVehicleSpeed)

                    egoVehicleDataManagerSocket.sendto(sendingData, vehicleControllerAddress)
                    
                    logger.consoleDisplay("Sending relative distance & speed, counter, and lead & ego vehicle speed for safe operation: " +
                                          + str(relativeDistance) + ", " + str(relativeSpeed) + ", " + str(counter) + ", " + str(leadVehicleSpeed) + ", " + str(egoVehicleSpeed))
                    
        elif dataLength == LEAD_VEHICLE_DATA_LENGTH:
            leadVehicleLat, leadVehicleLon, leadVehicleSpeed = struct.unpack("ddd", data)

            logger.consoleDisplay("Received lead vehicle data is following: \n" + str(leadVehicleLat) + ", " + str(leadVehicleLon) + ", " + str(leadVehicleSpeed))
            relativeDistance = haversine.haversine((leadVehicleLat, leadVehicleLon), (egoVehicleLat, egoVehicleLon), unit=haversine.Unit.METERS)
 
            leadVehicleDataReceivedTime = time.time()
            relativeSpeed = leadVehicleSpeed - egoVehicleSpeed
            counter = counter + 1.0
            sendingData =  struct.pack("dddd", relativeDistance, relativeSpeed, counter, leadVehicleSpeed)
            
            egoVehicleDataManagerSocket.sendto(sendingData, vehicleControllerAddress)
            
            logger.logLeadVehicleData(counter, relativeDistance, relativeSpeed, leadVehicleSpeed, egoVehicleSpeed)            
            logger.consoleDisplay("Sending relative distance & speed, counter, and lead & ego vehicle speed: " + 
                                          str(relativeDistance) + ", " + str(relativeSpeed) + ", " + str(counter) + ", " + str(leadVehicleSpeed) + ", " + str(egoVehicleSpeed))

        else:

            hexPacket = binascii.hexlify(data)
            packetString = str(hexPacket, encoding="utf-8")
            msgIdentifier = packetString.find('001')
            payload = packetString[msgIdentifier:].strip()
            msgType = getMessageType(payload)

            if msgType == "SPaT":
                trafficSignalState = spatManager.getDesiredSignalGroupState(payload)
                sendingData =  struct.pack("i", trafficSignalState)
                egoVehicleDataManagerSocket.sendto(sendingData, leadVehicleDataManagerAddress)

                logger.consoleDisplay("Sent traffic signal state " + str(trafficSignalState))
                
                
    egoVehicleDataManagerSocket.close()

if __name__ == "__main__":
    main()
