import socket
import json
import time
import os
import platform
import struct
import numpy as np
import matplotlib.pyplot as plt

def generate_trapezoidal_speed_profile(v_max, a_max, d_max, cruise_time, idle_time, num_cycles, dt):
    """
    Generate a trapezoidal speed profile with idle gaps between cycles.

    Parameters:
    - v_max: max speed (m/s)
    - a_max: acceleration rate (m/s²)
    - d_max: deceleration rate (m/s²)
    - cruise_time: steady-state cruising time per cycle (s)
    - idle_time: duration of idle (0 speed) between cycles (s)
    - num_cycles: number of full accel-cruise-decel cycles
    - dt: time step size (s)
    """
    t_accel = v_max / a_max
    t_decel = v_max / d_max
    time = []
    speed_profile = []
    current_time = 0.0

    # 🔹 Add idle at the beginning
    t = np.arange(0, idle_time, dt)
    v = np.zeros_like(t)
    speed_profile.extend(v.tolist())
    time.extend((current_time + t).tolist())
    current_time += idle_time

    for cycle in range(num_cycles):
        # Acceleration
        t = np.arange(0, t_accel, dt)
        v = a_max * t
        speed_profile.extend(v.tolist())
        time.extend((current_time + t).tolist())
        current_time += t_accel

        # Cruise
        t = np.arange(0, cruise_time, dt)
        v = np.full_like(t, v_max)
        speed_profile.extend(v.tolist())
        time.extend((current_time + t).tolist())
        current_time += cruise_time

        # Deceleration
        t = np.arange(0, t_decel, dt)
        v = v_max - d_max * t
        speed_profile.extend(v.tolist())
        time.extend((current_time + t).tolist())
        current_time += t_decel

        # Idle between cycles
        if cycle < num_cycles - 1:
            t = np.arange(0, idle_time, dt)
            v = np.zeros_like(t)
            speed_profile.extend(v.tolist())
            time.extend((current_time + t).tolist())
            current_time += idle_time

    # 🔹 Add idle at the end
    t = np.arange(0, idle_time, dt)
    v = np.zeros_like(t)
    speed_profile.extend(v.tolist())
    time.extend((current_time + t).tolist())
    current_time += idle_time

    return time, speed_profile

def plot_speed_profile(time, speed, title_name, plot_name):
    plt.figure(figsize=(10, 5))
    plt.plot(time, speed, label="Speed (m/s)")
    plt.title(title_name)
    plt.xlabel("Time (s)")
    plt.ylabel("Speed (m/s)")
    plt.grid(True)
    
    # Automatically increase y-axis limit by 10% for spacing
    max_speed = max(speed)
    plt.ylim(0, max_speed * 1.1)

    plt.legend(loc='upper right')  # Top-right corner
    plt.tight_layout()
    # plt.show()
    plt.savefig(plot_name)

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

    host_ip = config["IPAddress"]["HostIp"]
    host_port = config["PortNumber"]["VehicleSpy"]
    host_address = (host_ip, host_port)

    client_ip = config["IPAddress"]["HostIp"]
    client_port = config["PortNumber"]["DriverInLoopTestManager"]
    client_address = (client_ip, client_port)
    
    speedDataSenderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    speedDataSenderSocket.bind(host_address)
    
    
    v_max = 50.0 #in mph
    a_max = 2.0  #in mps2
    d_max = 2.0 #in mps2
    cruise_time = 100.0
    idle_time = 5.0
    num_cycles = 20
    dt = 0.1

    time_series, speed_series = generate_trapezoidal_speed_profile(v_max, a_max, d_max, cruise_time, idle_time, num_cycles, dt)
    
    print("📤 Sending speed data every 0.1s...")

    for t, speed in zip(time_series, speed_series):
        # data = {
        #     "timestamp": round(t, 2),
        #     "speed_mps": round(speed, 3)
        # }

        # message = json.dumps(data).encode("utf-8")
        # speedDataSenderSocket.sendto(message, client_address)
        # # Print sent data for debugging
        # print(f"Sent: {data}")
        
        encoded_lead_speed = struct.pack("d", speed)
        encoded_ego_speed = struct.pack("d", speed)

        sendingData =  encoded_lead_speed + encoded_ego_speed 
        speedDataSenderSocket.sendto(sendingData, client_address)

        time.sleep(dt)

    print("✅ Done sending all speed values.")
    title_name = "Trapezoidal Drive Cycle"
    plot_name = "trapezoidal_speed_profile.png"
    plot_speed_profile(time_series, speed_series, title_name, plot_name)
    speedDataSenderSocket.close()
    

if __name__ == "__main__":
    main()