
import time
import json
import binascii
from osys import v2x


GREEN = 1
YELLOW = 2
RED = 3

class SpatManager:
    def __init__(self, config):
        # self.spatDataDictionary = {str(29080): {'PhaseData': [
        #     {'SignalGroup': 1, 'startTime': 0, 'minEndTime': 10, 'maxEndTime': 15}]}}
        self.config = config
        self.desiredSignalGroup = self.config["SignalControllerInformation"]["DesiredSignalGroup"]
        self.eventState = GREEN
        self.spatDataDictionary = {}

    def getDesiredSignalGroupState(self, payload):
        unhexedPayload = binascii.unhexlify(payload)
        receivedJsonString = v2x.MessageFrame.to_json(unhexedPayload, len(unhexedPayload))        
        receivedJsonString = json.loads(receivedJsonString)
        # print("Received SPaT json string is following: \n", receivedJsonString)
        intersectionId = receivedJsonString["value"]["intersections"][0]["id"]["id"]
        
        for data in receivedJsonString["value"]["intersections"][0]["states"]:
            if data["signalGroup"] == self.desiredSignalGroup and (data["state-time-speed"][0]["eventState"] == "protected-Movement-Allowed" or
                                                                   data["state-time-speed"][0]["eventState"] == "permissive-Movement-Allowed"):
                self.eventState = GREEN
                
                
                
            elif data["signalGroup"] == self.desiredSignalGroup and (data["state-time-speed"][0]["eventState"] == "protected-clearance" or 
                                                                    data["state-time-speed"][0]["eventState"] == "permissive-clearance"):
                self.eventState = YELLOW
                
            elif data["signalGroup"] == self.desiredSignalGroup and data["state-time-speed"][0]["eventState"] == "stop-And-Remain":
                self.eventState = RED
                
        return self.eventState
    
    def manageSpatData(self, payload):
        """

        """
        phaseDataList = []
        phaseDataDictionary = {}
        unhexedPayload = binascii.unhexlify(payload)
        receivedJsonString = v2x.MessageFrame.to_json(unhexedPayload, len(unhexedPayload))        
        receivedJsonString = json.loads(receivedJsonString)
        # print("Received SPaT json string is following: \n", receivedJsonString)
        intersectionId = receivedJsonString["value"]["intersections"][0]["id"]["id"]

        for data in receivedJsonString["value"]["intersections"][0]["states"]:
            # phaseNo = data["SignalGroup"]
            # eventState = data["EventState"]
            # startTime = data["StartTime"]
            # minEndTime = (data["MinEndTime"] - (time.time() - receivedJsonString["TimeStamp"])) / 1000
            # maxEndTime = (data["MaxEndTime"] - (time.time() - receivedJsonString["TimeStamp"])) / 1000
            
            startTime = data["state-time-speed"][0]["timing"]["startTime"] if "startTime" in data["state-time-speed"][0]["timing"].keys() else 0.0
            minEndTime = data["state-time-speed"][0]["timing"]["minEndTime"] if "minEndTime" in data["state-time-speed"][0]["timing"].keys() else 0.0
            maxEndTime = data["state-time-speed"][0]["timing"]["maxEndTime"] if "maxEndTime" in data["state-time-speed"][0]["timing"].keys() else minEndTime
            
            if data["state-time-speed"][0]["eventState"] == "protected-Movement-Allowed":
                eventState = GREEN
                
            elif data["state-time-speed"][0]["eventState"] == "protected-clearance":
                eventState = YELLOW 
            
            elif data["state-time-speed"][0]["eventState"] == "stop-And-Remain":
                eventState = RED              
                        
            phaseDataDictionary = {
                "SignalGroup": data["signalGroup"],
                # "EventState": eventState,
                "StartTime": startTime,
                "MinEndTime": minEndTime,
                "MaxEndTime": maxEndTime
            }
            
            phaseDataList.append(phaseDataDictionary)
        
        self.spatDataDictionary.update({str(intersectionId): {"PhaseData": phaseDataList}})
        # print("Spat Dictionary is following:\n", self.spatDataDictionary)
        
    def getRequestedSignalGroupData(self, receivedJsonString):
        """
        """
        requestedIntersectionId = receivedJsonString["IntersectionId"]
        requestedSignalGroup = receivedJsonString["SignalGroup"]
        key = str(requestedIntersectionId) #str(1003)
        
        if key in self.spatDataDictionary.keys():
            for data in self.spatDataDictionary[key]["PhaseData"]: 
                if data["SignalGroup"] == requestedSignalGroup:
                    eventState = data["EventState"]
                    startTime = data["StartTime"]
                    minEndTime = data["MinEndTime"]
                    maxEndTime = data["MaxEndTime"]

            requestedSignalGroupData = json.dumps({
                "MsgType": "SignalGroupDataMessage",
                "DataAvalability": True,
                "EventState": eventState,
                "StartTime": startTime,
                "MinEndTime": minEndTime,
                "MaxEndTime": maxEndTime
                }
            )

        else:
            requestedSignalGroupData = json.dumps({
                "MsgType": "SignalGroupDataMessage",
                "DataAvalability": False
            }
        ) 

        return requestedSignalGroupData
