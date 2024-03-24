import json
import time, datetime

class Logger:
    def __init__(self, consoleStatus:bool, loggingStatus:bool):
        self.consoleStatus = consoleStatus
        self.loggingStatus = loggingStatus

        if (self.loggingStatus==True):
            timestamp = str(round(time.time(),4))
            initializationTimestamp = ('{:%m%d%Y_%H%M%S}'.format(datetime.datetime.now()))
            logfileName = "MsgDecoderLog_" + initializationTimestamp + ".log"
            self.logFile = open(logfileName, 'w', buffering=1)
            self.logFile.write(("[{}]".format(timestamp) + " " + "Open Message-Decoder log file\n"))
            
    def loggingAndConsoleDisplayDictionary(self, logString):
        
        timestamp = str(round(time.time(),4))
        logString = json.dumps(logString)

        if (self.consoleStatus==True):
            print(("\n[{}]".format(timestamp) + " " + logString))
        if (self.loggingStatus==True):
            self.logFile.write(("\n[{}]".format(timestamp) + " " + logString + "\n"))

    def loggingAndConsoleDisplayString(self, logString:str):
        
        timestamp = str(round(time.time(),4))
        
        if (self.consoleStatus==True):
            print(("\n[{}]".format(timestamp) + " " + logString))
        if (self.loggingStatus==True):
            self.logFile.write(("\n[{}]".format(timestamp) + " " + logString + "\n"))

    def loogingDictionary(self, logString):

        logString = json.dumps(logString)
        timestamp = str(round(time.time(),4))
        if (self.loggingStatus==True):
            self.logFile.write(("\n[{}]".format(timestamp) + " " + logString + "\n"))

    def loogingString(self, logString:str):
        
        timestamp = str(round(time.time(),4))
        if (self.loggingStatus==True):
            self.logFile.write(("\n[{}]".format(timestamp) + " " + logString + "\n"))  
    
    def consoleDisplayDictionary(self, consoleString):
        consoleString = json.dumps(consoleString)

        timestamp = str(round(time.time(),4))
        if (self.consoleStatus == True):
            print(("\n[{}]".format(timestamp) + " " + consoleString))

    def consoleDisplayString(self, consoleString:str):
        
        timestamp = str(round(time.time(),4))
        if (self.consoleStatus == True):
            print(("\n[{}]".format(timestamp) + " " + consoleString))

    def __del__(self):
        if (self.loggingStatus == True):
            self.logFile.close()

if __name__=="__main__":
    consoleStatus = True
    loggingStatus = True
    
    logger = Logger(consoleStatus, loggingStatus)
    logString = "Hello! This is a test output!"
    logger.loggingAndConsoleDisplay(logString)
    del logger