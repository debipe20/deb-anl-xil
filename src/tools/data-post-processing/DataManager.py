
import pandas as pd
import math

class DataManager:
    def __init__(self, config) -> None:
        self.config = config
        self.fileDirectory = self.config['FileDirectory']
        self.rawFileName = self.config["FileName"]
        self.rawDataFrame = pd.read_csv(self.fileDirectory + "/" + self.rawFileName)       

    def processRawData(self):
        """
        Method to call function to get vehicle and site identifier list
        This function calls a function to create csv file based on vehicle id
        """
        self.vehicleIdentifierList, self.siteIdentifierList = self.getUniqueVehicleIdentifierList(self.rawDataFrame)

        print(self.vehicleIdentifierList)
        print(self.siteIdentifierList)

        # for vehicleId in self.vehicleIdentifierList:
        #     self.getVehicleData(self.rawDataFrame, vehicleId)
        vehicleId = "ANL-MAN-1"    
        self.getVehicleData(self.rawDataFrame, vehicleId)

    def getUniqueVehicleIdentifierList(self, dataFrame):
        """
        Method to identify unique vehicle id and site id
        """
        uniqueVehicleIdentifierList = []
        uniqueSiteIndentifierList = []

        if not dataFrame.empty:
            for idx, row in dataFrame.loc[:].iterrows():
                # if row['const^identifier,String'] not in uniqueVehicleIdentifierList and row['timestamp_posix'] >= self.startTime and row['timestamp_posix'] <= self.endTime:
                if row['const^identifier,String'] not in uniqueVehicleIdentifierList:
                    uniqueVehicleIdentifierList.append(row['const^identifier,String'])
                    index = row['const^identifier,String'].find('-')
                    siteIdentifier = row['const^identifier,String'][:index]
                    uniqueSiteIndentifierList.append(siteIdentifier)

        return uniqueVehicleIdentifierList, uniqueSiteIndentifierList
    
    def is_float(self, data:str):
        """
        Method to verify if available speed data is or can be converted to float
        """
        try:
            isinstance(data, str) and float(data)
            return True
        
        except ValueError:
            return False

    def getVehicleData(self, dataFrame, vehicleId):
        """
        Method to obtain necessary vehicle for desired vehicle id and create a csv file
        """
        # logfile = open(self.fileDirectory + "/" + vehicleId + ".csv", "w")
        logFile = open(vehicleId + ".csv", "w")
        logFile.write("Time_Sent,Time_Received,Vehicle_Type,Vehicle_Speed,Grade\n")
        
        for idx, row in dataFrame.loc[:].iterrows():
            
            if row['const^identifier,String'] == vehicleId:
                vel_X = row['tspi.velocity.ltpENU_asTransmitted.vxInMetersPerSecond,Float32 (optional)']
                if (isinstance(vel_X, str) and self.is_float(vel_X)) or isinstance(vel_X, float):
                    vehicleSpeed = math.sqrt(pow(float(row['tspi.velocity.ltpENU_asTransmitted.vxInMetersPerSecond,Float32 (optional)']), 2) + 
                                        pow(float(row['tspi.velocity.ltpENU_asTransmitted.vyInMetersPerSecond,Float32 (optional)']), 2) + 
                                        pow(float(row['tspi.velocity.ltpENU_asTransmitted.vzInMetersPerSecond,Float32 (optional)']), 2))

                    csvRow = (str(row['Metadata,TimeOfCommit'] / (10**9)) + ","
                    + str(row['Metadata,TimeOfReceipt'] / (10**9)) + ","
                    + str(row['const^type,String']) + ","
                    + str(vehicleSpeed) + ","
                    + "NA" + "\n")
                    
                    logFile.write(csvRow)

                else:
                    print("\nsomething wrong for ", str(row['rowID']))

        logFile.close()

'''##############################################
                   Unit testing
##############################################'''
if __name__ == "__main__":
    import json

    # Read the config file into a json object:
    configFile = open("configuration.json", 'r')
    config = json.load(configFile)
    # Close the config file:
    configFile.close()
    
    dataManager = DataManager(config)
    dataManager.processRawData()