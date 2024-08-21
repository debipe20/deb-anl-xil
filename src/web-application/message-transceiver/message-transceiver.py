import socket
import json
import binascii
import struct
import time
from DataManager import DataManager

Time_Gap = 30.0

def get_message_length():
    config_file = open("../anl-master-config.json", "r")
    config = json.load(config_file)
    config_file.close()
    # Count the number of fields that are true
    simulation_true_count = sum(1 for value in config["FlexILUDPSignals"]["Simulation"].values() if value)
    vehicle_true_count = sum(1 for value in config["FlexILUDPSignals"]["Mabx"].values() if value)
    # vehicle_true_count = sum(1 for value in config["FlexILUDPSignals"]["Test"].values() if value)
    facilities_true_count = sum(1 for value in config["FlexILUDPSignals"]["Facilities"].values() if value)

    print(f"Number of fields that are true under 'Simulation', 'Vehicle', and 'Facilities': {simulation_true_count, vehicle_true_count, facilities_true_count}")   

    simulation_data_length =  simulation_true_count * 8
    vehicle_data_length = vehicle_true_count * 8
    facilities_data_length = facilities_true_count * 8

    return simulation_data_length, vehicle_data_length, facilities_data_length
    

def main():
    config_file = open("../anl-master-config.json", "r")
    config = json.load(config_file)
    config_file.close()

    host_ip = config["IPAddress"]["HostIP"]
    host_port = config["PortNumber"]["HostPort"]
    host_address = (host_ip, host_port)
    fallback_address = ("127.0.0.1", host_port)

    simpc_ip = config["IPAddress"]["SimPC"]
    simpc_port = config["PortNumber"]["SimPC"]
    simpc_address = (simpc_ip, simpc_port)
    
    mabx_ip = config["IPAddress"]["Mabx"]
    mabx_port = config["PortNumber"]["Mabx"]
    mabx_address = (mabx_ip, mabx_port)
    
    facility_ip = config["IPAddress"]["Facility"]
    facility_port = config["PortNumber"]["Facility"]
    facility_address = (facility_ip, facility_port)

    message_tranceiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message_tranceiver_socket.bind(host_address)

    # try:
    #     message_tranceiver_socket.bind(host_address)
    #     print(f"Successfully bound to {host_address}")
    # except OSError as e:
    #     print(f"Failed to bind to {host_address}: {e}")
    #     try:
    #         message_tranceiver_socket.bind(fallback_address)
    #         print(f"Successfully bound to {fallback_address}")
    #     except OSError as fallback_e:
    #         print(f"Failed to bind to {fallback_address} as well: {fallback_e}")
    #         return

    dataManager = DataManager()
    update_time = time.time()

    simulation_data_length, vehicle_data_length, facilities_data_length = get_message_length()

    while True:
        data, address = message_tranceiver_socket.recvfrom(1024)

        if (address == simpc_address) and (len(data) == simulation_data_length):
            dataManager.manageMsgInformation("simulation", "Received")
            message_tranceiver_socket.sendto(data, mabx_address)
        
        elif (address == simpc_address) and (len(data) != simulation_data_length):
            dataManager.manageMsgInformation("faulty-simulation", "Received")
        
        elif (address == mabx_address) and (len(data) == vehicle_data_length):
            dataManager.manageMsgInformation("mabx", "Received")
            
        elif (address == mabx_address) and (len(data) != vehicle_data_length):
            dataManager.manageMsgInformation("faulty-mabx", "Received")
        
        elif (address == facility_address) and (len(data) == facilities_data_length):
            dataManager.manageMsgInformation("facilities", "Received")
        
        elif (address == facility_address) and (len(data) != facilities_data_length):
            dataManager.manageMsgInformation("fauly-facilities", "Received")
        
        if (time.time() - update_time) >= (Time_Gap - 0.01):
            dataManager.write_msg_count()
            update_time = time.time()
            simulation_data_length, vehicle_data_length, facilities_data_length = get_message_length()            
            
    mabx_log.close()        
    message_tranceiver_socket.close()


if __name__ == "__main__":
    main()
