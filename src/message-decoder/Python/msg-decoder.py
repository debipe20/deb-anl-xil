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
import atexit

from MsgDecoder import MsgDecoder
from Logger import Logger

OneByTenMicroDegree_To_Degree = 10000000
Deca_Conversion = 10

def destruct_logger(logger:Logger):
    logger.loggingAndConsoleDisplayString("Message Decoder is shutting down now!")
    del logger



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
    msgDecoder = MsgDecoder()

    while True:
        data, address = msgDecoderSocket.recvfrom(4096)
        payload = data.decode()

        msgIdentifier = payload.find('001')
        payload = payload[msgIdentifier:].strip()
        msgType = msgDecoder.getMessageType(payload)
        
        if msgType == "MAP":
            logger.consoleDisplayString("Received MAP")
            mapJsonString = msgDecoder.getMapJsonString(payload)
            msgDecoderSocket.sendto(mapJsonString.encode(), vehicleStatusManagerAddress)
            logger.loggingAndConsoleDisplayDictionary(mapJsonString)

        elif msgType == "SPaT":
            logger.consoleDisplayString("Received SPaT")
            spatJsonString = msgDecoder.getSpatJsonString(payload)
            msgDecoderSocket.sendto(spatJsonString.encode(), spatManagerAddress)
            logger.loggingAndConsoleDisplayDictionary(spatJsonString)

        elif msgType == "BSM":
            logger.consoleDisplayString("Received BSM")
            bsmJsonString = msgDecoder.getBsmJsonString(payload)
            msgDecoderSocket.sendto(bsmJsonString.encode(), vehicleStatusManagerAddress)
            logger.loggingAndConsoleDisplayDictionary(bsmJsonString)

    msgDecoderSocket.close()


if __name__ == '__main__':
    main()
