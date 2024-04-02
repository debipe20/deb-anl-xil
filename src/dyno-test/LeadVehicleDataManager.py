import json
import binascii
from osys import v2x
import datetime

ONE_BY_TEN_MICRO_DEGREE_TO_DEGREE = 10000000
DECA_CONVERSION = 10
HEADING_CONVERSION = 0.0125
SPEED_CONVERSION = 0.02

class LeadVehicleDataManager:
    def __init__(self, config) -> None:
        self.config = config
        self.leadVehicleId = config["VehicleInformation"]["LeadVehicleId"]
        initializationTimestamp = ('{:%m%d%Y_%H%M%S}'.format(datetime.datetime.now()))
        self.logFile = open("/nojournal/bin/log/error_log_" + initializationTimestamp + ".log", "w")
        # self.logFile = open("/nojournal/bin/log/error_log.log", "w")
        self.leadVehicleLattitude = 0.0
        self.leadVehicleLongitude = 0.0
        self.leadVehicleElevation = 0.0
        self.leadVehicleHeading = 0.0
        self.leadVehicleSpeed = 0.0
        self.leadVehicleInformationStatus = False
        
        
    def getLeadVehicleInformation(self, data):
        """
        - "try and except" block is used to take care scenario if objetive system fails to decode e.g., mobility path message from carma platform
        - this method decodeds received bsm and checks if vehicle id matches with lead vehicle id
            - if vehicle id match obtain lead vehicle information
        """
               
        try:
            receivedJsonString = v2x.MessageFrame.to_json(data, len(data))        
            receivedJsonString = json.loads(receivedJsonString)
            # print("Vehicle Id: ", receivedJsonString["value"]["coreData"]["id"])
            
            if self.leadVehicleId == receivedJsonString["value"]["coreData"]["id"]:
                self.leadVehicleLattitude = receivedJsonString["value"]["coreData"]["lat"] / ONE_BY_TEN_MICRO_DEGREE_TO_DEGREE
                self.leadVehicleLongitude = receivedJsonString["value"]["coreData"]["long"] / ONE_BY_TEN_MICRO_DEGREE_TO_DEGREE
                self.leadVehicleElevation = receivedJsonString["value"]["coreData"]["elev"] / DECA_CONVERSION
                self.leadVehicleHeading = receivedJsonString["value"]["coreData"]["heading"] / HEADING_CONVERSION
                self.leadVehicleSpeed = receivedJsonString["value"]["coreData"]["speed"] * SPEED_CONVERSION
                self.leadVehicleInformationStatus = True
            
        except Exception as e:
            hexData = binascii.hexlify(data)
            self.logFile.write("Following error occurred:\n" + str(e) + "\n")
            self.logFile.write("Hexed Data in Lead Vehicle Data Manager class is:\n" + str(hexData) + "\n")
            self.leadVehicleInformationStatus = False

        
        return self.leadVehicleInformationStatus, self.leadVehicleLattitude, self.leadVehicleLongitude, self.leadVehicleSpeed
    
    def __del__(self):
        self.logFile.close()