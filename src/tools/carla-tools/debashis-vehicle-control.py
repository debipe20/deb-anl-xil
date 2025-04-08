import glob
import os
import sys

carla_egg_path = os.environ.get("CARLA_EGG_PATH")

# if carla_path:
#     sys.path.append(carla_path)
#     print(f"Added {carla_path} to Python path")
# else:
#     print("CARLAPATH environment variable is not set.")

try:
    sys.path.append(glob.glob(carla_egg_path + '/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
import carla

import random
import time
import numpy as np
import cv2
from carla import ColorConverter as cc
# from agents.navigation.controller import VehiclePIDController

IM_WIDTH = 640
IM_HEIGHT = 480


def process_img(image):
    i = np.array(image.raw_data)
    i2 = i.reshape((IM_HEIGHT, IM_WIDTH, 4))
    i3 = i2[:, :, :3]
    cv2.imshow("", i3)
    cv2.waitKey(1)
    return i3/255.0


actor_list = []
try:
    client = carla.Client('localhost', 2000)
    client.set_timeout(2.0)

    world = client.get_world()

    blueprint_library = world.get_blueprint_library()

    bp = blueprint_library.filter('model3')[0]
    print(bp)

    # spawn_point = random.choice(world.get_map().get_spawn_points())
    # spawn_point = carla.Transform(carla.Location(x=-189.172150, y=-509.719635, z=41.869663), carla.Rotation(pitch=1.192223, yaw=-64.276932, roll=0.000000))
    spawn_point = carla.Transform(carla.Location(x=24.0, y=1070, z=231.780380), carla.Rotation(pitch=0, yaw=-105, roll=0))
    vehicle = world.spawn_actor(bp, spawn_point)
    vehicle.apply_control(carla.VehicleControl(throttle=1.0, steer=0.0))
    # vehicle.set_autopilot(True)  # if you just wanted some NPCs to drive.

    actor_list.append(vehicle)

    # https://carla.readthedocs.io/en/latest/cameras_and_sensors
    # get the blueprint for this sensor
    blueprint = blueprint_library.find('sensor.camera.rgb')
    # change the dimensions of the image
    blueprint.set_attribute('image_size_x', f'{IM_WIDTH}')
    blueprint.set_attribute('image_size_y', f'{IM_HEIGHT}')
    blueprint.set_attribute('fov', '110')

    # Adjust sensor relative to vehicle
    spawn_point = carla.Transform(carla.Location(x=2.5, z=0.7))

    # spawn the sensor and attach to vehicle.
    sensor = world.spawn_actor(blueprint, spawn_point, attach_to=vehicle)

    # add sensor to list of actors
    actor_list.append(sensor)

    # do something with this sensor
    sensor.listen(lambda data: process_img(data))

    time.sleep(10)

finally:
    print('destroying actors')
    for actor in actor_list:
        actor.destroy()
    print('done.')