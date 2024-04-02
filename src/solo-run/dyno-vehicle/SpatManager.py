
import datetime
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
        initializationTimestamp = ('{:%m%d%Y_%H%M%S}'.format(datetime.datetime.now()))
        self.logFile = open("/nojournal/bin/log/error_log_" + initializationTimestamp + ".log", "w")
        # self.logFile = open("/nojournal/bin/log/error_log.log", "w")

    def getDesiredSignalGroupState(self, payload):
        
        try:
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
        
        except Exception as e:
            
            self.logFile.write("Following error occurred:\n" + str(e) + "\n")
            self.logFile.write("Hexed Data in Spat Manager class is:\n" + str(payload) + "\n")
            self.leadVehicleInformationStatus = False
                
        return self.eventState
    
    
    def __del__(self):
        self.logFile.close()
