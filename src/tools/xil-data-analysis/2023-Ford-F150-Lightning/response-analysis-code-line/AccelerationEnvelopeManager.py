import pandas as pd
import numpy as np
import os
import platform
from nptdms import TdmsFile
from PlotManager import PlotManager

g_value = 9.80665

class AccelerationEnvelopeManager:
    def __init__(self, config):
        self.config = config
        self.acc_override_test_file_list = self.config['AccOverrideTestFileList']
        self.stock_acc_test_file_list = self.config['StockAccTestFileList']
        self.acc_override_acceleration = []
        self.acc_override_speed_mps = []
        self.acc_override_speed_mph = []
        self.stock_acc_acceleration = []
        self.stock_acc_speed_mps = []
        self.stock_acc_speed_mph = []

        self.plot_manager = PlotManager(config)

    def get_data_directory(self):
        """
            Method to get the Data directory irrespective of operating system
        """
        current_os = platform.system()

        if current_os == "Linux":
            data_directory = os.path.join(os.path.expanduser("~"), "Downloads", "2023-Ford-F150-Lightning")
        elif current_os == "Windows":
            data_directory = os.path.join("C:\\", "Users", "ddas", "Documents", "Data", "2023-Ford-F150-Lightning")
        else:
            raise OSError(f"Unsupported operating system: {current_os}")
        
        return data_directory

    def get_groups_channels(self):

        self.group_data = self.tdms_file["Data"]

        self.time_channel = self.group_data['Time[s]']
        self.speed_channel_mph = self.group_data['Dyno_Spd[mph]']

        self.time_data = self.time_channel[:]
        self.speed_data_mph = self.speed_channel_mph[:]
        self.speed_data_mps = self.speed_channel_mph[:] * 0.44704

    def get_acc_data(self):
        """
            Extracts speed and acceleration data
        """
        calculated_accel = 0
        speed_mph = []
        speed_mps = []
        acceleration_g = []

        for i in range(1, len(self.speed_data_mps)):
            previous_calculated_accel = calculated_accel
            calculated_accel = (self.speed_data_mps[i] - self.speed_data_mps[i-1]) / (self.time_data[i] - self.time_data[i-1])
            
            if (abs(calculated_accel-previous_calculated_accel) >= 0.1):
                speed_mph.append(self.speed_channel_mph[i])
                speed_mps.append(self.speed_data_mps[i])
                acceleration_g.append(calculated_accel / g_value)

        return speed_mph, speed_mps, acceleration_g

    def manage_test_data(self):
        data = pd.DataFrame()
        data_directory = self.get_data_directory()
        
        for test_file_name in self.acc_override_test_file_list:
            tdms_file_path = os.path.join(data_directory, test_file_name)

            # Check if the file exists
            if not os.path.isfile(tdms_file_path):
                raise FileNotFoundError(f"No such file: {tdms_file_path}")
            
            self.tdms_file = TdmsFile.read(tdms_file_path)
            self.get_groups_channels()
            speed_mph, speed_mps, acceleration_g = self.get_acc_data()
            self.acc_override_speed_mph.extend(speed_mph)
            self.acc_override_speed_mps.extend(speed_mps)
            self.acc_override_acceleration.extend(acceleration_g)

        for test_file_name in self.stock_acc_test_file_list:
            tdms_file_path = os.path.join(data_directory, test_file_name)

            # Check if the file exists
            if not os.path.isfile(tdms_file_path):
                raise FileNotFoundError(f"No such file: {tdms_file_path}")
            
            self.tdms_file = TdmsFile.read(tdms_file_path)
            self.get_groups_channels()
            speed_mph, speed_mps, acceleration_g = self.get_acc_data()
            self.stock_acc_speed_mph.extend(speed_mph)
            self.stock_acc_speed_mps.extend(speed_mps)
            self.stock_acc_acceleration.extend(acceleration_g)

        self.plot_manager.generate_vehicle_envelope_scatter_plot(self.acc_override_speed_mph, self.acc_override_acceleration, self.stock_acc_speed_mph, self.stock_acc_acceleration)



        

'''##############################################
                   Unit testing
##############################################'''
if __name__ == "__main__":
    import json
    configFile = open("config-files/configuration.json", 'r')
    config = (json.load(configFile))
    configFile.close()
    acceleration_envelope_manager = AccelerationEnvelopeManager(config)
    acceleration_envelope_manager.manage_test_data()