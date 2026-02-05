import math
import pandas as pd

def get_starting_index(previous_index, current_lat, current_lon, current_heading):
    desired_index = 0
    lat1 = current_lat
    lon1 = current_lon
    heading1 = current_heading
    heading_status = 'behind'
    
    # Load the waypoint data from the CSV file
    way_points_data_file = "/home/debashis/Desktop/deb-anl-xil/data/kearney/ego-waypoints.csv"
    dataFrame = pd.read_csv(way_points_data_file)
    latitude_list = dataFrame["Latitude"].tolist()
    longitude_list = dataFrame["Longitude"].tolist()

    # Iterate over the latitude and longitude list to calculate the bearing
    for index, value in enumerate(latitude_list[previous_index:], start=previous_index):
        print("index,: ", index)
        lat2 = latitude_list[index]
        lon2 = longitude_list[index]
        
        # Print lat2, lon2 for debugging purposes
        print(f"lat2, lon2: {lat2}, {lon2}")
        
        # Convert latitudes and longitudes to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        diff_lon_rad = math.radians(lon2 - lon1)

        # Calculate the bearing using the spherical law of cosines
        x = math.sin(diff_lon_rad) * math.cos(lat2_rad)
        y = (math.cos(lat1_rad) * math.sin(lat2_rad)) - (math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(diff_lon_rad))

        bearing = math.atan2(x, y)
        bearing = math.degrees(bearing)
        bearing_to_target = (bearing + 360) % 360
        
        # Calculate the difference between the current heading and the target bearing
        angle_diff = (bearing_to_target - heading1 + 360) % 360
        
        # Adjust the condition to correctly reflect the direction (Ahead or Behind)
        if angle_diff < 90 or angle_diff > 270:
            desired_index = index
            heading_status = 'ahead'
            print(f"Now GPS point is Ahead for index: {desired_index}")
            break  # Exit the loop once the desired index is found
        else:
            heading_status = 'behind'
            continue  # Continue to the next waypoint if the point is behind
    
    # Return the heading status and the index of the next waypoint
    return heading_status, desired_index

# Example usage
previous_index = 87
current_lat = 41.700842609877725
current_lon = -87.99178760623737
current_heading = 344.9915709017801

heading_status, desired_index = get_starting_index(previous_index, current_lat, current_lon, current_heading)

print(f"Final Status: {heading_status}, Final Index: {desired_index}")
