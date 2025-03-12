"""
**********************************************************************************

Logger.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************
  
Description:
------------
The methods available from this class are the following:
- create_log_file(): Method to create all the required log files
- logHostVehicleBsmData(timeStep, msgCount, currentLatitude, currentLongitude, currentElevation, currentSpeed, currentHeading): Method to log host vehicle's GPS data and speed.
- logLeadVehicleData(counter, relativeDistance, relativeSpeed, leadVehicleSpeed, hostVehicleSpeed): Method to log lead and ego vehicle's speed data, relative distance and relative speed
- logHostVehicleData(counter, decodedSpeed): Method to log ego vehicle's speed
- logHostBsmHexData(bsmHex): Method to log ego vehicle's encoded BSM
- logLeadBsmHexData(bsmHex): Method to log lead vehicle's encoded BSM
- logErrorData(errorMsg, payload): Method to log payload that Objective Systems can not decode
- consoleDisplay(consoleString:str): Method to display information
***************************************************************************************
"""

import time, datetime
import os

class Logger:
    def __init__(self, console_status:bool, logging_status:bool, debug_status:bool):
        self.console_status = console_status
        self.logging_status = logging_status
        self.debug_status = debug_status
        
        if (self.logging_status == True):
            self.create_log_file()     
        
    def create_log_file(self):
    
        if (self.debug_status == True):
            logfileDirectory = "../../log/debug/"
                    
        else: logfileDirectory = "../../log/driver-in-loop/"
        
        if not os.path.exists(logfileDirectory):
                os.makedirs(logfileDirectory)
        
        initializationTimestamp = ('{:%m%d%Y_%H%M%S}'.format(datetime.datetime.now()))

        self.driver_in_loop_test_log_file = open(logfileDirectory + "driver_in_loop_test_log_" + initializationTimestamp + ".csv", "w") 
        self.error_log_file = open(logfileDirectory + "error_log_" + initializationTimestamp + ".log", "w")

        driver_in_loop_test_log_header = ("timestamp_verbose, lead_id, lead_time_step, lead_msg_count, lead_lat, lead_lon, lead_elevation, lead_speed, lead_heading, ego_id, ego_time_step, ego_msg_count, ego_lat, ego_lon, ego_elevation, ego_speed, ego_heading\n")
        self.driver_in_loop_test_log_file.write(driver_in_loop_test_log_header)



    def log_driver_in_loop_test_data(self, lead_id, lead_time_step, lead_msg_count, lead_lat, lead_lon, lead_elevation, lead_speed, lead_heading, ego_id, ego_time_step, ego_msg_count, ego_lat, ego_lon, ego_elevation, ego_speed, ego_heading):
        
        if self.logging_status:
            timestamp_verbose = str(time.time())

            lead_id = str(lead_id)
            lead_time_step = str(lead_time_step)
            lead_msg_count = str(lead_msg_count)
            lead_lat = str(lead_lat)
            lead_lon = str(lead_lon)
            lead_elevation = str(lead_elevation)
            lead_speed = str(round(lead_speed, 2))
            lead_heading = str(round(lead_heading, 2))
            
            ego_id = str(ego_id)
            ego_time_step = str(ego_time_step)
            ego_msg_count = str(ego_msg_count)
            ego_lat = str(ego_lat)
            ego_lon = str(ego_lon)
            ego_elevation = str(ego_elevation)
            ego_speed = str(round(ego_speed, 2))
            ego_heading = str(round(ego_heading,2))

            csvRow = (timestamp_verbose + ","
                + lead_id + ","
                + lead_time_step + ","
                + lead_msg_count + ","
                + lead_lat + ","
                + lead_lon + ","
                + lead_elevation + ","
                + lead_speed + ","
                + lead_heading + ","
                + ego_id + ","
                + ego_time_step + ","
                + ego_msg_count + ","
                + ego_lat + ","
                + ego_lon + ","
                + ego_elevation + ","
                + ego_speed + ","
                + ego_heading + "\n"
            )

            self.driver_in_loop_test_log_file.write(csvRow) 
               
    def logErrorData(self, errorMsg, payload):
        if (self.logging_status == True):
            self.error_log_file.write("Following error occurred:\n" + str(errorMsg) + "\n")
        
    def consoleDisplay(self, consoleString:str):
        
        timestamp = str(round(time.time(),4))
        if (self.console_status == True):
            print(("\n[{}]".format(timestamp) + " " + consoleString))
            
    def __del__(self):
        if (self.logging_status == True):
            self.consoleDisplay("Closing log files!")
            self.driver_in_loop_test_log_file.close()
            self.error_log_file.close()