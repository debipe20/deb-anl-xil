
import time
import json


class SpatManager:
    def __init__(self):
        self.spatDataDictionary = {str(29080): {'PhaseData': [
            {'SignalGroup': 1, 'startTime': 0, 'minEndTime': 10, 'maxEndTime': 15}]}}

    def manageSpatData(self, jsonData):
        """

        """
        phaseDataList = []
        phaseDataDictionary = {}
        """
        if msg-decoder is run using mmitss
        """
        intersectionId = jsonData["Spat"]["intersectionState"]["intersectionID"]
        print(intersectionId)

        for data in jsonData["Spat"]["phaseState"]:
            # phaseNo = data["phaseNo"]
            # currentState = data["currState"]
            # startTime = data["startTime"]
            # minEndTime = data["minEndTime"]
            # maxEndTime = data["maxEndTime"]
            phaseDataDictionary = {
                "signalGroup": data["phaseNo"],
                "currentState": data["currState"],
                "startTime": data["startTime"],
                "minEndTime": (data["minEndTime"] - (time.time() - jsonData["Timestamp_posix"])) / 100,
                "maxEndTime": (data["maxEndTime"] - (time.time() - jsonData["Timestamp_posix"])) / 100
   
            }
            phaseDataList.append(phaseDataDictionary)
        self.spatDataDictionary.update({str(intersectionId): {"PhaseData": phaseDataList}})
        print(self.spatDataDictionary)
        """
        if msg-decoder is run using objective-systems
        """
        # intersectionId = jsonData["value"]["intersections"][0]["id"]["id"]

        # for data in jsonData["value"]["intersections"][0]["states"]:
        #     startTime = data["state-time-speed"][0]["timing"]["startTime"] if "startTime" in data["state-time-speed"][0]["timing"].keys() else 0.0
        #     minEndTime = data["state-time-speed"][0]["timing"]["minEndTime"] if "minEndTime" in data["state-time-speed"][0]["timing"].keys() else 0.0
        #     maxEndTime = data["state-time-speed"][0]["timing"]["maxEndTime"] if "maxEndTime" in data["state-time-speed"][0]["timing"].keys() else minEndTime
        #     phaseDataDictionary = {
        #         "SignalGroup": data["signalGroup"],
                
        #         "startTime": startTime,
        #         "minEndTime": minEndTime,
        #         "maxEndTime": maxEndTime
        #     }
        #     phaseDataList.append(phaseDataDictionary)
        # self.spatDataDictionary.update({str(intersectionId): {"PhaseData": phaseDataList}})
        # print(self.spatDataDictionary)

        
            # print("value =", self.spatDataDictionary[key]["PhaseData"][1]["SignalGroup"])

    def getRequestedSignalGroupData(self, jsonData):
        """
        """
        requestedIntersectionId = jsonData["IntersectionId"]
        requestedSignalGroup = jsonData["SignalGroup"]
        key = str(requestedIntersectionId) #str(1003)
        
        if key in self.spatDataDictionary.keys():
            for data in self.spatDataDictionary[key]["PhaseData"]: 
                if data["SignalGroup"] == requestedSignalGroup:
                    startTime = data["startTime"]
                    minEndTime = data["minEndTime"]
                    maxEndTime = data["maxEndTime"]

        requestedSignalGroupData = json.dumps({
            "MsgType": "SignalGroupDataMessage",
            "startTime": startTime,
            "minEndTime": minEndTime,
            "maxEndTime": maxEndTime
            }

        )
        return requestedSignalGroupData
