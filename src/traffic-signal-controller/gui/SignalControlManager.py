

class SignalControlManager:
    def __init__(self):
        self.databaseFileName = ""
        self.signalControlType = ""
        self.startingPhase1 = 1
        self.startingPhase2 = 2

    def getDatabase(self):
        pass

    def getControlType(self):
        self.signalControlType = "Fixed-Time"

    def getDetectorStatus(self):
        """
        Not valid for fixed-time signal controller
        """
        pass

    def getRingStructure(self):
        pass