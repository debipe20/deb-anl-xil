import pandas as pd
import os
import platform
import matplotlib.pyplot as plt
from nptdms import TdmsFile


class AccelerationEnvelopeManager:
    def __init__(self, config):
        self.config = config
        self.vehicle_name = self.config['VehicleName']
        self.speed_unit_conversion = self.config['SpeedUnitConversion']
        self.acc_override_test_file_list = self.config['AccOverrideTestFileList']
        self.stock_acc_test_file_list = self.config['StockAccTestFileList']
        self.title_status = self.config['SetTitle']
        self.plot_save = self.config['PlotSave']
        self.acc_override_acceleration, self.acc_override_speed_mps, self.acc_override_speed_mph = ([] for i in range(3))
        self.stock_acc_acceleration, self.stock_acc_speed_mps, self.stock_acc_speed_mph = ([] for i in range(3))
        self.g_value = 9.80665

    def get_data_directory(self):
        """
            Method to get the Data directory irrespective of operating system
        """
        current_os = platform.system()

        if current_os == "Linux":
            data_directory = os.path.join(os.path.expanduser("~"), "Downloads", self.vehicle_name)
        elif current_os == "Windows":
            data_directory = os.path.join("C:\\", "Users", "ddas", "Documents", "Data", self.vehicle_name)
        else:
            raise OSError(f"Unsupported operating system: {current_os}")
        
        return data_directory

    def get_groups_channels(self):

        self.group_data = self.tdms_file["Data"]

        self.time_channel = self.group_data['Time[s]']
        self.speed_channel_mph = self.group_data['Dyno_Spd[mph]']

        self.time_data = self.time_channel[:]
        self.speed_data_mph = self.speed_channel_mph[:]
        self.speed_data_mps = self.speed_channel_mph[:] * self.speed_unit_conversion

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
                acceleration_g.append(calculated_accel / self.g_value)

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

        self.generate_vehicle_envelope_scatter_plot(self.acc_override_speed_mph, self.acc_override_acceleration, self.stock_acc_speed_mph, self.stock_acc_acceleration)


    def generate_vehicle_envelope_scatter_plot(self, acc_override_speed_mph, acc_override_acceleration, stock_acc_speed_mph, stock_acc_acceleration):
        """
        Generates a scatter plot for acceleration vs speed in mps, with additional overlay for ACC override data.
        """
        if not acc_override_acceleration or not acc_override_speed_mph:
            print("No data available for plotting. Please ensure data is processed first.")
            return

        plt.figure(figsize=(12, 8))
        
        # Plot the Stock ACC  data
        if stock_acc_speed_mph and stock_acc_acceleration:
            plt.scatter(stock_acc_speed_mph, stock_acc_acceleration, alpha=0.7, label="ACC Override OFF", color="orange", s=10)
        
        # Plot the main vehicle envelope data
        plt.scatter(acc_override_speed_mph, acc_override_acceleration, alpha=0.7, label="ACC Override ON", color="blue", s=10)
                
        # Add labels, title, and legend
        plt.title(f"{self.vehicle_name}_Acceleration Envelope", fontsize=16, weight="bold")
        plt.xlabel("Speed [mph]", fontsize=14)
        plt.ylabel("Acceleration [g]", fontsize=14)
        plt.legend(loc="upper right", fontsize=12)
        
        # Grid and formatting
        plt.grid(True, linestyle="--", alpha=0.6)

        # Save or show the plot
        if self.plot_save:
            file_directory = f"figure/{self.vehicle_name}_acceleration-envelop.jpg"

            plt.savefig(file_directory, dpi=300)
            print("saved file")
        else:
            plt.show()

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