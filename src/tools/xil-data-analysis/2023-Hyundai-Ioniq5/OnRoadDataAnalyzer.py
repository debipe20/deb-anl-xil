# Complete Object-Oriented Analysis Script for Hyundai Ioniq 5 On-Road Data
import platform
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D
from matplotlib.collections import LineCollection
import numpy as np
from matplotlib.collections import LineCollection

g_value = 9.80665

class Ioniq5Analyzer:
    def __init__(self, config):
        self.config = config
        self.acc_override_test_file_list = self.config['AccOverrideTestFileList']
        self.stock_acc_test_file_list = self.config['StockAccTestFileList']

        self.cumulative_distance_m = 0
        self.cumulative_highway_distance_m = 0
        self.cumulative_city_distance_m = 0
        self.cumulative_highway_distance_1000m = 0
        self.cumulative_city_distance_1000m = 0
        self.cumulative_soc_rate_highway_1000m = 0
        self.cumulative_soc_rate_city_1000m = 0

        self.stock_acc_time_data = []
        self.stock_acc_distance_m = []
        self.stock_acc_distance_km = []
        self.stock_acc_speed_mps = []
        self.stock_acc_speed_mph = []
        self.stock_acc_speed_kph = []
        self.stock_acc_acceleration_mps2 = []
        self.stock_acc_acceleration_g = []
        
        self.stock_acc_soc = []
        self.stock_acc_speed_type = []
        
        self.stock_acc_soc_rate_highway = []
        self.stock_acc_soc_rate_city = []
        self.stock_acc_highway_distance_m = []
        self.stock_acc_city_distance_m = []
        self.stock_acc_highway_speed_mph = []
        self.stock_acc_city_speed_mph = []
        
        self.stock_acc_highway_distance_1000m = []
        self.stock_acc_city_distance_1000m = []
        self.stock_acc_1000m_highway_speed_mph = []
        self.stock_acc_1000m_city_speed_mph = []
        self.stock_acc_soc_rate_highway_1000m = []
        self.stock_acc_soc_rate_city_1000m = []
        
        
    def get_data_directory(self):
        """
            Method to get the Data directory irrespective of operating system
        """
        current_os = platform.system()

        if current_os == "Linux":
            data_directory = os.path.join(os.path.expanduser("~"), "Downloads", "2023-Hyundai-Ioniq5")
        elif current_os == "Windows":
            data_directory = os.path.join("C:\\", "Users", "ddas", "Documents", "Data", "2023-Hyundai-Ioniq5")
        else:
            raise OSError(f"Unsupported operating system: {current_os}")
        
        return data_directory
    
    def set_variables(self, file_path):
        calculated_accel = 0
        df = pd.read_csv(file_path)
        
        # num_rows = df.shape[0]
        # self.time_data = [round(0.1 * i, 1) for i in range(num_rows)]
        
        self.time_data = df['Time (abs)']
       
        self.speed_data_kph = df['wheel_spd_1__rpm']
        self.speed_data_mps = df['wheel_spd_1__rpm'] * 0.277778
        self.speed_data_mph = df['wheel_spd_1__rpm'] * 0.621371 
        
        for i in range(1, len(self.speed_data_mps)):
            previous_calculated_accel = calculated_accel
            dt = self.time_data[i] - self.time_data[i-1]
            calculated_accel = (self.speed_data_mps[i] - self.speed_data_mps[i-1]) / dt

            incremental_distance_m = self.speed_data_mps[i] * dt
            self.cumulative_distance_m += incremental_distance_m
            
            delta_soc = df['HVBatt_SOC_BMS__per'][i] - df['HVBatt_SOC_BMS__per'][i-1]
            delta_distance = incremental_distance_m / 1000  # convert to km
            soc_rate = delta_soc / delta_distance if delta_distance != 0 else 0

            
            # if self.speed_data_mph[i] >= 50:
            #     self.cumulative_highway_distance_m += incremental_distance_m
            #     self.stock_acc_highway_distance_m.append(self.cumulative_highway_distance_m)
            #     self.stock_acc_highway_speed_mph.append(self.speed_data_mph[i])
            #     self.stock_acc_soc_rate_highway.append(soc_rate)
            #     self.stock_acc_speed_type.append('Highway')
                
            #     self.cumulative_highway_distance_1000m += incremental_distance_m
            #     self.cumulative_soc_rate_highway_1000m += delta_soc
                
            #     if self.cumulative_highway_distance_1000m >= 1000:
            #         self.stock_acc_highway_distance_1000m.append(self.cumulative_highway_distance_1000m)
            #         self.stock_acc_soc_rate_highway_1000m.append(self.cumulative_soc_rate_highway_1000m / (self.cumulative_highway_distance_1000m / 1000))
            #         self.cumulative_highway_distance_1000m = 0
            #         self.cumulative_soc_rate_highway_1000m = 0                
            # else:
            #     self.cumulative_city_distance_m += incremental_distance_m
            #     self.stock_acc_city_distance_m.append(self.cumulative_city_distance_m)
            #     self.stock_acc_city_speed_mph.append(self.speed_data_mph[i])
            #     self.stock_acc_soc_rate_city.append(soc_rate)
            #     self.stock_acc_speed_type.append('City')
                
            #     self.cumulative_city_distance_1000m += incremental_distance_m
            #     self.cumulative_soc_rate_city_1000m += delta_soc
            #     if self.cumulative_city_distance_1000m >= 1000:
            #         self.stock_acc_city_distance_1000m.append(self.cumulative_city_distance_1000m)
            #         self.stock_acc_soc_rate_city_1000m.append(self.cumulative_soc_rate_city_1000m / (self.cumulative_city_distance_1000m / 1000))
            #         self.cumulative_city_distance_1000m = 0
            #         self.cumulative_soc_rate_city_1000m = 0
            

            self.stock_acc_time_data.append(dt)
            self.stock_acc_distance_m.append(self.cumulative_distance_m)
            self.stock_acc_distance_km.append(self.cumulative_distance_m / 1000)  # use cumulative
            self.stock_acc_speed_mph.append(self.speed_data_mph[i])
            self.stock_acc_speed_mps.append(self.speed_data_mps[i])
            self.stock_acc_speed_kph.append(self.speed_data_kph[i])
            self.stock_acc_acceleration_mps2.append(calculated_accel)
            self.stock_acc_soc.append(df['HVBatt_SOC_BMS__per'][i])

            if abs(calculated_accel - previous_calculated_accel) >= 0.1:
                self.stock_acc_acceleration_g.append(calculated_accel / g_value)
        
    def manage_test_data(self):
        data = pd.DataFrame()
        data_directory = self.get_data_directory()
        
        for test_file_name in self.stock_acc_test_file_list:
            csv_file_path = os.path.join(data_directory, test_file_name)
            
            self.set_variables(csv_file_path)

        
    def plot_soc_vs_distance(self):
        if not self.stock_acc_distance_km or not self.stock_acc_soc:
            print("SOC or distance data is empty. Make sure to run 'manage_test_data()' first.")
            return

        plt.figure(figsize=(10, 6))
        plt.plot(self.stock_acc_distance_km, self.stock_acc_soc, label='SOC vs Distance', color='green')
        plt.xlabel("Distance Traveled (km)")
        plt.ylabel("SOC (%)")
        plt.title("SOC vs. Distance Traveled")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        
    def plot_soc_vs_distance_vs_speed(self):
        if not self.stock_acc_distance_km or not self.stock_acc_soc:
            print("SOC or distance data is empty. Make sure to run 'manage_test_data()' first.")
            return

        plt.figure(figsize=(10, 6))
        plt.plot(self.stock_acc_distance_km, self.stock_acc_soc, label='SOC vs Distance', color='green')
        plt.scatter(self.stock_acc_distance_km, self.stock_acc_speed_mph, c=self.stock_acc_speed_mph, cmap='viridis', alpha=0.5)
        plt.colorbar(label='Speed (mph)')
        plt.xlabel("Distance Traveled (km)")
        plt.ylabel("SOC (%)")
        plt.title("SOC vs. Distance Traveled")
        plt.grid(True)
        plt.tight_layout()
        # plt.show()
        file_directory = "figure/on-road-soc_vs-distance-vs-speed.jpg"
        plt.savefig(file_directory, dpi=300)
        plt.close()
        
    # def plot_soc_vs_distance_vs_speed(self):
    #     if not self.stock_acc_distance_km or not self.stock_acc_soc:
    #         print("SOC or distance data is empty. Make sure to run 'manage_test_data()' first.")
    #         return

    #     fig, ax1 = plt.subplots(figsize=(12, 6))

    #     # Plot SOC vs. Distance (green line)
    #     ax1.plot(self.stock_acc_distance_km, self.stock_acc_soc, color='green', label='SOC (%)')
    #     ax1.set_xlabel("Distance Traveled (km)")
    #     ax1.set_ylabel("SOC (%)", color='green')
    #     ax1.tick_params(axis='y', labelcolor='green')

    #     # Create a second y-axis for speed
    #     ax2 = ax1.twinx()
    #     ax2.plot(self.stock_acc_distance_km, self.stock_acc_speed_mph, color='purple', alpha=0.5, label='Speed (mph)')
    #     ax2.set_ylabel("Speed (mph)", color='purple')
    #     ax2.tick_params(axis='y', labelcolor='purple')

    #     # Title and grid
    #     plt.title("SOC and Speed vs. Distance Traveled")
    #     ax1.grid(True)

    #     # Legend combining both axes
    #     lines1, labels1 = ax1.get_legend_handles_labels()
    #     lines2, labels2 = ax2.get_legend_handles_labels()
    #     ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

    #     plt.tight_layout()
    #     plt.show()
    
    
    def plot_distance_vs_soc_and_speed_colormap(self):
        if not self.stock_acc_distance_km or not self.stock_acc_soc or not self.stock_acc_speed_mph:
            print("Data is missing. Run 'manage_test_data()' first.")
            return

        distance = np.array(self.stock_acc_distance_km)
        soc = np.array(self.stock_acc_soc)
        speed_raw = np.array(self.stock_acc_speed_mph)

        # Smooth the speed
        window = 10
        speed = np.convolve(speed_raw, np.ones(window)/window, mode='same')

        # Create color-mapped speed segments
        points = np.array([distance, speed]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        norm = plt.Normalize(speed.min(), speed.max())
        lc = LineCollection(segments, cmap='turbo', norm=norm)
        lc.set_array(speed)
        lc.set_linewidth(2)

        fig, ax1 = plt.subplots(figsize=(12, 6))

        # Draw color-mapped speed line behind
        ax1.add_collection(lc)
        ax1.set_xlim(distance.min(), distance.max())
        ax1.set_ylim(soc.min(), soc.max())
        ax1.set_xlabel("Distance Traveled (km)")
        ax1.set_ylabel("SOC (%)", color='green')
        ax1.tick_params(axis='y', labelcolor='green')
        ax1.grid(True)

        # Overlay SOC plot with higher zorder
        ax1.plot(distance, soc, color='green', linewidth=2.5, label='SOC (%)', zorder=10)

        # Add colorbar using the original color line
        cbar = plt.colorbar(lc, ax=ax1)
        cbar.set_label("Speed (mph)")

        # Add secondary y-axis just for speed labeling (optional)
        ax2 = ax1.twinx()
        ax2.set_ylim(speed.min(), speed.max())
        ax2.set_ylabel("Speed (mph)", color='blue')
        ax2.tick_params(axis='y', labelcolor='blue')
        ax2.set_yticks(np.linspace(0, 100, 6))

        # plt.title("Distance vs SOC and Speed")
        plt.tight_layout()
        # plt.show()


        file_directory = "figure/on-road-distance-vs-soc-and-speed.jpg"
        plt.savefig(file_directory, dpi=300)
        plt.close()

    def plot_soc_rate_by_speed_group(self, mph_threshold=50):
        # Create a DataFrame from collected lists
        df = pd.DataFrame({
            'distance_km': self.stock_acc_distance_km,
            'speed_mph': self.stock_acc_speed_mph,
            'soc': self.stock_acc_soc,
        })

        # Compute delta SOC and delta distance
        df['delta_soc'] = df['soc'].diff().fillna(0)
        df['delta_distance'] = df['distance_km'].diff().fillna(0.000001)  # avoid divide-by-zero
        df['soc_rate'] = df['delta_soc'] / df['delta_distance']

        # Split into city and highway based on speed
        highway_df = df[df['speed_mph'] >= mph_threshold]
        city_df = df[df['speed_mph'] < mph_threshold]

        fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

        # Highway plot
        axes[0].scatter(highway_df['distance_km'], highway_df['soc_rate'], color='red', alpha=0.5, s=10)
        axes[0].set_title(f"SOC Rate Change (Highway Driving, Speed ≥ {mph_threshold} mph)")
        axes[0].set_ylabel("ΔSOC / ΔDistance (%/km)")
        axes[0].grid(True)

        # City plot
        axes[1].scatter(city_df['distance_km'], city_df['soc_rate'], color='blue', alpha=0.5, s=10)
        axes[1].set_title(f"SOC Rate Change (City Driving, Speed < {mph_threshold} mph)")
        axes[1].set_xlabel("Distance Traveled (km)")
        axes[1].set_ylabel("ΔSOC / ΔDistance (%/km)")
        axes[1].grid(True)

        plt.tight_layout()
        plt.show()

    
    def plot_soc_rate_subplots_by_speed_type(self):
        fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=False)

        # --- Subplot 1: Highway Driving ---
        axes[0].scatter(self.stock_acc_highway_distance_m, self.stock_acc_soc_rate_highway, 
                        color='red', alpha=0.6, s=10)
        axes[0].set_title("SOC Rate Change - Highway Driving (Speed ≥ 50 mph)")
        axes[0].set_ylabel("ΔSOC / ΔDistance (%/km)")
        axes[0].grid(True)

        # --- Subplot 2: City Driving ---
        axes[1].scatter(self.stock_acc_city_distance_m, self.stock_acc_soc_rate_city, 
                        color='blue', alpha=0.6, s=10)
        axes[1].set_title("SOC Rate Change - City Driving (Speed < 50 mph)")
        axes[1].set_xlabel("Cumulative Distance Traveled (km)")
        axes[1].set_ylabel("ΔSOC / ΔDistance (%/km)")
        axes[1].grid(True)

        plt.tight_layout()
        plt.show()

    def plot_soc_change_per_1000m_by_speed_type(self):
        fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=False)

        # Subplot 1: Highway
        axes[0].scatter(self.stock_acc_highway_distance_1000m,
                        self.stock_acc_soc_rate_highway_1000m,
                        color='red', alpha=0.6, s=20)
        axes[0].set_title("SOC Change per 1000m - Highway Driving")
        axes[0].set_ylabel("ΔSOC per km (%)")
        axes[0].grid(True)

        # Subplot 2: City
        axes[1].scatter(self.stock_acc_city_distance_1000m,
                        self.stock_acc_soc_rate_city_1000m,
                        color='blue', alpha=0.6, s=20)
        axes[1].set_title("SOC Change per 1000m - City Driving")
        axes[1].set_xlabel("Cumulative Distance (m)")
        axes[1].set_ylabel("ΔSOC per km (%)")
        axes[1].grid(True)

        plt.tight_layout()
        plt.show()

   
'''##############################################
                   Unit testing
##############################################'''
if __name__ == "__main__":
    import json
    configFile = open("config-files/configuration.json", 'r')
    config = (json.load(configFile))
    configFile.close()
    ioniq5_analyzer = Ioniq5Analyzer(config)
    ioniq5_analyzer.manage_test_data()
    # ioniq5_analyzer.plot_soc_vs_distance()
    # ioniq5_analyzer.plot_soc_vs_distance_vs_speed()
    ioniq5_analyzer.plot_distance_vs_soc_and_speed_colormap()
    # ioniq5_analyzer.plot_soc_rate_by_speed_group(mph_threshold=50)
    # ioniq5_analyzer.plot_soc_rate_subplots_by_speed_type()
    # ioniq5_analyzer.plot_soc_change_per_1000m_by_speed_type()