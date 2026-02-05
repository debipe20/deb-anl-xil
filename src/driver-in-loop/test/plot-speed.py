import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
file_path = '../../../log/debug/carla_lead_controller_log.csv'
df = pd.read_csv(file_path)

# Strip any leading/trailing whitespace from column names
df.columns = df.columns.str.strip()

# Convert timestamp to relative time in seconds
df['time'] = df['timestamp'] - df['timestamp'].iloc[0]

# Plotting time vs desired_speed and current_speed
plt.figure(figsize=(12, 6))
plt.plot(df['time'], df['desired_speed'], label='Desired Speed')
plt.plot(df['time'], df['current_speed'], label='Current Speed', linestyle='--')
plt.xlabel('Time (seconds)')
plt.ylabel('Speed (mph)')
plt.title('Time vs Desired and Current Speed')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(12, 6))
plt.plot(df['time'], df['control'], label='Control', linestyle='--')
plt.plot(df['time'], df['throttle'], label='Throttle', linestyle='-')
plt.plot(df['time'], df['brake'], label='Brake', linestyle=':')
plt.plot(df['time'], df['steer'], label='Steer', linestyle='-.') 
plt.xlabel('Time (seconds)')
plt.ylabel('Value')
plt.title('Control, Throttle, and Brake over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
