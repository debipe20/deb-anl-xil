# Complete Object-Oriented Analysis Script for Hyundai Ioniq 5 On-Road Data
import platform
import os
import pandas as pd
import matplotlib.pyplot as plt

class Ioniq5Analyzer:
    def __init__(self, dataframe):
        self.df = dataframe.copy()
        # Parse datetime and remove timezones for consistent plotting
        self.df['timestamp'] = pd.to_datetime(self.df['Date'] + ' ' + self.df['Time'], errors='coerce', utc=True)
        self.df['timestamp'] = self.df['timestamp'].dt.tz_convert(None)
        self.df['time_diff'] = self.df['timestamp'].diff().dt.total_seconds().fillna(0)
        # self.df['speed_mps'] = self.df['Q5GPS_Speed'] * 1000 / 3600
        self.df['speed_mps'] = self.df['wheel_spd_1__rpm'] * 0.277778
        # self.df['delta_distance'] = self.df['speed_mps'] * self.df['time_diff']
        self.df['delta_distance'] = self.df['speed_mps'] * 0.1
        self.df['distance_km'] = self.df['delta_distance'].cumsum() / 1000
        
         # Convert speed to mph
        self.df['speed_mph'] = self.df['wheel_spd_1__rpm'] * 0.621371

        # Compute SOC rate of change
        self.df['delta_soc'] = self.df['HVBatt_SOC_BMS__per'].diff().fillna(0)
        self.df['soc_rate'] = self.df['delta_soc'] / self.df['delta_distance'].replace(0, 1e-6)  # avoid div by zero


    def plot_soc_over_time(self):
        plt.figure(figsize=(12, 5))
        plt.plot(self.df['timestamp'], self.df['HVBatt_SOC_BMS__per'], label='SOC (%)')
        plt.xlabel('Time')
        plt.ylabel('State of Charge (%)')
        plt.title('Battery SOC Over Time')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def motor_torque_analysis(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.df['timestamp'], self.df['motor_f_torque_actual_MCU__Nm'], label='Front Motor Torque Actual')
        plt.plot(self.df['timestamp'], self.df['motor_f_torque_desired_MCU__Nm'], label='Front Motor Torque Desired', alpha=0.7)
        plt.plot(self.df['timestamp'], self.df['motor_r_torque_actual_MCU__Nm'], label='Rear Motor Torque Actual')
        plt.plot(self.df['timestamp'], self.df['motor_r_torque_desired_MCU__Nm'], label='Rear Motor Torque Desired', alpha=0.7)
        plt.xlabel('Time')
        plt.ylabel('Torque (Nm)')
        plt.title('Motor Torque Over Time')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def speed_profile(self):
        plt.figure(figsize=(12, 5))
        plt.plot(self.df['timestamp'], self.df['veh_speed_HVAC__kph'], label='Vehicle Speed (HVAC)')
        plt.plot(self.df['timestamp'], self.df['Q5GPS_Speed'], label='Vehicle Speed (GPS)', alpha=0.7)
        plt.xlabel('Time')
        plt.ylabel('Speed (kph)')
        plt.title('Vehicle Speed Profile')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def battery_temperature_profile(self):
        plt.figure(figsize=(12, 5))
        plt.plot(self.df['timestamp'], self.df['HVBatt_max_temp_BMS__C'], label='Max Battery Temp')
        plt.plot(self.df['timestamp'], self.df['HVBatt_min_temp_BMS__C'], label='Min Battery Temp')
        plt.xlabel('Time')
        plt.ylabel('Temperature (°C)')
        plt.title('Battery Temperature Profile')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        
    def soc_vs_distance_plot(self):
        plt.figure(figsize=(12, 5))
        plt.plot(self.df['distance_km'], self.df['HVBatt_SOC_BMS__per'], label='SOC vs Distance')
        plt.xlabel('Distance Traveled (km)')
        plt.ylabel('State of Charge (%)')
        plt.title('Battery SOC vs Distance Traveled')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        
        
    def plot_soc_rate_by_speed_group(self, mph_threshold=50):
        high_speed_df = self.df[self.df['speed_mph'] > mph_threshold]
        low_speed_df = self.df[self.df['speed_mph'] <= mph_threshold]

        fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

        # Subplot 1: High-speed SOC drop rate
        axes[0].plot(high_speed_df['distance_km'], high_speed_df['soc_rate'], color='red')
        axes[0].set_title(f"SOC Change Rate at Speed > {mph_threshold} mph")
        axes[0].set_ylabel("ΔSOC / ΔDistance (%/km)")
        axes[0].grid(True)

        # Subplot 2: Low-speed SOC drop rate
        axes[1].plot(low_speed_df['distance_km'], low_speed_df['soc_rate'], color='blue')
        axes[1].set_title(f"SOC Change Rate at Speed ≤ {mph_threshold} mph")
        axes[1].set_xlabel("Distance Traveled (km)")
        axes[1].set_ylabel("ΔSOC / ΔDistance (%/km)")
        axes[1].grid(True)

        plt.tight_layout()
        plt.show()

   
# --- Data Loading and Execution (example usage) ---

# Load the CSVs (adjust path if running independently)
file1 = r"C:\Users\ddas\Documents\Data\2023-Hyundai-Ioniq5\On-Road 2025-04-03 07-06-01-920000.csv"

file2 = r"C:\Users\ddas\Documents\Data\2023-Hyundai-Ioniq5\On-Road 2025-04-03 08-12-21-651000.csv"

file3 = r"C:\Users\ddas\Documents\Data\2023-Hyundai-Ioniq5\On-Road 2025-04-03 09-36-27-040000.csv"
file4 = r"C:\Users\ddas\Documents\Data\2023-Hyundai-Ioniq5\On-Road 2025-04-03 10-35-30-090000.csv"
file5 = r"C:\Users\ddas\Documents\Data\2023-Hyundai-Ioniq5\On-Road 2025-04-03 11-39-16-145000.csv"

df1 = pd.read_csv(file1)
df2 = pd.read_csv(file2)
df3 = pd.read_csv(file3)
df4 = pd.read_csv(file4)
df5 = pd.read_csv(file5)

# Combine both datasets
combined_df = pd.concat([df1, df2, df3, df4, df5], ignore_index=True)

# Run analysis
analyzer = Ioniq5Analyzer(combined_df)
# analyzer.plot_soc_over_time()
# analyzer.motor_torque_analysis()
# analyzer.speed_profile()
# analyzer.battery_temperature_profile()

analyzer.soc_vs_distance_plot()
# analyzer.plot_soc_rate_by_speed_group(mph_threshold=50)
