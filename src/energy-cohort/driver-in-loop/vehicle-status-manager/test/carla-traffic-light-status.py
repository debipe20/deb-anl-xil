from __future__ import print_function


# ==============================================================================
# -- find carla module ---------------------------------------------------------
# ==============================================================================


import glob
import os
import sys
carla_egg_path = os.getenv("CARLA_EGG_PATH")

try:
    sys.path.append(glob.glob(carla_egg_path + '/carla-*%d.%d-%s.egg' % (sys.version_info.major, sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass


# ==============================================================================
# -- imports -------------------------------------------------------------------
# ==============================================================================


import carla
import socket
import json
import time
import os
import platform


# Read a config file into a json object:
current_os = platform.system()
    
if current_os == "Linux":
    config_file_path = os.path.join(os.path.expanduser("~"), "Desktop", "deb-anl-xil", "config", "anl-master-config.json")
    
# configFile = open("/nojournal/bin/mmitss-phase3-master-config.json", 'r')
configFile = open(config_file_path, 'r')
config = (json.load(configFile))
configFile.close()

hostIp = config["IPAddress"]["HostIp"]
port = config["PortNumber"]["SpatManager"]
carla_traffic_light_status_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
carla_traffic_light_status_sender_socket.bind((hostIp,port))

vehicleStatusManagerPort = config["PortNumber"]["VehicleStatusManager"]
client_address = (hostIp, vehicleStatusManagerPort)

# Connect to the CARLA server and retrieve world
carla_client = carla.Client('localhost', 2000)
carla_client.set_timeout(10.0)
world = carla_client.get_world()

# Retrieve all traffic light actors
traffic_lights = [actor for actor in world.get_actors() if 'traffic_light' in actor.type_id]

target_location = carla.Location(x=9.199999809265137, y=-110.39999389648438, z=227.0)
# Infinite loop to extract traffic light information every second
try:
    while True:
        for traffic_light in traffic_lights:
            state = traffic_light.get_state()
            location = traffic_light.get_transform().location
            
            distance_to_traffic_light = location.distance(target_location)
            # Check if the traffic light ID is 4 and location matches the target location
            if traffic_light.id == 6 and  distance_to_traffic_light<= 1.0:  # You can set an acceptable range
                # Formulate the JSON message
                traffic_light_message = {
                    "MsgType": "CarlaTrafficLightStatus",
                    "TrafficLightID": traffic_light.id,
                    "LightState": str(state)  # State converted to string for JSON
                }

                # Convert the message to a JSON string
                traffic_light_message_json = json.dumps(traffic_light_message, indent=4)
                
                carla_traffic_light_status_sender_socket.sendto(traffic_light_message_json.encode(),client_address)
                print(f"Following json message is sent:\n{traffic_light_message_json}")  # Print or send the JSON message
            print(f"Traffic Light ID: {traffic_light.id}")
            print(f"State: {state}")
            print(f"Location: x={location.x}, y={location.y}, z={location.z}")
            
        # Wait for 1 second before extracting information again
        time.sleep(0.999)
    
except KeyboardInterrupt:
    print("Loop interrupted by user")

finally:
    carla_traffic_light_status_sender_socket.close()
    print("Socket closed.")