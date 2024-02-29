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
        self.leadVehicleLattitude = 0.0
        self.leadVehicleLongitude = 0.0
        self.leadVehicleElevation = 0.0
        self.leadVehicleHeading = 0.0
        self.leadVehicleSpeed = 0.0
        
    def getLeadVehicleInformation(self, data):
        encodedBsm = binascii.hexlify(data)
        # print(encodedBsm)
        receivedJsonString = v2x.MessageFrame.to_json(data, len(data))
        # print(receivedJsonString)
        
        receivedJsonString = json.loads(receivedJsonString)
        # print("Vehicle Id: ", receivedJsonString["value"]["coreData"]["id"])
        
        if self.leadVehicleId == receivedJsonString["value"]["coreData"]["id"]:
            self.leadVehicleLattitude = receivedJsonString["value"]["coreData"]["lat"] / OneByTenMicroDegree_To_Degree
            self.leadVehicleLongitude = receivedJsonString["value"]["coreData"]["long"] / OneByTenMicroDegree_To_Degree
            self.leadVehicleElevation = receivedJsonString["value"]["coreData"]["elev"] / Deca_Conversion
            self.leadVehicleHeading = receivedJsonString["value"]["coreData"]["heading"] / Heading_Coneversion
            self.leadVehicleSpeed = receivedJsonString["value"]["coreData"]["speed"] * Speed_Conversion  * 3.6
            # if (self.leadVehicleSpeed > 0.0):
            #     print("Vehicle Speed is: ",self.leadVehicleSpeed)
        
            return self.leadVehicleLattitude, self.leadVehicleLongitude, self.leadVehicleSpeed