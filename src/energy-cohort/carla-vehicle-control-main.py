import glob
import platform
import os
import sys
import random
import json
import time
import math
from SteeringAngleManager import SteeringAngleManager

# ---------- Locate the CARLA egg ----------
def _append_carla_egg():
    carla_egg_path = os.environ.get("CARLA_EGG_PATH")
    if not carla_egg_path:
        print("Warning: CARLA_EGG_PATH not set. Ensure it points to the correct CARLA egg.")
    candidates = []
    if carla_egg_path:
        candidates += glob.glob(os.path.join(carla_egg_path, "carla-*%d.%d-*.egg" % (sys.version_info.major, sys.version_info.minor)))
    candidates += glob.glob(os.path.expanduser("~/CARLA*/PythonAPI/carla/dist/carla-*%d.%d-*.egg" % (sys.version_info.major, sys.version_info.minor)))
    candidates += glob.glob("/opt/carla-simulator/PythonAPI/carla/dist/carla-*%d.%d-*.egg" % (sys.version_info.major, sys.version_info.minor))
    if candidates:
        sys.path.append(candidates[0])
    else:
        print("Error: No CARLA egg found.")

# Add CARLA egg to sys.path before importing carla
_append_carla_egg()

# Now import carla after appending the egg path
import carla

# GNSS and IMU sensor data variables
latitude = None
longitude = None
elevation = None
imu_heading = None  # Use a separate variable for heading from IMU

# GNSS Callback function
def gnss_callback(data):
    global latitude, longitude, elevation
    latitude = data.latitude
    longitude = data.longitude
    elevation = data.altitude

# IMU Callback function
def imu_callback(data):
    global imu_heading
    imu_heading = math.degrees(data.compass) # Convert compass reading to degrees
    
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
    
    way_points_file_name = config["VehicleInformation"]["EgoBsmLogFileName"]
    
    if current_os == "Linux":
        way_points_file_directory = os.path.join(os.path.expanduser("~"), "Desktop", "deb-anl-xil", "data", "kearney", way_points_file_name)
    
    elif current_os == "Windows":
        way_points_file_directory = os.path.join("C:\\", "Users", "ddas", "deb-anl-xil", "data", "kearney", way_points_file_name)
    
    actor_list = []

    try:
        # === Connect to CARLA ===
        client = carla.Client('localhost', 2000)
        client.set_timeout(2.0)
        world = client.get_world()
        blueprint_library = world.get_blueprint_library()

        # Choose a vehicle blueprint (Tesla Model 3 if present, else any vehicle)
        veh_bps = blueprint_library.filter("vehicle.tesla.model3")
        bp = veh_bps[0] if veh_bps else random.choice(blueprint_library.filter("vehicle.*"))

        # Spawn point: using your fixed spawn point
        spawn_point = carla.Transform(carla.Location(x=21.6, y=984, z=231), carla.Rotation(pitch=0.4, yaw=-90, roll=0))  # Kearney Road
        try:
            vehicle = world.spawn_actor(bp, spawn_point)
            actor_list.append(vehicle)
            print(f"Spawned {vehicle.type_id} at {spawn_point}")
        except Exception as e:
            print(f"Failed to spawn vehicle: {e}")
            return
        
        # Attach GNSS sensor to the vehicle
        gnss_bp = blueprint_library.find('sensor.other.gnss')
        gnss_spawn_point = carla.Transform(carla.Location(x=0.0, y=0.0, z=2.0))  # Attach on top of the vehicle
        gnss_sensor = world.spawn_actor(gnss_bp, gnss_spawn_point, attach_to=vehicle)
        actor_list.append(gnss_sensor)

        # Attach IMU sensor to the vehicle
        imu_bp = blueprint_library.find('sensor.other.imu')
        imu_spawn_point = carla.Transform(carla.Location(x=0.0, y=0.0, z=2.0))  # Attach on top of the vehicle
        imu_sensor = world.spawn_actor(imu_bp, imu_spawn_point, attach_to=vehicle)
        actor_list.append(imu_sensor)

        # Listen to sensor data
        gnss_sensor.listen(gnss_callback)
        imu_sensor.listen(imu_callback)
        
        # Set vehicle controls (Throttle, Brake, Steer)
        vehicle.apply_control(carla.VehicleControl(throttle=0.0, brake=0.5, steer=0.0))
        time.sleep(3.0)
        # Initialize SteeringAngleManager
        current_position = (vehicle.get_location().x, vehicle.get_location().y)
        # print(f"Initial Position: {current_position}")
        print(f"[{time.time()}]:Latitude: {latitude}, Longitude: {longitude}, Altitude: {elevation}, IMU Heading: {imu_heading}")
        steering_angle_manager = SteeringAngleManager(way_points_file_directory, latitude, longitude, elevation, imu_heading)


        print("Vehicle spawned and moving. Press Enter to destroy and quit.")

        input()  # Wait for user to press Enter to quit
        
        while True:
            # Get the current vehicle position
            current_position = (vehicle.get_location().x, vehicle.get_location().y)
            transform = vehicle.get_transform()
            vehicle_heading = transform.rotation.yaw  # Get vehicle heading (yaw)
                        
            # Print GNSS and IMU data
            if latitude is not None and longitude is not None:
                print(f"[{time.time()}]:GNSS - Latitude: {latitude}, Longitude: {longitude}, Altitude: {elevation}")
            
            if imu_heading is not None:
                print(f"[{time.time()}]:IMU - Heading: {imu_heading} degrees")

            # # Calculate the steering angle
            steering_angle = steering_angle_manager.get_steering_angle(vehicle)
            # print(f"[{time.time()}]: Steering Angle is: {steering_angle}")

            # Apply control (steering and throttle)
            vehicle.apply_control(carla.VehicleControl(throttle=0.3, steer=steering_angle))

            # # Wait for the next tick (synchronization)
            world.wait_for_tick()
            # time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nCTRL+C detected. Exiting...")
    
    finally:
        print("Destroying actors...")
        for actor in actor_list:
            actor.destroy()
        print("Done.")

if __name__ == "__main__":
    main()
