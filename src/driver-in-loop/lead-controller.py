import glob
import os
import sys
import time
import numpy as np
import socket
import platform
import os
import json

# Add CARLA egg path
carla_egg_path = os.getenv("CARLA_EGG_PATH")
try:
    sys.path.append(glob.glob(carla_egg_path + '/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    print("CARLA egg not found. Make sure CARLA_EGG_PATH is set correctly.")
    sys.exit(1)

import carla
from carla import ColorConverter as cc


actor_list = []

def load_socket_config():
    current_os = platform.system()
    if current_os == "Linux":
        config_path = os.path.join(os.path.expanduser("~"), "Desktop", "deb-anl-xil", "config", "anl-master-config.json")
    elif current_os == "Windows":
        config_path = os.path.join("C:\\", "Users", "ddas", "deb-anl-xil", "config", "anl-master-config.json")
    else:
        raise OSError(f"Unsupported OS: {current_os}")

    with open(config_path, "r") as config_file:
        config = json.load(config_file)
    return config["IPAddress"]["HostIp"], config["PortNumber"]["LeadController"]

def main():

    try:
        # === Connect to CARLA ===
        client = carla.Client('localhost', 2000)
        client.set_timeout(2.0)
        world = client.get_world()
        blueprint_library = world.get_blueprint_library()

        bp = blueprint_library.filter('model3')[0]
        blueprint = world.get_blueprint_library().find('vehicle.lincoln.mkz2017')
        blueprint.set_attribute('role_name', "ANL-Lead")
        if blueprint.has_attribute('color'):
            # color = random.choice(blueprint.get_attribute('color').recommended_values)
            # print(blueprint.get_attribute('color').recommended_values)
            color = '229,28,0'
            blueprint.set_attribute('color', color)

        spawn_point = carla.Transform(carla.Location(x=21.970606, y=988.040283, z=232.248337), carla.Rotation(pitch=0, yaw=-105, roll=0))

        vehicle = world.spawn_actor(bp, spawn_point)
        actor_list.append(vehicle)

        # Apply basic control
        vehicle.apply_control(carla.VehicleControl(throttle=0.5, steer=0.0))

        # === Socket Setup ===
        host_ip, port = load_socket_config()
        print(f"Listening on {host_ip}:{port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((host_ip, port))
        sock.settimeout(1.0)  # Non-blocking receive with timeout

        while True:
            try:
                data, addr = sock.recvfrom(1024)
                decoded = data.decode("utf-8")
                print(f"Received from {addr}: {decoded}")
                # You can parse this and control the vehicle accordingly
            except socket.timeout:
                pass  # No data, just continue
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nCTRL+C detected. Exiting...")

    finally:
        print("Destroying actors...")
        for actor in actor_list:
            actor.destroy()
        print("Done.")


if __name__ == "__main__":
    main()