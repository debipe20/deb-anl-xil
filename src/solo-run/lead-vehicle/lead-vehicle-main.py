"""
**********************************************************************************

vehicle-data-manager.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************
  
Description:
------------
  1. This script contains API of LeadVehicleDataManager class to generate lead vehicle's speed profile.
"""

import socket
import json
import time
import struct
import atexit
from LeadVehicleDataManager import LeadVehicleDataManager
from Logger import Logger

def destruct_logger(logger:Logger):
    logger.consoleDisplay("Shutting down now!")
    del logger

def main():
    configFile = open("../../../config/anl-master-config.json", "r")
    config = json.load(configFile)
    configFile.close()

    hostIp = config["IPAddress"]["HostIp"]
    port = config["PortNumber"]["LeadVehicleDataManager"]
    leadVehicleDataManagerAddress = (hostIp, port)
    
    hostVehicleDataManagerPort = config["PortNumber"]["HostVehicleDataManager"]
    hostVehicleDataManagerAddress = (hostIp, hostVehicleDataManagerPort)

    leadVehicleDataManagerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    leadVehicleDataManagerSocket.bind(leadVehicleDataManagerAddress)
    leadVehicleDataManagerSocket.settimeout(0)
    
    # Get logging and console output variables
    consoleStatus = config["GeneralInformation"]["ConsoleOutput"]
    loggingStatus = config["GeneralInformation"]["Logging"]
    debugStatus =  config["GeneralInformation"]["Debug"]
    
    logger = Logger(consoleStatus, loggingStatus, debugStatus)
    atexit.register(lambda: destruct_logger(logger))
    leadVehicleDataManager = LeadVehicleDataManager(config, logger)
    
    timeGap = 0.1
    dataSentTime = time.time()

    while True:
        try:
            data, address = leadVehicleDataManagerSocket.recvfrom(1024)
            decodedTrafficSignalState = struct.unpack("i", data)[0]
            logger.consoleDisplay("Received traffic signal state is :" + str(decodedTrafficSignalState))
            leadVehicleDataManager.setTrafficSignalState(decodedTrafficSignalState)
            
        except:
            timeGap = time.time() - dataSentTime
            if timeGap >= 0.1:
                leadVehicleLat, leadVehicleLon, leadVehicleSpeed = leadVehicleDataManager.getLeadVehicleInformation()
                sendingData = struct.pack("ddd", leadVehicleLat, leadVehicleLon, leadVehicleSpeed)
                dataSentTime = time.time()
                
                leadVehicleDataManagerSocket.sendto(sendingData, hostVehicleDataManagerAddress)
                time.sleep(0.0998)
                
    leadVehicleDataManagerSocket.close()

if __name__ == "__main__":
    main()