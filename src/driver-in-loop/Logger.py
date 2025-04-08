"""
**********************************************************************************

Logger.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************
  
Description:
------------
This script implements the `Logger` class, responsible for:
- Creating and managing log files for **ego and lead vehicle data**.
- Logging **driver-in-loop test data**, including vehicle position, speed, and heading.
- Handling **error logs** for failed message decoding.
- Providing **real-time console display** for debugging.

The methods available from this class are the following:
- create_log_file(): Method to create all the required log files
- log_driver_in_loop_test_data(args): Method to log lead and ego vehicle's information
- logErrorData(errorMsg, payload): Method to log payload that Objective Systems can not decode
- consoleDisplay(consoleString:str): Method to display information
***************************************************************************************
"""

import time, datetime
import os

class Logger:
    """
    Logger class handles file-based and console-based logging for driver-in-loop testing.

    Attributes:
        console_status (bool): Flag to enable/disable console output.
        logging_status (bool): Flag to enable/disable logging to files.
        debug_status (bool): Flag to enable/disable debug mode.
    """
    def __init__(self, console_status:bool, logging_status:bool, debug_status:bool):
        """
        Initializes the Logger class and creates log files if logging is enabled.

        Args:
            console_status (bool): Whether to print logs to the console.
            logging_status (bool): Whether to log data to files.
            debug_status (bool): Whether debug mode is enabled.
        """
        self.console_status = console_status
        self.logging_status = logging_status
        self.debug_status = debug_status
        
        if (self.logging_status == True):
            self.create_log_file()     
        
    def create_log_file(self):
        """
        Creates log files for **driver-in-loop test data** and **error logs**.
        Stores logs in **debug mode or driver-in-loop directory** based on the debug flag.
        """
        if (self.debug_status == True):
            logfileDirectory = "../../log/debug/"
                    
        else: logfileDirectory = "../../log/driver-in-loop/"
        
        if not os.path.exists(logfileDirectory):
                os.makedirs(logfileDirectory)
        
        initializationTimestamp = ('{:%m%d%Y_%H%M%S}'.format(datetime.datetime.now()))

        self.driver_in_loop_test_log_file = open(logfileDirectory + "driver_in_loop_test_log_" + initializationTimestamp + ".csv", "w") 
        self.error_log_file = open(logfileDirectory + "error_log_" + initializationTimestamp + ".log", "w")

        driver_in_loop_test_log_header = ("timestamp_verbose, lead_id, lead_time_step, lead_msg_count, lead_lat, lead_lon, lead_elevation, lead_speed, lead_heading, ego_id, ego_time_step, ego_msg_count, ego_lat, ego_lon, ego_elevation, ego_speed, ego_heading, ego_steering\n")
        self.driver_in_loop_test_log_file.write(driver_in_loop_test_log_header)

    def log_driver_in_loop_test_data(self, lead_id, lead_time_step, lead_msg_count, lead_lat, lead_lon, lead_elevation, lead_speed, lead_heading, ego_id, ego_time_step, ego_msg_count, ego_lat, ego_lon, ego_elevation, ego_speed, ego_heading, ego_steering):
        """
        Logs **ego and lead vehicle data** into the test log file.

        Args:
            lead_id (str): Lead vehicle ID.
            lead_time_step (float): Lead vehicle timestamp.
            lead_msg_count (int): Lead vehicle message count.
            lead_lat (float): Lead vehicle latitude.
            lead_lon (float): Lead vehicle longitude.
            lead_elevation (float): Lead vehicle elevation.
            lead_speed (float): Lead vehicle speed.
            lead_heading (float): Lead vehicle heading.
            ego_id (str): Ego vehicle ID.
            ego_time_step (float): Ego vehicle timestamp.
            ego_msg_count (int): Ego vehicle message count.
            ego_lat (float): Ego vehicle latitude.
            ego_lon (float): Ego vehicle longitude.
            ego_elevation (float): Ego vehicle elevation.
            ego_speed (float): Ego vehicle speed.
            ego_heading (float): Ego vehicle heading.
        """
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
            ego_steering = str(ego_steering)

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
                + ego_heading + ","
                + ego_steering + "\n"
            )

            self.driver_in_loop_test_log_file.write(csvRow) 
               
    def logErrorData(self, errorMsg, payload):
        """
        Logs **error messages and payloads** when message decoding fails.

        Args:
            errorMsg (str): Description of the error.
            payload (str): Message payload that failed decoding.
        """
        if (self.logging_status == True):
            self.error_log_file.write("Following error occurred:\n" + str(errorMsg) + "\n")
        
    def consoleDisplay(self, consoleString:str):
        """
        Displays formatted logs to the console if `console_status` is enabled.

        Args:
            consoleString (str): Message to display on the console.
        """
        timestamp = str(round(time.time(),4))
        if (self.console_status == True):
            print(("\n[{}]".format(timestamp) + " " + consoleString))
            
    def __del__(self):
        """
        Destructor to close open log files when the Logger instance is deleted.
        """
        if (self.logging_status == True):
            self.consoleDisplay("Closing log files!")
            self.driver_in_loop_test_log_file.close()
            self.error_log_file.close()