import socket
import json
import time
import struct
import os
import platform
import pandas as pd

def main():
    current_os = platform.system()
    
    if current_os == "Linux":
        config_file_path = os.path.join(os.path.expanduser("~"), "Desktop", "deb-anl-xil", "config", "anl-master-config.json")
    elif current_os == "Windows":
        config_file_path = os.path.join(os.path.expanduser("~"), "deb-anl-xil", "config", "anl-master-config.json")
    else:
        raise OSError(f"Unsupported operating system: {current_os}")

    # Load configuration file safely
    with open(config_file_path, "r") as config_file:
        config = json.load(config_file)

    host_ip = config["IPAddress"]["HostIp"]
    host_port = config["PortNumber"]["VehicleSpy"]
    host_address = (host_ip, host_port)

    client_ip = config["IPAddress"]["HostIp"]
    client_port = config["PortNumber"]["DriverInLoopTestManager"]
    client_address = (client_ip, client_port)

    msgSenderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msgSenderSocket.bind(host_address)

    # Define the file path
    file_path = "Speed_Profiles_Master.xlsx"

    try:
        # Load the specified sheet
        sheet_name = "Extra Short Time Gap "
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        # Validate required columns
        required_columns = ["Lead Speed [mps]", "Simulated Ego Spd [mps]"]
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"Missing required columns: {required_columns}")
        
        # Send data row by row
        for index, row in df.iterrows():
            lead_speed = row["Lead Speed [mps]"]
            ego_speed = row["Simulated Ego Spd [mps]"]
            print(f"Row {index}: Lead Speed = {lead_speed}, Simulated Ego Speed = {ego_speed}")

            encoded_lead_speed = struct.pack("d", lead_speed)
            encoded_ego_speed = struct.pack("d", ego_speed)

            sendingData = encoded_lead_speed + encoded_ego_speed
            msgSenderSocket.sendto(sendingData, client_address)
            time.sleep(0.0997)

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    msgSenderSocket.close()

if __name__ == '__main__':
    main()
