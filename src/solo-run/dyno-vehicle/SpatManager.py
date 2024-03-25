
import time
import json
import binascii
from osys import v2x

class SpatManager:
    def __init__(self):
        # self.spatDataDictionary = {str(29080): {'PhaseData': [
        #     {'SignalGroup': 1, 'startTime': 0, 'minEndTime': 10, 'maxEndTime': 15}]}}
        self.spatDataDictionary = {}

    def manageSpatData(self, payload):
        """

        """
        phaseDataList = []
        phaseDataDictionary = {}
        unhexedPayload = binascii.unhexlify(payload)
        receivedJsonString = v2x.MessageFrame.to_json(unhexedPayload, len(unhexedPayload))        
        receivedJsonString = json.loads(receivedJsonString)
        print("Received SPaT json string is following: \n", receivedJsonString)
        intersectionId = receivedJsonString["IntersectionID"]

        for data in receivedJsonString["SPaTData"]:
            phaseNo = data["SignalGroup"]
            eventState = data["EventState"]
            startTime = data["StartTime"]
            minEndTime = (data["MinEndTime"] - (time.time() - receivedJsonString["TimeStamp"])) / 1000
            maxEndTime = (data["MaxEndTime"] - (time.time() - receivedJsonString["TimeStamp"])) / 1000
            
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
