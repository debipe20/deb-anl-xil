import json
import pandas as pd
import haversine
import time, datetime

MaxMsgCount = 127
MinMsgCount = 1
OneByTenMicroDegree_To_Degree = 10000000
Deca_Conversion = 10
# kph2unit = 0.277778/0.2
SECOND_MILISECOND_CONVERSION = 1000


class BsmGenerator:
    def __init__(self, config):
        self.config = config
        self.vehicleId = config["VehicleInformation"]["HostVehicleId"]
        self.currentLatitude = 0.0
        self.currentLongitude = 0.0
        self.currentElevation = 0.0
        self.currentSpeed = 0.0
        self.currentHeading = 0.0
        self.previousLatitude = (41.7007424,)  # ANL
        self.previousLongitude = -87.9915918
        self.previousIndex = 0
        self.previousTime = time.time()
        self.msgCount = 0
        self.timeStep = 0.0
        self.extraDistance = 0.0
        self.step = 0
        self.previousTimeStampSetStatus = False
        self.latitudeList, self.longitudeList, self.elevationList, self.headingList = ([] for i in range(4) )

        self.bsmLogFile = config["VehicleInformation"]["BsmLogFileName"]
        # self.logFile = open("Estimate-BSM-Log.csv", "w")
        # self.logFile.write("timestamp_verbose,timeStep,msgCount,temporaryId,secMark,latitude,longitude,elevation,speed,heading\n")
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
        - Iterate until haversine distance for current coordinate is close to the estimated distance compare to next coordinate
        """
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
                    unit=haversine.Unit.METERS,
                )

                calculatedDistanceNext = haversine.haversine(
                    (self.previousLatitude, self.previousLongitude),
                    (self.latitudeList[index + 1], self.longitudeList[index + 1]),
                    unit=haversine.Unit.METERS,
                )

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
        """ """
        self.currentSpeed = currentSpeed

        if self.currentSpeed > 0:
            self.getNearestCoordinates()

        self.setMsgCount()
        self.currentHeading = round(self.currentHeading, 2)

        bsmDictionary = {
            "messageId": 20,
            "value": {
                "coreData": {
                    "msgCnt": self.msgCount,
                    "id": self.vehicleId,
                    "secMark": int(self.getMsOfMinute()),
                    "lat": int(self.currentLatitude * OneByTenMicroDegree_To_Degree),
                    "long": int(self.currentLongitude * OneByTenMicroDegree_To_Degree),
                    "elev": int(self.currentElevation * Deca_Conversion),
                    "accuracy": {
                        "semiMajor": 255,
                        "semiMinor": 255,
                        "orientation": 65535,
                    },
                    "transmission": "forwardGears",
                    "speed": int(self.currentSpeed / 0.2),
                    "heading": int(self.currentHeading / 0.0125),
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
        # print("Index is", self.previousIndex)
        print("BSM Dictionary is following:\n", bsmDictionary)

        # self.logCoordinates()

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
        if self.msgCount < MaxMsgCount:
            self.msgCount += 1

        else:
            self.msgCount = MinMsgCount

    def getMsOfMinute(self):

        timeNow = datetime.datetime.now()
        msOfMinute = timeNow.second * SECOND_MILISECOND_CONVERSION

        return msOfMinute

    def logCoordinates(self):

        timestamp_verbose = str(time.time())
        timeStep = str(self.timeStep)
        msgCount = str(self.msgCount)
        temporaryId = "f03ad610"
        secMark = str(100)
        latitude = str(self.currentLatitude)
        longitude = str(self.currentLongitude)
        elevation = str(self.currentElevation)
        speed = str(round(self.currentSpeed, 2))
        heading = str(round(self.currentHeading,2))

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

        self.logFile.write(csvRow)
