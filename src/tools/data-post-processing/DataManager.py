import os
import pandas as pd
import math

KPH_TO_MPS = 0.277778

class DataManager:
    def __init__(self, config) -> None:
        self.config = config
        self.fileDirectory = self.config['FileDirectory']
        self.rawFileName = self.config["FileName"]
        # home_directory = os.path.expanduser( '~' )
        # self.rawDataFrame = pd.read_csv(home_directory + self.fileDirectory + "/" + self.rawFileName)
        self.logFileList = []
        self.vehicleTypeList = []
        self.roadGradeTypeList = []
        self.saveFileNameList = []          
        
    def processRawData(self):
        timeData, vehicleType, vehicleSpeed, roadGrade =([] for i in range(4))
        
        [self.logFileList.append(fileName) for fileName in self.config["FileName"]]
        [self.vehicleTypeList.append(vehicleModel) for vehicleModel in self.config["VehicleType"]]
        [self.roadGradeTypeList.append(roadGradeType) for roadGradeType in self.config["RoadGradColumn"]]
        [self.saveFileNameList.append(fileName) for fileName in self.config["SaveFileName"]]
        
        for index, logFile in enumerate(self.logFileList):
            processedDataFrame = pd.DataFrame()          
            logFileName = self.fileDirectory + "/" + logFile
            vehicleModel = self.vehicleTypeList[index]
            roadGradeType = self.roadGradeTypeList[index]
            saveFileName = self.saveFileNameList[index]
            self.startTime = self.config["StartTime"][index]
            self.endTime = self.config["EndTime"][index]
            
            print(logFileName)

            self.rawDataFrame = pd.read_csv(logFileName)
            
            # startTime = self.rawDataFrame['current_time'].iloc[0]
            startTimeIndex, endTimeIndex = self.getStartAndEndTimeIndex(self.rawDataFrame)
            startTime = self.rawDataFrame['current_time'].iloc[startTimeIndex]
            
            for index, row in self.rawDataFrame.loc[startTimeIndex:endTimeIndex].iterrows():
            # for index, row in self.rawDataFrame.iterrows():
                timeData.append(row['current_time'] - startTime)
                vehicleType.append(vehicleModel)
                vehicleSpeed.append(row['smoothed_speed'] * KPH_TO_MPS)
                roadGrade.append(row[roadGradeType])
            
            timeData = [round(val, 2) for val in timeData]
            vehicleSpeed = [round(val, 2) for val in vehicleSpeed]
            roadGrade = [round(val, 5) for val in roadGrade]
            # print(timeData)
            processedDataFrame = pd.DataFrame({'Time(s)':timeData,'VehicleType':vehicleType,'VehicleSpeed(m/s)':vehicleSpeed,'RoadGrade(degree)':roadGrade})
            [li.clear() for li in [timeData, vehicleType, vehicleSpeed, roadGrade]]
            
            processedDataFrame.to_csv('processed-data/' + saveFileName, index=False)  # Set index=False to exclude the index column in the CSV file            

  
    def getStartAndEndTimeIndex(self, dataframe):
        """
        method to get index for the start time and end time of the diagram
        """
        startTimeIndexList = dataframe.index[dataframe['current_time'] == self.startTime].tolist()
        endTimeIndexList = dataframe.index[dataframe['current_time'] == self.endTime].tolist()

        if not bool(startTimeIndexList):
            startTimeIndexList = dataframe.index[(dataframe['current_time'] > self.startTime) & (
                dataframe['current_time'] < self.startTime+1)].tolist()
        if not bool(endTimeIndexList):
            endTimeIndexList = dataframe.index[(dataframe['current_time'] > self.endTime) & (
                dataframe['current_time'] < self.endTime+1)].tolist()


        startTimeIndex = startTimeIndexList[0] if startTimeIndexList else int(dataframe['index'].iloc[0])         
        endTimeIndex = endTimeIndexList[0] if endTimeIndexList else int(dataframe['index'].iloc[-1])


        return startTimeIndex, endTimeIndex

# '''##############################################
#                    Unit testing
# ##############################################'''
# if __name__ == "__main__":
#     import json

#     # Read the config file into a json object:
#     configFile = open("configuration.json", 'r')
#     config = json.load(configFile)
#     # Close the config file:
#     configFile.close()
    
#     dataManager = DataManager(config)
#     # dataManager.processRawData()