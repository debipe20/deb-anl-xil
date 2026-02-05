"""
hmi_main.py
-----------
Main script for running the Driver-In-Loop HMI application. It initializes the GUI and 
starts a UDP socket server to receive and process vehicle and SPaT data updates.

Features:
- Reads configuration settings from a JSON file (`anl-master-config.json`).
- Starts a socket server to receive JSON-formatted messages over UDP.
- Updates the GUI dynamically based on received vehicle and SPaT data.

Dependencies:
- `tkinter` for GUI handling.
- `socket` and `threading` for network communication.
- `json` for parsing received messages.
- `platform` and `os` for handling configuration paths.

Author: Debashis Das
Organization: Argonne National Laboratory (Transportation and Power Systems Division)
"""
import tkinter as tk
import socket
import threading
import json
import os
import platform
from DriverInLoopGUI import DriverInLoopGUI

def socket_server():
    """
    Starts a UDP socket server to receive vehicle and SPaT updates.
    
    - Reads the IP and port configuration from `anl-master-config.json`.
    - Listens for incoming JSON messages.
    - Decodes and processes the received data to update the GUI.
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
    
    hmi_ip = config["IPAddress"]["HmiIp"]
    hmi_port = config["PortNumber"]["HMI"]
    hmi_address = (hmi_ip, hmi_port)
    
    hmi_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hmi_socket.bind(hmi_address)
    
    while True:
        data, address = hmi_socket.recvfrom(2048)
        data = data.decode("utf-8")
        try:
            update_info = json.loads(data)
            process_update(update_info)
        except json.JSONDecodeError:
            print("Received invalid JSON data")

def process_update(update_info):
    """
    Processes received JSON data and updates the GUI.

    Parameters:
        update_info (dict): JSON data containing vehicle and SPaT information.

    Updates:
        - Ego vehicle data (`update_ego_info`)
        - SPaT signal timing (`update_spat_data`)
        - Lead vehicle data (`update_lead_table`)
        - Summary information (`update_summary_info`)
    """
    if "ego_vehicle" in update_info:
        gui.update_ego_info(update_info["ego_vehicle"])
    if "spat" in update_info:
        gui.update_spat_data(update_info["spat"]["min_end"], update_info["spat"]["max_end"], update_info["spat"]["signal"])
    if "lead_vehicles" in update_info:
        gui.update_lead_table(update_info["lead_vehicles"])
    if "summary" in update_info:
        gui.update_summary_info(update_info["summary"])

root = tk.Tk()
gui = DriverInLoopGUI(root)
server_thread = threading.Thread(target=socket_server, daemon=True)
server_thread.start()
root.mainloop()
