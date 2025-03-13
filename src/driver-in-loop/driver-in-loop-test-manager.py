"""
**********************************************************************************

driver-in-loop-test-manager.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************

Description:
------------
This script:
1. **Manages driver-in-loop vehicle testing** for real-time data transmission.
2. **Generates BSM messages** for the ego vehicle.
3. **Receives and processes lead vehicle data.**
4. **Calculates distance gaps and relative speed** between ego and lead vehicles.
5. **Transmits processed data** to external systems.

**********************************************************************************
"""


import socket
import json
import struct
import haversine
import os, platform
import atexit
from osys import v2x
from BsmGenerator import BsmGenerator
from LeadVehicleDataManager import LeadVehicleDataManager
from Logger import Logger

SpeedDataLength = 16

def generate_hmi_json_string(lead_id, lead_model, lead_lat, lead_lon, lead_elevation, lead_speed, lead_heading, 
                             ego_id, ego_model, ego_lat, ego_lon, ego_elevation, ego_speed, ego_heading, relative_distance):
    """
    Generates a JSON string for the HMI containing ego and lead vehicle information.
    Args:
        lead_id (str): Lead vehicle ID.
        lead_model (str): Lead vehicle model.
        lead_lat (float): Lead vehicle latitude.
        lead_lon (float): Lead vehicle longitude.
        lead_elevation (float): Lead vehicle elevation.
        lead_speed (float): Lead vehicle speed.
        lead_heading (float): Lead vehicle heading.
        ego_id (str): Ego vehicle ID.
        ego_model (str): Ego vehicle model.
        ego_lat (float): Ego vehicle latitude.
        ego_lon (float): Ego vehicle longitude.
        ego_elevation (float): Ego vehicle elevation.
        ego_speed (float): Ego vehicle speed.
        ego_heading (float): Ego vehicle heading.
        relative_distance (float): Distance gap between ego and lead vehicle.

    Returns:
        str: JSON-formatted string containing the HMI data.
    """
    
    hmi_dictionary  = {        
        "lead_vehicles": [
            f"Vehicle ID: {lead_id}",
            f"Vehicle Model: {lead_model}",
            f"Speed: {round(lead_speed, 0)} mph",
            f"Latitude: {round(lead_lat, 6)}",
            f"Longitude: {round(lead_lon, 6)}",
            f"Elevation: {round(lead_elevation, 1)}",
            f"Heading: {round(lead_heading, 1)}"
        ],
        "ego_vehicle": [
            f"Vehicle ID: {ego_id}",
            f"Vehicle Model: {ego_model}",
            f"Speed: {round(ego_speed, 0)} mph",
            f"Latitude: {round(ego_lat, 6)}",
            f"Longitude: {round(ego_lon, 6)}",
            f"Elevation: {round(ego_elevation, 1)}",
            f"Heading: {round(ego_heading, 1)}"
        ],
        "spat": {
            "min_end": "--",
            "max_end": "--",
            "signal": "Dark"  # Default signal when no SPaT data is available
        },
        "summary": [
            f"Distance Gap: {round(relative_distance, 0)} meters",
            # "Distance to Intersection: NA",
            f"Lead Speed: {round(lead_speed, 0)} mph",
            f"Ego Speed: {round(ego_speed, 0)} mph",        
            # f"Relative Speed: {float(lead_speed) - float(ego_speed)} mph"
        ]
    }
    
    hmi_json_string = json.dumps(hmi_dictionary, indent=4)
    
    return hmi_json_string

def destruct_logger(logger:Logger):
    """
    Cleans up and deletes the logger instance before exiting.

    Args:
        logger (Logger): Logger instance.
    """
    logger.consoleDisplay("Shutting down now!")
    del logger

def main():
    """
    Main function to manage the driver-in-loop test.
    1. Reads configuration settings.
    2. Initializes sockets for communication.
    3. Generates BSM messages for ego and lead vehicles.
    4. Computes distance gaps and sends real-time updates.
    """
    current_os = platform.system()
    
    if current_os == "Linux":
        config_file_path = os.path.join(os.path.expanduser("~"), "Desktop", "deb-anl-xil", "config", "anl-master-config.json")
    
    elif current_os == "Windows":
        config_file_path = os.path.join("C:\\", "Users", "ddas", "deb-anl-xil", "config", "anl-master-config.json")
    
    else:
        raise OSError(f"Unsupported operating system: {current_os}")
    
    config_file = open(config_file_path, "r")
    config = json.load(config_file)
    config_file.close()

    driver_in_loop_test_manager_ip = config["IPAddress"]["HostIp"]
    driver_in_loop_test_manager_port = config["PortNumber"]["DriverInLoopTestManager"]
    driver_in_loop_test_manager_address = (driver_in_loop_test_manager_ip, driver_in_loop_test_manager_port)

    ego_message_receiver_ip = config["IPAddress"]["V2XHubIp"]
    ego_message_receiver_port = config["PortNumber"]["MessageReceiver"]
    ego_message_receiver_address = (ego_message_receiver_ip, ego_message_receiver_port)

    lead_message_receiver_ip = config["IPAddress"]["LeadVehicleV2XHubIp"]
    lead_message_receiver_port = config["PortNumber"]["MessageReceiver"]
    lead_message_receiver_address = (lead_message_receiver_ip, lead_message_receiver_port)

    vehicle_spy_ip = config["IPAddress"]["VehicleSpyIp"]
    # vehicle_spy_ip = config["IPAddress"]["HostIp"]
    vehicle_spy_port = config["PortNumber"]["VehicleSpy"]
    vehicle_spy_address = (vehicle_spy_ip, vehicle_spy_port)
    
    hmi_ip = config["IPAddress"]["HmiIp"]
    hmi_port = config["PortNumber"]["HMI"]
    hmi_address = (hmi_ip, hmi_port)

    driver_in_loop_test_manager_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    driver_in_loop_test_manager_socket.bind(driver_in_loop_test_manager_address)

    # Get logging and console output variables
    console_status = config["GeneralInformation"]["ConsoleOutput"]
    logging_status = config["GeneralInformation"]["Logging"]
    debug_status =  config["GeneralInformation"]["Debug"]
    ego_id = config["VehicleInformation"]["LeadVehicleId"]
    lead_id = config["VehicleInformation"]["EgoVehicleId"]
    ego_way_points_file = config["VehicleInformation"]["EgoBsmLogFileName"]
    lead_way_points_file = config["VehicleInformation"]["LeadBsmLogFileName"]
    ego_model = config["VehicleInformation"]["EgoVehicleModel"]
    lead_model = config["VehicleInformation"]["LeadVehicleModel"]
    
    logger = Logger(console_status, logging_status, debug_status)
    atexit.register(lambda: destruct_logger(logger))
    ego_bsm_generator = BsmGenerator(config, ego_id, ego_way_points_file, logger)
    lead_bsm_generator = BsmGenerator(config, lead_id, lead_way_points_file, logger)
    
    ego_lat, ego_lon, ego_speed = 0.0, 0.0, 0.0
    lead_lat, lead_lon, lead_speed = 0.0, 0.0, 0.0
    previous_ego_bsm_json_string = ""

    while True:
        data, address = driver_in_loop_test_manager_socket.recvfrom(2048)
        # logger.consoleDisplay("Received data is following:\n" + str(data))

        data_length = len(data)

        if data_length == SpeedDataLength:
        # if address[0] == vehicle_spy_ip:
            lead_speed, ego_speed = struct.unpack("dd", data)

            lead_id, lead_time_step, lead_msg_count, lead_lat, lead_lon, lead_elevation, lead_speed, lead_heading, lead_bsm_json_string = (lead_bsm_generator.get_bsm_json_string(lead_speed))
            ego_id, ego_time_step, ego_msg_count, ego_lat, ego_lon, ego_elevation, ego_speed, ego_heading, ego_bsm_json_string = (ego_bsm_generator.get_bsm_json_string(ego_speed))
            
            relative_distance = haversine.haversine((lead_lat, lead_lon), (ego_lat, ego_lon), unit=haversine.Unit.METERS)
            
            lead_encoded_bsm = v2x.MessageFrame.from_json(lead_bsm_json_string)
            
            if relative_distance >= 5:
                ego_encoded_bsm = v2x.MessageFrame.from_json(ego_bsm_json_string)
            
            else: ego_encoded_bsm = v2x.MessageFrame.from_json(previous_ego_bsm_json_string)
                           
            driver_in_loop_test_manager_socket.sendto(lead_encoded_bsm, lead_message_receiver_address)
            driver_in_loop_test_manager_socket.sendto(ego_encoded_bsm, ego_message_receiver_address)
            
            hmi_json_string = generate_hmi_json_string(lead_id, lead_model, lead_lat, lead_lon, lead_elevation, lead_speed, lead_heading, 
                             ego_id, ego_model, ego_lat, ego_lon, ego_elevation, ego_speed, ego_heading, relative_distance)
            
            driver_in_loop_test_manager_socket.sendto(hmi_json_string.encode(), hmi_address)
            logger.log_driver_in_loop_test_data(lead_id, lead_time_step, lead_msg_count, lead_lat, lead_lon, lead_elevation, lead_speed, lead_heading, ego_id, ego_time_step, ego_msg_count, ego_lat, ego_lon, ego_elevation, ego_speed, ego_heading)
            previous_ego_bsm_json_string = ego_bsm_json_string
        
    driver_in_loop_test_manager_socket.close()

if __name__ == "__main__":
    main()
