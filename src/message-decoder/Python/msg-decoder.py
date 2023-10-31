"""
**********************************************************************************

**********************************************************************************
  msg-decoder.py
  Created by: Debashis Das
  Argonne National Laboratory
  Transportation and Power Systems Division

  Revision History:
  1. This script is contains complete script for MAP, SPaT, and BSM decoder
"""

import socket
import json
import binascii
import atexit
from osys import v2x
from Logger import Logger

OneByTenMicroDegree_To_Degree = 10000000
Deca_Conversion = 10

def destruct_logger(logger:Logger):
    logger.loggingAndConsoleDisplayString("Message Decoder is shutting down now!")
    del logger

def getMessageType(jsonString):
    messageType = ""

    if (jsonString["messageId"]) == 18:
        messageType = "MAP"

    elif (jsonString["messageId"]) == 19:
        messageType = "SPaT"

    elif (jsonString["messageId"]) == 20:
        messageType = "BSM"

    return messageType


def getMapJsonString(jsonString, mapPayload):
    """
    Method to create MAP json string based on decoded MAP
    """
    mapJsonString = json.dumps({
        "MsgType": "MAP",
        "MapPayload": mapPayload,
        "IntersectionID": jsonString["value"]["intersections"][0]["id"]["id"]
    })

    return mapJsonString


def getSpatJsonString(jsonString, spatPayload):
    """
    Method to create SPaT json string based on decoded SPaT
    """
    spatJsonString = json.dumps({
        "MsgType": "SPaT",
        "SpatPayload":spatPayload,
        "IntersectionID": jsonString["value"]["intersections"][0]["id"]["id"]
    })

    return spatJsonString


def getBsmJsonString(jsonString):
    """
    Method to create BSM json string based on decoded BSM
    """

    bsmJsonString = json.dumps({
        "MsgType": "BSM",
        "BasicVehicle": {
            "temporaryID": str(jsonString["value"]["coreData"]["id"]),
            "secMark_Second": str(jsonString["value"]["coreData"]["secMark"]),
            "position": {
                "latitude_DecimalDegree":  str(jsonString["value"]["coreData"]["lat"] / OneByTenMicroDegree_To_Degree),
                "longitude_DecimalDegree": str(jsonString["value"]["coreData"]["long"] / OneByTenMicroDegree_To_Degree),
                "elevation_Meter": str(jsonString["value"]["coreData"]["elev"] / Deca_Conversion)
            },
            "speed_MeterPerSecond": str(jsonString["value"]["coreData"]["speed"] * 0.2),
            "heading_Degree": str(jsonString["value"]["coreData"]["heading"] * 0.0125),
            "size": {
                "length_cm": str(jsonString["value"]["coreData"]["size"]["length"]),
                "width_cm": str(jsonString["value"]["coreData"]["size"]["length"])
            }
        }
    })

    return bsmJsonString


def main():
    # Read the config file into a json object
    configFile = open("/nojournal/bin/anl-master-config.json", 'r')
    config = (json.load(configFile))
    configFile.close()

    # Open a socket and bind it to the IP and port dedicated for this application
    hostIp = config["HostIp"]
    port = config["PortNumber"]["MessageDecoder"]
    com_info = (hostIp, port)
    msgDecoderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msgDecoderSocket.bind(com_info)

    # Get the vehicle-status-manager and spat-manager communication address
    vehicleStatusManagerAddress = (hostIp, config["PortNumber"]["VehicleStatusManager"])
    spatManagerAddress = (hostIp, config["PortNumber"]["SpatManager"])

    # Get logging and console output variables
    consoleStatus = config["ConsoleOutput"]
    loggingStatus = config["Logging"]

    logger = Logger(consoleStatus, loggingStatus)
    atexit.register(lambda: destruct_logger(logger))

    while True:
        data, address = msgDecoderSocket.recvfrom(4096)
        print(data)
        payload = data.decode()
        '''If received from V2X-Hub'''
        spatIdentifier = payload.find('0013')
        payload = payload[spatIdentifier:].strip()
        print("Decoded payload is:\n",payload)
        '''***End of Block***'''
        print(type(payload))
        unhexedPayload = binascii.unhexlify(payload)
        decodedJsonString = v2x.MessageFrame.to_json(unhexedPayload, len(unhexedPayload))
        receivedJsonString = json.loads(decodedJsonString)
        print(receivedJsonString)
        logger.loggingAndConsoleDisplayDictionary(receivedJsonString)

        if getMessageType(receivedJsonString) == "MAP":
            logger.consoleDisplayString("Received MAP")
            mapJsonString = getMapJsonString(receivedJsonString, payload)
            msgDecoderSocket.sendto(mapJsonString.encode(), vehicleStatusManagerAddress)
            logger.loggingAndConsoleDisplayDictionary(mapJsonString)

        elif getMessageType(receivedJsonString) == "SPaT":
            logger.consoleDisplayString("Received SPaT")
            spatJsonString = getSpatJsonString(receivedJsonString, payload)
            msgDecoderSocket.sendto(spatJsonString.encode(), spatManagerAddress)
            logger.loggingAndConsoleDisplayDictionary(spatJsonString)

        elif getMessageType(receivedJsonString) == "BSM":
            logger.consoleDisplayString("Received BSM")
            bsmJsonString = getBsmJsonString(receivedJsonString)
            msgDecoderSocket.sendto(bsmJsonString.encode(), vehicleStatusManagerAddress)
            logger.loggingAndConsoleDisplayDictionary(bsmJsonString)

    msgDecoderSocket.close()


if __name__ == '__main__':
    main()
