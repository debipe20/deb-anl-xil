import pandas as pd
import matplotlib.pyplot as plt

# Create a sample dataset similar to the one in your plot
data = {
    'Time': list(range(0, 1000, 10)),  # Time from 0 to 900 seconds with 10-second intervals
    'Speed': [10 + (i % 10) for i in range(100)],  # Oscillating speed between 10 and 20 mph
    'Acceleration': [0.5 if i < 200 else 1 if i < 400 else 2 if i < 600 else 3 if i < 800 else 4 for i in range(100)],
    'Jerk': [(-1)**i * (0.5 if i < 200 else 1 if i < 400 else 4) for i in range(100)]  # Varying jerk values
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Create a new plot
fig, ax = plt.subplots(figsize=(12, 6))

# Plot for different jerk values (similar to your image)
ax.plot(df['Time'], df['Speed'], label='jerk=+/-0.5 mps³', color='blue')
ax.plot(df['Time'], df['Speed'], label='jerk=+/-1 mps³', color='red')
ax.plot(df['Time'], df['Speed'], label='jerk=+/-4 mps³', color='orange')

# Set plot labels, title, and legend
ax.set_xlabel('Time [sec]')
ax.set_ylabel('Vehicle Speed [mph]')
ax.set_title('Dynamic Response Tests Overview 10 to 20mph')

# Add horizontal lines representing speed limits
ax.axhline(y=10, color='magenta', linestyle='-', linewidth=2)
ax.axhline(y=20, color='green', linestyle='-', linewidth=2)

# Custom ticks and text annotations for acceleration segments (optional)
ax.text(50, 21, '0.5 m/s²', ha='center')
ax.text(150, 21, '1 m/s²', ha='center')
ax.text(300, 21, '2 m/s²', ha='center')
ax.text(450, 21, '3 m/s²', ha='center')
ax.text(600, 21, '4 m/s²', ha='center')

# Add a legend
ax.legend()

# Show the plot
plt.show()
