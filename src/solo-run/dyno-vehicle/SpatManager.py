
import datetime
import json
import binascii
from osys import v2x
from Logger import Logger


GREEN = 1
YELLOW = 2
RED = 3

class SpatManager:
    def __init__(self, config, logger: Logger):
        self.logger = logger
        self.config = config
        self.desiredSignalGroup = self.config["SignalControllerInformation"]["DesiredSignalGroup"]
        self.eventState = GREEN
        self.spatDataDictionary = {}


    def getDesiredSignalGroupState(self, payload):
        
        try:
            self.logger.logSpatHexData(payload)
            unhexedPayload = binascii.unhexlify(payload)
            receivedJsonString = v2x.MessageFrame.to_json(unhexedPayload, len(unhexedPayload))        
            receivedJsonString = json.loads(receivedJsonString)

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
            self.logger.logErrorData(e, payload)
                
        return self.eventState
    
    
    def __del__(self):
        self.logger.consoleDisplay("Closing SPaT Manager Application")
