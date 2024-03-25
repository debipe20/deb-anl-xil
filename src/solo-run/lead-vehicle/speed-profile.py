import numpy as np
import matplotlib.pyplot as plt

# Define parameters
acceleration_time = 2  # Time taken to accelerate from 0 to 5 m/s (seconds)
constant_speed_duration = 10  # Duration of constant speed at 5 m/s (seconds)
deceleration_time = 2  # Time taken to decelerate from 5 to 0 m/s (seconds)

# Calculate total time
total_time = acceleration_time + constant_speed_duration + deceleration_time

# Create time array
time = np.linspace(0, total_time, 1000)

# Create speed profile
acceleration = time <= acceleration_time
deceleration = time >= (total_time - deceleration_time)
constant_speed = np.logical_and(~acceleration, ~deceleration)

speed = np.zeros_like(time)  # Initialize speed array with zeros
speed[acceleration] = 5 * time[acceleration] / acceleration_time  # Acceleration phase
speed[constant_speed] = 5  # Constant speed phase
speed[deceleration] = 5 - 5 * (time[deceleration] - (total_time - deceleration_time)) / deceleration_time  # Deceleration phase

# Plot the speed profile
plt.plot(time, speed, color='blue')
plt.title('Speed Profile')
plt.xlabel('Time (seconds)')
plt.ylabel('Speed (m/s)')
plt.grid(True)
plt.show()
