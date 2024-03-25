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
        self.currentSpeed = 0.0
        self.distanceToFinalWayPoints = 50.0
        self.previousIndex = 20
        self.previousTime = time.time()
        self.timeStep = 0.0
        self.extraDistance = 0.0
        self.step = 0
        self.previousTimeStampSetStatus = False
        self.latitudeList, self.longitudeList, self.elevationList, self.headingList = (
            [] for i in range(4)
        )
        self.bsmLogFile = config["VehicleInformation"]["BsmLogFileName"]
        self.logFile = open("lead-vehicle-bsm-log.csv", "w")
        self.logFile.write("timestamp_verbose,timeStep,latitude,longitude,elevation,speed,heading,distanceToFinalWaypoints\n")
        self.readPreloadedCoordinates()

    def readPreloadedCoordinates(self):
        """
        - Method to get all the coordinates from preload waypoints/BSMs
        """

        dataFrame = pd.read_csv(self.bsmLogFile)
        self.latitudeList = dataFrame["latitude"].tolist()
        self.longitudeList = dataFrame["longitude"].tolist()
        self.elevationList = dataFrame["elevation"].tolist()
        self.headingList = dataFrame["heading"].tolist()

        self.currentLatitude = self.latitudeList[20]
        self.currentLongitude = self.longitudeList[20]
        self.currentElevation = self.elevationList[20]
        self.currentHeading = self.headingList[20]
        self.previousLatitude = self.latitudeList[20]
        self.previousLongitude = self.longitudeList[20]
        self.finalLatitude = self.latitudeList[-1]
        self.finalLongitude = self.longitudeList[-1]

    def setTrafficSignalState(self, evenState):

        self.trafficSignalState = evenState
        
        if self.previousIndex > 140:
            self.trafficSignalState = GREEN

    def getLeadVehicleSpeed(self):

        if (self.trafficSignalState == GREEN and self.distanceToFinalWayPoints <= 25):
            self.currentSpeed = self.currentSpeed + (DECELERATION * TIME_STEP)
        
        elif self.trafficSignalState == GREEN and self.currentSpeed < STEADY_STATE_SPEED:
            self.currentSpeed = self.currentSpeed + (ACCELERATION * TIME_STEP)

        elif (self.trafficSignalState == GREEN and self.currentSpeed >= STEADY_STATE_SPEED):
            self.currentSpeed = STEADY_STATE_SPEED

        elif (self.trafficSignalState == GREEN and self.currentSpeed > STEADY_STATE_SPEED):
            self.currentSpeed = self.currentSpeed + (DECELERATION * TIME_STEP)   
            
        elif ((self.trafficSignalState == RED or self.trafficSignalState == YELLOW) and self.distanceToFinalWayPoints <= 25 and self.currentSpeed >= STEADY_STATE_SPEED):
            self.currentSpeed = self.currentSpeed + (DECELERATION * TIME_STEP)
            
        elif ((self.trafficSignalState == RED or self.trafficSignalState == YELLOW) and self.distanceToFinalWayPoints > 25 and self.currentSpeed < STEADY_STATE_SPEED):
            self.currentSpeed = self.currentSpeed + (ACCELERATION * TIME_STEP)
        
        if self.currentSpeed < 0.0:
            self.currentSpeed = 0.0

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
            self.previousTimeStampSetStatus == True

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

        self.distanceToFinalWayPoints = haversine.haversine(
            (self.currentLatitude, self.currentLongitude),
            (self.finalLatitude, self.finalLongitude),
            unit=haversine.Unit.METERS)
        
        if self.previousIndex < 140:
            self.distanceToFinalWayPoints = 50
        
        print("Distance to final waypoints: ", self.distanceToFinalWayPoints)
        self.logCoordinates()
        
        return round(self.currentLatitude,8), round(self.currentLongitude,8), round(self.currentSpeed,2)
       
        
    def logCoordinates(self):

        timestamp_verbose = str(time.time())
        timeStep = str(self.timeStep)
        latitude = str(self.currentLatitude)
        longitude = str(self.currentLongitude)
        elevation = str(self.currentElevation)
        speed = str(round(self.currentSpeed, 2))
        heading = str(round(self.currentHeading, 2))
        distance = str(round(self.distanceToFinalWayPoints, 2))

        csvRow = (timestamp_verbose + ","
            + timeStep + ","
            + latitude + ","
            + longitude + ","
            + elevation + ","
            + speed + ","
            + heading + ","
            + distance + "\n"
        )

        self.logFile.write(csvRow)
