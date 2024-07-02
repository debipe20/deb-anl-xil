import socket
import json
import binascii
import struct

import time


def main():
    config_file = open("anl-master-config.json", "r")
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

    data_manager_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # data_manager_socket.bind(host_address)

    try:
        data_manager_socket.bind(host_address)
        print(f"Successfully bound to {host_address}")
    except OSError as e:
        print(f"Failed to bind to {host_address}: {e}")
        try:
            data_manager_socket.bind(fallback_address)
            print(f"Successfully bound to {fallback_address}")
        except OSError as fallback_e:
            print(f"Failed to bind to {fallback_address} as well: {fallback_e}")
            return


    # Count the number of fields that are true
    simulation_true_count = sum(1 for value in config["FlexILUDPSignals"]["Simulation"].values() if value)
    vehicle_true_count = sum(1 for value in config["FlexILUDPSignals"]["Vehicle"].values() if value)
    facilities_true_count = sum(1 for value in config["FlexILUDPSignals"]["Facilities"].values() if value)

    print(f"Number of fields that are true under 'Simulation', 'Vehicle', and 'Facilities': {simulation_true_count, vehicle_true_count, facilities_true_count}")   

    simulation_data_length =  simulation_true_count * 8
    vehicle_data_length = vehicle_true_count * 8
    facilities_data_length = facilities_true_count * 8

    while True:
        data, address = data_manager_socket.recvfrom(1024)

        if (address == simpc_address) and (len(data) == simulation_true_count):
            data_manager_socket.sendto(data, mabx_address)
        
        elif (address == simpc_address) and (len(data) != simulation_true_count):
            pass
        
        # elif (address == mabx_address) and (len(data) == vehicle_true_count):
        #     pass
            
        # elif (address == mabx_address) and (len(data) != vehicle_true_count):
        #     pass
        
        # elif (address == facility_address) and (len(data) == facilities_true_count):
        #     pass
        
        # elif (address == facility_address) and (len(data) != facilities_true_count):
        #     pass    
            
            
    data_manager_socket.close()




if __name__ == "__main__":
    main()
