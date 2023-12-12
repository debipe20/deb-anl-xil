
import time
import json


class SpatManager:
    def __init__(self):
        # self.spatDataDictionary = {str(29080): {'PhaseData': [
        #     {'SignalGroup': 1, 'startTime': 0, 'minEndTime': 10, 'maxEndTime': 15}]}}
        self.spatDataDictionary = {}

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
