"""
 Line graph with single speed range
"""

# import matplotlib.pyplot as plt
# import pandas as pd
# import seaborn as sns

# # Sample Data
# data = {
#     'Acceleration (m/s²)': [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
#     'Vehicle A': [3.2, 2.8, 2.5, 2.3, 2.0, 1.8, 1.7, 1.5, 1.4, 1.3],
#     'Vehicle B': [3.5, 3.0, 2.7, 2.4, 2.2, 2.0, 1.9, 1.7, 1.5, 1.4],
#     'Vehicle C': [4.0, 3.6, 3.2, 2.8, 2.5, 2.2, 2.0, 1.8, 1.7, 1.5],
# }

# df = pd.DataFrame(data)

# #Plot multiple line graph
# plt.figure(figsize=(10, 6))
# for vehicle in df.columns[1:]:  # Excluding 'Acceleration (m/s²)'
#     plt.plot(df['Acceleration (m/s²)'], df[vehicle], marker='o', label=vehicle)

# # Labels and title
# plt.xlabel("Acceleration (m/s²)")
# plt.ylabel("Response Time (s)")
# plt.title("Response Time vs Acceleration for Multiple Vehicles")
# plt.legend()
# plt.grid(True)
# plt.show()

# #Heat Map
# heatmap_df = df.set_index('Acceleration (m/s²)')

# plt.figure(figsize=(10, 7))
# sns.heatmap(heatmap_df.T, annot=True, cmap="coolwarm", linewidths=0.5)
# plt.xlabel("Acceleration (m/s²)")
# plt.ylabel("Vehicle")
# plt.title("Heatmap of Response Time vs Acceleration for Multiple Vehicles")
# plt.show()

"""
    Line graph with multiple speed range 2D plot
"""

# Sample Data: Response Time over Acceleration for Multiple Vehicles at Different Speed Ranges
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt

# # Define acceleration levels
# acceleration_levels = np.array([0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0])

# # Simulated response time for multiple vehicles at different speed ranges
# speed_ranges = ["0-20mph", "20-40mph", "40-60mph", "60-80mph"]
# vehicles = ["Vehicle A", "Vehicle B", "Vehicle C"]

# # Create a dictionary to hold the data
# data = {"Acceleration (m/s²)": np.tile(acceleration_levels, len(speed_ranges) * len(vehicles)),
#         "Speed Range": np.repeat(speed_ranges, len(acceleration_levels) * len(vehicles)),
#         "Vehicle": np.tile(np.repeat(vehicles, len(acceleration_levels)), len(speed_ranges))}

# # Generate synthetic response times
# np.random.seed(42)
# response_times = []
# for speed in speed_ranges:
#     for vehicle in vehicles:
#         base_time = 4.0 if vehicle == "Vehicle A" else (3.5 if vehicle == "Vehicle B" else 3.0)
#         speed_factor = 0.05 * speed_ranges.index(speed)
#         response_times.extend([base_time - (a * 0.3) + speed_factor + np.random.normal(0, 0.1) for a in acceleration_levels])

# data["Response Time (s)"] = response_times

# # Convert to DataFrame
# df = pd.DataFrame(data)

# # Plot Line Graph for Different Speed Ranges
# plt.figure(figsize=(10, 6))
# for speed_range in speed_ranges:
#     subset = df[df["Speed Range"] == speed_range]
#     for vehicle in vehicles:
#         vehicle_data = subset[subset["Vehicle"] == vehicle]
#         plt.plot(vehicle_data["Acceleration (m/s²)"], vehicle_data["Response Time (s)"],
#                  marker='o', linestyle='-', label=f"{vehicle} ({speed_range})")

# # Labels and title
# plt.xlabel("Acceleration (m/s²)")
# plt.ylabel("Response Time (s)")
# plt.title("Response Time vs Acceleration for Multiple Vehicles Across Speed Ranges")
# plt.legend(loc="upper right", fontsize=8)
# plt.grid(True)
# # plt.show()
# plt.savefig("response-time-vs-acceleration-speed-range-2d.png") 
# plt.close()



"""
    Line graph with multiple speed range 3D plot
"""
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D

# # Define acceleration levels
# acceleration_levels = np.array([0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0])

# # Define speed ranges and vehicle types
# speed_ranges = ["0-20mph", "20-40mph", "40-60mph", "60-80mph"]
# vehicles = ["Vehicle A", "Vehicle B", "Vehicle C"]

# # Create a dictionary to hold the data
# data = {
#     "Acceleration (m/s²)": np.tile(acceleration_levels, len(speed_ranges) * len(vehicles)),
#     "Speed Range": np.repeat(speed_ranges, len(acceleration_levels) * len(vehicles)),
#     "Vehicle": np.tile(np.repeat(vehicles, len(acceleration_levels)), len(speed_ranges)),
# }

# # Generate synthetic response times with some variation
# np.random.seed(42)
# response_times = []
# for speed in speed_ranges:
#     for vehicle in vehicles:
#         base_time = 4.0 if vehicle == "Vehicle A" else (3.5 if vehicle == "Vehicle B" else 3.0)
#         speed_factor = 0.05 * speed_ranges.index(speed)
#         response_times.extend([base_time - (a * 0.3) + speed_factor + np.random.normal(0, 0.1) for a in acceleration_levels])

# data["Response Time (s)"] = response_times

# # Convert to DataFrame
# df = pd.DataFrame(data)

# # Map speed ranges to numeric values for plotting in 3D
# speed_range_mapping = {speed: idx for idx, speed in enumerate(speed_ranges)}
# df["Speed Range Numeric"] = df["Speed Range"].map(speed_range_mapping)

# # Create a 3D plot
# fig = plt.figure(figsize=(10, 7))
# ax = fig.add_subplot(111, projection='3d')

# # Define colors for different vehicles
# colors = {"Vehicle A": "r", "Vehicle B": "g", "Vehicle C": "b"}

# # Plot data points for each vehicle
# for vehicle in vehicles:
#     subset = df[df["Vehicle"] == vehicle]
#     ax.scatter(subset["Acceleration (m/s²)"], subset["Speed Range Numeric"], subset["Response Time (s)"],
#                label=vehicle, color=colors[vehicle], marker='o')

# # Set axis labels and title
# ax.set_xlabel("Acceleration (m/s²)")
# ax.set_ylabel("Speed Range (mph)")
# ax.set_zlabel("Response Time (s)")
# ax.set_title("3D Plot of Response Time vs Acceleration & Speed Ranges")

# # Convert numeric speed values back to labels for clarity
# ax.set_yticks(list(speed_range_mapping.values()))
# ax.set_yticklabels(speed_ranges)

# # Rotate the plot for better visibility
# ax.view_init(elev=20, azim=135)

# # Show legend
# ax.legend(loc="upper right")

# # plt.show()
# plt.savefig("response-time-vs-acceleration-speed-range-3d.png") 
# plt.close()


"""
    Surface Plot with multiple speed range 3D plot
"""

# Import required libraries
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# from scipy.interpolate import griddata

# # Define acceleration levels
# acceleration_levels = np.array([0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0])

# # Define speed ranges and vehicle types
# speed_ranges = ["0-20mph", "20-40mph", "40-60mph", "60-80mph"]
# vehicles = ["Vehicle A", "Vehicle B", "Vehicle C"]

# # Create a dictionary to hold the data
# data = {
#     "Acceleration (m/s²)": np.tile(acceleration_levels, len(speed_ranges) * len(vehicles)),
#     "Speed Range": np.repeat(speed_ranges, len(acceleration_levels) * len(vehicles)),
#     "Vehicle": np.tile(np.repeat(vehicles, len(acceleration_levels)), len(speed_ranges)),
# }

# # Generate synthetic response times with some variation
# np.random.seed(42)
# response_times = []
# for speed in speed_ranges:
#     for vehicle in vehicles:
#         base_time = 4.0 if vehicle == "Vehicle A" else (3.5 if vehicle == "Vehicle B" else 3.0)
#         speed_factor = 0.05 * speed_ranges.index(speed)
#         response_times.extend([base_time - (a * 0.3) + speed_factor + np.random.normal(0, 0.1) for a in acceleration_levels])

# data["Response Time (s)"] = response_times

# # Convert to DataFrame
# df = pd.DataFrame(data)

# # Map speed ranges to numeric values for plotting in 3D
# speed_range_mapping = {speed: idx for idx, speed in enumerate(speed_ranges)}
# df["Speed Range Numeric"] = df["Speed Range"].map(speed_range_mapping)

# # Prepare data for surface plot
# X = df["Acceleration (m/s²)"].values
# Y = df["Speed Range Numeric"].values
# Z = df["Response Time (s)"].values

# # Create grid for surface plot
# xi = np.linspace(min(X), max(X), 30)  # Fine grid for acceleration
# yi = np.linspace(min(Y), max(Y), 30)  # Fine grid for speed range
# Xi, Yi = np.meshgrid(xi, yi)
# Zi = griddata((X, Y), Z, (Xi, Yi), method='cubic')  # Interpolate response times

# # Create 3D surface plot for multiple vehicles
# fig = plt.figure(figsize=(12, 8))
# ax = fig.add_subplot(111, projection='3d')

# # Define colors for different vehicles
# colors = {"Vehicle A": "Reds", "Vehicle B": "Greens", "Vehicle C": "Blues"}

# # Plot surface for each vehicle
# for vehicle in vehicles:
#     subset = df[df["Vehicle"] == vehicle]
#     X = subset["Acceleration (m/s²)"].values
#     Y = subset["Speed Range Numeric"].values
#     Z = subset["Response Time (s)"].values

#     # Create grid for surface plot
#     xi = np.linspace(min(X), max(X), 30)  
#     yi = np.linspace(min(Y), max(Y), 30)  
#     Xi, Yi = np.meshgrid(xi, yi)
#     Zi = griddata((X, Y), Z, (Xi, Yi), method='cubic')  

#     # Plot surface for each vehicle with a unique color map
#     surf = ax.plot_surface(Xi, Yi, Zi, cmap=colors[vehicle], edgecolor='k', alpha=0.7, label=vehicle)

# # Set labels and title
# ax.set_xlabel("Acceleration (m/s²)")
# ax.set_ylabel("Speed Range (mph)", labelpad=15)  # Move axis label away for clarity
# ax.set_zlabel("Response Time (s)")
# ax.set_title("3D Surface Plot of Response Time vs Acceleration & Speed Ranges for Multiple Vehicles")

# # Convert numeric speed values back to labels
# ax.set_yticks(list(speed_range_mapping.values()))
# ax.set_yticklabels(speed_ranges)

# # Add color bar and move it to the right
# cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, pad=0.15, label="Response Time (s)")

# # Rotate for better visibility
# ax.view_init(elev=25, azim=135)

# plt.show()


"""
Step Response Plot (Control System Analysis)
"""

# import numpy as np
# import matplotlib.pyplot as plt

# # Simulated step response from acceleration requested to achieved
# time = np.linspace(0, 5, 100)  # Time from 0 to 5 seconds
# accel_requested = np.ones_like(time) * 2  # Requested acceleration (2 m/s²)
# accel_achieved = 2 * (1 - np.exp(-time))  # Simulated first-order response

# # Plot step response
# plt.figure(figsize=(10, 6))
# plt.plot(time, accel_requested, linestyle="dashed", label="Requested Acceleration", color="red")
# plt.plot(time, accel_achieved, label="Achieved Acceleration", color="blue")

# # Customize plot
# plt.xlabel("Time (s)", fontsize=14)
# plt.ylabel("Acceleration (m/s²)", fontsize=14)
# plt.title("Step Response: Acceleration Requested vs. Achieved", fontsize=16)
# plt.legend()
# plt.grid(True)

# # Show plot
# plt.show()

"""
Frequency Response (Bode Plot)
"""

# import control as ctrl  # Control system toolbox for frequency analysis
# import matplotlib.pyplot as plt

# # Define a simple transfer function for acceleration response
# num = [1]  # Numerator (gain)
# den = [1, 2, 1]  # Denominator (second-order system)
# sys = ctrl.TransferFunction(num, den)

# # Generate Bode plot
# plt.figure(figsize=(10, 6))
# ctrl.bode_plot(sys, dB=True)
# plt.show()


"""
3D Plot
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Define acceleration levels
acceleration_levels = np.array([0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0])

# Define speed ranges and vehicle types
speed_ranges = ["0-20mph", "20-40mph", "40-60mph", "60-80mph"]
vehicles = ["Vehicle A", "Vehicle B", "Vehicle C"]

# Create a dictionary to hold the data
data = {
    "Acceleration (m/s²)": np.tile(acceleration_levels, len(speed_ranges) * len(vehicles)),
    "Speed Range": np.repeat(speed_ranges, len(acceleration_levels) * len(vehicles)),
    "Vehicle": np.tile(np.repeat(vehicles, len(acceleration_levels)), len(speed_ranges)),
}

# Generate synthetic response times with some variation
np.random.seed(42)
response_times = []
for speed in speed_ranges:
    for vehicle in vehicles:
        base_time = 4.0 if vehicle == "Vehicle A" else (3.5 if vehicle == "Vehicle B" else 3.0)
        speed_factor = 0.05 * speed_ranges.index(speed)
        response_times.extend([base_time - (a * 0.3) + speed_factor + np.random.normal(0, 0.1) for a in acceleration_levels])

data["Response Time (s)"] = response_times

# Convert to DataFrame
df = pd.DataFrame(data)

# Map speed ranges to numeric values for plotting in 3D
speed_range_mapping = {speed: idx for idx, speed in enumerate(speed_ranges)}
df["Speed Range Numeric"] = df["Speed Range"].map(speed_range_mapping)

# Create a 3D plot
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

# Define colors for different vehicles
colors = {"Vehicle A": "r", "Vehicle B": "g", "Vehicle C": "b"}

# Plot data points for each vehicle
for vehicle in vehicles:
    subset = df[df["Vehicle"] == vehicle]
    ax.scatter(subset["Acceleration (m/s²)"], subset["Speed Range Numeric"], subset["Response Time (s)"],
               label=vehicle, color=colors[vehicle], marker='o')

# Set axis labels and title
ax.set_xlabel("Acceleration (m/s²)")
ax.set_ylabel("Speed Range (mph)")
ax.set_zlabel("Response Time (s)")
ax.set_title("3D Plot of Response Time vs Acceleration & Speed Ranges")

# Convert numeric speed values back to labels for clarity
ax.set_yticks(list(speed_range_mapping.values()))
ax.set_yticklabels(speed_ranges)

# Rotate the plot for better visibility
ax.view_init(elev=20, azim=135)

# Show legend
ax.legend(loc="upper right")

plt.show()
