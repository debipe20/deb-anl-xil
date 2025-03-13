"""
**********************************************************************************

BSMGenerator.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************
  
Description:
------------
This script implements the `BsmGenerator` class, which is responsible for:
- Reading vehicle waypoints and determining the current position based on distance traveled.
- Generating a **Basic Safety Message (BSM)** JSON structure using vehicle telemetry data.
- Managing message counts and timestamps for BSM transmission.
- Providing methods to retrieve estimated GPS coordinates using the Haversine formula.

The methods available from this class are the following:
- read_way_points(): Method to read all the coordinates from waypoints
- get_nearest_coordinates(): Method to find vehicle's estimated GPS location based on the travel distance
- get_bsm_json_string(currentSpeed):Method to generate bsm json string using objective systems
- set_msg_count(): Method to get the msgCount
- get_ms_of_minute(): Method to get current time in mili second unit
***************************************************************************************
"""

import json
import pandas as pd
import haversine
import time, datetime
import os, platform
from Logger import Logger

MAX_MSG_COUNT = 127
MIN_MSG_COUNT = 1
ONE_BY_TEN_MICRO_DEGREE_TO_DEGREE = 10000000
DECA_CONVERSION = 10
HEADING_CONVERSION = 0.0125
SPEED_CONVERSION = 0.02
SECOND_MILISECOND_CONVERSION = 1000


class BsmGenerator:
    """
    BsmGenerator class generates BSM messages using vehicle telemetry data.
    It calculates real-time location updates based on vehicle speed and distance traveled.

    Attributes:
        config (dict): Configuration settings.
        vehicleId (str): Unique identifier for the vehicle.
        currentLatitude (float): Current latitude of the vehicle.
        currentLongitude (float): Current longitude of the vehicle.
        currentElevation (float): Current elevation of the vehicle.
        currentSpeed (float): Current speed of the vehicle.
        currentHeading (float): Current heading direction.
    """
    def __init__(self, config, vehicle_id, way_points_file, logger: Logger):
        """
        Initializes the BSM Generator with vehicle parameters and waypoints.

        Args:
            config (dict): Configuration settings.
            vehicle_id (str): Unique vehicle ID.
            way_points_file (str): File containing preloaded waypoints.
            logger (Logger): Logger instance for debugging and tracking.
        """
        self.logger = logger
        self.config = config
        self.vehicleId = vehicle_id
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
        self.way_points_file = way_points_file
        self.read_way_points()

    def read_way_points(self):
        """
        - Method to get all the coordinates from preload waypoints/BSMs
        """
        current_os = platform.system()
        
        if current_os == "Linux":
            self.wayPointsLogFile = os.path.join(os.path.expanduser("~"), "Desktop", "deb-anl-xil", "data", self.way_points_file)
        
        elif current_os == "Windows":
            self.wayPointsLogFile = os.path.join("C:\\", "Users", "ddas", "deb-anl-xil", "config", self.way_points_file)
        
        else:
            raise OSError(f"Unsupported operating system: {current_os}")
        
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

    def get_nearest_coordinates(self):
        """
        - Estimates the vehicle's real-time GPS location based on travel distance.
        - Uses the Haversine formula to find the closest matching waypoint.
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

    def get_bsm_json_string(self, currentSpeed):
        """
        Generates a Basic Safety Message (BSM) JSON string using vehicle telemetry data and Objective Systems Library.

        Args:
            currentSpeed (float): Current speed of the vehicle.

        Returns:
            tuple: Contains vehicle parameters and the BSM JSON string.
        """
        self.currentSpeed = currentSpeed

        if self.currentSpeed > 0:
            self.get_nearest_coordinates()
            
        else: self.previousTime = time.time()

        self.set_msg_count()
        self.currentHeading = round(self.currentHeading, 2)

        try:
            bsmDictionary = {
                "messageId": 20,
                "value": {
                    "coreData": {
                        "msgCnt": self.msgCount,
                        "id": self.vehicleId,
                        "secMark": int(self.get_ms_of_minute()),
                        "lat": int(self.currentLatitude * ONE_BY_TEN_MICRO_DEGREE_TO_DEGREE),
                        "long": int(self.currentLongitude * ONE_BY_TEN_MICRO_DEGREE_TO_DEGREE),
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
 
        return (
            self.vehicleId,
            self.timeStep,
            self.msgCount,
            self.currentLatitude,
            self.currentLongitude,
            self.currentElevation,
            self.currentSpeed,
            self.currentHeading, 
            bsmJsonString,
        )

    def set_msg_count(self):
        """
        Increments the message count, resetting it after reaching MAX_MSG_COUNT.
        """
        if self.msgCount < MAX_MSG_COUNT:
            self.msgCount += 1

        else:
            self.msgCount = MIN_MSG_COUNT

    def get_ms_of_minute(self):
        """
        Retrieves the current time in milliseconds within a given minute.

        Returns:
            int: Millisecond count within the current minute.
        """

        timeNow = datetime.datetime.now()
        msOfMinute = timeNow.second * SECOND_MILISECOND_CONVERSION

        return msOfMinute
        
    def __del__(self):
        """
        Destructor method to close the BSM Generator instance.
        """
        self.logger.consoleDisplay("Closing BSM Generator Application")