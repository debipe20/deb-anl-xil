"""
**********************************************************************************

Logger.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************
  
Description:
------------
The methods available from this class are the following:
- createLogFile(): Method to create all the required log files
- logEgoVehicleBsmData(timeStep, msgCount, currentLatitude, currentLongitude, currentElevation, currentSpeed, currentHeading): Method to log ego vehicle's GPS data and speed.
- logLeadVehicleData(counter, relativeDistance, relativeSpeed, leadVehicleSpeed, egoVehicleSpeed): Method to log lead and ego vehicle's speed data, relative distance and relative speed
- logEgoVehicleData(counter, decodedSpeed): Method to log ego vehicle's speed
- logEgoBsmHexData(bsmHex): Method to log ego vehicle's encoded BSM
- logSpatHexData(spatHex): Method to log encoded SPaT messages
- logErrorData(errorMsg, payload): Method to log payload that Objective Systems can not decode
- consoleDisplay(consoleString:str): Method to display information
***************************************************************************************
"""

import time, datetime
import os

class Logger:
    def __init__(self, consoleStatus:bool, loggingStatus:bool, debugStatus:bool):
        self.consoleStatus = consoleStatus
        self.loggingStatus = loggingStatus
        self.debugStatus = debugStatus
        
        if (self.loggingStatus == True):
            self.createLogFile()     
        
    def createLogFile(self):
        if (self.debugStatus == True):
            logfileDirectory = "../../../log/debug/"
        
        else: logfileDirectory = "../../../log/solo-run/"
        
        if not os.path.exists(logfileDirectory):
                os.makedirs(logfileDirectory)
        
        initializationTimestamp = ('{:%m%d%Y_%H%M%S}'.format(datetime.datetime.now()))
        
        self.egoVehicleBsmLogFile = open(logfileDirectory + "ego_vehicle_bsm_log_" + initializationTimestamp + ".csv", "w")        
        self.egoVehicleLogFile = open(logfileDirectory + "ego_vehicle_log_" + initializationTimestamp + ".csv", "w")
        self.leadVehicleLogFile = open(logfileDirectory + "lead_vehicle_log_" + initializationTimestamp + ".csv", "w")
        self.egoBsmHexLogFile = open(logfileDirectory + "ego_bsm_hex_log_" + initializationTimestamp + ".log","w")
        self.spatHexLogFile = open(logfileDirectory + "lead_bsm_hex_log_" + initializationTimestamp + ".log","w")
        self.errorLogFile = open(logfileDirectory + "error_log_" + initializationTimestamp + ".log", "w")

        bsmHeader = ("timestamp_verbose,timeStep,msgCount,temporaryId,secMark,latitude,longitude,elevation,speed,heading\n")
        egoHeader = ("TimeStamp, Counter, EgoVehicleSpeed\n")
        leadHeader = ("TimeStamp, Counter, RelativeDistance, RelativeSpeed, LeadVehicleSpeed, EgoVehicleSpeed\n")

        self.egoVehicleBsmLogFile.write(bsmHeader)
        self.egoVehicleLogFile.write(egoHeader)
        self.leadVehicleLogFile.write(leadHeader) 
            
    def logEgoVehicleBsmData(self, timeStep, msgCount, vehcileID, currentLatitude, currentLongitude, currentElevation, currentSpeed, currentHeading):
        if (self.loggingStatus == True):
            timestamp_verbose = str(time.time())
            timeStep = str(timeStep)
            msgCount = str(msgCount)
            temporaryId = vehcileID
            secMark = str(100)
            latitude = str(currentLatitude)
            longitude = str(currentLongitude)
            elevation = str(currentElevation)
            speed = str(round(currentSpeed, 2))
            heading = str(round(currentHeading,2))

            csvRow = (timestamp_verbose + ","
                + timeStep + ","
                + msgCount + ","
                + temporaryId + ","
                + secMark + ","
                + latitude + ","
                + longitude + ","
                + elevation + ","
                + speed + ","
                + heading + "\n"
            )

            self.egoVehicleBsmLogFile.write(csvRow)
        
    def logLeadVehicleData(self, counter, relativeDistance, relativeSpeed, leadVehicleSpeed, egoVehicleSpeed):
        if (self.loggingStatus == True):
            csvrow = (
                    str(round(time.time(), 4)) + ","
                    + str(round(counter, 0))  + ","
                    + str(round(relativeDistance, 3)) + ","
                    + str(round(relativeSpeed, 2)) + ","
                    + str(round(leadVehicleSpeed, 2)) + ","
                    + str(round(egoVehicleSpeed, 2)) + "\n")
            
            self.leadVehicleLogFile.write(csvrow)
    
    def logEgoVehicleData(self, counter, decodedSpeed):
        if (self.loggingStatus == True):
            csvrow = (str(round(time.time(), 4)) + "," 
                    + str(round(counter, 0)) + "," 
                    + str(round(decodedSpeed, 2)) + "\n")
            
            self.egoVehicleLogFile.write(csvrow)
        
    def logEgoBsmHexData(self, bsmHex):
        if (self.loggingStatus == True):
            self.egoBsmHexLogFile.write(str(bsmHex) + "\n")
            
    def logSpatHexData(self, spatHex):
        if (self.loggingStatus == True):
            self.spatHexLogFile.write(str(spatHex) + "\n")
        
    def logErrorData(self, errorMsg, payload):
        if (self.loggingStatus == True):
            self.errorLogFile.write("Following error occurred:\n" + str(errorMsg) + "\n")
            self.errorLogFile.write("Hexed Data in Spat Manager class is:\n" + str(payload) + "\n")
        
    def consoleDisplay(self, consoleString:str):
        
        timestamp = str(round(time.time(),4))
        if (self.consoleStatus == True):
            print(("\n[{}]".format(timestamp) + " " + consoleString))
            
    def __del__(self):
        if (self.loggingStatus == True):
            self.consoleDisplay("Closing log files!")
            self.egoVehicleBsmLogFile.close()
            self.egoVehicleLogFile.close()
            self.leadVehicleLogFile.close()
            self.egoBsmHexLogFile.close()
            self.spatHexLogFile.close()
            self.errorLogFile.close()
        
        
        


