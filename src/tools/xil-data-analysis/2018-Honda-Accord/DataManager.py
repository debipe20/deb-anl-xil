import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from nptdms import TdmsFile
from PlotManager import PlotManager

class DataManager:
    def __init__(self, config):
        self.config = config
        self.platform = self.config['Platform']
        self.window_size = self.config['WindowSize']
        self.end_data_to_discard = self.config['NoOfEndDataDiscard']
        self.plot_manager = PlotManager(config)

    def get_files(self):
        if self.platform == "Linux":
            filePath = os.path.expanduser("~") + "/Downloads/2018-Honda-Accord/62409002 2018 Honda Accord Blank 1Bag 3600/"
            

        else: filePath = "C:\\Users\ddas\\Documents\\Data\\2018-Honda-Accord\\62409002 2018 Honda Accord Blank 1Bag 3600\\"
        self.tdms_file = TdmsFile.read(filePath + "62409002 Test Data.tdms")

    def get_groups_channels_name(self):
        # Get all groups in the TDMS file
        groups = self.tdms_file.groups()

        # Iterate over groups and print their names and channels
        for group in groups:
            print(f"Group: {group.name}")

            # Get all channels in the current group
            channels = group.channels()
            
            # Iterate over channels in the group and print their names
            for channel in channels:
                print(f"  Channel: {channel.name}")

    def get_groups_channels(self):

        self.group_data = self.tdms_file["Data"]
        self.group_vspy = self.tdms_file["Vspy"]

        self.time_channel = self.group_vspy['Time[s]']
        self.speed_channel = self.group_vspy['CAR_SPEED (Value [kph])']
        self.accel_channel = self.group_vspy['ACCEL_COMMAND (Value [m/s2])']

    def get_data_from_channel(self):
   
        self.time_data = self.time_channel[:-self.end_data_to_discard]
        self.speed_data_mph = self.speed_channel[:-self.end_data_to_discard]* 0.621371
        self.speed_data_mps = self.speed_channel[:-self.end_data_to_discard]* 0.277778
        self.accel_data = self.accel_channel[:-self.end_data_to_discard]

    # def calculate_acceleration_achv(self):
        
    #     # Initialize an array of the same shape as B with zeros
    #     self.accel_achv = np.zeros_like(self.speed_data_mps, dtype=float)

    #     # Variable to check for two consecutive non-zero elements
    #     found_consecutive_non_zero = False
    #     self.accel_achv[0] = self.accel_data[0]

    #     # Loop to calculate C based on the given conditions
    #     for i in range(1, len(self.speed_data_mps)):

    #         if self.speed_data_mps[i] > 0 and self.speed_data_mps[i-1] > 0:
    #             found_consecutive_non_zero = True

    #         else: found_consecutive_non_zero = False

    #         if found_consecutive_non_zero:
    #             self.accel_achv[i] = (self.speed_data_mps[i] - self.speed_data_mps[i-1]) / (self.time_data[i] - self.time_data[i-1])

    #         else: self.accel_achv[i] = self.accel_data[i] 

    #     self.accel_achv = np.convolve(self.accel_achv, np.ones(self.window_size) / self.window_size, mode='same')

    def calculate_acceleration_achv(self):
        # Initialize an array of the same shape as speed_data_mps with zeros
        self.accel_achv = np.zeros_like(self.speed_data_mps, dtype=float)

        # Variable to check for two consecutive non-zero elements
        found_consecutive_non_zero = False
        self.accel_achv[0] = self.accel_data[0]

        # A list to store the last 'window_size' acceleration values for averaging
        window = []
        self.window_size = max(self.window_size, 1)  # Ensure window size is at least 1

        # Loop to calculate acceleration with smoothing
        for i in range(1, len(self.speed_data_mps)):
            # Check for two consecutive non-zero speeds
            if self.speed_data_mps[i] > 0 and self.speed_data_mps[i - 1] > 0:
                found_consecutive_non_zero = True
            else:
                found_consecutive_non_zero = False

            # Calculate acceleration if consecutive non-zero speeds are found
            if found_consecutive_non_zero:
                accel_value = (self.speed_data_mps[i] - self.speed_data_mps[i - 1]) / (self.time_data[i] - self.time_data[i - 1])
                # Update the smoothing window
                window.append(accel_value)
                if len(window) > self.window_size:
                    window.pop(0)  # Remove the oldest value to keep the window size consistent

                # Calculate the average of the current window and assign it to accel_achv
                self.accel_achv[i] = sum(window) / len(window)
            
            elif not found_consecutive_non_zero and self.accel_data[i] > 0:
                self.accel_achv[i] = self.accel_achv[i-1] 

            else:
                self.accel_achv[i] = self.accel_data[i]

            

        # For the first few elements (less than window_size), no smoothing is applied.
        # They can be directly assigned from the original acceleration values or left as zero.



    def save_data_to_csv(self):

        data = pd.DataFrame({
            "Time [s]": self.time_data,
            "Speed [mph]": self.speed_data_mph,
            "Speed [mps]": self.speed_data_mps,
            "Acceleration Command [m/s²]": self.accel_data,
            "Calculated Acceleration [m/s²]": self.accel_achv
        })

        # Save to CSV
        csv_file_path = "output_data.csv"
        # result.to_csv(csv_file_path, index=False)
        data.to_csv(csv_file_path, index=False)
        print(f"Data saved to {csv_file_path}")

    def generate_plots(self):
        self.get_files()
        self.get_groups_channels()
        self.get_data_from_channel()
        # # self.get_groups_channels_name()
        self.calculate_acceleration_achv()
        self.save_data_to_csv()
        self.plot_manager.plot_primary_yaxis(self.time_data, self.speed_data_mph, "Time [s]", "Speed [mph]", "Time vs Speed Plot", "0-20_mph_time_vs_speed")
        self.plot_manager.plot_primary_secondary_yaxis(self.time_data, self.speed_data_mph, self.accel_data, "Time [s]", "Speed [mph]", "Acceleration [m/s²]", "Time vs Speed and Acceleration Plot", "0-20_mph_time_vs_speed_Accel")      
        self.plot_manager.plot_primary_secondary_yaxis(self.time_data, self.speed_data_mph, self.accel_achv, "Time [s]", "Speed [mph]", "Acceleration [m/s²]", "Time vs Speed and Acceleration Plot", "0-20_mph_time_vs_speed_Accel_achv")
        self.plot_manager.plot_twice_secondary_yaxis(self.time_data, self.speed_data_mph, self.accel_data, self.accel_achv, "Time [s]", "Speed [mph]", "Acceleration [m/s²]",  "Time vs Speed and Acceleration Plot", "0-20_mph_time_vs_speed_Accel_rqst_achv")

'''##############################################
                   Unit testing
##############################################'''
if __name__ == "__main__":
    import json
    configFile = open("config-files/configuration.json", 'r')
    config = (json.load(configFile))
    configFile.close()
    data_manager = DataManager(config)
    data_manager.generate_plots()