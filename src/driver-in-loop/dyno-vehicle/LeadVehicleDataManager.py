"""
**********************************************************************************

LeadVehicleDataManager.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************
  
Description:
------------
The methods available from this class are the following:
- getLeadVehicleInformation(data): Method to decode messages received from VOICES J2735 Adapter and obtain lead vehicle information
***************************************************************************************
"""

import json
import binascii
from osys import v2x
from Logger import Logger

ONE_BY_TEN_MICRO_DEGREE_TO_DEGREE = 10000000
DECA_CONVERSION = 10
HEADING_CONVERSION = 0.0125
SPEED_CONVERSION = 0.02

class LeadVehicleDataManager:
    def __init__(self, config, logger: Logger) -> None:
        self.logger = logger
        self.config = config
        self.leadVehicleId = config["VehicleInformation"]["LeadVehicleId"]
        self.leadVehicleLattitude = 0.0
        self.leadVehicleLongitude = 0.0
        self.leadVehicleElevation = 0.0
        self.leadVehicleHeading = 0.0
        self.leadVehicleSpeed = 0.0
        self.leadVehicleInformationStatus = False
        
    def getLeadVehicleInformation(self, data):
        """
        - "try and except" block is used to take care scenario if objetive system fails to decode e.g., mobility path message from carma platform
        - This method decodeds received bsm and checks if vehicle id matches with lead vehicle id
            - if vehicle id match obtain lead vehicle information
        """
        self.leadVehicleInformationStatus = False
              
        try:
            receivedJsonString = v2x.MessageFrame.to_json(data, len(data))        
            receivedJsonString = json.loads(receivedJsonString)
            
            if self.leadVehicleId == receivedJsonString["value"]["coreData"]["id"]:
                self.leadVehicleLattitude = receivedJsonString["value"]["coreData"]["lat"] / ONE_BY_TEN_MICRO_DEGREE_TO_DEGREE
                self.leadVehicleLongitude = receivedJsonString["value"]["coreData"]["long"] / ONE_BY_TEN_MICRO_DEGREE_TO_DEGREE
                self.leadVehicleElevation = receivedJsonString["value"]["coreData"]["elev"] / DECA_CONVERSION
                self.leadVehicleHeading = receivedJsonString["value"]["coreData"]["heading"] / HEADING_CONVERSION
                self.leadVehicleSpeed = receivedJsonString["value"]["coreData"]["speed"] * SPEED_CONVERSION
                self.leadVehicleInformationStatus = True
            
        except Exception as e:
            hexData = binascii.hexlify(data)
            self.logger.logErrorData(e, hexData)
            self.leadVehicleInformationStatus = False

        
        return self.leadVehicleInformationStatus, self.leadVehicleLattitude, self.leadVehicleLongitude, self.leadVehicleSpeed
    
    def __del__(self):
        self.logger.consoleDisplay("Closing Lead Vehicle Manager Application")