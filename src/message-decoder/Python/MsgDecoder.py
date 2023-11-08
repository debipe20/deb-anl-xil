import json
import time
import binascii
from osys import v2x

OneByTenMicroDegree_To_Degree = 10000000
Deca_Conversion = 10
 
class  MsgDecoder:
    def __init__(self):
        self.green = 1
        self.yellow = 2
        self.red = 3
    
    def getMessageType(self, string):
        messageType = ""

        if (string[:4]) == "0012":
            messageType = "MAP"

        elif (string[:4]) == "0013":
            messageType = "SPaT"

        elif (string[:4]) == "0014":
            messageType = "BSM"
        # if (string["messageId"]) == 18:
        #     messageType = "MAP"

        # elif (string["messageId"]) == 19:
        #     messageType = "SPaT"

        # elif (string["messageId"]) == 20:
        #     messageType = "BSM"

        return messageType


    def getMapJsonString(self, mapPayload):
        """
        Method to create MAP json string based on decoded MAP
        """
        unhexedPayload = binascii.unhexlify(mapPayload)
        decodedJsonString = v2x.MessageFrame.to_json(unhexedPayload, len(unhexedPayload))
        jsonString = json.loads(decodedJsonString)
        
        mapJsonString = json.dumps({
            "MsgType": "MAP",
            "MapPayload": mapPayload,
            "IntersectionID": jsonString["value"]["intersections"][0]["id"]["id"]
        })

        return mapJsonString


    def getSpatJsonString(self, spatPayload):
        """
        Method to create SPaT json string based on decoded SPaT
        """
        phaseDataList = []
        phaseDataDictionary = {}
        
        unhexedPayload = binascii.unhexlify(spatPayload)
        decodedJsonString = v2x.MessageFrame.to_json(unhexedPayload, len(unhexedPayload))
        print(decodedJsonString)
        jsonString = json.loads(decodedJsonString)
        print(jsonString)

        # intersectionName = jsonString["value"]["intersections"][0]["name"]
        # intersectionID = jsonString["value"]["intersections"][0]["id"]["id"]
        
        for data in jsonString["value"]["intersections"][0]["states"]:
            
            startTime = data["state-time-speed"][0]["timing"]["startTime"] if "startTime" in data["state-time-speed"][0]["timing"].keys() else 0.0
            minEndTime = data["state-time-speed"][0]["timing"]["minEndTime"] if "minEndTime" in data["state-time-speed"][0]["timing"].keys() else 0.0
            maxEndTime = data["state-time-speed"][0]["timing"]["maxEndTime"] if "maxEndTime" in data["state-time-speed"][0]["timing"].keys() else minEndTime
            
            if data["state-time-speed"][0]["eventState"] == "protected-Movement-Allowed":
                eventState = self.green
                
            elif data["state-time-speed"][0]["eventState"] == "stop-And-Remain":
                eventState = self.red
                
            elif data["state-time-speed"][0]["eventState"] == "protected-clearance":
                eventState = self.yellow 
            
            phaseDataDictionary = {
                "SignalGroup": data["signalGroup"],
                "EventState": eventState,
                "StartTime": startTime,
                "MinEndTime": minEndTime,
                "MaxEndTime": maxEndTime
            }
            phaseDataList.append(phaseDataDictionary)
            
        spatJsonString = json.dumps({
            "MsgType": "SPaT",
            "IntersectionName": jsonString["value"]["intersections"][0]["name"],
            "IntersectionID": 2515,
            # "IntersectionID": jsonString["value"]["intersections"][0]["id"]["id"],
            "MinuteOfYear": jsonString["value"]["intersections"][0]["moy"],
            # "TimeStamp": jsonString["value"]["intersections"][0]["timeStamp"],
            "TimeStamp": time.time(),
            "SPaTData": phaseDataList
        })
        
        # print("Following Spat Json String will send:\n", spatJsonString)

        return spatJsonString


    def getBsmJsonString(self, bsmPayload):
        """
        Method to create BSM json string based on decoded BSM
        """
        unhexedPayload = binascii.unhexlify(bsmPayload)
        decodedJsonString = v2x.MessageFrame.to_json(unhexedPayload, len(unhexedPayload))
        jsonString = json.loads(decodedJsonString)
        
        bsmJsonString = json.dumps({
            "MsgType": "BSM",
            "BasicVehicle": {
                "temporaryID": int(str(jsonString["value"]["coreData"]["id"])[:4],16),
                "type": str("car"),
                "secMark_Second": float(jsonString["value"]["coreData"]["secMark"]),
                "position": {
                    "latitude_DecimalDegree":  float(jsonString["value"]["coreData"]["lat"] / OneByTenMicroDegree_To_Degree),
                    "longitude_DecimalDegree": float(jsonString["value"]["coreData"]["long"] / OneByTenMicroDegree_To_Degree),
                    "elevation_Meter": float(jsonString["value"]["coreData"]["elev"] / Deca_Conversion)
                },
                # "speed_MeterPerSecond": float(jsonString["value"]["coreData"]["speed"] * 0.2),
                "speed_MeterPerSecond": float(jsonString["value"]["coreData"]["speed"] / 14),
                "heading_Degree": float(jsonString["value"]["coreData"]["heading"] * 0.0125),
                "size": {
                    "length_cm": float(jsonString["value"]["coreData"]["size"]["length"]),
                    "width_cm": float(jsonString["value"]["coreData"]["size"]["length"])
                }
            }
        })

        return bsmJsonString