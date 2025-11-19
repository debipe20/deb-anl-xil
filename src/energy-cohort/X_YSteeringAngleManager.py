import pandas as pd
import math

# Parameters
LOOKAHEAD_DISTANCE = 10.0  # Adjust this distance for how far ahead the vehicle looks
WHEELBASE = 2.8  # Example wheelbase of the car (in meters)

class XY_SteeringAngleManager:
    def __init__(self, way_points_file, current_position):
        """
        Initializes the waypoints file and prepares lists for coordinate data.
        """
        self.way_points_file = way_points_file
        self.previous_index = 0  # Index for tracking the previous waypoint
        
        # Read waypoints from file during initialization
        self.read_way_points()
        
        # Set initial index based on the vehicle's current position
        self.set_initial_points(current_position)
        
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
        
    def set_initial_points(self, current_position):
        """
        Set the initial waypoint index based on the vehicle's current position.
        """
        min_distance = float('inf')

        for index in range(len(self.x_list)):
            # Calculate the distance to the current waypoint
            distance = math.sqrt((self.x_list[index] - current_position[0]) ** 2 + (self.y_list[index] - current_position[1]) ** 2)

            # Update the previous_index to the closest waypoint
            if distance < min_distance:
                min_distance = distance
                self.previous_index = index
                
                print(f"Setting distance and previous index: {distance}, {index}")
                
            else:
            # If the distance starts increasing, stop the loop early since points are ordered
                break
    
    def get_next_lookahead_points(self, current_position, lookahead_distance):
        """
        Get the next lookahead point from the waypoints file based on the current position.
        """
        lookahead_point = None

        # Safeguard to ensure index doesn't go below 0
        start_index = max(self.previous_index - 1, 0)  # Prevent index from being less than 0

        # Iterate through the waypoints starting from the previous index - 1 (safeguarded)
        for index in range(start_index, len(self.x_list)):
            distance = math.sqrt((self.x_list[index] - current_position[0]) ** 2 + (self.y_list[index] - current_position[1]) ** 2)

            if distance >= lookahead_distance:
                # Found a lookahead point
                lookahead_point = (self.x_list[index], self.y_list[index])  # Return x, y coordinates as a tuple
                self.previous_index = index  # Update previous_index for next cycle
                print(f"distance and lookahead distance: {distance}, {lookahead_distance}")
                break

        # If no lookahead point is found (all points are too close)
        if lookahead_point is None:
            return None  # No valid lookahead point found
        
        return lookahead_point
        
    def get_steering_angle(self, vehicle, current_position):
        """
        Calculate the steering angle using the pure pursuit algorithm.
        """
        velocity = vehicle.get_velocity()
        current_speed_mps = math.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2)

        # Dynamically adjust lookahead distance based on speed
        if current_speed_mps < 1:  # Speed threshold
            lookahead_distance = 5.0  # Short lookahead for low speeds
        else:
            lookahead_distance = 5.0 + current_speed_mps * 2  # Longer lookahead for higher speeds
            
        # Get the next lookahead point
        lookahead_point = self.get_next_lookahead_points(current_position, lookahead_distance)

        # If no lookahead point found, return a default value (e.g., 0 steering)
        if lookahead_point is None:
            return 0  # No valid point to pursue, no steering

        # Calculate the steering angle to the lookahead point
        dx = lookahead_point[0] - current_position[0]
        dy = lookahead_point[1] - current_position[1]

        # Calculate the angle to the target point
        alpha = math.atan2(dy, dx) - math.radians(vehicle.get_transform().rotation.yaw)

        # Calculate the steering angle using the pure pursuit formula
        steering_angle = math.atan2(2 * WHEELBASE * math.sin(alpha), lookahead_distance)
        
        # Log important values for debugging
        print(f"Current Speed: {current_speed_mps}")
        print(f"Current Position: {current_position}")
        print(f"Lookahead Point: {lookahead_point}")
        print(f"Alpha (Vehicle Heading): {alpha}")
        print(f"Steering Angle (Raw): {steering_angle}")

        # Limit the steering angle to a maximum value (e.g., ±30 degrees or 0.5236 radians)
        max_steering_angle = math.radians(30)  # Limit to 30 degrees (in radians)

        # Clamp the steering angle to be within the limits
        if steering_angle > max_steering_angle:
            steering_angle = max_steering_angle
        elif steering_angle < -max_steering_angle:
            steering_angle = -max_steering_angle

        # Normalize the steering angle to CARLA's range [-1, 1]
        normalized_steering = steering_angle / max_steering_angle

        # Optionally: Apply rate limiting to prevent sudden jumps in steering (if needed)
        if hasattr(self, 'previous_steering_angle'):
            max_steering_delta = math.radians(5)  # Limit change to 5 degrees per tick
            steering_delta = steering_angle - self.previous_steering_angle

            # Limit the rate of change
            if steering_delta > max_steering_delta:
                steering_angle = self.previous_steering_angle + max_steering_delta
            elif steering_delta < -max_steering_delta:
                steering_angle = self.previous_steering_angle - max_steering_delta

        # Store the current steering angle for the next tick
        self.previous_steering_angle = steering_angle
        print(f"Normalize Steering Angle: {normalized_steering}")

        return normalized_steering
