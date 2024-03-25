import time
import haversine
import pandas as pd


GREEN = 1
YELLOW = 2
RED = 3
STEADY_STATE_SPEED = 8.0
TIME_STEP = 0.1
ACCELERATION = 1.0
DECELERATION = -2.0


class LeadVehicleDataManager:
    def __init__(self, config) -> None:
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
        self.bsmLogFile = config["VehicleInformation"]["BsmLogFileName"]
        self.logFile = open("lead-vehicle-bsm-log.csv", "w")
        self.logFile.write("timestamp_verbose,timeStep,latitude,longitude,elevation,speed,heading,distanceToFinalWaypoints,distanceToIntersection\n")
        self.readWayPoints()

    def readWayPoints(self):
        """
        - Method to get all the coordinates from preload waypoints/BSMs
        """

        dataFrame = pd.read_csv(self.bsmLogFile)
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
        
        if self.previousIndex > 130:
            self.trafficSignalState = GREEN

    def getLeadVehicleSpeed(self):
                
        if self.previousIndex < 130 and self.stoppedAtIntersection == False:
            distance = self.distanceToIntersection
            
        else:
            distance = self.distanceToFinalWayPoints
            
        if (self.trafficSignalState == GREEN and distance <= 20):
            self.currentSpeed = self.currentSpeed + (DECELERATION * TIME_STEP)
        
        elif self.trafficSignalState == GREEN and self.currentSpeed < STEADY_STATE_SPEED:
            self.currentSpeed = self.currentSpeed + (ACCELERATION * TIME_STEP)

        elif (self.trafficSignalState == GREEN and self.currentSpeed >= STEADY_STATE_SPEED):
            self.currentSpeed = STEADY_STATE_SPEED

        elif (self.trafficSignalState == GREEN and self.currentSpeed > STEADY_STATE_SPEED):
            self.currentSpeed = self.currentSpeed + (DECELERATION * TIME_STEP)   
            
        elif ((self.trafficSignalState == RED or self.trafficSignalState == YELLOW) and distance <= 20 and self.currentSpeed >= 0):
            self.currentSpeed = self.currentSpeed + (DECELERATION * TIME_STEP)
            
        elif ((self.trafficSignalState == RED or self.trafficSignalState == YELLOW) and distance > 20 and self.currentSpeed < STEADY_STATE_SPEED):
            self.currentSpeed = self.currentSpeed + (ACCELERATION * TIME_STEP)
        
        if self.currentSpeed < 0.0:
            self.currentSpeed = 0.0
        
        if self.distanceToIntersection < 10 and self.trafficSignalState == GREEN and self.currentSpeed == 0:
            self.stoppedAtIntersection = True

    def getLeadVehicleInformation(self):
        """
        - Method to find the estimated location based on the travel time
            - Haversine distance is calculated
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
        
        if self.previousIndex < 130 and self.trafficSignalState == GREEN:
            self.distanceToFinalWayPoints = 50
        
        print("Previous Index, Current speed, Distance to intersection, & Distance to final waypoints: \n", self.previousIndex, self. currentSpeed, self.distanceToIntersection, self.distanceToFinalWayPoints)
        self.logCoordinates()
        
        return round(self.currentLatitude,10), round(self.currentLongitude,10), round(self.currentSpeed,2)
       
        
    def logCoordinates(self):

        timestamp_verbose = str(time.time())
        timeStep = str(self.timeStep)
        latitude = str(self.currentLatitude)
        longitude = str(self.currentLongitude)
        elevation = str(self.currentElevation)
        speed = str(round(self.currentSpeed, 2))
        heading = str(round(self.currentHeading, 2))
        wayPointsDistance = str(round(self.distanceToFinalWayPoints, 2))
        intersectionDistance = str(round(self.distanceToIntersection, 2))

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

        self.logFile.write(csvRow)
