import pandas as pd
import numpy as np
import os
import platform
import re
from nptdms import TdmsFile
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import seaborn as sns

class RoadGradeAnalyzer:
    """
    A class for analyzing electric vehicle performance data (speed, energy consumption, regeneration, etc.)
    from TDMS files across different road grades and driving scenarios.

    This class supports loading and processing TDMS files, computing energy metrics such as power,
    energy consumed/regenerated, and energy efficiency, and visualizing results with plots such as 
    speed vs. time, energy usage across grades, tractive force analysis, and heatmaps.
    
    Attributes:
    -----------
    config : dict
        Configuration dictionary specifying paths, test files, debug options, and plot settings.
    
    debug_status : bool
        Flag for toggling debug mode (controls plot saving behavior).
    
    title_status : bool
        If True, titles are shown on generated plots.
    
    plot_save : bool
        Determines whether plots are saved or shown interactively.

    """
    def __init__(self, config):
        self.config = config
        self.debug_status = self.config['Debug']
        self.title_status = self.config['SetTitle']
        self.plot_save = False if self.debug_status else self.config['PlotSave']
        self.highway_road_grade_test_file_list = self.config['HighwayRoadGradeFileList']
        self.highway_road_grade_list = self.config['HighwayRoadGrade']
        self.udds_road_grade_test_file_list = self.config['UDDSRoadGradeFileList']
        self.udds_road_grade_list = self.config['UDDSRoadGrade']        
        self.repeatability_check_test_file_list = self.config['UDDSRepeatabilityCheckTestFileList']
        self.repeatbility_check_road_grade_list = self.config['UDDSRepeatabilityCheckRoadGrade']
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
        # self.drive_trace_speed_channel = self.group_data['Dyno_Data_Drivetrace_Spd_Vspy']
        self.drive_trace_speed_channel = self.group_data['Dyno_Data_Drivetrace_Spd']
        self.tractive_force_channel = self.group_data['Dyno_TractiveForce[N]']
        
        # self.tractive_force_front_channel = self.group_data['Dyno_TractiveForce_Front[N]']
        self.tractive_force_front_channel = self.group_data['Dyno_LoadCell_Front[N]']
        self.tractive_force_rear_channel = self.group_data['Dyno_TractiveForce_Rear[N]']
        
        self.front_axle_speed_channel = self.group_data['DIF_axleSpeed']
        self.rear_axle_speed_channel = self.group_data['DIR_axleSpeed']
        self.front_torque_actual_channel = self.group_data['DIF_torqueActual']
        self.rear_torque_actual_channel = self.group_data['DIR_torqueActual']
        self.front_torque_commanded_channel = self.group_data['DIF_torqueCommand']
        self.rear_torque_commanded_channel = self.group_data['DIR_torqueCommand']
        self.front_electric_power_channel = self.group_data['DIF_elecPower']
        self.rear_electric_power_channel = self.group_data['DIR_elecPower']
        
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
        
        self.front_axle_speed = self.front_axle_speed_channel[:]
        self.rear_axle_speed = self.rear_axle_speed_channel[:]
        self.front_torque_actual = self.front_torque_actual_channel[:]
        self.rear_torque_actual = self.rear_torque_actual_channel[:]
        self.front_torque_commanded = self.front_torque_commanded_channel[:]
        self.rear_torque_commanded = self.rear_torque_commanded_channel[:]
        self.front_electric_power = self.front_electric_power_channel[:]
        self.rear_electric_power = self.rear_electric_power_channel[:]
        
        
    def compute_torque_distribution_with_current(self):
        """
        Classifies torque behavior (regen vs propulsion) using actual torque and battery current.
        Uses front/rear motor torque and sign of current:
        - Positive current => regen
        - Negative current => propulsion
        """

        # Convert inputs to numpy arrays for efficiency
        front_torque = np.array(self.front_torque_actual)
        rear_torque = np.array(self.rear_torque_actual)
        current = np.array(self.current_channel)
        time = np.array(self.time_data)

        # Initialize results
        mode_flags = []
        torque_split_ratios = []
        total_front_regen = 0
        total_rear_regen = 0
        total_front_prop = 0
        total_rear_prop = 0

        for f_t, r_t, i in zip(front_torque, rear_torque, current):
            if i > 0:  # Regen
                if f_t < 0 and r_t >= 0:
                    mode_flags.append("Front-only Regen")
                    total_front_regen += abs(f_t)
                elif r_t < 0 and f_t >= 0:
                    mode_flags.append("Rear-only Regen")
                    total_rear_regen += abs(r_t)
                elif f_t < 0 and r_t < 0:
                    mode_flags.append("Both Regen")
                    total_front_regen += abs(f_t)
                    total_rear_regen += abs(r_t)
                else:
                    mode_flags.append("Neutral Regen / Coasting")
            elif i < 0:  # Propulsion
                if f_t > 0 and r_t > 0:
                    mode_flags.append("Both Propulsion")
                    total_front_prop += f_t
                    total_rear_prop += r_t
                    total = f_t + r_t
                    ratio = f_t / total if total != 0 else 0
                    torque_split_ratios.append(ratio)
                elif f_t > 0 and r_t <= 0:
                    mode_flags.append("Front-only Propulsion")
                    total_front_prop += f_t
                elif r_t > 0 and f_t <= 0:
                    mode_flags.append("Rear-only Propulsion")
                    total_rear_prop += r_t
                else:
                    mode_flags.append("Neutral Propulsion / Coasting")
            else:
                mode_flags.append("Zero Current")

        # Store for later use
        self.torque_analysis = {
            "time": time,
            "front_torque": front_torque,
            "rear_torque": rear_torque,
            "current": current,
            "mode_flags": mode_flags,
            "torque_split_ratios": torque_split_ratios,
            "total_front_regen": total_front_regen,
            "total_rear_regen": total_rear_regen,
            "total_front_prop": total_front_prop,
            "total_rear_prop": total_rear_prop
        }

        print("✓ Torque distribution analysis completed based on current direction.")
        print(f"→ Front Regen Torque Total: {total_front_regen:.2f} Nm")
        print(f"→ Rear Regen Torque Total : {total_rear_regen:.2f} Nm")
        print(f"→ Front Propulsion Total  : {total_front_prop:.2f} Nm")
        print(f"→ Rear Propulsion Total   : {total_rear_prop:.2f} Nm")

         
        
    def compute_energy_metrics_highway(self):
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
        
        
    def compute_energy_metrics_udds(self):
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
        energy_consumed_kwh = energy_kwh_signed[energy_kwh_signed < 0].sum()
        energy_regenerated_kwh = energy_kwh_signed[energy_kwh_signed > 0].sum()
        net_energy_kwh = energy_kwh_signed.sum()

        # Cumulative absolute energy (for plotting)
        cumulative_energy_kwh = np.cumsum(energy_kwh_abs)

        # Print summary
        print(f"Energy Consumed     : {abs(energy_consumed_kwh):.3f} kWh")
        print(f"Energy Regenerated  : {energy_regenerated_kwh:.3f} kWh")
        print(f"Net Energy Used     : {net_energy_kwh:.3f} kWh")
        print(f"Cumulative Absolute Energy: {cumulative_energy_kwh[-1]:.3f} kWh")
        
        # Compute average energy rate in kWh/mile
        # Total distance = speed (mps) * delta_t summed and converted to miles
        speed_mps = np.array(self.speed_data_mps)
        distance_m = np.sum(speed_mps * delta_t)  # meters
        distance_miles = distance_m / 1609.34     # convert to miles
        print(f"Total Distance      : {distance_miles:.3f} miles")
        
        if distance_miles > 0:
            avg_energy_rate_kwh_per_mile = net_energy_kwh / distance_miles
            print(f"Average Energy Rate : {avg_energy_rate_kwh_per_mile:.3f} kWh/mile")
        else:
            avg_energy_rate_kwh_per_mile = np.nan
            print("Average Energy Rate : NaN (zero distance)")
                    
        
        return abs(energy_consumed_kwh), energy_regenerated_kwh, net_energy_kwh, cumulative_energy_kwh, avg_energy_rate_kwh_per_mile
        
    def manage_highway_test_data(self):

        data_directory = self.get_data_directory()
        
        for index, test_file_name in enumerate(self.highway_road_grade_test_file_list):
            tdms_file_path = os.path.join(data_directory, test_file_name)
            
            # Check if the file exists
            if not os.path.isfile(tdms_file_path):
                raise FileNotFoundError(f"No such file: {tdms_file_path}")
            print(f"Processing test file: {test_file_name}")
            
            road_grade = self.highway_road_grade_list[index]
            print(f"Road Grade: {road_grade} %")
            
            self.tdms_file = TdmsFile.read(tdms_file_path)
            self.get_data_from_group_channel()
            
            self.compute_energy_metrics_highway()
            
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
        
        
    def manage_udds_test_data(self):
        """
        Generalized method to manage UDDS test data, storing results by category and road grade.
        """
        self.energy_summary = {}  # Clear or initialize summary storage

        data_directory = self.get_data_directory()
        
        

        for category, file_list in self.udds_road_grade_test_file_list.items():
            self.energy_summary[category] = {}
            grade_index = 0  # global index into flat grade list
            
            for test_file_name in file_list:
                tdms_file_path = os.path.join(data_directory, test_file_name)
                
                # Check if the file exists
                if not os.path.isfile(tdms_file_path):
                    raise FileNotFoundError(f"No such file: {tdms_file_path}")
                print(f"Processing test file: {test_file_name}")
                    
                road_grade = self.udds_road_grade_list[grade_index]
                print(f"Road Grade: {road_grade} %")
                grade_index += 1
                

                try:
                    self.tdms_file = TdmsFile.read(tdms_file_path)
                    self.get_data_from_group_channel()
                    energy_consumed_kwh, energy_regenerated_kwh, net_energy_kwh, cumulative_energy_kwh, avg_energy_rate_kwh_per_mile = self.compute_energy_metrics_udds()
                    self.compute_torque_distribution_with_current()
                
                except Exception as e:
                    print(f"Failed to process {test_file_name}: {e}")
                    continue

                # Normalize grade key
                grade_key = str(road_grade).replace("-", "neg_").replace(".", "_")

                # Initialize storage if not exists
                if grade_key not in self.energy_summary[category]:
                    self.energy_summary[category][grade_key] = {
                        "consumed": [],
                        "regenerated": [],
                        "net": [],
                        "avg_rate": [],
                        "cumulative": []
                    }

                # Append values
                self.energy_summary[category][grade_key]["consumed"].append(abs(energy_consumed_kwh))
                self.energy_summary[category][grade_key]["regenerated"].append(energy_regenerated_kwh)
                self.energy_summary[category][grade_key]["net"].append(net_energy_kwh * (-1))
                self.energy_summary[category][grade_key]["avg_rate"].append(avg_energy_rate_kwh_per_mile * (-1))
                self.energy_summary[category][grade_key]["cumulative"].append(abs(cumulative_energy_kwh))
                
                self.plot_speed_instantenous_power(self.time_data, self.speed_data_mph, self.power_kw, 
                                                x_label = "Time [s]",
                                                y_label1 = "Speed [mph]", 
                                                y_label2 = "Power [kW]", 
                                                title = f"{road_grade}% Road Grade: Speed and Instantaneous Power Plot",
                                                fileName = f"{road_grade}%_road_grade_speed_and_instantaneous_power_plot")
                
                self.plot_speed_power_energy(self.time_data, self.speed_data_mph, self.power_kw, cumulative_energy_kwh,
                                x_label = "Time [s]",
                                y_label1 = "Speed [mph]",
                                y_label2 = "Instantaneous Power [kW]",
                                y_label3 = "Cumulative Energy [kWh]",
                                title = f"{road_grade}% Road Grade: Speed, Instantaneous Power and Cumulative Energy Plot",
                                fileName = f"udds_{road_grade}%_road_grade_speed_power_and_energy_plot")
                
                self.plot_torque_distribution_over_time(title= f"{road_grade}% Road Grade: Torque Distribution and Battery Current Over Time",
                                                        fileName = f"udds_{road_grade}%_road_grade_torque_distribution_over_time")
        print("Iterated through all UDDS test files and stored energy metrics by category and road grade.")
        
        self.plot_energy_metric_histograms_by_category()
        self.plot_energy_heatmap_by_category()
    
    

    def manage_udds_repeatability_check_test_data(self):
        """
        Manage UDDS repeatability check test data and generate:
        - Speed vs Time plots for Road Grade 0 and Dynamic
        - RMSE bar charts for each group
        """
        data_directory = self.get_data_directory()

        # Grouped data containers
        time_data_list_0 = []
        speed_data_list_0 = []
        drive_trace_speed_data_list_0 = []

        time_data_list_dynamic = []
        speed_data_list_dynamic = []
        drive_trace_speed_data_list_dynamic = []

        for index, test_file_name in enumerate(self.repeatability_check_test_file_list):
            tdms_file_path = os.path.join(data_directory, test_file_name)

            if not os.path.isfile(tdms_file_path):
                print(f"Skipping missing file: {tdms_file_path}")
                continue

            road_grade = self.repeatbility_check_road_grade_list[index]
            print(f"Processing test file: {test_file_name} | Road Grade: {road_grade}")

            # Read and extract time/speed data
            self.tdms_file = TdmsFile.read(tdms_file_path)
            self.get_data_from_group_channel()  # Populates time, speed, and drive trace speed


           
            if road_grade == 0:
                time_data_list_0.append(self.time_data)
                speed_data_list_0.append(self.speed_data_mph)
                drive_trace_speed_data_list_0.append(self.drive_trace_speed_data_mph)

            elif road_grade == "Dynamic":
                time_data_list_dynamic.append(self.time_data)
                speed_data_list_dynamic.append(self.speed_data_mph)
                drive_trace_speed_data_list_dynamic.append(self.drive_trace_speed_data_mph)

        # Speed vs Time plots
        # self.plot_multiple_speed_traces(time_data_list_0, speed_data_list_0,
        #                                 title="Speed vs Time for Road Grade 0%",
        #                                 fileName="udd_repeatability_road_grade_0")

        # self.plot_multiple_speed_traces(time_data_list_dynamic, speed_data_list_dynamic,
        #                                 title="Speed vs Time for Dynamic Road Grade",
        #                                 fileName="udd_repeatability_dynamic")
        
        
        # Speed vs Time plots (each run as a separate subplot)
        self.plot_speed_subplots(time_data_list_0, speed_data_list_0, drive_trace_speed_data_list_0,
                                title="Road Grade 0% - Speed vs Time (per run)",
                                fileName="udds_repeatability_grade0_subplots")

        self.plot_speed_subplots(time_data_list_dynamic, speed_data_list_dynamic, drive_trace_speed_data_list_dynamic,
                                title="Dynamic Grade - Speed vs Time (per run)",
                                fileName="udds_repeatability_dynamic_subplots")


    

    def plot_speed_subplots(self, time_list, ego_speed_list, drive_trace_speed_list, title, fileName):
        """
        Plots each speed vs. time run as a separate subplot.
        """
        num_runs = len(time_list)
        if num_runs == 0:
            print(f"No data to plot for {title}")
            return

        fig, axes = plt.subplots(num_runs, 1, figsize=(20, 4 * num_runs), sharex=False)
        
        # Ensure axes is iterable (even if only one run)
        if num_runs == 1:
            axes = [axes]
                       
        for i, (t, s_ego, s_trace) in enumerate(zip(time_list, ego_speed_list, drive_trace_speed_list)):
            axes[i].plot(t, s_ego, color='tab:blue', label='Ego Speed')
            axes[i].plot(t, s_trace, color='tab:orange', linestyle='--', label='Drive Trace Speed')

            # Compute RMS error
            error = np.array(s_ego) - np.array(s_trace)
            rms_error = np.sqrt(np.mean(error ** 2))

            axes[i].set_title(f"Run {i+1}: Speed vs Time (RMS Error = {rms_error:.2f} mph)", fontsize=18, fontweight='bold')
            axes[i].set_ylabel("Speed [mph]", fontsize=16, fontweight='bold')
            axes[i].set_xlabel("Time [s]", fontsize=16, fontweight='bold')
            axes[i].grid(True)
            axes[i].legend()

        if self.title_status:
            fig.suptitle(title, fontsize=16, fontweight='bold')

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])

        if self.plot_save:
            path = f"figures/{fileName}.jpg"
            plt.savefig(path, dpi=300)
            print(f"Saved subplot to {path}")
        else:
            plt.show()

        plt.close(fig)


    def plot_multiple_speed_traces(self, time_list, ego_speed_list, title, fileName):
        """
        Plots multiple speed vs. time traces on the same figure.
        """
        if not time_list or not ego_speed_list:
            print(f"No data to plot for {title}")
            return

        plt.figure(figsize=(14, 6))

        for t, s in zip(time_list, ego_speed_list):
            plt.plot(t, s, linewidth=1)

        plt.xlabel("Time [s]")
        plt.ylabel("Speed [mph]")
        if self.title_status:
            plt.title(title, fontweight='bold')
        plt.grid(True)
        plt.legend([f"Run {i+1}" for i in range(len(time_list))], fontsize=10, loc='upper right')

        if self.plot_save:
            file_directory = f"figures/{fileName}.jpg"
            plt.savefig(file_directory, bbox_inches='tight', dpi=300)
            print(f"Saved plot: {file_directory}")
        else:
            plt.show()

        plt.close()

    
   
    def plot_energy_metrics_by_grade(self):
        """
        Plots bar charts for different road grades showing:
        - Energy Consumed
        - Energy Regenerated
        - Net Energy Used
        - Average Energy Rate (kWh/mile)
        """

        grades = self.highway_road_grade_list
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
            print("Data not found. Please run manage_highway_test_data() first.")
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
        
    
    def plot_energy_heatmap_by_category(self):
        """
        Plots heatmaps showing energy metric values vs road grades for each category.
        Rows = energy metrics, Columns = road grades.
        """
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np
        import pandas as pd

        metrics = {
            "consumed": "Energy Consumed (kWh)",
            "regenerated": "Energy Regenerated (kWh)",
            "net": "Net Energy Used (kWh)",
            "cumulative": "Cumulative Energy (kWh)",
            "avg_rate": "Avg. Energy Rate (kWh/mile)"
        }

        def safe_grade_sort_key(grade):
            if grade == "Dynamic":
                return float('inf')
            try:
                return float(grade.replace("neg_", "-").replace("_", "."))
            except:
                return float('inf')

        def format_grade_label(key):
            if key == "Dynamic":
                return "Dynamic"
            return key.replace("neg_", "-").replace("_", ".")

        n_categories = len(self.energy_summary)
        fig, axs = plt.subplots(n_categories, 1, figsize=(14, 4.5 * n_categories), squeeze=False)

        for idx, (category, grade_data) in enumerate(self.energy_summary.items()):
            ax = axs[idx, 0]
            grade_keys = sorted(grade_data.keys(), key=safe_grade_sort_key)
            grade_labels = [format_grade_label(k) for k in grade_keys]

            # Build 2D matrix: rows=metrics, cols=grades
            data_matrix = []
            for metric_key in metrics.keys():
                row = []
                for grade in grade_keys:
                    values = grade_data[grade][metric_key]
                    avg = np.mean(values) if values else 0
                    row.append(avg)
                data_matrix.append(row)

            df = pd.DataFrame(data_matrix, index=list(metrics.values()), columns=grade_labels)

            sns.heatmap(df, annot=True, fmt=".2f", cmap="coolwarm", cbar_kws={"label": "Average Value"}, ax=ax)
            ax.set_title(f"{category.replace('_', ' ')} - Energy Metrics by Road Grade", fontsize=13, weight='bold')
            ax.set_xlabel("Road Grade")
            ax.set_ylabel("Energy Metric")

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        if self.title_status:
            plt.suptitle("Heatmap of Energy Metrics by Road Grade for Each Category", fontsize=16, weight='bold')

        if self.plot_save:
            filename = "figures/udds_energy_metric_heatmaps_by_category.jpg"
            plt.savefig(filename, dpi=300)
            print(f"Saved heatmap plot: {filename}")
        else:
            plt.show()

        plt.close()

    
    def plot_energy_metric_histograms_by_category(self):
        """
        Plots a single figure with subplots for each category, showing grouped bar charts of
        energy metrics (consumed, regenerated, net, cumulative, avg_rate) across road grades.
        """
        import matplotlib.pyplot as plt
        import numpy as np

        # metrics = {
        #     "consumed": "Energy Consumed (kWh)",
        #     "regenerated": "Energy Regenerated (kWh)",
        #     "net": "Net Energy Used (kWh)",
        #     "cumulative": "Cumulative Energy (kWh)",
        #     "avg_rate": "Avg. Energy Rate (kWh/mile)"
        # }

        metrics = {
            "consumed":     {"label": "Energy Consumed (kWh)",       "color": "red"},
            "regenerated":  {"label": "Energy Regenerated (kWh)",    "color": "green"},
            "net":          {"label": "Net Energy Used (kWh)",       "color": "blue"},
            "cumulative":   {"label": "Cumulative Energy (kWh)",     "color": "orange"},
            "avg_rate":     {"label": "Avg. Energy Rate (kWh/mile)", "color": "purple"}
        }

        def safe_grade_sort_key(grade):
            if grade == "Dynamic":
                return float('inf')
            try:
                return float(grade.replace("neg_", "-").replace("_", "."))
            except ValueError:
                return float('inf')

        def format_grade_label(key):
            if key == "Dynamic":
                return "Dynamic"
            return key.replace("neg_", "-").replace("_", ".")

        def format_category_label(cat):
            # Step 1: Replace underscores with spaces
            cat = cat.replace("_", " ")

            # Step 2: Insert a space between lowercase-uppercase transitions (e.g., "StandardRegen" → "Standard Regen")
            import re
            cat = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', cat)

            # Step 3: Optional title-casing (if you want each word capitalized)
            # cat = cat.title()

            return cat

        categories = list(self.energy_summary.keys())
        n_categories = len(categories)

        fig, axs = plt.subplots(n_categories, 1, figsize=(14, 5 * n_categories), squeeze=False)

        for ax_idx, category in enumerate(categories):
            ax = axs[ax_idx, 0]
            grade_dict = self.energy_summary[category]
            grade_keys = sorted(grade_dict.keys(), key=safe_grade_sort_key)
            grade_labels = [format_grade_label(g) for g in grade_keys]

            # Prepare average values for each metric
            avg_values = {metric: [] for metric in metrics}
            for grade in grade_keys:
                for metric in metrics:
                    values = grade_dict[grade][metric]
                    avg = np.mean(values) if values else 0
                    avg_values[metric].append(avg)

            x = np.arange(len(grade_keys))
            width = 0.15
            offsets = np.linspace(-width*2, width*2, len(metrics))

            # for i, (metric_key, label) in enumerate(metrics.items()):
            #     ax.bar(x + offsets[i], avg_values[metric_key], width, label=label)
                
            for i, (metric_key, info) in enumerate(metrics.items()):
                ax.bar(
                    x + offsets[i],
                    avg_values[metric_key],
                    width,
                    label=info["label"],
                    color=info["color"]
                )    

            ax.set_xticks(x)
            ax.set_xticklabels(grade_labels)
            ax.set_xlabel("Road Grade")
            ax.set_ylabel("Metric Value")
            ax.set_title(f"{format_category_label(category)} - Energy Metrics by Road Grade", fontsize=12, weight='bold')
            ax.grid(True)
            ax.legend()

        plt.tight_layout(rect=[0, 0.03, 1, 0.97])
        
        if self.title_status:
            plt.suptitle("Energy Metrics Across Categories and Road Grades", fontsize=16, weight='bold')

        if self.plot_save:
            filename = "figures/udds_all_categories_energy_metrics.jpg"
            plt.savefig(filename, dpi=300)
            print(f"Saved histogram plots: {filename}")
        else:
            plt.show()

        plt.close()
      
    def plot_torque_distribution_over_time(self, title = "Torque Distribution and Battery Current Over Time",
                                        fileName = "torque_distribution_over_time"):
        """
        Plot front and rear motor torque over time along with battery current.
        Shaded regions indicate regenerative braking.
        """
        import matplotlib.pyplot as plt

        time = self.time_data
        front_torque = self.front_torque_actual
        rear_torque = self.rear_torque_actual
        battery_current = self.current

        fig, ax1 = plt.subplots(figsize=(12, 6))

        # Plot front and rear torque
        # ax1.plot(time, front_torque, label='Front Torque (Nm)', color='blue', alpha=0.7)
        ax1.plot(time, rear_torque, label='Rear Torque (Nm)', color='green', alpha=0.7)
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Torque (Nm)', color='black')
        ax1.tick_params(axis='y')

        # Add regen regions
        for i in range(1, len(time)):
            if battery_current[i] > 0:  # Regen region
                ax1.axvspan(time[i-1], time[i], color='lightblue', alpha=0.3)

        # Create second y-axis for battery current
        ax2 = ax1.twinx()
        ax2.plot(time, battery_current, label='Battery Current (A)', color='red', linestyle='--', alpha=0.5)
        ax2.set_ylabel('Battery Current (A)', color='red')
        ax2.tick_params(axis='y', labelcolor='red')

        # Legend and layout
        fig.legend(loc="upper right", bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)
        plt.title(title, fontweight='bold')
        plt.grid(True)
        plt.tight_layout()

        if self.plot_save:
            file_directory = "figures/" + fileName + ".jpg"
            plt.savefig(file_directory, bbox_inches='tight', dpi=300)
        else:
            plt.show()
                        
    def plot_speed_power_energy_torque(self, time_data, speed_data_mph, instantaneous_power_data, cumulative_energy_kwh, front_torque, rear_torque,
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
        # Plot front and rear torque
        ax1.plot(time_data, front_torque, label='Front Torque (Nm)', color='blue', alpha=0.7)
        ax1.plot(time_data, rear_torque, label='Rear Torque (Nm)', color='green', alpha=0.7)
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

    
    # def plot_check(self):

    #     # Example data — replace these with your actual aligned variable arrays
    #     # These should be lists or NumPy arrays of equal length
    #     # You can replace these with real data from your TDMS parsing logic

    #     # Example data with missing and constant values
    #     data = {
    #         "v":   [0.5, 0.6, 0.4, 0.7, 0.8],
    #         "a":   [0.1, 0.2, 0.05, 0.25, 0.15],
    #         "m":   [0.1, -0.2, 0.0, 0.3, -0.1],         # slope now varies
    #         "W":   [180, 200, 220, 210, 190],  
    #         "I":   [10, 12, 11, 14, 13],
    #         "SOC": [80, 79, 78, 77, 76]
    #     }

    #     # Convert to DataFrame
    #     df = pd.DataFrame(data)

    #     # Compute correlation matrix
    #     corr_matrix = df.corr(method='pearson')

    #     # Mask cells with NaN (due to all-NaN or constant columns)
    #     mask = corr_matrix.isnull()

    #     # Create the heatmap
    #     plt.figure(figsize=(6, 6))
    #     sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='BuGn', 
    #                 linewidths=0.5, square=True, vmin=-0.8, vmax=1.0, cbar=True)

    #     # Formatting
    #     plt.title("BEV", fontsize=16, weight='bold')
    #     plt.xticks(rotation=0)
    #     plt.yticks(rotation=0)
    #     plt.tight_layout()

    #     # Show or save
    #     plt.show()



'''##############################################
                   Unit testing
##############################################'''
if __name__ == "__main__":
    import json
    configFile = open("config-files/configuration.json", 'r')
    config = (json.load(configFile))
    configFile.close()
    roadGradeAnalyzer = RoadGradeAnalyzer(config)
    # roadGradeAnalyzer.manage_highway_test_data()
    # roadGradeAnalyzer.manage_udds_test_data()
    roadGradeAnalyzer.manage_udds_repeatability_check_test_data()
    # roadGradeAnalyzer.plot_check()
    
    # "RoadGradeFileList": ["62505020 Test Data.tdms", "62505021 Test Data.tdms", "62505022 Test Data.tdms", "62505023 Test Data.tdms", "62505024 Test Data.tdms", "62505025 Test Data.tdms"]

    # "UDDSRoadGradeFileList": 
    # {
    #     "StandardRegen_RollStopping":["62506063 Test Data.tdms", "62506064 Test Data.tdms", "62506065 Test Data.tdms", "62506066 Test Data.tdms", "62506067 Test Data.tdms", "62506061 Test Data.tdms", "62506020 Test Data.tdms", "62506068 Test Data.tdms"],
        # "StandardRegen_CreepStopping":["62506040 Test Data.tdms", "62506041 Test Data.tdms", "62506042 Test Data.tdms", "62506044 Test Data.tdms", "62506045 Test Data.tdms", "62506046 Test Data.tdms", "62506048 Test Data.tdms", "62506049 Test Data.tdms"],
    #     "LowRegen_RollStopping":["62506021 Test Data.tdms", "62506022 Test Data.tdms", "62506023 Test Data.tdms", "62506024 Test Data.tdms", "62506025 Test Data.tdms", "62506026 Test Data.tdms", "62506027 Test Data.tdms", "62506028 Test Data.tdms"],
    #     "LowRegen_CreepStopping":["62506030 Test Data.tdms", "62506031 Test Data.tdms", "62506032 Test Data.tdms", "62506035 Test Data.tdms", "62506036 Test Data.tdms", "62506037 Test Data.tdms", "62506039 Test Data.tdms", "62506029 Test Data.tdms"]
    # },