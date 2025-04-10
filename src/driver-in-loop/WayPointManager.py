import time
import os
import platform
import math
import haversine
import pandas as pd

# ==============================================================================
# -------------------------- WayPointsManager ---------------------------
# ==============================================================================
          
class WayPointsManager:

    def __init__(self, config, way_points_file):
        """
        Initializes the BSM Generator with vehicle parameters and waypoints.

        Args:
            config (dict): Configuration settings.
            vehicle_id (str): Unique vehicle ID.
            way_points_file (str): File containing preloaded waypoints.
            logger (Logger): Logger instance for debugging and tracking.
        """

        self.config = config
        self.current_lat = 0.0
        self.current_lon = 0.0
        self.current_elev = 0.0
        self.current_speed = 0.0
        self.current_heading = 0.0
        self.previous_lat = 41.7007424 
        self.previous_lon = -87.9915918
        self.previous_index = 0
        self.previous_time = time.time()
        self.desired_lat = 0.0
        self.desired_lon = 0.0
        self.desired_x = 0.0
        self.desired_y = 0.0
        # self.desired_z = 0.0
        self.desired_yaw = 0.0
        self.time_step = 0.0
        self.extra_distance = 0.0
        self.step = 0
        self.previous_time_stamp_set_status = False
        self.latitude_list, self.longitude_list, self.elevation_list, self.heading_list = ([] for i in range(4) )
        self.way_points_file = way_points_file
        self.read_way_points()
        
        self.debug_log_file = open("../../log/debug/debug_lead_controller_log.csv", "w")
        log_header = ("timestamp, desired_lat, desired_lon, desired_heading, current_lat, current_lon, current_speed, current_heading, travel_distance, calculated_distance, calculated_distance_next, starting_index, selected_index\n")
        self.debug_log_file.write(log_header)
        
        self.heading_log_file = open("../../log/debug/debug_heading_log.log", "w")
        write_msg = f"[{time.time()}]: {{'TimeStamp'}}, {{'previous_index'}}, {{'desired_index'}}, {{'current_lat'}}, {{'current_lon'}}, {{'current_heading'}}, {{'desired_lat'}}, {{'desired_lon'}}, {{'heading_status'}} \n"
        self.heading_log_file.write(write_msg)

    def read_way_points(self):
        """
        - Method to get all the coordinates from preload waypoints/BSMs
        """
        current_os = platform.system()
        
        if current_os == "Linux":
            self.way_points_data_file = os.path.join(os.path.expanduser("~"), "Desktop", "deb-anl-xil", "data", "kearney", self.way_points_file)
        
        elif current_os == "Windows":
            self.way_points_data_file = os.path.join("C:\\", "Users", "ddas", "deb-anl-xil", "data", "kearney", self.way_points_file)
        
        else:
            raise OSError(f"Unsupported operating system: {current_os}")
        
        dataFrame = pd.read_csv(self.way_points_data_file)
        self.latitude_list = dataFrame["Latitude"].tolist()
        self.longitude_list = dataFrame["Longitude"].tolist()
        self.elevation_list = dataFrame["Elevation"].tolist()
        self.heading_list = dataFrame["Heading"].tolist()
        
        self.x_list = dataFrame["X"].tolist()
        self.y_list = dataFrame["Y"].tolist()
        # self.z_list = dataFrame["Z"].tolist()
        self.yaw_list = dataFrame["Yaw"].tolist()

        self.current_lat = self.latitude_list[0]
        self.current_lon = self.longitude_list[0]
        self.current_elev = self.elevation_list[0]
        self.current_heading = self.heading_list[0]
        self.previous_lat = self.latitude_list[0]
        self.previous_lon = self.longitude_list[0]
        
    def get_starting_index(self, previous_index, current_lat, current_lon, current_heading):
        desired_index = 0
        lat1 = current_lat
        lon1 = current_lon
        heading1 = current_heading
        heading_status = 'behind'
        

        # Iterate over the latitude and longitude list to calculate the bearing
        for index, value in enumerate(self.latitude_list[previous_index:], start=previous_index):
            lat2 = self.latitude_list[index]
            lon2 = self.longitude_list[index]
            
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
        
        write_msg = f"[{time.time()}]: {previous_index}, {desired_index}, {current_lat}, {current_lon}, {current_heading}, {self.latitude_list[desired_index]}, {self.longitude_list[desired_index]}, {heading_status}\n"
        self.heading_log_file.write(write_msg)
        
        return desired_index    
                
    def get_next_coordinates(self, current_speed_mps, current_lat, current_lon, current_heading):
        """
        - Estimates the vehicle's real-time GPS location based on travel distance.
        - Uses the Haversine formula to find the closest matching waypoint.
        - Method to find the estimated location based on the travel time
            - Haversine distance is calculated
        - Distance between two waypoints may greater than the actual distance travel by the vehicle
            - extraDistance variable stores the difference between waypoints distance and vehicle travel distance
            - if extraDistance is greater than vehicle's travel distance, no neeed to iterate
            - if extraDistance is greater than vehicle's travel distance, deduct extraDistance from vehicle's travel distance
        - Iterate until haversine distance for current coordinate is close to the estimated distance compare to next coordinate
        """
        starting_index = 0
        desired_lat, desired_lon, desired_heading, desired_x, desired_y, desired_yaw = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        current_time = time.time()
        
        if self.previous_time_stamp_set_status == False:
            self.previous_time = current_time - 0.1
            self.previous_time_stamp_set_status = True
            self.previous_index = 1
            
        # current_speed_mps = round(current_speed_mps, 2)
        if current_speed_mps < 0.005:
            current_speed_mps = 0.0
        self.time_step = current_time - self.previous_time
        travel_distance = current_speed_mps * self.time_step
        starting_index = self.get_starting_index(self.previous_index, current_lat, current_lon, current_heading)
        
        for index in range(starting_index, len(self.latitude_list) - 2):
            calculated_distance = haversine.haversine((self.current_lat, self.current_lon), (self.latitude_list[index], self.longitude_list[index]), unit=haversine.Unit.METERS)
            calculated_distance_next = haversine.haversine((self.current_lat, self.current_lon), (self.latitude_list[index + 1], self.longitude_list[index + 1]), unit=haversine.Unit.METERS)
    
            if (calculated_distance < travel_distance) and (calculated_distance_next < travel_distance):
                continue
            
            elif (calculated_distance >= travel_distance) and (calculated_distance_next > travel_distance):
                self.previous_time = time.time()
                self.previous_index = index
                desired_lat = self.latitude_list[index]
                desired_lon = self.longitude_list[index]
                desired_heading = self.heading_list[index]
                desired_x = self.x_list[index]
                desired_y = self.y_list[index]
                desired_yaw = self.yaw_list[index]
                break
            
            elif (calculated_distance < travel_distance) and (calculated_distance_next >= travel_distance):
                self.previous_time = time.time()
                self.previous_index = index + 1
                desired_lat = self.latitude_list[index + 1]
                desired_lon = self.longitude_list[index + 1]
                desired_heading = self.heading_list[index + 1]
                desired_x = self.x_list[index + 1]
                desired_y = self.y_list[index + 1]
                desired_yaw = self.yaw_list[index + 1]
                break
            
        
        # Only after all math operations:
        csv_row = (
            f"{time.time()},{desired_lat},{desired_lon},{desired_heading},"
            f"{current_lat},{current_lon},{current_speed_mps},{current_heading},"
            f"{travel_distance},{calculated_distance},{calculated_distance_next},"
            f"{starting_index},{self.previous_index}\n"
        )
        self.debug_log_file.write(csv_row)

        return desired_lat, desired_lon, desired_heading, desired_x, desired_y, desired_yaw
    