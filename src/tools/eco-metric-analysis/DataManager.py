import pandas as pd
import matplotlib.pyplot as plt

class DataManager:
    def __init__(self, config) -> None:
        self.config = config
        self.dataFileName = config['FileName']

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
