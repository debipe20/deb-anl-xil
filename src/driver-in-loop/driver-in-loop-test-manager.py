"""
**********************************************************************************

driver-in-loop-test-manager.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************
  
Description:
------------
  1. This script contains API of BSMGenerator and LeadVehicleDataManager class to generate ego vehicle's BSM and feed required information to vehicle controller.
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


def destruct_logger(logger:Logger):
    logger.consoleDisplay("Shutting down now!")
    del logger

def main():
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
            
            relativeDistance = haversine.haversine((lead_lon, lead_lon), (ego_lat, ego_lon), unit=haversine.Unit.METERS)
            
            lead_encoded_bsm = v2x.MessageFrame.from_json(lead_bsm_json_string)
            
            if relativeDistance >= 5:
                ego_encoded_bsm = v2x.MessageFrame.from_json(ego_bsm_json_string)
            
            else: ego_encoded_bsm = v2x.MessageFrame.from_json(previous_ego_bsm_json_string)
                           
            driver_in_loop_test_manager_socket.sendto(lead_encoded_bsm, lead_message_receiver_address)
            driver_in_loop_test_manager_socket.sendto(ego_encoded_bsm, ego_message_receiver_address)
            
            
            logger.log_driver_in_loop_test_data(lead_id, lead_time_step, lead_msg_count, lead_lat, lead_lon, lead_elevation, lead_speed, lead_heading, ego_id, ego_time_step, ego_msg_count, ego_lat, ego_lon, ego_elevation, ego_speed, ego_heading)
            previous_ego_bsm_json_string = ego_bsm_json_string
        
    driver_in_loop_test_manager_socket.close()

if __name__ == "__main__":
    main()
