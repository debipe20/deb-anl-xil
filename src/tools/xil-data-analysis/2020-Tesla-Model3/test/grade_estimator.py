import time
import datetime
import socket
import haversine
import csv
import pandas as pd

class GradeEstimator:

    def __init__(self, gps_data_file_path= 'DaisyMountainArizona.csv'):
        self.gps_data_file_path = gps_data_file_path
        dataFrame = pd.read_csv(gps_data_file_path)
        self.latitudeList = dataFrame["latitude"].tolist()
        self.longitudeList = dataFrame["longitude"].tolist()
        self.elevationList = dataFrame["elevation(m)"].tolist()
        self.headingList = dataFrame["heading"].tolist()
        
        self.previousTime = 0 
        self.previousIndex = 0 
        self.previous_horizontalDistance = 0
        self.previous_elevation = self.elevationList[0]
        self.delta_horizontalDistance = 0
        self.delta_elevation = 0      
        self.currentLatitude = self.latitudeList[0]
        self.currentLongitude = self.longitudeList[0]
        self.currentElevation = self.elevationList[0]
        self.currentHeading = self.headingList[0]
        self.previousLatitude = self.latitudeList[0]
        self.previousLongitude = self.longitudeList[0]
        
        # Open CSV log file
        self.log_file = open("grade_log.csv", "w", newline="")
        self.log_writer = csv.writer(self.log_file)
        self.log_writer.writerow([
            "timestamp", "currenttime", "index", "speed (mps)", "latitude", "longitude", "elevation (m)",
            "delta_horizontal_distance (m)", "delta_elevation (m)", "total_horizontal_distance (m)", "grade (%)"
        ])
        
        
    def get_nearest_coordinate_elevation(self, current_time, current_speed_mps):
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

        self.time_step = current_time - self.previousTime
        travel_distance = current_speed_mps * self.time_step
        self.extra_distance = 0
        
        if self.extra_distance >= travel_distance:
            self.previousTime = time.time()
            self.extra_distance = self.extra_distance - travel_distance

        else:
            travel_distance = travel_distance - self.extra_distance

            for index in range(self.previousIndex + 1, len(self.latitudeList) - 2):
                calculated_distance = haversine.haversine((self.previousLatitude, self.previousLongitude),
                    (self.latitudeList[index], self.longitudeList[index]),
                    unit=haversine.Unit.METERS)
                # if index==115:
                #     print("Reached index 115")
                #     print(f"Previous Latitude: {self.previousLatitude}, Previous Longitude: {self.previousLongitude}")
                #     print(f"Current Latitude and Longitude: {self.latitudeList[index]}, {self.longitudeList[index]}")

                calculated_distance_next = haversine.haversine((self.previousLatitude, self.previousLongitude),
                    (self.latitudeList[index + 1], self.longitudeList[index + 1]),
                    unit=haversine.Unit.METERS)
                
                # print(f"Current Next Latitude and Longitude: {self.latitudeList[index+1]},  {self.longitudeList[index+1]}")

                if (calculated_distance <= travel_distance) and (calculated_distance_next <= travel_distance):
                    continue

                elif (calculated_distance >= travel_distance) and (calculated_distance_next > travel_distance):
                    self.delta_horizontalDistance = self.previous_horizontalDistance - calculated_distance
                    self.delta_elevation = self.previous_elevation - self.elevationList[index]
                    self.previousLatitude = self.latitudeList[index]
                    self.previousLongitude = self.longitudeList[index]
                    self.previous_elevation = self.elevationList[index]                    
                    self.previousTime = current_time
                    self.previousIndex = index
                    self.currentLatitude = self.latitudeList[index]
                    self.currentLongitude = self.longitudeList[index]
                    self.currentElevation = self.elevationList[index]
                    self.currentHeading = self.headingList[index]
                    self.current_index = index
                    self.extra_distance = calculated_distance - travel_distance
                    self.previous_horizontalDistance = calculated_distance
                                        
                    break

                elif (calculated_distance < travel_distance) and (calculated_distance_next >= travel_distance):
                    self.delta_horizontalDistance = self.previous_horizontalDistance - calculated_distance_next
                    self.delta_elevation = self.previous_elevation - self.elevationList[index + 1]
                    self.previousLatitude = self.latitudeList[index + 1]
                    self.previousLongitude = self.longitudeList[index + 1]
                    self.previous_elevation = self.elevationList[index+1]                     
                    self.previousIndex = index + 1
                    self.previousTime = current_time
                    self.currentLatitude = self.latitudeList[index + 1]
                    self.currentLongitude = self.longitudeList[index + 1]
                    self.currentElevation = self.elevationList[index + 1]
                    self.currentHeading = self.headingList[index + 1]
                    self.current_index = index + 1
                    self.extra_distance = calculated_distance_next - travel_distance
                    self.previous_horizontalDistance = calculated_distance_next
                    
                    break 
                
        return self.delta_horizontalDistance, self.delta_elevation

    def estimate_grade(self, delta_horizontal_distance, delta_elevation):
        
        """
        - Estimates the grade of the vehicle based on the change in elevation and horizontal distance.
        - Returns the estimated grade as a percentage.
        """
        grade = 0.0
        if delta_horizontal_distance == 0:
            grade = 0.0
        
        else:
            grade = (delta_elevation / delta_horizontal_distance) * 100
        
        print(f"Estimated grade: {grade:.2f}%")
        
        return grade
    
    
    def log_estimation(self, received_time_data, speed_mps, grade):
        """
        Logs current grade estimation data into CSV file.
        """
        log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        current_time = received_time_data

        self.log_writer.writerow([
            log_time,
            received_time_data,
            self.previousIndex,
            round(speed_mps, 2),
            round(self.currentLatitude, 6),
            round(self.currentLongitude, 6),
            round(self.currentElevation, 2),
            round(self.delta_horizontalDistance, 2),
            round(self.delta_elevation, 2),
            round(self.previous_horizontalDistance, 2),
            round(grade, 2)
        ])
        self.log_file.flush()  # Ensure real-time writing

    
def main():
    
    gps_data_file_path = 'DaisyMountainArizona.csv'
    host_ip = '127.0.0.1'
    host_port = 5001  # Port to listen on
    
    grade_estimator_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    grade_estimator_socket.bind((host_ip, host_port))
    grade_estimator_socket.settimeout(1.0)  # Set timeout to 1 second

    # print(f"Listening on {host_ip}:{host_port}... Press Ctrl+C to stop.")
    grade_estimator = GradeEstimator(gps_data_file_path)
    
    try:
        while True:
            try:
                data, addr = grade_estimator_socket.recvfrom(1024)
                decoded = data.decode('utf-8')
                time_stamp, speed_mps = decoded.split(',')
                print(f"From {addr} → Time: {float(time_stamp):.2f} s, Speed: {float(speed_mps):.2f} m/s")
                time_stamp = float(time_stamp)
                speed_mps = float(speed_mps)

                if speed_mps > 0:
                    delta_horizontal_distance, delta_elevation = grade_estimator.get_nearest_coordinate_elevation(time_stamp,speed_mps)
                    grade = grade_estimator.estimate_grade(delta_horizontal_distance, delta_elevation)
                else:
                    grade = 0.0
                grade_estimator.log_estimation(time_stamp, speed_mps, grade)
                    
            except socket.timeout:
                continue  # Loop again to allow KeyboardInterrupt to be detected
    except KeyboardInterrupt:
        print("Grade estimator stopped by user.")
    finally:
        grade_estimator_socket.close()
        grade_estimator.log_file.close()
        print("Socket and log file closed.")

if __name__ == "__main__": 
    main()
