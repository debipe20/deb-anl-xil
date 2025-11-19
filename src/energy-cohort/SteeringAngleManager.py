import pandas as pd
import math
import time
import haversine

# Parameters
WHEELBASE = 2.8  # Example wheelbase of the car (in meters)

class SteeringAngleManager:
    def __init__(self, way_points_file, current_lat, current_lon, current_elev, current_heading):
        """
        Initializes the waypoints file and prepares lists for coordinate data.
        """
        self.way_points_file = way_points_file
        self.current_lat = current_lat
        self.current_lon = current_lon
        self.current_elev = current_elev
        self.current_heading = current_heading
        
        self.lookahead_lat = 0.0
        self.lookahead_lon = 0.0
        self.lookahead_elev = 0.0
        self.lookahead_heading = 0.0
        
        self.start_index = 0  # Index for tracking the previous waypoint
        
        # Read waypoints from file during initialization
        self.read_way_points()
        self.set_starting_index(self.start_index)
        
    def read_way_points(self):
        """
        Method to read coordinates and waypoints from the file with case-insensitive column names,
        handling both 'Elevation' and 'Altitude' as possible column names.
        """
        # Read the CSV into a DataFrame
        dataFrame = pd.read_csv(self.way_points_file)
        
        # Normalize column names to lowercase to make them case-insensitive
        dataFrame.columns = dataFrame.columns.str.lower()
        
        # Access columns by their lowercase names
        self.latitude_list = dataFrame["latitude"].tolist()
        self.longitude_list = dataFrame["longitude"].tolist()
        
        # Check if 'elevation' or 'altitude' exists and assign the appropriate one
        if "elevation" in dataFrame.columns:
            self.elevation_list = dataFrame["elevation"].tolist()
        elif "altitude" in dataFrame.columns:
            self.elevation_list = dataFrame["altitude"].tolist()
        else:
            self.elevation_list = []  # Default to an empty list if neither is found

        self.heading_list = dataFrame["heading"].tolist()
        
        self.x_list = dataFrame["x"].tolist()
        self.y_list = dataFrame["y"].tolist()
        self.z_list = dataFrame["z"].tolist()
        self.yaw_list = dataFrame["yaw"].tolist()   
        
    def set_starting_index(self, previous_index):
        """
        Sets the initial waypoint index based on the vehicle's current position and heading.
        This method calculates the bearing to the next waypoint and checks if the target waypoint
        is ahead of the vehicle's current heading. It continues checking waypoints until it finds one
        that is ahead of the vehicle. The `previous_index` is used to start searching from the last known
        waypoint, which helps avoid unnecessary searching from the beginning.

        Args:
            previous_index (int): The index of the previous waypoint to start searching from.
        """
        lat1 = self.current_lat
        lon1 = self.current_lon
        heading1 = self.current_heading       

        # Iterate over the latitude and longitude list to calculate the bearing
        for index, value in enumerate(self.latitude_list[previous_index:], start=previous_index):
            lat2 = self.latitude_list[index]
            lon2 = self.longitude_list[index]
            
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
                self.start_index = index
                print(f"[{time.time()}]:Starting Index: {index}")
                break  # Exit the loop once the desired index is found
            
            else:
                continue  # Continue to the next waypoint if the point is behind
        
            
    def get_lookahead_coordinates(self, lookahead_distance):
        """
        Finds the next waypoint that is at least `lookahead_distance` meters away from the vehicle's current position.
        The method uses the Haversine formula to calculate the distance between the vehicle's current position
        and each waypoint, and updates the lookahead coordinates when a suitable waypoint is found.

        Args:
            lookahead_distance (float): The minimum distance (in meters) to the next waypoint to be considered a lookahead point.
        """
        self.set_starting_index(self.start_index)
        
        for index in range(self.start_index, len(self.latitude_list)):
            # Calculate the distance between current position and the waypoint using the Haversine formula
            calculated_distance = haversine.haversine((self.current_lat, self.current_lon), (self.latitude_list[index], self.longitude_list[index]), unit=haversine.Unit.METERS)
            
            # Continue to the next waypoint if the current one is within the lookahead distance
            if calculated_distance < lookahead_distance:
                continue
            
            else:
                # Update lookahead coordinates and heading
                self.lookahead_lat = self.latitude_list[index]
                self.lookahead_lon = self.longitude_list[index]
                self.lookahead_elev = self.elevation_list[index]
                self.lookahead_heading = self.heading_list[index]
                print(f"[{time.time()}]:Starting Index, Lookahead Index, and Distance: {self.start_index}, {index}, {calculated_distance}")
                break
            
            
    def get_steering_angle(self, vehicle):
        """
        Calculate the steering angle using the pure pursuit algorithm based on GPS coordinates and IMU heading.
        The method calculates the difference between the vehicle's heading and the heading of the lookahead point.
        It then uses the pure pursuit formula to calculate the steering angle.

        Args:
            vehicle (carla.Vehicle): The vehicle object used to retrieve the vehicle's speed.

        Returns:
            float: The normalized steering angle for the vehicle to follow the path.
        """
        # Get the vehicle's speed (in m/s)
        velocity = vehicle.get_velocity()
        current_speed_mps = math.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2)

        # Dynamically adjust lookahead distance based on speed
        if current_speed_mps < 1:  # Speed threshold
            lookahead_distance = 5.0  # Short lookahead for low speeds
        else:
            lookahead_distance = 5.0 + current_speed_mps * 2  # Longer lookahead for higher speeds
            
        self.get_lookahead_coordinates(lookahead_distance)
        
        # Get the current heading from IMU sensor (vehicle's heading in degrees)
        vehicle_heading = self.current_heading  # Heading from IMU sensor (yaw)

        # Get the heading of the lookahead point (from the waypoints file)
        lookahead_heading = self.lookahead_heading

        # Calculate the difference between the vehicle's heading and the lookahead point's heading
        alpha = lookahead_heading - vehicle_heading
        alpha = (alpha + 180) % 360 - 180  # Normalize the angle to be within [-180, 180] degrees
        

        # Calculate the steering angle using the pure pursuit formula
        steering_angle = math.atan2(2 * WHEELBASE * math.sin(math.radians(alpha)), lookahead_distance)

        # Limit the steering angle to a maximum value (e.g., ±30 degrees or 0.5236 radians)
        max_steering_angle = math.radians(30)  # Limit to 30 degrees (in radians)

        # Clamp the steering angle to be within the limits
        if steering_angle > max_steering_angle:
            steering_angle = max_steering_angle
        elif steering_angle < -max_steering_angle:
            steering_angle = -max_steering_angle

        # Normalize the steering angle to CARLA's range [-1, 1]
        normalized_steering = steering_angle / max_steering_angle

        # Log the steering angle
        print(f"[{time.time()}]:Calculated Steering Angle: {steering_angle} rad, Normalized: {normalized_steering}")

        return normalized_steering
