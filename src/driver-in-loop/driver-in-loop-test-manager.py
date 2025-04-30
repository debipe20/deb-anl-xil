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

Speed_Data_Length = 16
Lead_Controller_Data_Length = 40
Ego_Controller_Data_Length = 40
MPS_To_MPH = 2.23694
MPH_To_MPS = 0.44704
Min_Distance_gap = 10

def generate_hmi_json_string(lead_id, lead_model, lead_lat, lead_lon, lead_elevation, lead_speed, lead_heading, 
                             ego_id, ego_model, ego_lat, ego_lon, ego_elevation, ego_speed, ego_heading, relative_distance, desired_distance_gap):
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

    lead_speed = lead_speed * MPS_To_MPH
    ego_speed = ego_speed * MPS_To_MPH
    
    if desired_distance_gap < Min_Distance_gap:
        desired_distance_gap = Min_Distance_gap        
     
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
            f"Distance Gap: {round(relative_distance, 0)} m",
            f"Desired Distance Gap: {round(desired_distance_gap, 0)} m",
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
        
def encode_vehicle_command(desired_speed, intersection_name, distance_to_intersection,
    signal_group, traffic_light, min_time_to_change, max_time_to_change,
    headway, desired_headway, lead_speed, approach_id, lane_id):

    def pack_string(s):
        if not isinstance(s, str):
            s = str(s)
        b = s.encode('utf-8')
        return struct.pack(f'I{len(b)}s', len(b), b)

    data = b''
    data += struct.pack('d', desired_speed)
    data += pack_string(intersection_name)

    # distance_to_intersection
    if isinstance(distance_to_intersection, (float, int)):
        data += struct.pack('B', 1)  # flag: 1 = double
        data += struct.pack('d', distance_to_intersection)
    else:
        data += struct.pack('B', 0)  # flag: 0 = string
        data += pack_string(distance_to_intersection)

    data += pack_string(signal_group)
    data += pack_string(traffic_light)

    # min_time_to_change
    if isinstance(min_time_to_change, (float, int)):
        data += struct.pack('B', 1)
        data += struct.pack('d', min_time_to_change)
    else:
        data += struct.pack('B', 0)
        data += pack_string(min_time_to_change)

    # max_time_to_change
    if isinstance(max_time_to_change, (float, int)):
        data += struct.pack('B', 1)
        data += struct.pack('d', max_time_to_change)
    else:
        data += struct.pack('B', 0)
        data += pack_string(max_time_to_change)

    data += struct.pack('d', headway)
    data += struct.pack('d', desired_headway)
    data += struct.pack('d', lead_speed)

    data += pack_string(approach_id)
    data += pack_string(lane_id)

    return data

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

    # vehicle_spy_ip = config["IPAddress"]["VehicleSpyIp"]
    vehicle_spy_ip = config["IPAddress"]["HostIp"]
    vehicle_spy_port = config["PortNumber"]["VehicleSpy"]
    vehicle_spy_address = (vehicle_spy_ip, vehicle_spy_port)
    
    # hmi_ip = config["IPAddress"]["HmiIp"]
    # hmi_port = config["PortNumber"]["HMI"]
    # hmi_address = (hmi_ip, hmi_port)
    
    lead_controller_ip = config["IPAddress"]["HostIp"]
    lead_controller_port = config["PortNumber"]["LeadController"]
    lead_controller_address = (lead_controller_ip, lead_controller_port)
    
    ego_controller_ip = config["IPAddress"]["HostIp"]
    ego_controller_port = config["PortNumber"]["EgoController"]
    ego_controller_address = (ego_controller_ip, ego_controller_port)
    
    vehicle_status_manager_ip = config["IPAddress"]["HostIp"]
    vehicle_status_manager_port = config["PortNumber"]["VehicleStatusManager"]
    vehicle_status_manager_address = (vehicle_status_manager_ip, vehicle_status_manager_port)

    driver_in_loop_test_manager_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    driver_in_loop_test_manager_socket.bind(driver_in_loop_test_manager_address)

    # Get logging and console output variables
    time_gap = config["GeneralInformation"]["TimeGap"]
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
    
    ego_time_step, ego_msg_count, ego_lat, ego_lon, ego_elevation, ego_heading, ego_speed = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    lead_time_step, lead_msg_count, lead_lat, lead_lon, lead_elevation, lead_heading, lead_speed  = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    previous_ego_bsm_json_string = ""
    intersection_name, intersection_distance, signal_group, signal_state, min_time_to_change, max_time_to_change, approach_id, lane_id = "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA"    

    while True:
        data, address = driver_in_loop_test_manager_socket.recvfrom(2048)
        # logger.consoleDisplay("Received data is following:\n" + str(data))

        received_data_length = len(data)
            
        if address == vehicle_spy_address and received_data_length == Speed_Data_Length:
            lead_speed, ego_speed = struct.unpack("dd", data)
            lead_speed = lead_speed * MPH_To_MPS
            ego_speed = ego_speed * MPH_To_MPS
            
            # pass speed data in mps
            # lead_id, lead_time_step, lead_msg_count, lead_lat, lead_lon, lead_elevation, lead_speed, lead_heading, lead_bsm_json_string, lead_steering_input = (lead_bsm_generator.get_bsm_json_string(lead_speed))
            # ego_id, ego_time_step, ego_msg_count, ego_lat, ego_lon, ego_elevation, ego_speed, ego_heading, ego_bsm_json_string, ego_steering_input = (ego_bsm_generator.get_bsm_json_string(ego_speed))
            
            relative_distance = haversine.haversine((lead_lat, lead_lon), (ego_lat, ego_lon), unit=haversine.Unit.METERS)
            desired_distance_gap = ego_speed * time_gap
            # ego_encoded_bsm = v2x.MessageFrame.from_json(ego_bsm_json_string)
            # lead_encoded_bsm = v2x.MessageFrame.from_json(lead_bsm_json_string)
            
            # if relative_distance >= 5:
            #     ego_encoded_bsm = v2x.MessageFrame.from_json(ego_bsm_json_string)
            
            # else: ego_encoded_bsm = v2x.MessageFrame.from_json(previous_ego_bsm_json_string)
            # if debug_status: relative_distance = 5.0
            
            encoded_lead_speed = struct.pack("d", lead_speed)
            encoded_ego_data= encode_vehicle_command(ego_speed, intersection_name, 1200, signal_group, signal_state, min_time_to_change, max_time_to_change, relative_distance, desired_distance_gap, lead_speed, approach_id, lane_id)
            
            # encoded_ego_data= encode_vehicle_command(ego_speed, "Kearney & Watertower", "120", "2", "green", "10", "15", relative_distance, desired_distance_gap, lead_speed,  approach_id, lane_id)

            driver_in_loop_test_manager_socket.sendto(encoded_ego_data, ego_controller_address)
            driver_in_loop_test_manager_socket.sendto(encoded_lead_speed, lead_controller_address)
            
            
            # hmi_json_string = generate_hmi_json_string(lead_id, lead_model, lead_lat, lead_lon, lead_elevation, lead_speed, lead_heading, 
            #                  ego_id, ego_model, ego_lat, ego_lon, ego_elevation, ego_speed, ego_heading, relative_distance, desired_distance_gap)
            
            # driver_in_loop_test_manager_socket.sendto(hmi_json_string.encode(), hmi_address)
            logger.log_driver_in_loop_test_data(lead_id, lead_time_step, lead_msg_count, lead_lat, lead_lon, lead_elevation, lead_speed, lead_heading, ego_id, ego_time_step, ego_msg_count, ego_lat, ego_lon, ego_elevation, ego_speed, ego_heading)
            # previous_ego_bsm_json_string = ego_bsm_json_string
            
        elif address == ego_controller_address and received_data_length == Ego_Controller_Data_Length:
            
            ego_lat, ego_lon, ego_elevation, ego_heading, ego_speed = struct.unpack("ddddd", data) #speed in mps
            bsm_json_string = ego_bsm_generator.generate_bsm_json_string(ego_lat, ego_lon, ego_elevation, ego_heading, ego_speed)
            driver_in_loop_test_manager_socket.sendto(bsm_json_string.encode(),vehicle_status_manager_address)
            
        elif address == lead_controller_address and received_data_length == Lead_Controller_Data_Length:
            lead_lat, lead_lon, lead_elevation, lead_heading, lead_speed = struct.unpack("ddddd", data) #speed in mps

        elif address == vehicle_status_manager_address:
            decoded_data = data.decode('utf-8')
            parsed_json = json.loads(decoded_data)
            
            map_spat_data = parsed_json.get("Map-SPat-Data", {})
            intersection_name = map_spat_data.get("IntersectionName")
            intersection_distance = map_spat_data.get("IntersectionDistance")
            signal_group = map_spat_data.get("SignalGroup")
            signal_state = map_spat_data.get("SignalState")
            min_time_to_change = map_spat_data.get("MinTimeToChange")
            max_time_to_change = map_spat_data.get("MaxTimeToChange")
            approach_id = map_spat_data.get("ApproachID")
            lane_id = map_spat_data.get("LaneID")
            
            if signal_group == 0:
                intersection_name, intersection_distance, signal_group, signal_state, min_time_to_change, max_time_to_change, approach_id, lane_id = "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA"    
  
    driver_in_loop_test_manager_socket.close()

if __name__ == "__main__":
    main()
