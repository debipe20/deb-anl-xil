import pandas as pd
import os
import matplotlib.pyplot as plt
from nptdms import TdmsFile

class PlotManager:
    def __init__(self, config):
        self.config = config

    def get_files(self):
        filePath = os.path.expanduser("~") + "/Downloads/2018-Honda-Accord/62409002 2018 Honda Accord Blank 1Bag 3600"

        self.tdms_file = TdmsFile.read(filePath + "/62409002 Test Data.tdms")

    def get_groups_channels_name(self, tdms_file):
        # Get all groups in the TDMS file
        groups = tdms_file.groups()

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
   
        self.time_data = self.time_channel[:]
        self.speed_data = self.speed_channel[:]* 0.621371
        self.accel_data = self.accel_channel[:]

    def plot_primary_yaxis(self, x_data, y_data, x_label, y_label, title):

        plt.plot(x_data, y_data)
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.grid(True)
        plt.show()
        plt.close()

    def plot_primary_secondary_yaxis(self, x_data, y_data1, y_data2, x_label, y_label1, y_label2, title):
        # # Create a figure and axis object
        fig, ax1 = plt.subplots()

        # Plot speed (on primary y-axis)
        ax1.set_xlabel(x_label)
        ax1.set_ylabel(y_label1, color='tab:blue')
        ax1.plot(x_data, y_data1, color='tab:blue', label='Speed (kph)')
        ax1.tick_params(axis='y', labelcolor='tab:blue')

        # Create a secondary y-axis to plot acceleration
        ax2 = ax1.twinx()  # Instantiate a second axes that shares the same x-axis
        ax2.set_ylabel(y_label2, color='tab:red')
        ax2.plot(x_data, y_data2, color='tab:red', label='Acceleration (m/s²)')
        ax2.tick_params(axis='y', labelcolor='tab:red')

        # Add a title
        plt.title(title)

        # Show grid
        ax1.grid(True)

        # Show the  plot
        plt.show()
        # plt.savefig(fileName+'.jpg', bbox_inches='tight', dpi=72)
        plt.close(fig)

    def generate_plots(self):
        self.get_files()
        self.get_groups_channels()
        self.get_data_from_channel()
        self.plot_primary_yaxis(self.time_data, self.speed_data, "Time[s]", "Speed[mph]", "Time vs. Speed Plot")
        self.plot_primary_secondary_yaxis(self.time_data, self.speed_data, self.accel_data, "Time[s]", "Speed[mph]", "Acceleration [m/s²]", "Time vs. Speed and Acceleration Plot")


    