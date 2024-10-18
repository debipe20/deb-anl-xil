import pandas as pd
import os
import matplotlib.pyplot as plt
from nptdms import TdmsFile

class PlotManager:
    def __init__(self, config):
        self.config = config
        self.plot_save = self.config['PlotSave']
        self.platform = self.config['Platform']
        self.end_data_to_discard = self.config['NoOfEndDataDiscard']

    def get_files(self):
        if self.platform == "Linux":
            filePath = os.path.expanduser("~") + "/Downloads/2018-Honda-Accord/62409002 2018 Honda Accord Blank 1Bag 3600"

        else: filePath = "C:\\Users\ddas\\Documents\\Data\\2018-Honda-Accord\\62409002 2018 Honda Accord Blank 1Bag 3600"
        self.tdms_file = TdmsFile.read(filePath + "\\62409002 Test Data.tdms")

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
        self.speed_data = self.speed_channel[:-self.end_data_to_discard]* 0.621371
        self.accel_data = self.accel_channel[:-self.end_data_to_discard]

    def plot_primary_yaxis(self, x_data, y_data, x_label, y_label, title, fileName, plot_save_status):

        plt.plot(x_data, y_data, label="Speed")
        # plt.title(title, fontsize=18, fontweight='bold')
        # plt.xlabel(x_label, color='tab:green', fontsize=16)
        # plt.ylabel(y_label, color='tab:blue', fontsize=16)
        # plt.tick_params(axis='both', which='major', labelsize=12)
        # plt.legend(fontsize=16)
        plt.title(title, fontweight='bold')
        plt.xlabel(x_label, color='tab:green')
        plt.ylabel(y_label, color='tab:blue')
        plt.tick_params(axis='both', which='major')
        plt.grid(True)
        
        if plot_save_status:
            file_directory = "figure/" + fileName + ".jpg"
            plt.savefig(file_directory, bbox_inches='tight', dpi=300)
            print("saved file")
        
        else:plt.show()
        
        plt.close()

    def plot_primary_secondary_yaxis(self, x_data, y_data1, y_data2, x_label, y_label1, y_label2, title, fileName, plot_save_status):
        # # Create a figure and axis object
        fig, ax1 = plt.subplots()

        # ax1.set_xlabel(x_label, color='tab:green', fontsize=16)
        # ax1.set_ylabel(y_label1, color='tab:blue', fontsize=16)
        # primary_axis_line, = ax1.plot(x_data, y_data1, color='tab:blue', label='Speed')
        # ax1.tick_params(axis='y', labelcolor='tab:blue', labelsize=12)
        # ax1.tick_params(axis='x', labelsize=12)  # Set label size for x-axis ticks
        ax1.set_xlabel(x_label, color='tab:green')
        ax1.set_ylabel(y_label1, color='tab:blue')
        primary_axis_line, = ax1.plot(x_data, y_data1, color='tab:blue', label='Speed')
        ax1.tick_params(axis='y', labelcolor='tab:blue')


        ax2 = ax1.twinx()  # Instantiate a second axes that shares the same x-axis
        # ax2.set_ylabel(y_label2, color='tab:red', fontsize=16)
        ax2.set_ylabel(y_label2, color='tab:red')
        secondary_axis_line, = ax2.plot(x_data, y_data2, color='tab:red', label='Acceleration')
        # ax2.tick_params(axis='y', labelcolor='tab:red', labelsize=12)
        ax2.tick_params(axis='y', labelcolor='tab:red')

        # Combine legends from both axes
        lines = [primary_axis_line, secondary_axis_line]  # Handles for both lines
        labels = [line.get_label() for line in lines]  # Labels for the lines

        # ax1.legend(lines, labels, loc='upper right', fontsize=16)
        ax1.grid(True)
        # plt.title(title, fontsize=18, fontweight='bold')
        plt.title(title, fontweight='bold')
        
        if plot_save_status:
            file_directory = "figure/" + fileName + ".jpg"
            plt.savefig(file_directory, bbox_inches='tight', dpi=300)
            print("saved file")

        else:plt.show()

        plt.close(fig)

    def generate_plots(self):
        self.get_files()
        self.get_groups_channels()
        self.get_data_from_channel()
        # self.get_groups_channels_name()
        self.plot_primary_yaxis(self.time_data, self.speed_data, "Time [s]", "Speed [mph]", "Time vs. Speed Plot", "0-20_mph_time_vs_speed", self.plot_save)
        self.plot_primary_secondary_yaxis(self.time_data, self.speed_data, self.accel_data, "Time [s]", "Speed [mph]", "Acceleration [m/s²]", "Time vs. Speed and Acceleration Plot", "0-20_mph_time_vs_speed_Accel", self.plot_save)


    