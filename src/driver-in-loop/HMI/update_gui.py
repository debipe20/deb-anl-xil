import tkinter as tk
import socket
import threading
import json
from driver_gui import DriverInLoopGUI

def socket_server():
    """Opens a socket server to receive updates and update the GUI accordingly."""
    HOST, PORT = "0.0.0.0", 5000

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Listening for connections on {HOST}:{PORT}...")

        while True:
            conn, addr = server_socket.accept()
            with conn:
                data = conn.recv(1024).decode("utf-8")
                if not data:
                    continue
                try:
                    update_info = json.loads(data)
                    process_update(update_info)
                except json.JSONDecodeError:
                    print("Received invalid JSON data")

def process_update(update_info):
    """Processes received JSON data and updates GUI."""
    if "host_vehicle" in update_info:
        gui.update_host_info(update_info["host_vehicle"])
    if "spat" in update_info:
        gui.update_spat_data(update_info["spat"]["min_end"], update_info["spat"]["max_end"], update_info["spat"]["signal"])
    if "remote_vehicles" in update_info:
        gui.update_remote_table(update_info["remote_vehicles"])
    if "lead_vehicle" in update_info:
        gui.update_lead_vehicle_info(update_info["lead_vehicle"])

root = tk.Tk()
gui = DriverInLoopGUI(root)
server_thread = threading.Thread(target=socket_server, daemon=True)
server_thread.start()
root.mainloop()
