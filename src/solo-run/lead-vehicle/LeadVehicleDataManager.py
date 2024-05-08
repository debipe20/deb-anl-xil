import time, datetime
import haversine
import pandas as pd
from Logger import Logger

GREEN = 1
YELLOW = 2
RED = 3
STEADY_STATE_SPEED = 4.5
DISTANCE_GAP = 10
MIN_GAP_TO_INTERSECTION = 5
TIME_STEP = 0.1
ACCELERATION = 1.0
DECELERATION = -2.0
INTERSECTION_INDEX = 130


class LeadVehicleDataManager:
    def __init__(self, config, logger: Logger) -> None:
        self.logger = logger
        self.config = config
        self.leadVehicleId = config["VehicleInformation"]["LeadVehicleId"]
        self.trafficSignalState = GREEN
        self.stoppedAtIntersection = False
        self.currentSpeed = 0.0
        self.distanceToFinalWayPoints = 50.0
        self.previousIndex = 10        
        self.previousTime = time.time()
        self.timeStep = 0.0
        self.extraDistance = 0.0
        self.step = 0
        self.previousTimeStampSetStatus = False
        self.latitudeList, self.longitudeList, self.elevationList, self.headingList = ([] for i in range(4))
        self.intersectionLattitude = self.config["IntersectionInformation"]["IntersectionReferencePoint"]["Latitude_DecimalDegree"]
        self.intersectionLongitude = self.config["IntersectionInformation"]["IntersectionReferencePoint"]["Longitude_DecimalDegree"]
        
        self.wayPointsLogFile = config["VehicleInformation"]["LeadBsmLogFileName"] 
        self.readWayPoints()

    def readWayPoints(self):
        """
        - Method to get all the coordinates from preload waypoints/BSMs
        """

        dataFrame = pd.read_csv(self.wayPointsLogFile)
        self.latitudeList = dataFrame["latitude"].tolist()
        self.longitudeList = dataFrame["longitude"].tolist()
        self.elevationList = dataFrame["elevation"].tolist()
        self.headingList = dataFrame["heading"].tolist()

        self.currentLatitude = self.latitudeList[self.previousIndex]
        self.currentLongitude = self.longitudeList[self.previousIndex]
        self.currentElevation = self.elevationList[self.previousIndex]
        self.currentHeading = self.headingList[self.previousIndex]
        self.previousLatitude = self.latitudeList[self.previousIndex]
        self.previousLongitude = self.longitudeList[self.previousIndex]
        self.finalLatitude = self.latitudeList[-1]
        self.finalLongitude = self.longitudeList[-1]
        
        self.distanceToIntersection = haversine.haversine(
            (self.currentLatitude, self.currentLongitude),
            (self.intersectionLattitude, self.intersectionLongitude),
            unit=haversine.Unit.METERS)
        
        self.distanceToFinalWayPoints = haversine.haversine(
            (self.currentLatitude, self.currentLongitude),
            (self.finalLatitude, self.finalLongitude),
            unit=haversine.Unit.METERS)

    def setTrafficSignalState(self, evenState):

        self.trafficSignalState = evenState
        
        if self.previousIndex > INTERSECTION_INDEX:
            self.trafficSignalState = GREEN

    def getLeadVehicleSpeed(self):
                
        if self.previousIndex < INTERSECTION_INDEX and self.stoppedAtIntersection == False:
            distance = self.distanceToIntersection
            
        else:
            distance = self.distanceToFinalWayPoints
            
        # if (self.trafficSignalState == GREEN and distance <= self.distanceToFinalWayPoints):
        if (self.trafficSignalState == GREEN and distance <= DISTANCE_GAP and self.stoppedAtIntersection == True):
            self.currentSpeed = self.currentSpeed + (DECELERATION * TIME_STEP)
            self.logger.consoleDisplay("Slowing down since signal is green and distance is less than " + str(self.distanceToFinalWayPoints) + " m") 
        
        elif self.trafficSignalState == GREEN and self.currentSpeed < STEADY_STATE_SPEED:
            self.currentSpeed = self.currentSpeed + (ACCELERATION * TIME_STEP)

        elif (self.trafficSignalState == GREEN and self.currentSpeed >= STEADY_STATE_SPEED):
            self.currentSpeed = STEADY_STATE_SPEED

        elif (self.trafficSignalState == GREEN and self.currentSpeed > STEADY_STATE_SPEED):
            self.currentSpeed = self.currentSpeed + (DECELERATION * TIME_STEP)
            self.logger.consoleDisplay("Slowing down since signal is green and speed is greater than steady state speed")   
            
        elif ((self.trafficSignalState == RED or self.trafficSignalState == YELLOW) and distance <= DISTANCE_GAP and self.currentSpeed >= 0):
            self.currentSpeed = self.currentSpeed + (DECELERATION * TIME_STEP)
            self.logger.consoleDisplay("Slowing down since signal is red or yellow and speed is greater than zero") 
            
        elif ((self.trafficSignalState == RED or self.trafficSignalState == YELLOW) and distance > DISTANCE_GAP and self.currentSpeed < STEADY_STATE_SPEED):
            self.currentSpeed = self.currentSpeed + (ACCELERATION * TIME_STEP)
        
        if self.currentSpeed < 0.0:
            self.currentSpeed = 0.0
        
        if self.distanceToIntersection < MIN_GAP_TO_INTERSECTION and self.trafficSignalState == GREEN and self.currentSpeed == 0:
            self.stoppedAtIntersection = True
            self.logger.consoleDisplay("Setting stopped at intersection flag true as distance to intersection is " + (self.distanceToIntersection))

    def getLeadVehicleInformation(self):
        """
        - Method to find the estimated location based on the travel time
            - Haversine distance is calculated
        - Distance between two waypoints may greater than the actual distance travel by the vehicle
            - extraDistance variable stores the difference between waypoints distance and vehicle travel distance
            - if extraDistance is greater than vehicle's travel distance, no neeed to iterate
            - if extraDistance is greater than vehicle's travel distance, deduct extraDistance from vehicle's travel distance
        - Iterate until haversine distance for current coordinate is close to the estimated distance compare to next coordinate
        """
        
        self.getLeadVehicleSpeed()
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

        self.distanceToIntersection = haversine.haversine(
            (self.currentLatitude, self.currentLongitude),
            (self.intersectionLattitude, self.intersectionLongitude),
            unit=haversine.Unit.METERS)
        
        self.distanceToFinalWayPoints = haversine.haversine(
            (self.currentLatitude, self.currentLongitude),
            (self.finalLatitude, self.finalLongitude),
            unit=haversine.Unit.METERS)
        
        if self.previousIndex < INTERSECTION_INDEX and self.trafficSignalState == GREEN:
            self.distanceToFinalWayPoints = 50
        
        self.logger.consoleDisplay("Previous Index, Current speed, Distance to intersection, & Distance to final waypoints: \n" + str(self.previousIndex) + ", " + str(self. currentSpeed) + ", " + str(self.distanceToIntersection) + ", " + str(self.distanceToFinalWayPoints))
        self.logger.logLeadVehicleBsmData(self.timeStep, self.currentLatitude, self.currentLongitude, self.currentElevation, self.currentSpeed, self.currentHeading, self.distanceToFinalWayPoints, self.distanceToIntersection)
        
        return round(self.currentLatitude,10), round(self.currentLongitude,10), round(self.currentSpeed,2)
       
        

        
    def __del__(self):
        self.logger.consoleDisplay("Closing Lead Vehicle Manager Application")
