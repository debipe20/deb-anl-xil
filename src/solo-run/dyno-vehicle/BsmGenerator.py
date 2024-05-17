"""
**********************************************************************************

BSMGenerator.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************
  
Description:
------------
The methods available from this class are the following:
- readPreloadedCoordinates(): Method to read all the coordinates from waypoints
- getNearestCoordinates(): Method to find vehicle's estimated GPS location based on the travel distance
- getBsmJsonString(currentSpeed):Method to generate bsm json string using objective systems
- setMsgCount(): Method to get the msgCount
- getMsOfMinute(): Method to get current time in mili second unit
***************************************************************************************
"""

import json
import pandas as pd
import haversine
import time, datetime
from Logger import Logger


MAX_MSG_COUNT = 127
MIN_MSG_COUNT = 1
ONE_BY_TEN_MICRO_DEGREE_TO_DEGREE = 10000000
DECA_CONVERSION = 10
HEADING_CONVERSION = 0.0125
SPEED_CONVERSION = 0.02
SECOND_MILISECOND_CONVERSION = 1000


class BsmGenerator:
    def __init__(self, config, logger: Logger):
        self.logger = logger
        self.config = config
        self.vehicleId = config["VehicleInformation"]["HostVehicleId"]
        self.currentLatitude = 0.0
        self.currentLongitude = 0.0
        self.currentElevation = 0.0
        self.currentSpeed = 0.0
        self.currentHeading = 0.0
        self.previousLatitude = 41.7007424
        self.previousLongitude = -87.9915918
        self.previousIndex = 0
        self.previousTime = time.time()
        self.msgCount = 0
        self.timeStep = 0.0
        self.extraDistance = 0.0
        self.step = 0
        self.previousTimeStampSetStatus = False
        self.latitudeList, self.longitudeList, self.elevationList, self.headingList = ([] for i in range(4) )

        self.wayPointsLogFile = "../" + self.config["VehicleInformation"]["HostBsmLogFileName"]
        self.readPreloadedCoordinates()

    def readPreloadedCoordinates(self):
        """
        - Method to get all the coordinates from preload waypoints/BSMs
        """

        dataFrame = pd.read_csv(self.wayPointsLogFile)
        self.latitudeList = dataFrame["latitude"].tolist()
        self.longitudeList = dataFrame["longitude"].tolist()
        self.elevationList = dataFrame["elevation"].tolist()
        self.headingList = dataFrame["heading"].tolist()

        self.currentLatitude = self.latitudeList[0]
        self.currentLongitude = self.longitudeList[0]
        self.currentElevation = self.elevationList[0]
        self.currentHeading = self.headingList[0]
        self.previousLatitude = self.latitudeList[0]
        self.previousLongitude = self.longitudeList[0]

    def getNearestCoordinates(self):
        """
        - Method to find the estimated location based on the travel time
            - Haversine distance is calculated
        - Distance between two waypoints may greater than the actual distance travel by the vehicle
            - extraDistance variable stores the difference between waypoints distance and vehicle travel distance
            - if extraDistance is greater than vehicle's travel distance, no neeed to iterate
            - if extraDistance is greater than vehicle's travel distance, deduct extraDistance from vehicle's travel distance
        - Iterate until haversine distance for current coordinate is close to the estimated distance compare to next coordinate
        """
        currentTime = time.time()

        if self.previousTimeStampSetStatus == False:
            self.previousTime = currentTime - 0.1
            self.previousTimeStampSetStatus = True

        self.timeStep = currentTime - self.previousTime
        travelDistance = self.currentSpeed * self.timeStep
        
        if self.extraDistance >= travelDistance:
            self.previousTime = time.time()
            self.extraDistance = self.extraDistance - travelDistance

        else:
            travelDistance = travelDistance - self.extraDistance

            for index in range(self.previousIndex + 1, len(self.latitudeList) - 2):
                calculatedDistance = haversine.haversine(
                    (self.previousLatitude, self.previousLongitude),
                    (self.latitudeList[index], self.longitudeList[index]),
                    unit=haversine.Unit.METERS)

                calculatedDistanceNext = haversine.haversine(
                    (self.previousLatitude, self.previousLongitude),
                    (self.latitudeList[index + 1], self.longitudeList[index + 1]),
                    unit=haversine.Unit.METERS)

                if (calculatedDistance <= travelDistance) and (calculatedDistanceNext <= travelDistance):
                    continue

                elif (calculatedDistance >= travelDistance) and (calculatedDistanceNext > travelDistance):
                    self.previousLatitude = self.latitudeList[index]
                    self.previousLongitude = self.longitudeList[index]
                    self.previousTime = time.time()
                    self.previousIndex = index
                    self.currentLatitude = self.latitudeList[index]
                    self.currentLongitude = self.longitudeList[index]
                    self.currentElevation = self.elevationList[index]
                    self.currentHeading = self.headingList[index]
                    self.step = index
                    self.extraDistance = calculatedDistance - travelDistance
                    break

                elif (calculatedDistance < travelDistance) and (calculatedDistanceNext >= travelDistance):
                    self.previousLatitude = self.latitudeList[index + 1]
                    self.previousLongitude = self.longitudeList[index + 1]
                    self.previousIndex = index + 1
                    self.previousTime = time.time()
                    self.currentLatitude = self.latitudeList[index + 1]
                    self.currentLongitude = self.longitudeList[index + 1]
                    self.currentElevation = self.elevationList[index + 1]
                    self.currentHeading = self.headingList[index + 1]
                    self.step = index + 1
                    self.extraDistance = calculatedDistanceNext - travelDistance
                    break

    def getBsmJsonString(self, currentSpeed):
        """ 
        - Method to generate bsm json string using objective systems
        """
        self.currentSpeed = currentSpeed

        if self.currentSpeed > 0:
            self.getNearestCoordinates()
            
        else: self.previousTime = time.time()

        self.setMsgCount()
        self.currentHeading = round(self.currentHeading, 2)        
        
        try:
            bsmDictionary = {
                "messageId": 20,
                "value": {
                    "coreData": {
                        "msgCnt": self.msgCount,
                        "id": self.vehicleId,
                        "secMark": int(self.getMsOfMinute()),
                        "lat": int(self.currentLatitude * ONE_BY_TEN_MICRO_DEGREE_TO_DEGREE ),
                        "long": int(self.currentLongitude * ONE_BY_TEN_MICRO_DEGREE_TO_DEGREE ),
                        "elev": int(self.currentElevation * DECA_CONVERSION),
                        "accuracy": {
                            "semiMajor": 255,
                            "semiMinor": 255,
                            "orientation": 65535,
                        },
                        "transmission": "forwardGears",
                        "speed": int(self.currentSpeed / SPEED_CONVERSION),
                        "heading": int(self.currentHeading / HEADING_CONVERSION),
                        "angle": -1,
                        "accelSet": {"long": 0, "lat": 0, "vert": 0, "yaw": 0},
                        "brakes": {
                            "wheelBrakes": "00",
                            "traction": "unavailable",
                            "abs": "unavailable",
                            "scs": "unavailable",
                            "brakeBoost": "unavailable",
                            "auxBrakes": "unavailable",
                        },
                        "size": {"width": 230, "length": 600},
                    },
                    "partII": [
                        {
                            "partII-Id": 0,
                            "partII-Value": {"events": {"value": "c000", "length": 13}},
                        }
                    ],
                },
            }

            bsmJsonString = json.dumps(bsmDictionary, sort_keys=True, indent=4)
            
        except Exception as e:
            self.logger.consoleDisplay("Following error occurred:\n", str(e))

        self.logger.logHostVehicleBsmData(self.timeStep, self.msgCount, self.currentLatitude, self.currentLongitude, self.currentElevation, self.currentSpeed, self.currentHeading)

        return (
            self.currentLatitude,
            self.currentLongitude,
            self.currentSpeed,
            bsmJsonString,
        )

    def setMsgCount(self):
        """
        Method to get the msgCount
        """
        if self.msgCount < MAX_MSG_COUNT:
            self.msgCount += 1

        else:
            self.msgCount = MIN_MSG_COUNT 

    def getMsOfMinute(self):
        """
        Method to get current time in mili second unit
        """
        
        timeNow = datetime.datetime.now()
        msOfMinute = timeNow.second * SECOND_MILISECOND_CONVERSION

        return msOfMinute
        
    def __del__(self):
        self.logger.consoleDisplay("Closing BSM Generator Application")

