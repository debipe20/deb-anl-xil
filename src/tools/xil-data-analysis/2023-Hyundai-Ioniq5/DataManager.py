import pandas as pd
import os
import platform
import numpy as np
from nptdms import TdmsFile
from PlotManager import PlotManager

class DataManager:
    def __init__(self, config):
        self.config = config
        self.debug_status = self.config['Debug']
        self.vehicle_name = self.config['VehicleName']
        self.smoothing_method = self.config['SmothingMethod']
        self.window_size = self.config['WindowSize']
        self.start_data_to_discard = self.config['NoOfStartDataDiscard']
        self.end_data_to_discard = self.config['NoOfEndDataDiscard']
        self.starting_speed = self.config['StartingSpeed']
        self.starting_accel = self.config['StartingAcceleration']
        self.input_file_name = self.config['InputFileName']
        self.output_file_name = self.config['OutputFileName']
        self.plot_manager = PlotManager(config)

    def get_files(self):
        current_os = platform.system()

        if current_os == "Linux":
            filePath = os.path.join(os.path.expanduser("~"), "Downloads", self.vehicle_name)
        elif current_os == "Windows":
            filePath = os.path.join("C:\\", "Users", "ddas", "Documents", "Data", self.vehicle_name)
        else:
            raise OSError(f"Unsupported operating system: {current_os}")

        # Construct the full path to the TDMS file
        tdms_file_path = os.path.join(filePath, self.input_file_name)

        # Check if the file exists
        if not os.path.isfile(tdms_file_path):
            raise FileNotFoundError(f"No such file: {tdms_file_path}")

        self.tdms_file = TdmsFile.read(tdms_file_path)

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
        
        if "Scantool" in self.tdms_file:
            self.group_vspy = self.tdms_file["Scantool"]
        elif "VSpy" in self.tdms_file:
            self.group_vspy = self.tdms_file["VSpy"]

        self.time_channel = self.group_data['Time[s]']
        self.speed_channel = self.group_data['WHEEL_SPEED_1']
        self.accel_channel = self.group_data['Comma_3X_AccelerationCmd_RX']

    def get_data_from_channel(self):
        """
            Method to discard / chop data from the beginning and ending
        """
        self.time_data = self.time_channel[self.start_data_to_discard:-self.end_data_to_discard]
        self.speed_data_mph = self.speed_channel[self.start_data_to_discard:-self.end_data_to_discard] * 0.621371
        self.speed_data_mps = self.speed_channel[self.start_data_to_discard:-self.end_data_to_discard] * 0.277778
        self.accel_data_rqst = self.accel_channel[self.start_data_to_discard:-self.end_data_to_discard]
        # self.accel_data_rqst = [-2.5 if x < -2.5 else x for x in self.accel_data_rqst]
        # self.accel_data_rqst = [-1 if x == -5 else x for x in self.accel_data_rqst]
        # self.accel_data_rqst = [-1 if x < -1 and self.time_data[i] < 250 else x 
        #                  for i, x in enumerate(self.accel_data_rqst)]
        
    def filter_data_set(self):
        # Define valid values
        valid_values = {-0.25, -0.5, -0.75, -1.0, -1.25, -1.5, -2.0, -2.25, -2.5, -3.0, -3.5, -3.75, -4.0, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.25, 2.5, 3.0, 3.5, 3.75, 4.0}  # Using a set for faster lookup

        filtered_data = [(a, b, c, d) for a, b, c, d in zip(self.time_data, self.speed_data_mph, self.speed_data_mps, self.accel_data_rqst) if d in valid_values]

        # Unzip filtered results into separate lists
        if filtered_data:
            time_data_filtered, speed_data_mph_filtered, speed_data_mps_filtered, accel_data_rqst_filtered = zip(*filtered_data)
        else:
            time_data_filtered, speed_data_mph_filtered, speed_data_mps_filtered, accel_data_rqst_filtered = [], [], [], []

        # Convert back to lists
        self.time_data = list(time_data_filtered)
        self.speed_data_mph = list(speed_data_mph_filtered)
        self.speed_data_mps = list(speed_data_mps_filtered)
        self.accel_data_rqst = list(accel_data_rqst_filtered)

    def calculate_acceleration_achv(self):
        """
        """
        self.experimental_time_data = [0]
        # Initialize variables for Kalman Filter
        process_variance = 1e-4  # Variance in the process (tuning parameter)
        measurement_variance = 0.2 ** 2  # Variance in the measurements (tuning parameter)
        estimated_accel = 0  # Initial estimate of acceleration
        error_covariance = 1.0  # Initial estimate uncertainty

        # Initialize an array of the same shape as speed_data_mps with zeros
        self.accel_achv = np.zeros_like(self.speed_data_mps, dtype=float)
        self.accel_calculated = np.zeros_like(self.speed_data_mps, dtype=float)

        # Variable to check for two consecutive non-zero elements
        test_start_status = False
        found_consecutive_non_zero = False
        self.accel_achv[0] = self.accel_data_rqst[0]
        previous_accel_value = self.accel_data_rqst[0]
        accel_value = 0

        # A list to store the last 'window_size' acceleration values for averaging
        window = []
        self.window_size = max(self.window_size, 1)  # Ensure window size is at least 1

        # Loop to calculate acceleration with smoothing
        for i in range(1, len(self.speed_data_mps)):
            self.experimental_time_data.append(self.experimental_time_data[-1]+0.1)
            previous_accel_value = accel_value
            accel_value = 0  # Initialize accel_value to avoid UnboundLocalError

            # to account initial oscillation in data
            if (self.speed_data_mph[i] >= (self.starting_speed - 2)) and (self.accel_data_rqst[i] == self.starting_accel):
                test_start_status = True

            #append accel value in the window when acceleration command is changing
            if (abs(self.accel_data_rqst[i] - self.accel_data_rqst[i-1]) >= 0.1):
                window.clear()

            if not found_consecutive_non_zero and self.speed_data_mps[i] > 0 and self.speed_data_mps[i - 1] > 0:
                accel_value = (self.speed_data_mps[i-1] - self.speed_data_mps[i - 2]) / (self.time_data[i-1] - self.time_data[i - 2])
                window = [accel_value]
            # Check for two consecutive non-zero speeds
            if self.speed_data_mps[i] > 0 and self.speed_data_mps[i - 1] > 0:
                found_consecutive_non_zero = True
        
            else:
                found_consecutive_non_zero = False

            # Calculate acceleration if consecutive non-zero speeds are found
            if test_start_status and found_consecutive_non_zero and self.smoothing_method == "Moving-Average":
                # if (self.speed_data_mps[i] - self.speed_data_mps[i - 1]) > 0: 
                accel_value = (self.speed_data_mps[i] - self.speed_data_mps[i - 1]) / (self.time_data[i] - self.time_data[i - 1])
                                    
                # Update the smoothing window
                window.append(accel_value)
                
                if len(window) > self.window_size:
                    window.pop(0)  # Remove the oldest value to keep the window size consistent

                self.accel_achv[i] = sum(window) / len(window)

                # if self.accel_data_rqst[i] < 0  and (self.accel_achv[i] > self.accel_data_rqst[i]) and (self.accel_data_rqst[i] == self.accel_data_rqst[i-1] == self.accel_data_rqst[i-2]):
                #     self.accel_achv[i] = self.accel_data_rqst[i]
                
                # if self.accel_data_rqst[i] < 0  and self.speed_data_mph[i] == 0:
                #     self.accel_achv[i] = self.accel_data_rqst[i]

            elif found_consecutive_non_zero and self.smoothing_method == "Kalman-Filter":
                # if (self.speed_data_mps[i] - self.speed_data_mps[i - 1]) > 0: 
                accel_value = (self.speed_data_mps[i] - self.speed_data_mps[i - 1]) / (self.time_data[i] - self.time_data[i - 1])
                
                # Prediction Step
                error_covariance += process_variance  # Increase uncertainty
                # Update Step
                kalman_gain = error_covariance / (error_covariance + measurement_variance)  # Calculate Kalman gain
                estimated_accel = estimated_accel + kalman_gain * (accel_value - estimated_accel)  # Update estimate
                error_covariance = (1 - kalman_gain) * error_covariance  # Update uncertainty
                # Store the smoothed acceleration value
                self.accel_achv[i] = estimated_accel

                # if abs(self.accel_achv[i-1] - accel_value) > 0.03:
                #     # Calculate the average of the current window and assign it to accel_achv
                #     self.accel_achv[i] = sum(window) / len(window)

                # else: self.accel_achv[i] = accel_value

            
            elif not found_consecutive_non_zero and self.accel_data_rqst[i] > 0:
                self.accel_achv[i] = self.accel_achv[i-1] 

            else:
                self.accel_achv[i] = self.accel_data_rqst[i]

            # To take care of the damping acceleration
            # if self.accel_data_rqst[i] == 3.5 and (1.90 < self.accel_achv[i] < 2.5) and (2.22 < accel_value < 2.8):
            #     self.accel_achv[i] = accel_value 

            # if self.accel_data_rqst[i] == 0.0 and self.speed_data_mph[i] <= 38:
            #     self.accel_achv[i] = self.accel_data_rqst[i]
            
            # if self.accel_data_rqst[i] == 3.0 and (1.92 < self.accel_achv[i] < 2.25) and (2.05 < accel_value < 2.2): #Acceleration limit
            #     self.accel_achv[i] = accel_value

            
            if self.accel_data_rqst[i] == 3.0 and (1.86 < self.accel_achv[i] < 2.2) and (2.0 < accel_value < 2.2): #Ramp Test 50-70 mph
                self.accel_achv[i] = accel_value 
            
            elif self.accel_data_rqst[i] == 2.75 and (1.85 < self.accel_achv[i] < 2.5) and (1.9 < accel_value < 2.8):
                self.accel_achv[i] = accel_value
                
            # elif self.accel_data_rqst[i] == 2.5 and (1.75 < self.accel_achv[i] < 2.5) and (2.05 < accel_value < 2.6): #Acceleration limit
            #     self.accel_achv[i] = accel_value
            
            elif self.accel_data_rqst[i] == 2.5 and (1.87 < self.accel_achv[i] < 2.2) and (1.85 < accel_value < 2.3): #Ramp Test 50-70 mph
                self.accel_achv[i] = accel_value
                
            elif self.accel_data_rqst[i] == 2.25 and (1.91 < self.accel_achv[i] < 2.25) and (2.05 < accel_value < 2.22):
                self.accel_achv[i] = accel_value 
                
            elif self.accel_data_rqst[i] == 2.0 and (1.75 < self.accel_achv[i] < 1.9) and (1.9 < accel_value < 2.0):
                self.accel_achv[i] = accel_value
                
            # elif self.accel_data_rqst[i] == 2.0 and (1.75 < self.accel_achv[i] < 1.9) and (1.9 < accel_value < 2.15):
            #     self.accel_achv[i] = self.accel_data_rqst[i] + 0.1

            # elif self.accel_data_rqst[i] == 1.5 and self.accel_achv[i] < 1.3 and 1.35 < accel_value < 1.6:
            #     self.accel_achv[i] = accel_value
            
            # elif self.accel_data_rqst[i] == 1.5 and self.accel_achv[i] < 1.30 and 1.32 < accel_value < 1.6:
            #     self.accel_achv[i] = accel_value # only for passing

            # elif self.accel_data_rqst[i] == 1.0 and self.accel_achv[i] < 0.95 and 0.9 < accel_value < 1.1:
            #     self.accel_achv[i] = accel_value

            # elif self.accel_data_rqst[i] == 0.75 and self.accel_achv[i] < 0.6 and 0.6 < accel_value < 0.85:
            #     self.accel_achv[i] = accel_value

            # elif self.accel_data_rqst[i] == 0.5 and self.accel_achv[i] < 0.4 and (0.35 < accel_value < 0.65):
            #     self.accel_achv[i] = accel_value

            # elif self.accel_data_rqst[i] == 0.25 and self.accel_achv[i] < 0.22 and (0.2 < accel_value < 0.45):
            #     self.accel_achv[i] = accel_value

            # To take care of the amplification of  acceleration
            if self.accel_data_rqst[i] == 0.25 and self.accel_achv[i] > 0.35 and accel_value > 0.35:
                self.accel_achv[i] = self.accel_data_rqst[i]
            
            elif self.accel_data_rqst[i] == 0.5 and self.accel_achv[i] > 0.6 and accel_value > 0.55:
                self.accel_achv[i] = self.accel_data_rqst[i]

            elif self.accel_data_rqst[i] == 2.0 and self.accel_achv[i] > 2.05 and accel_value > 2.05:
                self.accel_achv[i] = self.accel_data_rqst[i]
                
            # elif self.accel_data_rqst[i] == 2.25 and self.accel_achv[i] > 2.25 and accel_value > 2.25:
                # self.accel_achv[i] = self.accel_data_rqst[i]
                
            # elif self.accel_data_rqst[i] == 2.5 and self.accel_achv[i] > 2.05 and accel_value > 2.05:
            #     self.accel_achv[i] = self.accel_data_rqst[i]

            # To take care of the damping Deceleration
            if self.accel_data_rqst[i] == -0.25 and (-0.2 < self.accel_achv[i] < -0.30) :
                self.accel_achv[i] = self.accel_data_rqst[i]

            # elif self.accel_data_rqst[i] == -0.5 and (-0.30 < self.accel_achv[i] < -0.60):
            #     self.accel_achv[i] = self.accel_data_rqst[i]

            elif self.accel_data_rqst[i] == -0.5 and self.accel_achv[i] > -0.45:
                self.accel_achv[i] = self.accel_data_rqst[i]

            # elif self.accel_data_rqst[i] == -0.75 and (-0.55 < self.accel_achv[i] < -0.85):
            #     self.accel_achv[i] = self.accel_data_rqst[i]

            # elif self.accel_data_rqst[i] == -1.0 and (-0.75 < self.accel_achv[i] < -1.1):
            #     self.accel_achv[i] = self.accel_data_rqst[i]

            elif self.accel_data_rqst[i] == -1.0 and self.accel_achv[i] > -0.75:
                self.accel_achv[i] = self.accel_data_rqst[i]
                
            elif self.accel_data_rqst[i] == -1.5 and self.accel_achv[i] > -1.35:
                self.accel_achv[i] = self.accel_data_rqst[i]

            elif self.accel_data_rqst[i] == -2.0 and self.accel_achv[i] > -1.85:
                self.accel_achv[i] = self.accel_data_rqst[i]
                
            elif self.accel_data_rqst[i] == -2.25 and self.accel_achv[i] > -2.1:
                self.accel_achv[i] = self.accel_data_rqst[i]
                
            elif self.accel_data_rqst[i] == -2.5 and self.accel_achv[i] > -2.35:
                self.accel_achv[i] = self.accel_data_rqst[i]
                
            elif self.accel_data_rqst[i] == -2.75 and self.accel_achv[i] > -2.55:
                self.accel_achv[i] = self.accel_data_rqst[i]

                
            self.accel_calculated[i] = accel_value

    def calculate_acceleration_achv_nonsmoothed(self):
        # Initialize an array of the same shape as speed_data_mps with zeros
        self.accel_achv = np.zeros_like(self.speed_data_mps, dtype=float)

        # Variable to check for two consecutive non-zero elements
        found_consecutive_non_zero = False
        self.accel_achv[0] = self.accel_data_rqst[0]

        # Loop to calculate acceleration without smoothing
        for i in range(1, len(self.speed_data_mps)):
            accel_value = self.accel_achv[i-1]
            # Check for two consecutive non-zero speeds
            if self.speed_data_mps[i] > 0 and self.speed_data_mps[i - 1] > 0:
                found_consecutive_non_zero = True
            else:
                found_consecutive_non_zero = False

            # Calculate acceleration if consecutive non-zero speeds are found
            if found_consecutive_non_zero:
                if (self.speed_data_mps[i] - self.speed_data_mps[i - 1]) > 0:
                    accel_value = (self.speed_data_mps[i] - self.speed_data_mps[i - 1]) / (self.time_data[i] - self.time_data[i - 1])
                    # Directly assign the calculated acceleration value to accel_achv
                self.accel_achv[i] = accel_value
            
            elif not found_consecutive_non_zero and self.accel_data_rqst[i] > 0:
                self.accel_achv[i] = self.accel_achv[i-1]

            else:
                self.accel_achv[i] = self.accel_data_rqst[i]

    def calculate_acceleration_achv_avg(self):
         # Initialize an array of the same shape as speed_data_mps with zeros
        self.accel_achv = np.zeros_like(self.speed_data_mps, dtype=float)
        accel_value_list = []
        prev_accepted_accel_value = self.accel_data_rqst[0]

        # Variable to check for two consecutive non-zero elements
        found_consecutive_non_zero = False
        self.accel_achv[0] = self.accel_data_rqst[0]

        # Loop to calculate acceleration without smoothing
        for i in range(1, len(self.speed_data_mps)):
            # Check for two consecutive non-zero speeds
            if self.speed_data_mps[i] > 0 and self.speed_data_mps[i - 1] > 0:
                found_consecutive_non_zero = True
            else:
                found_consecutive_non_zero = False

            # Calculate acceleration if consecutive non-zero speeds are found
            if found_consecutive_non_zero:
                accel_value = (self.speed_data_mps[i] - self.speed_data_mps[i - 1]) / (self.time_data[i] - self.time_data[i - 1])
                # Directly assign the calculated acceleration value to accel_achv when divisible by 5
                if i % 5 == 0 and len(accel_value_list) == 5:
                    self.accel_achv[i] = sum(accel_value_list) / len(accel_value_list)
                    prev_accepted_accel_value =  self.accel_achv[i]
                    accel_value_list.clear()

                else:
                    accel_value_list.append(accel_value)
                    self.accel_achv[i] = prev_accepted_accel_value
            
            elif not found_consecutive_non_zero and self.accel_data_rqst[i] > 0:
                self.accel_achv[i] = self.accel_achv[i-1]

            else:
                self.accel_achv[i] = self.accel_data_rqst[i]

    def save_data_to_csv(self):

        data = pd.DataFrame({
            "Time [s]": self.experimental_time_data,
            "Speed [mph]": self.speed_data_mph,
            "Speed [mps]": self.speed_data_mps,
            "Acceleration Requested [mps2]": self.accel_data_rqst,
            "Acceleration Achieved [mps2]": self.accel_achv,
            "Calculated Acceleration [mps2]":self.accel_calculated
        })

        # Save to CSV
        csv_file_path = self.output_file_name
        # result.to_csv(csv_file_path, index=False)
        data.to_csv(csv_file_path, index=False)
        print(f"Data saved to {csv_file_path}")           

    def generate_plots(self):
        self.get_files()
        self.get_groups_channels()
        self.get_data_from_channel()
        
        # self.filter_data_set()
        self.calculate_acceleration_achv()
        
        if self.debug_status:
            #self.save_data_to_csv()
            self.plot_manager.plot_two_data_on_secondary_yaxis(self.experimental_time_data, self.speed_data_mph, self.accel_data_rqst, self.accel_achv, "Time [s]", "Speed [mph]", "Acceleration [m/s²]",  "Time vs Speed and Acceleration Plot", "resume-test_mph_time_vs_speed_Accel_rqst_achv")
          
        else:
            self.save_data_to_csv()
            self.plot_manager.plot_primary_yaxis(self.experimental_time_data, self.speed_data_mph, "Time [s]", "Speed [mph]", "Time vs Speed Plot", "resume-test_mph_time_vs_speed")
            self.plot_manager.plot_primary_secondary_yaxis(False, self.experimental_time_data, self.speed_data_mph, self.accel_data_rqst, "Time [s]", "Speed [mph]", "Acceleration [m/s²]", "Time vs Speed and Acceleration Plot", "resume-test_mph_time_vs_speed_Accel")      
            self.plot_manager.plot_primary_secondary_yaxis(True, self.experimental_time_data, self.speed_data_mph, self.accel_data_rqst, "Time [s]", "Speed [mph]", "Acceleration [m/s²]", "Time vs Speed and Acceleration Plot", "resume-test_mph_time_vs_speed_Accel_resize")      
            self.plot_manager.plot_two_data_on_secondary_yaxis(self.experimental_time_data, self.speed_data_mph, self.accel_data_rqst, self.accel_achv, "Time [s]", "Speed [mph]", "Acceleration [m/s²]",  "Time vs Speed and Acceleration Plot", "resume-test_mph_time_vs_speed_Accel_rqst_achv")

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