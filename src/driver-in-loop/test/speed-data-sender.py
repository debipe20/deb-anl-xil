import socket
import json
import struct
import random
import time
import os
import platform


MPS_To_MPH = 2.23694
def getSpeed(previousSpeed):

    currentSpeed = previousSpeed * (random.randint(80,130)/100)
    
    if(currentSpeed > 10.0):
        currentSpeed = 8.0

            
    return currentSpeed

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
    
    speedDataSenderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    speedDataSenderSocket.bind(host_address)
    
    lead_speed = 0.0
    previous_ego_speed = 1.0
    previous_time = time.time()

    while True:
        ego_speed = getSpeed(previous_ego_speed)
        previous_ego_speed = ego_speed
        lead_speed = ego_speed

        encoded_lead_speed = struct.pack("d", lead_speed)
        encoded_ego_speed = struct.pack("d", ego_speed)

        sendingData =  encoded_lead_speed + encoded_ego_speed 
        speedDataSenderSocket.sendto(sendingData, client_address)
        print("Sent following speed data : " + str(lead_speed) + ", " + str(ego_speed))
        time.sleep(0.0997)

    speedDataSenderSocket.close()

if __name__ == '__main__':
    main()