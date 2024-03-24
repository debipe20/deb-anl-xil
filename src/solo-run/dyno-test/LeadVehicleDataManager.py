import json
import binascii
from osys import v2x

OneByTenMicroDegree_To_Degree = 10000000
Deca_Conversion = 10
Heading_Coneversion = 0.0125
Speed_Conversion = 0.02

class LeadVehicleDataManager:
    def __init__(self, config) -> None:
        self.config = config
        self.leadVehicleId = config["VehicleInformation"]["LeadVehicleId"]
        
        
    def getLeadVehicleInformation(self, data):
        leadVehicleLattitude = 0.0
        leadVehicleLongitude = 0.0
        leadVehicleElevation = 0.0
        leadVehicleHeading = 0.0
        leadVehicleSpeed = 0.0
        leadVehicleInformationStatus = False

        receivedJsonString = v2x.MessageFrame.to_json(data, len(data))        
        receivedJsonString = json.loads(receivedJsonString)
        # print("Vehicle Id: ", receivedJsonString["value"]["coreData"]["id"])
        
        if self.leadVehicleId == receivedJsonString["value"]["coreData"]["id"]:
            leadVehicleLattitude = receivedJsonString["value"]["coreData"]["lat"] / OneByTenMicroDegree_To_Degree
            leadVehicleLongitude = receivedJsonString["value"]["coreData"]["long"] / OneByTenMicroDegree_To_Degree
            leadVehicleElevation = receivedJsonString["value"]["coreData"]["elev"] / Deca_Conversion
            leadVehicleHeading = receivedJsonString["value"]["coreData"]["heading"] / Heading_Coneversion
            leadVehicleSpeed = receivedJsonString["value"]["coreData"]["speed"] * Speed_Conversion
            leadVehicleInformationStatus = True

        
        return leadVehicleInformationStatus, leadVehicleLattitude, leadVehicleLongitude, leadVehicleSpeed