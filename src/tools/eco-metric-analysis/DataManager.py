import pandas as pd
import os
import matplotlib.pyplot as plt

MPH_TO_MPS = 0.44704

class DataManager:
    def __init__(self, config) -> None:
        self.config = config
        self.home_directory = os.path.expanduser("~")
        self.startTime = 0.0
        self.endTime = 0.0
        
        # self.dataFileName = config['FileName']
        # self.dataFrame = pd.read_csv(self.dataFileName)
        # columnFile = open("cloumn-name.log", 'w')
        
        # for col in self.dataFrame.columns:
        #     columnFile.write(col + '\n')
            
        # columnFile.close()


    def analyzeDynoLog(self):
        timeDataList, transmissionOilTempDataList, motorTemperatureDataList, motorInverterTemperatureDataList, coolantPumpCommandDataList, hV_BattCoolantTempDataList, aC_CompressorPowerDataList = ([] for i in range(7))
        ecoDrivingLogFileList, soloRunLogFileList = ([] for i in range(2)) 
        [ecoDrivingLogFileList.append(fileDirectory) for fileDirectory in self.config["Dyno"]['Eco-Driving']]
        [soloRunLogFileList.append(fileDirectory) for fileDirectory in self.config["Dyno"]['Solo-Run']]
        
        def plotDiagram(logFileList, fileLocation):
            
            colorList = ['green', 'blue', 'red', 'navy', 'orange', 'darkcyan', 'yellow']
            roundNo = 0
            
            fig1, ax1 = plt.subplots(figsize=(18,12))                
            ax1.set_xlabel('Time (s)', fontsize = 14, fontweight='bold')
            ax1.set_ylabel('Trans_oil_temp_CAN__C', fontsize = 14, fontweight='bold')
            ax1.set_title('Transmission Oil Temperature [C]', fontsize = 18, fontweight = 'bold')
            ax1.grid(color = 'black', linestyle = '-', linewidth = 0.5)
            ax1.set_ylim(0,50)
            
            
            fig2, ax2 = plt.subplots(figsize=(18,12))                
            ax2.set_xlabel('Time (s)', fontsize = 14, fontweight='bold')
            ax2.set_ylabel('Motor_1_temp_calc_DMCM1__C', fontsize = 14, fontweight='bold')
            ax2.set_title('Motor Temperature [C]', fontsize = 18, fontweight = 'bold')
            ax2.grid(color = 'black', linestyle = '-', linewidth = 0.5)
            ax2.set_ylim(0,50)
            
            fig3, ax3 = plt.subplots(figsize=(18,12))                
            ax3.set_xlabel('Time (s)', fontsize = 14, fontweight='bold')
            ax3.set_ylabel('Motor_1_inverter_temp_sensor1_DMCM1__C', fontsize = 14, fontweight='bold')
            ax3.set_title('Motor Inverter Temperature [C]', fontsize = 18, fontweight = 'bold')
            ax3.grid(color = 'black', linestyle = '-', linewidth = 0.5)
            ax3.set_ylim(0,50)
            
            
            fig4, ax4 = plt.subplots(figsize=(18,12))                
            ax4.set_xlabel('Time (s)', fontsize = 14, fontweight='bold')
            ax4.set_ylabel('HVBatt_electronics_coolant_pump_command_HPCM2__per', fontsize = 14, fontweight='bold')
            ax4.set_title('Coolant Pump Command [%]', fontsize = 18, fontweight = 'bold')
            ax4.grid(color = 'black', linestyle = '-', linewidth = 0.5)
            ax4.set_ylim(0,60)
            
            fig5, ax5 = plt.subplots(figsize=(18,12))                
            ax5.set_xlabel('Time (s)', fontsize = 14, fontweight='bold')
            ax5.set_ylabel('HVBatt_coolant_temp_sensor_1_BECM__C', fontsize = 14, fontweight='bold')
            ax5.set_title('HV Battery Coolant Temperature Sensor [C]', fontsize = 18, fontweight = 'bold')
            ax5.grid(color = 'black', linestyle = '-', linewidth = 0.5)
            ax5.set_ylim(0,50)
            
            fig6, ax6 = plt.subplots(figsize=(18,12))                
            ax6.set_xlabel('Time (s)', fontsize = 14, fontweight='bold')
            ax6.set_ylabel('HVAC_AC_Compressor', fontsize = 14, fontweight='bold')
            ax6.set_title('AC compressor [W]', fontsize = 18, fontweight = 'bold')
            ax6.grid(color = 'black', linestyle = '-', linewidth = 0.5)
            # ax6.set_ylim(0,50)
            
            for index, logFile in enumerate(logFileList):
                self.startTime = self.config['Dyno']['StartTime_EcoDriving'][index] if fileLocation == 'eco-driving' else self.config['Dyno']['StartTime_SoloRun'][index]
                self.endTime = self.config['Dyno']['EndTime_EcoDriving'][index] if fileLocation == 'eco-driving' else self.config['Dyno']['EndTime_SoloRun'][index]
                
                logFileName = self.home_directory + '/Desktop/voices-log/dyno/' + fileLocation + '/' + logFile +'.csv'
                df = pd.read_csv(logFileName)
                
                startTimeIndex, endTimeIndex = self.getStartAndEndTimeIndex(df)
                startTime = df['Greyware_time__s'].iloc[startTimeIndex]
                
                for i, row in df.loc[startTimeIndex:endTimeIndex].iterrows():                
                    timeDataList.append(row['Greyware_time__s'] - startTime)
                    transmissionOilTempDataList.append(row['Trans_oil_temp_CAN__C'])
                    motorTemperatureDataList.append(row['Motor_1_temp_calc_DMCM1__C'])
                    motorInverterTemperatureDataList.append(row['Motor_1_inverter_temp_sensor1_DMCM1__C'])
                    coolantPumpCommandDataList.append(row['HVBatt_electronics_coolant_pump_command_HPCM2__per'])
                    hV_BattCoolantTempDataList.append(row['HVBatt_coolant_temp_sensor_1_BECM__C'])
                    aC_CompressorPowerDataList.append(row['HVAC_AC_Compressor_Current_unk_CAN'] * row['HVAC_AC_Compressor_Voltage_CAN__V'])
                                   
                color = colorList[roundNo]
                roundNo += 1
                
                if fileLocation == 'eco-driving':
                    ax1.plot(timeDataList, transmissionOilTempDataList, label = 'Group Run' + str(roundNo), c = color)
                    ax2.plot(timeDataList, motorTemperatureDataList, label = 'Group Run' + str(roundNo), c = color)
                    ax3.plot(timeDataList, motorInverterTemperatureDataList, label = 'Group Run' + str(roundNo), c = color)
                    ax4.plot(timeDataList, coolantPumpCommandDataList, label = 'Group Run' + str(roundNo), c = color)
                    ax5.plot(timeDataList, hV_BattCoolantTempDataList, label = 'Group Run' + str(roundNo), c = color)
                    ax6.plot(timeDataList, aC_CompressorPowerDataList, label = 'Group Run' + str(roundNo), c = color)
                    
                else:
                    ax1.plot(timeDataList, transmissionOilTempDataList, label = 'Solo Run' + str(roundNo), c = color)
                    ax2.plot(timeDataList, motorTemperatureDataList, label = 'Solo Run' + str(roundNo), c = color)
                    ax3.plot(timeDataList, motorInverterTemperatureDataList, label = 'Solo Run' + str(roundNo), c = color)
                    ax4.plot(timeDataList, coolantPumpCommandDataList, label = 'Solo Run' + str(roundNo), c = color)
                    ax5.plot(timeDataList, hV_BattCoolantTempDataList, label = 'Solo Run' + str(roundNo), c = color)
                    ax6.plot(timeDataList, aC_CompressorPowerDataList, label = 'Solo Run' + str(roundNo), c = color)
                    
                ax1.legend(loc = 'upper right', bbox_to_anchor = (1, 1))
                ax2.legend(loc = 'upper right', bbox_to_anchor = (1, 1))
                ax3.legend(loc = 'upper right', bbox_to_anchor = (1, 1))
                ax4.legend(loc = 'upper right', bbox_to_anchor = (1, 1))
                ax5.legend(loc = 'upper right', bbox_to_anchor = (1, 1))
                ax6.legend(loc = 'upper right', bbox_to_anchor = (1, 1))
                
                
                [li.clear() for li in [timeDataList, transmissionOilTempDataList, motorTemperatureDataList, motorInverterTemperatureDataList, coolantPumpCommandDataList, hV_BattCoolantTempDataList, aC_CompressorPowerDataList]]                
                
            
            fig1.savefig('diagram/' + fileLocation + '/' +'transmission-oil-temperature-plot.jpg', bbox_inches='tight', dpi=72) 
            fig2.savefig('diagram/' + fileLocation + '/' +'motor-temperature-plot.jpg', bbox_inches='tight', dpi=72)
            fig3.savefig('diagram/' + fileLocation + '/' +'motor-inverter-temperature-plot.jpg', bbox_inches='tight', dpi=72)                
            fig4.savefig('diagram/' + fileLocation + '/' +'coolant-pump-command-plot.jpg', bbox_inches='tight', dpi=72) 
            fig5.savefig('diagram/' + fileLocation + '/' +'hv-battery-coolant-temperature-plot.jpg', bbox_inches='tight', dpi=72)
            fig6.savefig('diagram/' + fileLocation + '/' +'ac-compressor-power-plot.jpg', bbox_inches='tight', dpi=72)                
            
            plt.close(fig1)
            plt.close(fig2)
            plt.close(fig3)
            plt.close(fig4)
            plt.close(fig5)
            plt.close(fig6)
                        
                
                
        if ecoDrivingLogFileList:
            plotDiagram(ecoDrivingLogFileList, 'eco-driving')
            
        if soloRunLogFileList:
            plotDiagram(soloRunLogFileList, 'solo-run')

           
        
    def getStartAndEndTimeIndex(self, dataframe):
        """
        method to get index for the start time and end time of the diagram
        """
        startTimeIndexList = dataframe.index[dataframe['Greyware_time__s'] == self.startTime].tolist()
        endTimeIndexList = dataframe.index[dataframe['Greyware_time__s'] == self.endTime].tolist()

        if not bool(startTimeIndexList):
            startTimeIndexList = dataframe.index[(dataframe['Greyware_time__s'] >= self.startTime) & (
                dataframe['Greyware_time__s'] < self.startTime+1)].tolist()
        if not bool(endTimeIndexList):
            endTimeIndexList = dataframe.index[(dataframe['Greyware_time__s'] > self.endTime) & (
                dataframe['Greyware_time__s'] < self.endTime+1)].tolist()


        startTimeIndex = startTimeIndexList[0] if startTimeIndexList else int(dataframe['index'].iloc[0])         
        endTimeIndex = endTimeIndexList[0] if endTimeIndexList else int(dataframe['index'].iloc[-1])


        return startTimeIndex, endTimeIndex
        
    def plotRelativeDistanceAndSpeedProfileIndividually(self):
        ecoDrivingLeadVehicleLogFileList, soloRunLeadVehicleLogFileList = ([] for i in range(2))
        time, relativeDistance, leadVehicleSpeed, hostVehicleSpeed, speedLimit = ([] for i in range(5)) 
        
        [ecoDrivingLeadVehicleLogFileList.append(fileDirectory) for fileDirectory in self.config["LeadVehicleLogFileDirectory"]['Eco-Driving']]
        [soloRunLeadVehicleLogFileList.append(fileDirectory) for fileDirectory in self.config["LeadVehicleLogFileDirectory"]['Solo-Run']]
               
        
        def plotDiagram(leadVehicleLogFileList, fileLocation):
            for index, leadVehicleLogFile in enumerate(leadVehicleLogFileList):
                logFileName = self.home_directory + '/Desktop/voices-log/log/' + fileLocation + '/' + leadVehicleLogFile +'.csv'
                df = pd.read_csv(logFileName)           
                startIndex = next((idx for idx, val in df['LeadVehicleSpeed'].items() if val > 0), None)
                endIndex = next((idx+1 for idx, val in reversed(list(df['HostVehicleSpeed'].items())) if val > 0), None)
                startTime = df.loc[startIndex,'TimeStamp']

                for idx in range(startIndex, endIndex + 1):
                    time.append(df.loc[idx,'TimeStamp'] - startTime)
                    relativeDistance.append(df.loc[idx,'RelativeDistance'])
                    leadVehicleSpeed.append((df.loc[idx,'LeadVehicleSpeed']) * MPH_TO_MPS)
                    hostVehicleSpeed.append(df.loc[idx,'HostVehicleSpeed'])
                    speedLimit.append(10* MPH_TO_MPS)
                    
                fig, axs = plt.subplots(1, 2, figsize=(12,8))  # 1 row, 2 columns
                axs[0].plot(time, relativeDistance, label='Inter-Vehicle Distance', c="orange")
                axs[0].set_xlabel('Time (s)', fontweight = 'bold')
                axs[0].set_ylabel('Distance (m)', fontweight = 'bold')
                axs[0].set_title('Inter-Vehicle Distance between ANL & UCLA', fontsize = 18, fontweight = 'bold')
                axs[0].legend(loc = 'upper right', bbox_to_anchor = (1, 1))
                
                axs[1].plot(time, leadVehicleSpeed, label='Lead Vehicle (UCLA) Speed', c="blue")
                axs[1].plot(time, hostVehicleSpeed, label='Ego Vehicle (ANL) Speed', c="green")
                axs[1].set_xlabel('Time (s)', fontweight = 'bold')
                axs[1].set_ylabel('Vehicle Speed (m/s)', fontweight = 'bold')
                axs[1].set_title('ANL & UCLA Speed Profile', fontsize = 18, fontweight = 'bold')
                axs[1].legend(loc = 'upper right', bbox_to_anchor = (1, 1))

                plt.subplots_adjust(wspace = 3.0)
                # Adjust layout to prevent overlap
                plt.tight_layout()
                plt.savefig('diagram/' + fileLocation + '/' + leadVehicleLogFile +'-plot.jpg', bbox_inches='tight', dpi=72)
                # plt.show()
                plt.close(fig)
                
                [li.clear() for li in [time, relativeDistance, leadVehicleSpeed, hostVehicleSpeed, speedLimit]]
            

        if ecoDrivingLeadVehicleLogFileList:
            plotDiagram(ecoDrivingLeadVehicleLogFileList, 'eco-driving')
            
            
        if soloRunLeadVehicleLogFileList:
            plotDiagram(soloRunLeadVehicleLogFileList, 'solo-run')
            
            
            
    def plotRelativeDistanceAndSpeedProfileJointly(self):
        ecoDrivingLeadVehicleLogFileList, soloRunLeadVehicleLogFileList = ([] for i in range(2))
        time, relativeDistance, leadVehicleSpeed, hostVehicleSpeed, speedLimit = ([] for i in range(5)) 
        
        [ecoDrivingLeadVehicleLogFileList.append(fileDirectory) for fileDirectory in self.config["LeadVehicleLogFileDirectory"]['Eco-Driving']]
        [soloRunLeadVehicleLogFileList.append(fileDirectory) for fileDirectory in self.config["LeadVehicleLogFileDirectory"]['Solo-Run']]
               
        
        def plotDiagram(leadVehicleLogFileList, fileLocation):
            for index, leadVehicleLogFile in enumerate(leadVehicleLogFileList):
                logFileName = self.home_directory + '/Desktop/voices-log/log/' + fileLocation + '/' + leadVehicleLogFile +'.csv'
                df = pd.read_csv(logFileName)           
                startIndex = next((idx for idx, val in df['LeadVehicleSpeed'].items() if val > 0), None)
                endIndex = next((idx+1 for idx, val in reversed(list(df['HostVehicleSpeed'].items())) if val > 0), None)
                startTime = df.loc[startIndex,'TimeStamp']

                for idx in range(startIndex, endIndex + 1):
                    time.append(df.loc[idx,'TimeStamp'] - startTime)
                    relativeDistance.append(df.loc[idx,'RelativeDistance'])
                    leadVehicleSpeed.append((df.loc[idx,'LeadVehicleSpeed']) * MPH_TO_MPS)
                    hostVehicleSpeed.append(df.loc[idx,'HostVehicleSpeed'])
                    speedLimit.append(10* MPH_TO_MPS)

                fig, ax1 = plt.subplots(figsize=(18,12))
                
                ax1.set_xlabel('Time (s)', fontsize = 14, fontweight='bold')
                ax1.plot(time, relativeDistance, label = 'Inter-Vehicle Distance', c = "orange")
                ax1.plot(time, leadVehicleSpeed, label = 'Lead Vehicle (UCLA) Speed', c = "blue")
                ax1.plot(time, hostVehicleSpeed, label = 'Ego Vehicle (ANL) Speed', c = "green")
                plt.grid(color = 'black', linestyle = '-', linewidth = 0.5)
                
                if fileLocation == 'eco-driving':      
                    ax1.set_title('ANL & UCLA Speed Profile Group Run' + str(index + 1), fontsize = 18, fontweight = 'bold')
                
                else: ax1.set_title('ANL & UCLA Speed Profile Solo Run' + str(index + 1), fontsize = 18, fontweight = 'bold')
                
                ax1.legend(loc = 'upper right', bbox_to_anchor = (1, 1))
                # plt.show()
                plt.savefig('diagram/' + fileLocation + '/' + leadVehicleLogFile +'-plot.jpg', bbox_inches='tight', dpi=72)                
                plt.close(fig)
                        
                [li.clear() for li in [time, relativeDistance, leadVehicleSpeed, hostVehicleSpeed, speedLimit]]
            

        if ecoDrivingLeadVehicleLogFileList:
            plotDiagram(ecoDrivingLeadVehicleLogFileList, 'eco-driving')
            
            
        if soloRunLeadVehicleLogFileList:
            plotDiagram(soloRunLeadVehicleLogFileList, 'solo-run')
            
            
    def plotEgoVehicleSpeedProfile(self):
        ecoDrivingLeadVehicleLogFileList, soloRunLeadVehicleLogFileList = ([] for i in range(2))
        # time, relativeDistance, leadVehicleSpeed, hostVehicleSpeed = ([] for i in range(4))
        
        [ecoDrivingLeadVehicleLogFileList.append(fileDirectory) for fileDirectory in self.config["LeadVehicleLogFileDirectory"]['Eco-Driving']]
        [soloRunLeadVehicleLogFileList.append(fileDirectory) for fileDirectory in self.config["LeadVehicleLogFileDirectory"]['Solo-Run']]
        
        
        def plotDiagram(leadVehicleLogFileList, fileLocation):
            timeNameList, relativeDistanceNameList, leadVehicleSpeedNameList, hostVehicleSpeedNameList = {}, {}, {}, {}
            
            for i in range(len(leadVehicleLogFileList)):
                # Accessing the dynamically created lists
                timeNameList[f"time{i}"], relativeDistanceNameList[f"relativeDistance{i}"], leadVehicleSpeedNameList[f"leadVehicleSpeed{i}"], hostVehicleSpeedNameList[f"hostVehicleSpeed{i}"] = ([] for i in range(4))
                
            for index, leadVehicleLogFile in enumerate(leadVehicleLogFileList):
                logFileName = self.home_directory + '/Desktop/voices-log/log/' + fileLocation + '/' + leadVehicleLogFile +'.csv'
                df = pd.read_csv(logFileName)           
                startIndex = next((idx for idx, val in df['LeadVehicleSpeed'].items() if val > 0), None)
                endIndex = next((idx+1 for idx, val in reversed(list(df['HostVehicleSpeed'].items())) if val > 0), None)
                startTime = df.loc[startIndex,'TimeStamp']
                
                time_var, relativeDistance_var, leadVehicleSpeed_var, hostVehicleSpeed_var  = f"time{index}", f"relativeDistance{index}", f"leadVehicleSpeed{index}", f"hostVehicleSpeed{index}"

                for idx in range(startIndex, endIndex + 1):
                    timeNameList[time_var].append(df.loc[idx,'TimeStamp'] - startTime)
                    relativeDistanceNameList[relativeDistance_var].append(df.loc[idx,'RelativeDistance'])
                    leadVehicleSpeedNameList[leadVehicleSpeed_var].append((df.loc[idx,'LeadVehicleSpeed']) * MPH_TO_MPS)
                    hostVehicleSpeedNameList[hostVehicleSpeed_var].append(df.loc[idx,'HostVehicleSpeed'])
            
            fig, ax1 = plt.subplots(figsize=(18,12))

            ax1.set_xlabel('Time (s)', fontsize = 14, fontweight='bold')
            ax1.set_ylabel('Speed (m/s)', fontsize = 14, fontweight='bold')
            colorList = ['green', 'blue', 'red', 'darkcyan', 'orange', 'navy', 'yellow']
            roundNo = 0
            
            for (key1, value1), (key2, value2) in zip(timeNameList.items(), hostVehicleSpeedNameList.items()):
                color = colorList[roundNo]
                roundNo += 1
                
                if fileLocation == 'eco-driving':
                    ax1.plot(value1, value2, label = 'Group Run' + str(roundNo), c = color)
                
                else: ax1.plot(value1, value2, label = 'Solo Run' + str(roundNo), c = color)
                

            ax1.set_title("ANL Speed Profile", fontsize = 18, fontweight='bold')
            fig.tight_layout()  # otherwise the right y-label is slightly clipped
            plt.grid(color = 'black', linestyle = '-', linewidth = 0.5)
            # ax1.legend(loc = 'upper right', bbox_to_anchor = (1.0, 1.22), prop={"size": 16})
            ax1.legend(loc = 'upper right', prop={"size": 16})
            # plt.show()
                
            plt.savefig('diagram/' + fileLocation + '/anl-speed-profile-plot.jpg', bbox_inches='tight', dpi=72)
            plt.close(fig)
        
        if ecoDrivingLeadVehicleLogFileList:
            plotDiagram(ecoDrivingLeadVehicleLogFileList, 'eco-driving')
        
        if soloRunLeadVehicleLogFileList:
            plotDiagram(soloRunLeadVehicleLogFileList, 'solo-run')    
            
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
    dataManager.plotEgoVehicleSpeedProfile()
    dataManager.analyzeDynoLog()