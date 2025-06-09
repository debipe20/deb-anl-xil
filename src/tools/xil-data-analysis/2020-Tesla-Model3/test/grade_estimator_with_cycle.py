import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import haversine

def compute_road_grade(udds_df, gps_df):
    """
    Compute smoothed road grade for the UDDS cycle using GPS elevation data.

    Logic:
        - Align UDDS and GPS lengths.
        - Compute Haversine distance and elevation change.
        - Calculate road grade = (delta elevation / horizontal distance) * 100.
        - Smooth the grade with a centered rolling average.

    Parameters:
        udds_df (DataFrame): UDDS cycle with 'Time (s)', 'Speed (mph)', etc.
        gps_df (DataFrame): GPS data with 'latitude', 'longitude', 'elevation(m)'.

    Returns:
        DataFrame: Updated UDDS dataframe with new 'Grade' column.
        float: Max smoothed grade.
        float: Min smoothed grade.
    """
    udds_df['Speed (m/s)'] = udds_df['Speed (mph)'] * 0.44704

    min_len = min(len(udds_df), len(gps_df))
    udds_trimmed = udds_df.iloc[:min_len].copy()
    gps_trimmed = gps_df.iloc[:min_len].copy()

    gps_trimmed['smoothed_elevation'] = gps_trimmed['elevation(m)'].rolling(window=3, center=True).mean()

    grades = [None]
    for i in range(1, min_len):
        lat1, lon1 = gps_trimmed.loc[i - 1, ['latitude', 'longitude']]
        lat2, lon2 = gps_trimmed.loc[i, ['latitude', 'longitude']]
        ele1 = gps_trimmed.loc[i - 1, 'smoothed_elevation']
        ele2 = gps_trimmed.loc[i, 'smoothed_elevation']

        if pd.notna([lat1, lon1, lat2, lon2, ele1, ele2]).all():
            dist = haversine.haversine((lat1, lon1), (lat2, lon2), unit=haversine.Unit.METERS)
            delta_elev = ele2 - ele1
            grade = (delta_elev / dist) * 100 if dist > 0 else 0
        else:
            grade = None

        grades.append(grade)

    udds_trimmed['raw_grade'] = grades
    
    ## Without Controlling Min/Max Grade
    # udds_trimmed['Grade'] = udds_trimmed['raw_grade'].rolling(window=15, center=True).mean().round(1)
    # # Fill missing grades with forward fill, fallback to 0
    # udds_trimmed['Grade'] = udds_trimmed['Grade'].fillna(method='ffill').fillna(0)
    
    
    # Smooth and round the grade by controlling min and max grade values
    smoothed = (udds_trimmed['raw_grade'].rolling(window=15, center=True).mean().round(1).fillna(method='ffill').fillna(0))

    # Clip to range [-6.0, 6.0]
    udds_trimmed['Grade'] = smoothed.clip(lower=-5.9, upper=6.0)

    # Drop raw if not needed
    udds_trimmed.drop(columns='raw_grade', inplace=True)

    max_grade = udds_trimmed['Grade'].max(skipna=True)
    min_grade = udds_trimmed['Grade'].min(skipna=True)

    return udds_trimmed, max_grade, min_grade

def export_grade_to_csv(df, filename="UDDS-cycle_dynamic_grade.csv"):
    """
    Export the UDDS cycle with computed Grade column to CSV format.

    Parameters:
        df (DataFrame): DataFrame with columns including 'Grade'.
        filename (str): Output file name.
    """
    export_cols = ['Time (s)', 'Speed (mph)', 'Gear', 'Bag', 'Grade']
    df[export_cols].to_csv(filename, index=False)
    print(f"✅ CSV exported: {filename}")

def plot_speed_and_grade(df):
    """
    Plot UDDS cycle speed and computed smoothed road grade.

    Parameters:
        df (DataFrame): Must contain 'Time (s)', 'Speed (mph)', 'Grade'.
    """
    fig, ax1 = plt.subplots(figsize=(14, 6))

    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Speed (mph)", color='tab:blue')
    ax1.plot(df['Time (s)'], df['Speed (mph)'], color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.set_ylabel("Smoothed Grade (%)", color='tab:red')
    ax2.plot(df['Time (s)'], df['Grade'], color='tab:red', linestyle='--')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    plt.title("UDDS Cycle: Speed and Smoothed Road Grade Profile")
    fig.tight_layout()
    plt.grid(True)
    plt.show()

def main():
    """
    Main function:
        - Loads input CSVs.
        - Computes smoothed road grade.
        - Saves updated cycle to CSV.
        - Visualizes results.
    """
    udds_df = pd.read_csv("UDDS-cycle_zero_grade.csv")
    gps_df = pd.read_csv("DaisyMountainArizona.csv")

    udds_with_grade, max_grade, min_grade = compute_road_grade(udds_df, gps_df)

    print(f"📈 Max smoothed road grade: {max_grade:.1f}%")
    print(f"📉 Min smoothed road grade: {min_grade:.1f}%")

    export_grade_to_csv(udds_with_grade)
    plot_speed_and_grade(udds_with_grade)

if __name__ == "__main__":
    main()
