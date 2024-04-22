import pandas as pd
import matplotlib.pyplot as plt

# Replace the list with the paths to your local CSV files
csv_files = [
    '20240405-180405_ORNL-AUTO-1_eco_data.csv',
    '20240405-180636_carma_1_eco_data.csv',
    '20240405-180637_MCITY-CAV-01_eco_data.csv',
    '20240405-180641_UCLA-OPENCDA_eco_data.csv',
    '20240405-180644_ANL-DYNO-1_eco_data.csv'
]

# Read each file and plot the calculated_speed with respect to current_time
for file_path in csv_files:
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)
    
    # Ensure 'calculated_speed' and 'current_time' columns exist
    if 'calculated_speed' in df.columns and 'current_time' in df.columns:
        # Plot calculated_speed over time
        plt.plot(pd.to_datetime(df['current_time']), df['smoothed_speed'], label=file_path)

plt.title('Calculated Speed Over Time for Multiple Files')
plt.xlabel('Time')
plt.ylabel('Calculated Speed (units)')
plt.legend()
plt.show()