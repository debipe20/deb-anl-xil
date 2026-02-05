import glob
import os
import sys
import time
import numpy as np
import socket
import platform
import os
import json
import struct
import math
from WayPointManager import WayPointsManager
from SpeedPIDController import SpeedPIDController

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

MPH_To_MPS = 0.44704
MPS_To_MPH = 2.23694
KPH_To_MPH = 0.621371
KPH_To_MPS = 0.277778
    
def main():
    actor_list = []
    
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
    
    lead_controller_ip = config["IPAddress"]["HostIp"]
    lead_controller_port = config["PortNumber"]["LeadController"]
    lead_controller_socket = None
    
    pid = SpeedPIDController(Kp=0.9, Ki=0.1, Kd=0.01,
                 max_integral=10.0, deadband=0.3,
                 min_throttle=0.15, min_brake=0.05,
                 filter_alpha=0.2, throttle_smoothing=0.05)
        
    way_points_file = config["VehicleInformation"]["LeadBsmLogFileName"]
    way_points_manager = WayPointsManager(config, way_points_file)
    
    try:
        # === Connect to CARLA ===
        client = carla.Client('localhost', 2000)
        client.set_timeout(2.0)
        world = client.get_world()
        blueprint_library = world.get_blueprint_library()

        # bp = blueprint_library.filter('model3')[0]
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
        sensor_data = {"lat": None, "lon": None, "heading": None}

        gnss_bp = world.get_blueprint_library().find('sensor.other.gnss')
        gnss_bp.set_attribute("sensor_tick",str(0.1))
        lead_gnss = world.spawn_actor(gnss_bp, carla.Transform(carla.Location(x=1.0, z=2.8)), attach_to=vehicle, attachment_type=carla.AttachmentType.Rigid)
        # ego_gnss.listen(lambda gnss: gnss_callback(gnss))


        imu_bp = world.get_blueprint_library().find('sensor.other.imu')
        imu_bp.set_attribute("sensor_tick",str(0.1))
        lead_imu = world.spawn_actor(imu_bp, carla.Transform(), attach_to=vehicle, attachment_type=carla.AttachmentType.Rigid)
        # ego_imu.listen(lambda imu: imu_callback(imu))
        
        lead_gnss.listen(lambda data: sensor_data.update({"lat": data.latitude, "lon": data.longitude}))
        lead_imu.listen(lambda data: sensor_data.update({"heading": data.compass % 360}))


        # Apply basic control
        # vehicle.apply_control(carla.VehicleControl(throttle=0.5, steer=0.0))

        # === Socket Setup ===
        lead_controller_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        lead_controller_socket.bind((lead_controller_ip, lead_controller_port))
        
        last_time = None

        while True:

            data, addr = lead_controller_socket.recvfrom(1024)
            # decoded = data.decode("utf-8")
            # print(f"Received from {addr}: {decoded}")
            
            # desired_lead_speed_mps = struct.unpack("d", data)
            desired_lead_speed_mps = struct.unpack("d", data)[0]
            velocity = vehicle.get_velocity()
            current_speed_kmh = 3.6 * math.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2)  # km/h
            current_speed_mps = current_speed_kmh * KPH_To_MPS #kph to mph = speed_kph * 0.621371 
            current_speed_mph = current_speed_kmh * KPH_To_MPH

            if desired_lead_speed_mps < 0.1 and current_speed_mps < 0.1:
                    pid.reset()

            current_lat = sensor_data["lat"]
            current_lon = sensor_data["lon"]
            current_heading = sensor_data["heading"]
                
            print(f"Desired: {desired_lead_speed_mps:.2f} m/s | Current: {current_speed_mps:.2f} m/s | "
                f"Lat: {current_lat} | Lon: {current_lon} | Heading: {current_heading}")
            
            desired_lat, desired_lon, desired_heading, desired_x, desired_y, desired_yaw = way_points_manager.get_next_coordinates(current_speed_mps, current_lat, current_lon, current_heading)
                
            current_time = time.time()
            dt = current_time - last_time if last_time is not None else 0.05
            dt = max(dt, 0.01)  # Clamp to a reasonable minimum
            last_time = current_time
            
            # Get throttle, brake, and steer 
            throttle, brake, control = pid.compute_control(current_speed_mps, desired_lead_speed_mps, dt)

            steer = pid.compute_steering_angle(current_heading, desired_heading, current_speed_mps)
            # steer =  self.pid.compute_steering_from_xy(current_x, current_y, current_yaw, desired_x, desired_y)
            vehicle.apply_control(carla.VehicleControl(throttle=throttle, brake=brake, steer=steer))


    except KeyboardInterrupt:
        print("\nCTRL+C detected. Exiting...")

    finally:
        if lead_controller_socket:
            lead_controller_socket.close()
        print("Destroying actors...")
        for actor in actor_list:
            actor.destroy()
        print("Done.")
        

if __name__ == "__main__":
    main()