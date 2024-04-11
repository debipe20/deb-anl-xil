import pandas as pd
import matplotlib.pyplot as plt

class DataManager:
    def __init__(self, config) -> None:
        self.config = config
        self.dataFileName = config['FileName']
        self.ecoDrivingLeadVehicleLogFileList = []
        self.soloRunLeadVehicleLogFileList = []

        self.dataFrame = pd.read_csv(self.dataFileName)
        # print(self.dataFrame.head(5))

        # print(self.dataFrame.columns.tolist())

    def plotTransmissionOilTemperature(self):
        # transOilTempDataFrame = self.dataFrame['DAQ_Time[s]','Trans_oil_temp_CAN__C']
        X = self.dataFrame['DAQ_Time[s]']
        Y = self.dataFrame['Trans_oil_temp_CAN__C']

        plt.scatter(X,Y)
        plt.show()

    
    def plotMotorTemperature(self):
        
        X = self.dataFrame['DAQ_Time[s]']
        Y = self.dataFrame['Motor_1_temp_calc_DMCM1__C']

        plt.scatter(X,Y)

    def plotMotorInverterTemperature(self):
        
        X = self.dataFrame['DAQ_Time[s]']
        Y = self.dataFrame['Motor_1_inverter_temp_sensor1_DMCM1__C']

        plt.scatter(X,Y)

    def plotCoolantPumpCommand(self):
        
        X = self.dataFrame['DAQ_Time[s]']
        Y = self.dataFrame['HVBatt_electronics_coolant_pump_command_HPCM2__per']

        plt.scatter(X,Y)

    def plotHV_BattCoolantTemp(self):
        
        X = self.dataFrame['DAQ_Time[s]']
        Y = self.dataFrame['HVBatt_coolant_temp_sensor_1_BECM__C']

        plt.scatter(X,Y)

    def plotAC_CompressorPower(self):
        
        X = self.dataFrame['DAQ_Time[s]']
        Y = self.dataFrame['HVAC_AC_Compressor_Current_unk_CAN'] * self.dataFileName['HVAC_AC_Compressor_Voltage_CAN__V']

        plt.scatter(X,Y)
        
    def plotRelativeDistanceAndSpeedProfile(self):
        
        [self.ecoDrivingLeadVehicleLogFileList.append(fileDirectory) for fileDirectory in self.config["LeadVehicleLogFileDirectory"]['Eco-Driving']]
        [self.soloRunLeadVehicleLogFileList.append(fileDirectory) for fileDirectory in self.config["LeadVehicleLogFileDirectory"]['Solo-Run']]
        time, relativeDistance, leadVehicleSpeed, hostVehicleSpeed, speedLimit = ([] for i in range(5))        
        
        def plotDiagram(leadVehicleLogFileList, fileLocation):
            for index, leadVehicleLogFile in enumerate(leadVehicleLogFileList):

                logFileName = '/nojournal/bin/log/' + fileLocation + '/' + leadVehicleLogFile +'.csv'
                df = pd.read_csv(logFileName)           
                startIndex = next((idx for idx, val in df['LeadVehicleSpeed'].items() if val > 0), None)
                endIndex = next((idx+1 for idx, val in reversed(list(df['HostVehicleSpeed'].items())) if val > 0), None)
                startTime = df.loc[startIndex,'TimeStamp']
                # print("Start Index is: ", startIndex)
                # print("End Index is: ", endIndex, "\n")
                for idx in range(startIndex, endIndex + 1):
                    time.append(df.loc[idx,'TimeStamp'] - startTime)
                    relativeDistance.append(df.loc[idx,'RelativeDistance'])
                    leadVehicleSpeed.append((df.loc[idx,'LeadVehicleSpeed']) * 0.44704)
                    hostVehicleSpeed.append(df.loc[idx,'HostVehicleSpeed'])
                    speedLimit.append(10* 0.44704)
                    
                fig, axs = plt.subplots(1, 2, figsize=(12,8))  # 1 row, 2 columns
                axs[0].plot(time, relativeDistance, label='Inter-Vehicle Distance', c="orange")
                axs[0].set_xlabel('Time (s)', fontweight = 'bold')
                axs[0].set_ylabel('Distance (m)', fontweight = 'bold')
                axs[0].set_title('Inter-Vehicle Distance between ANL & UCLA', fontsize = 14, fontweight = 'bold')
                axs[0].legend(loc='upper right', bbox_to_anchor=(1, 1))
                # axs[0].grid(color='black', linestyle='-', linewidth=0.5, axis='y')
                
                # axs[1].plot(time, speedLimit, label='SpeedLimit', marker=".", c="red",)
                axs[1].plot(time, leadVehicleSpeed, label='Lead Vehicle (UCLA) Speed', c="blue")
                axs[1].plot(time, hostVehicleSpeed, label='Ego Vehicle (ANL) Speed', c="green")
                axs[1].set_xlabel('Time (s)', fontweight = 'bold')
                axs[1].set_ylabel('Vehicle Speed (m/s)', fontweight = 'bold')
                axs[1].set_title('ANL & UCLA Speed Profile', fontsize = 14, fontweight = 'bold')
                axs[1].legend(loc='upper right', bbox_to_anchor=(1, 1))
                # axs[1].grid(color='black', linestyle='-', linewidth=0.5, axis='y')
                
                plt.subplots_adjust(wspace = 3.0)
                # Adjust layout to prevent overlap
                plt.tight_layout()
                plt.savefig('diagram/' + fileLocation + '/' + leadVehicleLogFile +'-plot.jpg', bbox_inches='tight', dpi=72)
                # plt.show()
                
                [li.clear() for li in [time, relativeDistance, leadVehicleSpeed, hostVehicleSpeed, speedLimit]]
            

        if self.ecoDrivingLeadVehicleLogFileList:
            plotDiagram(self.ecoDrivingLeadVehicleLogFileList, 'eco-driving')
            
        if self.soloRunLeadVehicleLogFileList:
            plotDiagram(self.soloRunLeadVehicleLogFileList, 'solo-run')