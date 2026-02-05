import folium
import pandas as pd
import math
import haversine


# Function to determine the threshold distance based on speed
def get_threshold_by_speed(speed):
    if speed > 50:
        return 15  # Threshold of 5 meters for speeds over 50 mph
    elif speed > 30:
        return 15  # Threshold of 3 meters for speeds between 30-50 mph
    else:
        return 15  # Threshold of 1 meter for speeds between 0-30 mph

# List of file paths for multiple CSV files
files = [
    r"C:\Users\ddas\Documents\Data\2023-Hyundai-Ioniq5\On-Road 2025-04-03 07-06-01-920000.csv",
    # r"C:\Users\ddas\Documents\Data\2023-Hyundai-Ioniq5\On-Road 2025-04-03 08-12-21-651000.csv",
    r"C:\Users\ddas\Documents\Data\2023-Hyundai-Ioniq5\On-Road 2025-04-03 09-36-27-040000.csv",
    r"C:\Users\ddas\Documents\Data\2023-Hyundai-Ioniq5\On-Road 2025-04-03 10-35-30-090000.csv",
    r"C:\Users\ddas\Documents\Data\2023-Hyundai-Ioniq5\On-Road 2025-04-03 11-39-16-145000.csv"
]

# Create a base map (using the first file to center the map)
df_first = pd.read_csv(files[0])
latitudes = df_first['Q5GPS_Latitude']
longitudes = df_first['Q5GPS_Longitude']
m = folium.Map(location=[latitudes.iloc[0], longitudes.iloc[0]], zoom_start=13)

# Loop through each file and add its route to the map
for file in files:
    # Load GPS data from each file
    df = pd.read_csv(file)
    
    # Extract latitude, longitude, and speed columns
    latitudes = df['Q5GPS_Latitude'] 
    longitudes = df['Q5GPS_Longitude']
    speeds = df['wheel_spd_1__rpm'] * 0.621371 # Assuming the speed column is in kph, so converted to mph
    
    # Filter out points where the distance from the previous point is less than the dynamic threshold
    filtered_route = []
    prev_lat, prev_lon = latitudes.iloc[0], longitudes.iloc[0]
    filtered_route.append((prev_lat, prev_lon))  # Start with the first point
    
    for i in range(1, len(latitudes)):
        curr_lat, curr_lon = latitudes.iloc[i], longitudes.iloc[i]
        if curr_lat == 0 or curr_lon == 0:
            continue
        speed = speeds.iloc[i]  # Get the speed for the current point
        distance = haversine.haversine((prev_lat, prev_lon), (curr_lat, curr_lon), unit=haversine.Unit.METERS)
   
        # Get the dynamic threshold for the current speed
        threshold_distance = get_threshold_by_speed(speed)
        
        if distance > threshold_distance:  # Only keep points that exceed the threshold
            filtered_route.append((curr_lat, curr_lon))
        
        prev_lat, prev_lon = curr_lat, curr_lon  # Update the previous point
    
    # Add the filtered route to the map
    folium.PolyLine(filtered_route, color='blue', weight=2.5, opacity=1).add_to(m)
    
    # Optionally, add markers for each point in the filtered route
    for lat, lon in filtered_route:
        folium.Marker([lat, lon]).add_to(m)

# Save the map to an HTML file
m.save("filtered_route_map_dynamic_threshold.html")
