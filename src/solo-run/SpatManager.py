
import time
import json
from osys import v2x

class SpatManager:
    def __init__(self):
        # self.spatDataDictionary = {str(29080): {'PhaseData': [
        #     {'SignalGroup': 1, 'startTime': 0, 'minEndTime': 10, 'maxEndTime': 15}]}}
        self.spatDataDictionary = {}

    def getSpatJsonString(self, data):
        """
        Method to create SPaT json string based on decoded SPaT
        """
        phaseDataList = []
        phaseDataDictionary = {}
        
        decodedJsonString = v2x.MessageFrame.to_json(data, len(data))
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
    
    
    def manageSpatData(self, jsonString):
        """

        """
        phaseDataList = []
        phaseDataDictionary = {}
        intersectionId = jsonString["IntersectionID"]

        for data in jsonString["SPaTData"]:
            phaseNo = data["SignalGroup"]
            eventState = data["EventState"]
            startTime = data["StartTime"]
            minEndTime = (data["MinEndTime"] - (time.time() - jsonString["TimeStamp"])) / 1000
            maxEndTime = (data["MaxEndTime"] - (time.time() - jsonString["TimeStamp"])) / 1000
            
            phaseDataDictionary = {
                "SignalGroup": phaseNo,
                "EventState": eventState,
                "StartTime": startTime,
                "MinEndTime": minEndTime,
                "MaxEndTime": maxEndTime 
   
            }
            phaseDataList.append(phaseDataDictionary)
        self.spatDataDictionary.update({str(intersectionId): {"PhaseData": phaseDataList}})
        # print("Spat Dictionary is following:\n", self.spatDataDictionary)
        
    def getRequestedSignalGroupData(self, jsonString):
        """
        """
        requestedIntersectionId = jsonString["IntersectionId"]
        requestedSignalGroup = jsonString["SignalGroup"]
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
