import pandas as pd
import numpy as np
import os
import platform
from nptdms import TdmsFile
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

class RoadGradeAnalyzer:
    def __init__(self, config):
        self.config = config
        self.debug_status = self.config['Debug']
        self.title_status = self.config['SetTitle']
        self.plot_save = False if self.debug_status else self.config['PlotSave']
        self.road_grade_test_file_list = self.config['RoadGradeFileList']
        self.road_grade_list = self.config['RoadGrade']
        self.grade_data = []
        self.speed_data_mps = []
        self.speed_data_mph = []
        self.energy_consumed_list, self.energy_regenerated_list, self.net_energy_used_list, self.average_energy_rate_list = [], [], [], []
        
    def get_data_directory(self):
        """
            Method to get the Data directory irrespective of operating system
        """
        current_os = platform.system()

        if current_os == "Linux":
            data_directory = os.path.join(os.path.expanduser("~"), "Downloads", "2020-Tesla-Model3")
        elif current_os == "Windows":
            data_directory = os.path.join("C:\\", "Users", "ddas", "Documents", "Data", "2020-Tesla-Model3", "road-grada-data")
        else:
            raise OSError(f"Unsupported operating system: {current_os}")
        
        return data_directory      
        
    def get_data_from_group_channel(self):
        """
            Method to get data from group and channel
        """
        
        self.group_data = self.tdms_file["Data"]

        self.time_channel = self.group_data['Time[s]']
        self.speed_channel_kph = self.group_data['veh_speed']       
        self.voltage_channel = self.group_data['BMS_packVoltage']
        self.current_channel = self.group_data['BMS_packCurrent']
        self.drive_trace_speed_channel = self.group_data['Dyno_Data_Drivetrace_Spd_Vspy']
        self.tractive_force_channel = self.group_data['Dyno_TractiveForce[N]']
        
        # self.tractive_force_front_channel = self.group_data['Dyno_TractiveForce_Front[N]']
        self.tractive_force_front_channel = self.group_data['Dyno_LoadCell_Front[N]']
        self.tractive_force_rear_channel = self.group_data['Dyno_TractiveForce_Rear[N]']
        
        self.time_data = self.time_channel[:]
        self.speed_data_mph = self.speed_channel_kph[:] * 0.62137 
        self.speed_data_mps = self.speed_channel_kph[:] * 0.277778
        self.drive_trace_speed_data_mph = self.drive_trace_speed_channel[:]
        
        self.voltage = self.voltage_channel[:]
        self.current = self.current_channel[:]
        self.power_kw = (self.voltage * self.current) / 1000
        
        self.tractive_force = self.tractive_force_channel[:]
        self.tractive_force_front = self.tractive_force_front_channel[:]
        self.tractive_force_rear = self.tractive_force_rear_channel[:]
        
    def compute_energy_metrics(self):
        """
        Computes:
        - Instantaneous power
        - Signed energy (consumption, regeneration, net) in kWh
        - Cumulative absolute energy (for plotting)
        Stores all relevant results as class attributes.
        """
        # Convert lists to NumPy arrays
        time_sec = np.array(self.time_data)
        voltage = np.array(self.voltage)
        current = np.array(self.current)

        # Compute delta_t for each interval
        delta_t = np.diff(time_sec, prepend=time_sec[0])  # in seconds

        # Instantaneous power in watts
        power_w = voltage * current
        self.power_w = power_w  # Save for downstream plots if needed

        # Signed energy in watt-seconds
        energy_ws_signed = power_w * delta_t

        # Absolute energy in watt-seconds (for cumulative)
        energy_ws_abs = np.abs(power_w) * delta_t

        # Convert to kilowatt-hours
        energy_kwh_signed = energy_ws_signed / (3600 * 1000)
        energy_kwh_abs = energy_ws_abs / (3600 * 1000)

        # Store signed energy metrics
        self.energy_consumed_kwh = energy_kwh_signed[energy_kwh_signed < 0].sum()
        self.energy_regenerated_kwh = energy_kwh_signed[energy_kwh_signed > 0].sum()
        self.net_energy_kwh = energy_kwh_signed.sum()

        # Cumulative absolute energy (for plotting)
        self.cumulative_energy_kwh = np.cumsum(energy_kwh_abs)

        # Print summary
        print(f"Energy Consumed     : {abs(self.energy_consumed_kwh):.3f} kWh")
        print(f"Energy Regenerated  : {self.energy_regenerated_kwh:.3f} kWh")
        print(f"Net Energy Used     : {self.net_energy_kwh:.3f} kWh")
        print(f"Cumulative Absolute Energy: {self.cumulative_energy_kwh[-1]:.3f} kWh")
        
        # Compute average energy rate in kWh/mile
        # Total distance = speed (mps) * delta_t summed and converted to miles
        speed_mps = np.array(self.speed_data_mps)
        distance_m = np.sum(speed_mps * delta_t)  # meters
        distance_miles = distance_m / 1609.34     # convert to miles
        print(f"Total Distance      : {distance_miles:.3f} miles")
        
        if distance_miles > 0:
            self.avg_energy_rate_kwh_per_mile = self.net_energy_kwh / distance_miles
            print(f"Average Energy Rate : {self.avg_energy_rate_kwh_per_mile:.3f} kWh/mile")
        else:
            self.avg_energy_rate_kwh_per_mile = np.nan
            print("Average Energy Rate : NaN (zero distance)")
            
        self.energy_consumed_list.append(abs(self.energy_consumed_kwh))
        self.energy_regenerated_list.append(self.energy_regenerated_kwh)
        self.net_energy_used_list.append(self.net_energy_kwh * (-1))
        self.average_energy_rate_list.append(self.avg_energy_rate_kwh_per_mile * (-1))
        
    def manage_test_data(self):

        data_directory = self.get_data_directory()
        
        for index, test_file_name in enumerate(self.road_grade_test_file_list):
            tdms_file_path = os.path.join(data_directory, test_file_name)
            
            # Check if the file exists
            if not os.path.isfile(tdms_file_path):
                raise FileNotFoundError(f"No such file: {tdms_file_path}")
            print(f"Processing test file: {test_file_name}")
            
            road_grade = self.road_grade_list[index]
            print(f"Road Grade: {road_grade} %")
            
            self.tdms_file = TdmsFile.read(tdms_file_path)
            self.get_data_from_group_channel()
            
            self.compute_energy_metrics()
            
            self.plot_speed(self.time_data, self.speed_data_mph, self.drive_trace_speed_data_mph,
                            x_label = "Time [s]", 
                            y_label = "Speed [mph]", 
                            title = f"{road_grade}% Road Grade: Dive Trace and Vehicle Speed Plot", 
                            fileName = f"{road_grade}%_road_grade_drive_trace_and_vehicle_speed_plot")
            
            self.plot_speed_instantenous_power(self.time_data, self.speed_data_mph, self.power_kw, 
                                                x_label = "Time [s]",
                                                y_label1 = "Speed [mph]", 
                                                y_label2 = "Power [kW]", 
                                                title = f"{road_grade}% Road Grade: Speed and Instantaneous Power Plot",
                                                fileName = f"{road_grade}%_road_grade_speed_and_instantaneous_power_plot")
            
            self.plot_speed_power_energy(self.time_data, self.speed_data_mph, self.power_kw, self.cumulative_energy_kwh,
                                x_label = "Time [s]",
                                y_label1 = "Speed [mph]",
                                y_label2 = "Instantaneous Power [kW]",
                                y_label3 = "Cumulative Energy [kWh]",
                                title = f"{road_grade}% Road Grade: Speed, Instantaneous Power and Cumulative Energy Plot",
                                fileName = f"{road_grade}%_road_grade_speed_power_and_energy_plot")
            
            
            self.plot_speed_vs_tractive_force(title = f"{road_grade}% Road Grade: Speed and Tractive Force Plot",
                                              fileName = f"{road_grade}%_speed_vs_tractive_force_plot")
        
        self.plot_energy_metrics_by_grade()
    
    # def plot_energy_histograms_by_grade(self):
    def plot_energy_metrics_by_grade(self):
        """
        Plots bar charts for different road grades showing:
        - Energy Consumed
        - Energy Regenerated
        - Net Energy Used
        - Average Energy Rate (kWh/mile)
        """

        grades = self.road_grade_list
        consumed = self.energy_consumed_list
        regenerated = self.energy_regenerated_list
        net = self.net_energy_used_list
        rate = self.average_energy_rate_list

        # Convert to NumPy arrays for consistency
        grades = np.array(grades)
        consumed = np.array(consumed)
        regenerated = np.array(regenerated)
        net = np.array(net)
        rate = np.array(rate)

        # Create 2x2 subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle("Energy Metrics by Road Grade", fontsize=16, fontweight='bold')

        # Energy Consumed
        axes[0, 0].bar(grades, consumed, color='red')
        axes[0, 0].set_title("Energy Consumed (kWh)")
        axes[0, 0].set_ylabel("kWh")

        # Energy Regenerated
        axes[0, 1].bar(grades, regenerated, color='green')
        axes[0, 1].set_title("Energy Regenerated (kWh)")
        axes[0, 1].set_ylabel("kWh")

        # Net Energy Used
        axes[1, 0].bar(grades, net, color='blue')
        axes[1, 0].set_title("Net Energy Used (kWh)")
        axes[1, 0].set_ylabel("kWh")

        # Average Energy Rate
        axes[1, 1].bar(grades, rate, color='purple')
        axes[1, 1].set_title("Average Energy Rate (kWh/mile)")
        axes[1, 1].set_ylabel("kWh/mile")

        for ax in axes.flatten():
            ax.set_xlabel("Road Grade (%)")
            ax.set_xticks(grades)  # Explicit tick positions from your grade list
            ax.grid(True)


        plt.tight_layout(rect=[0, 0.03, 1, 0.95])

        if self.plot_save:
            file_path = "figures/energy_bar_by_grade.jpg"
            plt.savefig(file_path, dpi=300)
            print(f"Saved energy summary plot to {file_path}")
        else:
            plt.show()

        plt.close()


    def plot_speed_vs_tractive_force(self, title, fileName):
        """
        Plots tractive force and speed over time using dual y-axes.
        """
        if not hasattr(self, 'time_data') or not hasattr(self, 'tractive_force'):
            print("Data not found. Please run manage_test_data() first.")
            return

        fig, ax1 = plt.subplots(figsize=(14, 6))

        # Primary y-axis: Speed
        ax1.set_xlabel("Time [s]")
        ax1.set_ylabel("Speed [mph]", color='tab:blue')
        # ax1.plot(self.time_data, self.speed_data_mph, label="Speed [mph]", color='tab:blue')
        ax1.plot(self.time_data, self.speed_data_mph, color='tab:blue')
        ax1.tick_params(axis='y', labelcolor='tab:blue')

        # Secondary y-axis: Tractive Force
        ax2 = ax1.twinx()
        ax2.set_ylabel("Tractive Force [N]", color='tab:red')
        ax2.plot(self.time_data, self.tractive_force_front, label="Tractive Force Front", color='tab:green')
        ax2.plot(self.time_data, self.tractive_force_rear, label="Tractive Force Rear", color='tab:red')
        ax2.tick_params(axis='y', labelcolor='tab:red')

        # Optional legend
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', fontsize=12)

        # Title and layout        
        if self.title_status:
            plt.title(title, fontweight='bold')

        ax1.grid(True)

        if self.plot_save:
            file_directory = "figures/" + fileName + ".jpg"
            plt.savefig(file_directory, bbox_inches='tight', dpi=300)
            print("Saved plot successfully at:", file_directory)
        else:
            plt.show()

        plt.close(fig)

    
    def plot_speed(self, time_data, ego_speed_data_mph, lead_speed_data_mph, x_label, y_label, title, fileName):
        """
        Plots speed data against time.
        """
        fig, ax = plt.subplots(figsize=(14, 5))
        ax.plot(time_data, lead_speed_data_mph, color='tab:green', label='Drive Trace Speed [mph]')
        ax.plot(time_data, ego_speed_data_mph, color='tab:blue', label='Ego Speed [mph]')
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label, color='tab:blue')
        ax.tick_params(axis='y', labelcolor='tab:blue')
        
        if self.title_status:
            plt.title(title, fontweight='bold')

        ax.grid(True)

        if self.plot_save:
            file_directory = "figures/" + fileName + ".jpg"
            plt.savefig(file_directory, bbox_inches='tight', dpi=300)
            print("Saved plot successfully at:", file_directory)
        else:
            plt.show()

        plt.close(fig)
            
    def plot_speed_instantenous_power(self, time_data, speed_data_mph, instantaneous_power_data, x_label, y_label1, y_label2, title, fileName):
        """
        Plots speed and instantaneous power on the same graph with dual y-axes.
        Positive power (consumption) is shown in red, negative (regeneration) in green.
        """
        fig, ax1 = plt.subplots(figsize=(14, 5))

        # Primary y-axis for speed
        ax1.set_xlabel(x_label)
        ax1.set_ylabel(y_label1, color='tab:blue')
        primary_axis_line, = ax1.plot(time_data, speed_data_mph, color='tab:blue', label='Speed [mph]')
        ax1.tick_params(axis='y', labelcolor='tab:blue')
        
        # # Secondary y-axis for power
        # ax2 = ax1.twinx()
        # ax2.set_ylabel(y_label2, color='tab:red')
        # secondary_axis_line, = ax2.plot(time_data, instantaneous_power_data, color='tab:red', label='Instantaneous Power [KW]')
        # ax2.tick_params(axis='y', labelcolor='tab:red')

        # # Combine legends from both axes
        # lines = [primary_axis_line, secondary_axis_line]
        # labels = [line.get_label() for line in lines]
        

        # Secondary y-axis for power
        ax2 = ax1.twinx()
        ax2.set_ylabel(y_label2)

        # Create segments for LineCollection
        points = np.array([time_data, instantaneous_power_data]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        # Assign colors: red for consumption, green for regeneration
        colors = ['green' if p >= 0 else 'red' for p in instantaneous_power_data[:-1]]
        
        # Build the color-coded line collection
        lc = LineCollection(segments, colors=colors, linewidths=1.5)
        ax2.add_collection(lc)

        # Set limits to ensure plot renders all data
        ax2.set_xlim(min(time_data), max(time_data))
        ax2.set_ylim(min(instantaneous_power_data), max(instantaneous_power_data))
        ax2.tick_params(axis='y')

        # Custom legend for both axes
        legend_elements = [
            primary_axis_line,
            Line2D([0], [0], color='green', label='Power (Regeneration)'),
            Line2D([0], [0], color='red', label='Power (Consumption)')
        ]
        ax1.legend(handles=legend_elements, loc='upper left', fontsize=12)
        
        
        if self.title_status:
            plt.title(title, fontweight='bold')

        
        ax1.grid(True)

        if self.plot_save:
            file_directory = "figures/" + fileName + ".jpg"
            plt.savefig(file_directory, bbox_inches='tight', dpi=300)
            print("Saved plot successfully at:", file_directory)
        else:
            plt.show()

        plt.close(fig)      
        
    def plot_speed_power_energy(self, time_data, speed_data_mph, instantaneous_power_data, cumulative_energy_kwh,
                                x_label="Time [s]",
                                y_label1="Speed [mph]",
                                y_label2="Instantaneous Power [kW]",
                                y_label3="Cumulative Energy [kWh]",
                                title="Speed, Instantaneous Power, and Cumulative Energy",
                                fileName="speed_power_energy_plot"):
        """
        Plots speed, instantaneous power (with regen/consumption coloring), and cumulative energy on one plot.
        - Speed: primary y-axis (blue)
        - Power: secondary y-axis (red/green)
        - Cumulative energy: third y-axis (black dashed)
        """

        fig, ax1 = plt.subplots(figsize=(15, 6))

        # Primary y-axis for speed
        ax1.set_xlabel(x_label)
        ax1.set_ylabel(y_label1, color='tab:blue')
        speed_line, = ax1.plot(time_data, speed_data_mph, color='tab:blue', label='Speed [mph]')
        ax1.tick_params(axis='y', labelcolor='tab:blue')

        # Secondary y-axis for instantaneous power
        ax2 = ax1.twinx()
        ax2.set_ylabel(y_label2, color='tab:red')
        ax2.tick_params(axis='y', labelcolor='tab:red')

        # Create color-coded segments for power line
        points = np.array([time_data, instantaneous_power_data]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        colors = ['green' if p >= 0 else 'red' for p in instantaneous_power_data[:-1]]
        lc = LineCollection(segments, colors=colors, linewidths=1.5)
        ax2.add_collection(lc)

        # Set power axis limits
        ax2.set_xlim(min(time_data), max(time_data))
        ax2.set_ylim(min(instantaneous_power_data), max(instantaneous_power_data))
        

        # Third y-axis for cumulative energy
        ax3 = ax1.twinx()
        ax3.spines.right.set_position(("axes", 1.08))  # Shift to far right
        ax3.set_frame_on(True)
        ax3.patch.set_visible(False)
        for spine in ax3.spines.values():
            spine.set_visible(False)
        ax3.spines["right"].set_visible(True)
        ax3.set_ylabel(y_label3, color='black')
        ax3.tick_params(axis='y', labelcolor='black')
        energy_line, = ax3.plot(time_data, cumulative_energy_kwh, linestyle='--', color='black', label='Cumulative Energy [kWh]')

        # Custom legend
        # legend_elements = [
        #     speed_line,
        #     Line2D([0], [0], color='green', label='Power (Regeneration)'),
        #     Line2D([0], [0], color='red', label='Power (Consumption)'),
        #     Line2D([0], [0], linestyle='--', color='black', label='Cumulative Energy [kWh]')
        # ]
        legend_elements = [
            Line2D([0], [0], color='green', label='Regeneration'),
            Line2D([0], [0], color='red', label='Consumption')
        ]
        ax1.legend(handles=legend_elements, loc='upper left', fontsize=12)
        # ax1.legend(handles=legend_elements, loc='best', fontsize=12)

        # Title and grid
        if self.title_status:
            plt.title(title, fontweight='bold')
        ax1.grid(True)

        # Save or show
        if self.plot_save:
            file_directory = "figures/" + fileName + ".jpg"
            plt.savefig(file_directory, bbox_inches='tight', dpi=300)
            print("Saved plot successfully at:", file_directory)
        else:
            plt.show()

        plt.close(fig)
    


'''##############################################
                   Unit testing
##############################################'''
if __name__ == "__main__":
    import json
    configFile = open("config-files/configuration.json", 'r')
    config = (json.load(configFile))
    configFile.close()
    roadGradeAnalyzer = RoadGradeAnalyzer(config)
    roadGradeAnalyzer.manage_test_data()
    
    # "RoadGradeFileList": ["62505020 Test Data.tdms", "62505021 Test Data.tdms", "62505022 Test Data.tdms", "62505023 Test Data.tdms", "62505024 Test Data.tdms", "62505025 Test Data.tdms"]
