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
- logLeadVehicleBsmData(timeStep, currentLatitude, currentLongitude, currentElevation, currentSpeed, currentHeading, distanceToFinalWayPoints, distanceToIntersection): Method to log lead vehicle's GPS data, speed, etc.
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
        
        self.leadVehicleBsmLogFile = open(logfileDirectory + "lead_vehicle_bsm_log_" + initializationTimestamp + ".csv", "w")        
        leadHeader = ("timestamp_verbose,timeStep,latitude,longitude,elevation,speed,heading,distanceToFinalWaypoints,distanceToIntersection\n")
        self.leadVehicleBsmLogFile.write(leadHeader) 
            
    def logLeadVehicleBsmData(self, timeStep, currentLatitude, currentLongitude, currentElevation, currentSpeed, currentHeading, distanceToFinalWayPoints, distanceToIntersection):
        if (self.loggingStatus == True):
            timestamp_verbose = str(time.time())
            timeStep = str(timeStep)
            latitude = str(currentLatitude)
            longitude = str(currentLongitude)
            elevation = str(currentElevation)
            speed = str(round(currentSpeed, 2))
            heading = str(round(currentHeading, 2))
            wayPointsDistance = str(round(distanceToFinalWayPoints, 2))
            intersectionDistance = str(round(distanceToIntersection, 2))

            csvRow = (timestamp_verbose + ","
                + timeStep + ","
                + latitude + ","
                + longitude + ","
                + elevation + ","
                + speed + ","
                + heading + ","
                + wayPointsDistance + ","
                + intersectionDistance + "\n"
            )

            self.leadVehicleBsmLogFile.write(csvRow)
        
    def consoleDisplay(self, consoleString:str):
        
        timestamp = str(round(time.time(),4))
        if (self.consoleStatus == True):
            print(("\n[{}]".format(timestamp) + " " + consoleString))
            
    def __del__(self):
        if (self.loggingStatus == True):
            self.consoleDisplay("Closing log file!")
            self.leadVehicleBsmLogFile.close()