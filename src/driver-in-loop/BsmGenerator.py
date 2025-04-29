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
- compute_steering_input(): Method to compute the normalized steering input for CARLA in range [-1, 1]
***************************************************************************************
"""

import json
import pandas as pd
import haversine
import time, datetime
import os, platform
from Logger import Logger
import math

MAX_STEERING_ANGLE = 70  # Max vehicle steering angle in degrees
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
            self.wayPointsLogFile = os.path.join(os.path.expanduser("~"), "Desktop", "deb-anl-xil", "data", "kearney", self.way_points_file)
        
        elif current_os == "Windows":
            self.wayPointsLogFile = os.path.join("C:\\", "Users", "ddas", "deb-anl-xil", "data", "kearney", self.way_points_file)
        
        else:
            raise OSError(f"Unsupported operating system: {current_os}")
        
        dataFrame = pd.read_csv(self.wayPointsLogFile)
        self.latitudeList = dataFrame["Latitude"].tolist()
        self.longitudeList = dataFrame["Longitude"].tolist()
        self.elevationList = dataFrame["Elevation"].tolist()
        self.headingList = dataFrame["Heading"].tolist()

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
                calculatedDistance = haversine.haversine((self.previousLatitude, self.previousLongitude),
                    (self.latitudeList[index], self.longitudeList[index]),
                    unit=haversine.Unit.METERS)

                calculatedDistanceNext = haversine.haversine((self.previousLatitude, self.previousLongitude),
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
        lat1 = self.previousLatitude # need to specify before executing get_nearest_coordinates() function to store previous lat and lon
        lon1 = self.previousLongitude
        heading = self.currentHeading
        steering_input = 0.0

        if self.currentSpeed > 0:
            self.get_nearest_coordinates()
            
        else: self.previousTime = time.time()
        
        lat2 = self.currentLatitude
        lon2 = self.currentLongitude

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
            steering_input = self.compute_steering_input(lat1, lon1, lat2, lon2, heading)
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
            steering_input
        )
        
    def generate_bsm_json_string(self, lat, lon, elev, heading, speed_mps):
        
        current_time = time.time()
    
        # Calculate the current minute (seconds modulo 60)
        seconds_in_minute = int(current_time % 60)
            
        # Convert seconds to milliseconds
        dsecond_value = seconds_in_minute * 1000 + int((current_time % 1) * 1000)
        
        bsm_dictionary = {
            "MsgType": "BSM",
            "BasicVehicle": {
                "heading_Degree": heading,
                "position": {
                    "elevation_Meter": elev,
                    "latitude_DecimalDegree":  lat,
                    "longitude_DecimalDegree": lon,
                },
                "secMark_Second": dsecond_value,
                "size": {
                    "length_cm": 1239.994,
                    "width_cm": 304.013
                },
                "speed_MeterPerSecond": speed_mps,
                "temporaryID": -1898502772,
                "type": "Car"
            }            
        }

        bsm_json_string = json.dumps(bsm_dictionary, sort_keys=True, indent=4)
        
        return bsm_json_string
        
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
        
    def compute_steering_input(self, lat1, lon1, lat2, lon2, current_heading):
        """
        Computes the normalized steering input for CARLA in range [-1, 1].

        Args:
            lat1, lon1: Current GPS coordinates (degrees)
            lat2, lon2: Target GPS coordinates (degrees)
            current_heading: Current vehicle heading (degrees)

        Returns:
            Steering input in CARLA's range [-1, 1]
        """
        # Convert degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Compute bearing
        delta_lon = lon2 - lon1
        x = math.sin(delta_lon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
        bearing = math.degrees(math.atan2(x, y))  # Convert back to degrees

        # Compute steering angle difference
        steering_angle = (bearing - current_heading + 360) % 360  # Normalize to [0, 360]
        if steering_angle > 180:
            steering_angle -= 360  # Convert to [-180, 180]

        # Normalize to CARLA range [-1, 1]
        steering_input = max(-1, min(steering_angle / MAX_STEERING_ANGLE, 1))
        
        return steering_input
    
    import math

    ### Generative AI Logic
    def compute_steering_angle(self, current_location, target_location, vehicle_heading):
        """
        Computes the steering angle between two points in CARLA.

        Args:
            current_location: A tuple (x, y, z) representing the vehicle's current location.
            target_location: A tuple (x, y, z) representing the target location.
            vehicle_heading: The vehicle's current heading angle in radians.

        Returns:
            A float representing the steering angle input (-1.0 to 1.0).
        """

        # Calculate the direction vector
        direction_vector = (target_location[0] - current_location[0], target_location[1] - current_location[1])

        # Calculate the angle between the heading and direction vector
        angle = math.atan2(direction_vector[1], direction_vector[0]) - vehicle_heading

        # Normalize the angle to the range [-pi, pi]
        angle = (angle + math.pi) % (2 * math.pi) - math.pi

        # Convert the angle to steering angle input
        steering_angle = angle / math.pi

        return steering_angle


    # def compute_throttle_brake_control(self, vehicle, desired_speed, Kp_throttle=0.5, Kp_brake=1.0):
    #     """
    #     Compute throttle and brake values to follow a desired speed using a simple proportional controller.

    #     Args:
    #         vehicle (carla.Vehicle): The vehicle actor in CARLA.
    #         desired_speed (float): Target speed in meters per second (m/s).
    #         Kp_throttle (float): Proportional gain for throttle.
    #         Kp_brake (float): Proportional gain for brake.

    #     Returns:
    #         tuple: (throttle, brake), both in range [0.0, 1.0]
    #     """

    #     # Compute speed error
    #     speed_error = desired_speed - current_speed

    #     # Initialize control variables
    #     throttle = 0.0
    #     brake = 0.0

    #     # Proportional control logic
    #     if speed_error > 0.1:  # Allow small deadband
    #         throttle = min(Kp_throttle * speed_error, 1.0)
    #         brake = 0.0
    #     elif speed_error < -0.1:
    #         throttle = 0.0
    #         brake = min(Kp_brake * abs(speed_error), 1.0)
    #     else:
    #         # In deadband range: no throttle or brake
    #         throttle = 0.0
    #         brake = 0.0

    #     return throttle, brake
    
    
    # def compute_throttle_brake_control(self, vehicle, desired_speed, last_speed, dt,
    #                                max_accel=2.0, max_decel=3.0,
    #                                Kp_throttle=0.5, Kp_brake=1.0, deadband=0.1):
    #     velocity = vehicle.get_velocity()
    #     current_speed = math.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2)
    #     speed_error = desired_speed - current_speed

    #     # Limit speed change
    #     desired_delta_speed = max(-max_decel * dt, min(speed_error, max_accel * dt))
    #     smooth_target_speed = last_speed + desired_delta_speed
    #     adjusted_error = smooth_target_speed - current_speed

    #     # Control logic
    #     throttle = brake = 0.0
    #     if adjusted_error > deadband:
    #         throttle = min(Kp_throttle * adjusted_error, 1.0)
    #     elif adjusted_error < -deadband:
    #         brake = min(Kp_brake * abs(adjusted_error), 1.0)

    #     return throttle, brake, current_speed



    def __del__(self):
        """
        Destructor method to close the BSM Generator instance.
        """
        self.logger.consoleDisplay("Closing BSM Generator Application")