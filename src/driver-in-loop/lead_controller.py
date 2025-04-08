#!/usr/bin/env python

# Copyright (c) 2019 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

# Allows controlling a vehicle with a keyboard. For a simpler and more
# documented example, please take a look at tutorial.py.

"""
Welcome to CARLA manual control.

Use ARROWS or WASD keys for control.

    W            : throttle
    S            : brake
    A/D          : steer left/right
    Q            : toggle reverse
    Space        : hand-brake
    P            : toggle autopilot
    M            : toggle manual transmission
    ,/.          : gear up/down
    CTRL + W     : toggle constant velocity mode at 60 km/h

    L            : toggle next light type
    SHIFT + L    : toggle high beam
    Z/X          : toggle right/left blinker
    I            : toggle interior light

    TAB          : change sensor position
    ` or N       : next sensor
    [1-9]        : change to sensor [1-9]
    G            : toggle radar visualization
    C            : change weather (Shift+C reverse)
    Backspace    : change vehicle

    R            : toggle recording images to disk

    CTRL + R     : toggle recording of simulation (replacing any previous)
    CTRL + P     : start replaying last recorded simulation
    CTRL + +     : increments the start time of the replay by 1 second (+SHIFT = 10 seconds)
    CTRL + -     : decrements the start time of the replay by 1 second (+SHIFT = 10 seconds)

    F1           : toggle HUD
    H/?          : toggle help
    ESC          : quit
"""

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

from carla import ColorConverter as cc

import argparse
import collections
import datetime
import logging
import math
import random
import re
import weakref
import threading
import socket
import json
import time
import os
import platform
import haversine
import pandas as pd
from carla import Location, Rotation, Transform

try:
    import pygame
    from pygame.locals import KMOD_CTRL
    from pygame.locals import KMOD_SHIFT
    from pygame.locals import K_0
    from pygame.locals import K_9
    from pygame.locals import K_BACKQUOTE
    from pygame.locals import K_BACKSPACE
    from pygame.locals import K_COMMA
    from pygame.locals import K_DOWN
    from pygame.locals import K_ESCAPE
    from pygame.locals import K_F1
    from pygame.locals import K_LEFT
    from pygame.locals import K_PERIOD
    from pygame.locals import K_RIGHT
    from pygame.locals import K_SLASH
    from pygame.locals import K_SPACE
    from pygame.locals import K_TAB
    from pygame.locals import K_UP
    from pygame.locals import K_a
    from pygame.locals import K_c
    from pygame.locals import K_g
    from pygame.locals import K_d
    from pygame.locals import K_h
    from pygame.locals import K_m
    from pygame.locals import K_n
    from pygame.locals import K_p
    from pygame.locals import K_q
    from pygame.locals import K_r
    from pygame.locals import K_s
    from pygame.locals import K_w
    from pygame.locals import K_l
    from pygame.locals import K_i
    from pygame.locals import K_z
    from pygame.locals import K_x
    from pygame.locals import K_MINUS
    from pygame.locals import K_EQUALS
except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')

try:
    import numpy as np
except ImportError:
    raise RuntimeError('cannot import numpy, make sure numpy package is installed')

MPH_To_MPS = 0.44704
MPS_To_MPH = 2.23694
KPH_To_MPH = 0.621371
KPH_To_MPS = 0.277778

# ==============================================================================
# -- Global functions ----------------------------------------------------------
# ==============================================================================


def find_weather_presets():
    rgx = re.compile('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)')
    name = lambda x: ' '.join(m.group(0) for m in rgx.finditer(x))
    presets = [x for x in dir(carla.WeatherParameters) if re.match('[A-Z].+', x)]
    return [(getattr(carla.WeatherParameters, x), name(x)) for x in presets]


def get_actor_display_name(actor, truncate=250):
    name = ' '.join(actor.type_id.replace('_', '.').title().split('.')[1:])
    return (name[:truncate - 1] + u'\u2026') if len(name) > truncate else name


# ==============================================================================
# -- World ---------------------------------------------------------------------
# ==============================================================================


class World(object):
    def __init__(self, carla_world, hud, args):
        self.world = carla_world
        """to avoid crashing"""
        settings = self.world.get_settings()
        settings.synchronous_mode = False  # ✅ Run CARLA in async mode
        self.world.apply_settings(settings)
        """" finish """
        self.actor_role_name = args.rolename
        try:
            self.map = self.world.get_map()
        except RuntimeError as error:
            print('RuntimeError: {}'.format(error))
            print('  The server could not send the OpenDRIVE (.xodr) file:')
            print('  Make sure it exists, has the same name of your town, and is correct.')
            sys.exit(1)
        self.hud = hud
        self.player = None
        self.collision_sensor = None
        self.lane_invasion_sensor = None
        self.gnss_sensor = None
        self.imu_sensor = None
        self.radar_sensor = None
        self.camera_manager = None
        self._weather_presets = find_weather_presets()
        self._weather_index = 0
        self._actor_filter = args.filter
        self._gamma = args.gamma
        self.restart()
        self.world.on_tick(hud.on_world_tick)
        self.recording_enabled = False
        self.recording_start = 0
        self.constant_velocity_enabled = False

    def restart(self):
        self.player_max_speed = 1.589
        self.player_max_speed_fast = 3.713
        # Keep same camera config if the camera manager exists.
        cam_index = self.camera_manager.index if self.camera_manager is not None else 0
        cam_pos_index = self.camera_manager.transform_index if self.camera_manager is not None else 0
        # Get a random blueprint.
        # blueprint = random.choice(self.world.get_blueprint_library().filter(self._actor_filter))
        # blueprint = self.world.get_blueprint_library().find('vehicle.tesla.model3') ## Vehicle will be Tesla model 3
        blueprint = self.world.get_blueprint_library().find('vehicle.lincoln.mkz2017')
        blueprint.set_attribute('role_name', self.actor_role_name)
        if blueprint.has_attribute('color'):
            color = random.choice(blueprint.get_attribute('color').recommended_values)
            blueprint.set_attribute('color', color)
        if blueprint.has_attribute('driver_id'):
            driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
            blueprint.set_attribute('driver_id', driver_id)
        if blueprint.has_attribute('is_invincible'):
            blueprint.set_attribute('is_invincible', 'true')
        # set the max speed
        if blueprint.has_attribute('speed'):
            self.player_max_speed = float(blueprint.get_attribute('speed').recommended_values[1])
            self.player_max_speed_fast = float(blueprint.get_attribute('speed').recommended_values[2])
        else:
            print("No recommended values for 'speed' attribute")
        # Spawn the player.
        if self.player is not None:
            spawn_point = self.player.get_transform()
            spawn_point.location.z += 2.0
            spawn_point.rotation.roll = 0.0
            spawn_point.rotation.pitch = 0.0
            self.destroy()
            self.player = self.world.try_spawn_actor(blueprint, spawn_point)
        while self.player is None:
            if not self.map.get_spawn_points():
                print('There are no spawn points available in your map/town.')
                print('Please add some Vehicle Spawn Point to your UE4 scene.')
                sys.exit(1)
            # spawn_points = self.map.get_spawn_points()
            # spawn_point = random.choice(spawn_points) if spawn_points else carla.Transform()
            spawn_point = carla.Transform(carla.Location(x=24.0, y=1070, z=231.780380), carla.Rotation(pitch=0, yaw=-105, roll=0)) #Kearney Road
            self.player = self.world.try_spawn_actor(blueprint, spawn_point)
        # Set up the sensors.
        self.collision_sensor = CollisionSensor(self.player, self.hud)
        self.lane_invasion_sensor = LaneInvasionSensor(self.player, self.hud)
        self.gnss_sensor = GnssSensor(self.player)
        self.imu_sensor = IMUSensor(self.player)
        self.camera_manager = CameraManager(self.player, self.hud, self._gamma)
        self.camera_manager.transform_index = cam_pos_index
        self.camera_manager.set_sensor(cam_index, notify=False)
        actor_type = get_actor_display_name(self.player)
        self.hud.notification(actor_type)
        self.player.gnss_sensor = self.gnss_sensor  # 🔗 attach to vehicle
        self.player.imu_sensor = self.imu_sensor    # 🔗 attach to vehicle


    def next_weather(self, reverse=False):
        self._weather_index += -1 if reverse else 1
        self._weather_index %= len(self._weather_presets)
        preset = self._weather_presets[self._weather_index]
        self.hud.notification('Weather: %s' % preset[1])
        self.player.get_world().set_weather(preset[0])

    def toggle_radar(self):
        if self.radar_sensor is None:
            self.radar_sensor = RadarSensor(self.player)
        elif self.radar_sensor.sensor is not None:
            self.radar_sensor.sensor.destroy()
            self.radar_sensor = None

    def tick(self, clock):
        self.hud.tick(self, clock)

    def render(self, display):
        self.camera_manager.render(display)
        self.hud.render(display)

    def destroy_sensors(self):
        self.camera_manager.sensor.destroy()
        self.camera_manager.sensor = None
        self.camera_manager.index = None

    def destroy(self):
        if self.radar_sensor is not None:
            self.toggle_radar()
        sensors = [
            self.camera_manager.sensor,
            self.collision_sensor.sensor,
            self.lane_invasion_sensor.sensor,
            self.gnss_sensor.sensor,
            self.imu_sensor.sensor]
        for sensor in sensors:
            if sensor is not None:
                sensor.stop()
                sensor.destroy()
        if self.player is not None:
            self.player.destroy()
            
# ==============================================================================
# -------------------------- WayPointsManager ---------------------------
# ==============================================================================
          
class WayPointsManager:

    def __init__(self, config, way_points_file):
        """
        Initializes the BSM Generator with vehicle parameters and waypoints.

        Args:
            config (dict): Configuration settings.
            vehicle_id (str): Unique vehicle ID.
            way_points_file (str): File containing preloaded waypoints.
            logger (Logger): Logger instance for debugging and tracking.
        """

        self.config = config
        self.current_lat = 0.0
        self.current_lon = 0.0
        self.current_elev = 0.0
        self.current_speed = 0.0
        self.current_heading = 0.0
        self.previous_lat = 41.7007424 
        self.previous_lon = -87.9915918
        self.previous_index = 0
        self.previous_time = time.time()
        self.desired_lat = 0.0
        self.desired_lon = 0.0
        self.desired_x = 0.0
        self.desired_y = 0.0
        # self.desired_z = 0.0
        self.desired_yaw = 0.0
        self.time_step = 0.0
        self.extra_distance = 0.0
        self.step = 0
        self.previous_time_stamp_set_status = False
        self.latitude_list, self.longitude_list, self.elevation_list, self.heading_list = ([] for i in range(4) )
        self.way_points_file = way_points_file
        self.read_way_points()
        
        self.debug_log_file = open("../../log/debug/debug_lead_controller_log.csv", "w")
        log_header = ("timestamp, desired_lat, desired_lon, desired_heading, current_lat, current_lon, current_speed, current_heading, travel_distance, calculated_distance, calculated_distance_next, starting_index, selected_index\n")
        self.debug_log_file.write(log_header)
        
        self.heading_log_file = open("../../log/debug/debug_heading_log.log", "w")
        write_msg = f"[{time.time()}]: {{'TimeStamp'}}, {{'previous_index'}}, {{'desired_index'}}, {{'current_lat'}}, {{'current_lon'}}, {{'current_heading'}}, {{'desired_lat'}}, {{'desired_lon'}}, {{'heading_status'}} \n"
        self.heading_log_file.write(write_msg)

    def read_way_points(self):
        """
        - Method to get all the coordinates from preload waypoints/BSMs
        """
        current_os = platform.system()
        
        if current_os == "Linux":
            self.way_points_data_file = os.path.join(os.path.expanduser("~"), "Desktop", "deb-anl-xil", "data", "kearney", self.way_points_file)
        
        elif current_os == "Windows":
            self.way_points_data_file = os.path.join("C:\\", "Users", "ddas", "deb-anl-xil", "data", "kearney", self.way_points_file)
        
        else:
            raise OSError(f"Unsupported operating system: {current_os}")
        
        dataFrame = pd.read_csv(self.way_points_data_file)
        self.latitude_list = dataFrame["Latitude"].tolist()
        self.longitude_list = dataFrame["Longitude"].tolist()
        self.elevation_list = dataFrame["Elevation"].tolist()
        self.heading_list = dataFrame["Heading"].tolist()
        
        self.x_list = dataFrame["X"].tolist()
        self.y_list = dataFrame["Y"].tolist()
        # self.z_list = dataFrame["Z"].tolist()
        self.yaw_list = dataFrame["Yaw"].tolist()

        self.current_lat = self.latitude_list[0]
        self.current_lon = self.longitude_list[0]
        self.current_elev = self.elevation_list[0]
        self.current_heading = self.heading_list[0]
        self.previous_lat = self.latitude_list[0]
        self.previous_lon = self.longitude_list[0]
        
    def get_starting_index(self, previous_index, current_lat, current_lon, current_heading):
        desired_index = 0
        lat1 = current_lat
        lon1 = current_lon
        heading1 = current_heading
        heading_status = 'behind'
        

        # Iterate over the latitude and longitude list to calculate the bearing
        for index, value in enumerate(self.latitude_list[previous_index:], start=previous_index):
            lat2 = self.latitude_list[index]
            lon2 = self.longitude_list[index]
            
            # Print lat2, lon2 for debugging purposes
            print(f"lat2, lon2: {lat2}, {lon2}")
            
            # Convert latitudes and longitudes to radians
            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            diff_lon_rad = math.radians(lon2 - lon1)

            # Calculate the bearing using the spherical law of cosines
            x = math.sin(diff_lon_rad) * math.cos(lat2_rad)
            y = (math.cos(lat1_rad) * math.sin(lat2_rad)) - (math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(diff_lon_rad))

            bearing = math.atan2(x, y)
            bearing = math.degrees(bearing)
            bearing_to_target = (bearing + 360) % 360
            
            # Calculate the difference between the current heading and the target bearing
            angle_diff = (bearing_to_target - heading1 + 360) % 360
            
            # Adjust the condition to correctly reflect the direction (Ahead or Behind)
            if angle_diff < 90 or angle_diff > 270:
                desired_index = index
                heading_status = 'ahead'
                print(f"Now GPS point is Ahead for index: {desired_index}")
                break  # Exit the loop once the desired index is found
            else:
                heading_status = 'behind'
                continue  # Continue to the next waypoint if the point is behind
        
        write_msg = f"[{time.time()}]: {previous_index}, {desired_index}, {current_lat}, {current_lon}, {current_heading}, {self.latitude_list[desired_index]}, {self.longitude_list[desired_index]}, {heading_status}\n"
        self.heading_log_file.write(write_msg)
        
        return desired_index    
    
    def get_desired_coordinates(self, current_lat, current_lon, current_heading):
        desired_index = 0
        desired_lat, desired_lon, desired_heading, desired_x, desired_y, desired_yaw = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        
        desired_index = self.get_starting_index(self.previous_index, current_lat, current_lon, current_heading)
        self.previous_index = desired_index
        
        desired_lat = self.latitude_list[desired_index]
        desired_lon = self.longitude_list[desired_index]
        desired_heading = self.heading_list[desired_index]
        desired_x = self.x_list[desired_index]
        desired_y = self.y_list[desired_index]
        desired_yaw = self.yaw_list[desired_index]
        
        return desired_lat, desired_lon, desired_heading, desired_x, desired_y, desired_yaw
                
    def get_next_coordinates(self, current_speed_mps, current_lat, current_lon, current_heading):
        starting_index = 0
        desired_lat, desired_lon, desired_heading, desired_x, desired_y, desired_yaw = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        current_time = time.time()
        
        if self.previous_time_stamp_set_status == False:
            self.previous_time = current_time - 0.1
            self.previous_time_stamp_set_status = True
            self.previous_index = 1
            
        # current_speed_mps = round(current_speed_mps, 2)
        if current_speed_mps < 0.005:
            current_speed_mps = 0.0
        self.time_step = current_time - self.previous_time
        travel_distance = current_speed_mps * self.time_step
        starting_index = self.get_starting_index(self.previous_index, current_lat, current_lon, current_heading)
        
        for index in range(starting_index, len(self.latitude_list) - 2):
            calculated_distance = haversine.haversine((self.current_lat, self.current_lon), (self.latitude_list[index], self.longitude_list[index]), unit=haversine.Unit.METERS)
            calculated_distance_next = haversine.haversine((self.current_lat, self.current_lon), (self.latitude_list[index + 1], self.longitude_list[index + 1]), unit=haversine.Unit.METERS)
    
            if (calculated_distance < travel_distance) and (calculated_distance_next < travel_distance):
                continue
            
            elif (calculated_distance >= travel_distance) and (calculated_distance_next > travel_distance):
                self.previous_time = time.time()
                self.previous_index = index
                desired_lat = self.latitude_list[index]
                desired_lon = self.longitude_list[index]
                desired_heading = self.heading_list[index]
                desired_x = self.x_list[index]
                desired_y = self.y_list[index]
                desired_yaw = self.yaw_list[index]
                break
            
            elif (calculated_distance < travel_distance) and (calculated_distance_next >= travel_distance):
                self.previous_time = time.time()
                self.previous_index = index + 1
                desired_lat = self.latitude_list[index + 1]
                desired_lon = self.longitude_list[index + 1]
                desired_heading = self.heading_list[index + 1]
                desired_x = self.x_list[index + 1]
                desired_y = self.y_list[index + 1]
                desired_yaw = self.yaw_list[index + 1]
                break
            
        
        # Only after all math operations:
        csv_row = (
            f"{time.time()},{desired_lat},{desired_lon},{desired_heading},"
            f"{current_lat},{current_lon},{current_speed_mps},{current_heading},"
            f"{travel_distance},{calculated_distance},{calculated_distance_next},"
            f"{starting_index},{self.previous_index}\n"
        )
        self.debug_log_file.write(csv_row)

        return desired_lat, desired_lon, desired_heading, desired_x, desired_y, desired_yaw
    
    def get_nearest_coordinates(self):
        """
        - Estimates the vehicle's real-time GPS location based on travel distance.
        - Uses the Haversine formula to find the closest matching waypoint.
        - Method to find the estimated location based on the travel time
            - Haversine distance is calculated
        - Distance between two waypoints may greater than the actual distance travel by the vehicle
            - extraDistance variable stores the difference between waypoints distance and vehicle travel distance
            - if extraDistance is greater than vehicle's travel distance, no neeed to iterate
            - if extraDistance is greater than vehicle's travel distance, deduct extraDistance from vehicle's travel distance
        - Iterate until haversine distance for current coordinate is close to the estimated distance compare to next coordinate
        """
        
        currentTime = time.time()

        if self.previous_time_stamp_set_status == False:
            self.previous_time = currentTime - 0.1
            self.previous_time_stamp_set_status = True

        self.time_step = currentTime - self.previous_time
        travelDistance = self.current_speed * self.time_step
        
        if self.extra_distance >= travelDistance:
            self.previous_time = time.time()
            self.extra_distance = self.extra_distance - travelDistance

        else:
            travelDistance = travelDistance - self.extra_distance

            for index in range(self.previous_index + 1, len(self.latitude_list) - 2):
                calculatedDistance = haversine.haversine((self.previous_lat, self.previous_lon),
                    (self.latitude_list[index], self.longitude_list[index]),
                    unit=haversine.Unit.METERS)

                calculatedDistanceNext = haversine.haversine((self.previous_lat, self.previous_lon),
                    (self.latitude_list[index + 1], self.longitude_list[index + 1]),
                    unit=haversine.Unit.METERS)

                if (calculatedDistance <= travelDistance) and (calculatedDistanceNext <= travelDistance):
                    continue

                elif (calculatedDistance >= travelDistance) and (calculatedDistanceNext > travelDistance):
                    self.previous_lat = self.latitude_list[index]
                    self.previous_lon = self.longitude_list[index]
                    self.previous_time = time.time()
                    self.previous_index = index
                    self.current_lat = self.latitude_list[index]
                    self.current_lon = self.longitude_list[index]
                    self.current_elev = self.elevation_list[index]
                    self.current_heading = self.heading_list[index]
                    self.step = index
                    self.extra_distance = calculatedDistance - travelDistance
                    self.desired_x = self.x_list[index]
                    self.desired_y = self.y_list[index]
                    self.desired_yaw = self.yaw_list[index]
                    break

                elif (calculatedDistance < travelDistance) and (calculatedDistanceNext >= travelDistance):
                    self.previous_lat = self.latitude_list[index + 1]
                    self.previous_lon = self.longitude_list[index + 1]
                    self.previous_index = index + 1
                    self.previous_time = time.time()
                    self.current_lat = self.latitude_list[index + 1]
                    self.current_lon = self.longitude_list[index + 1]
                    self.current_elev = self.elevation_list[index + 1]
                    self.current_heading = self.heading_list[index + 1]
                    self.step = index + 1
                    self.extra_distance = calculatedDistanceNext - travelDistance
                    self.desired_x = self.x_list[index + 1]
                    self.desired_y = self.y_list[index + 1]
                    self.desired_yaw = self.yaw_list[index + 1]
                    break

    def get_desired_location(self, current_lat, current_lon, current_speed):

        self.current_speed = current_speed

        if self.current_speed > 0:
            self.get_nearest_coordinates()
            
        else: self.previous_time = time.time()
    
 
        return (
            self.current_lat,
            self.current_lon,
            self.current_elev,
            self.current_heading,
            self.desired_x,
            self.desired_y,
            self.desired_yaw
        )

# ==============================================================================
# -------------------------- PID Controller ---------------------------
# ==============================================================================

class SpeedPIDController:
    def __init__(self, Kp=0.3, Ki=0.05, Kd=0.01,
                 max_integral=5.0, deadband=0.2,
                 min_throttle=0.2, min_brake=0.1,
                 filter_alpha=0.2, throttle_smoothing=0.05):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.max_integral = max_integral
        self.deadband = deadband
        self.min_throttle = min_throttle
        self.min_brake = min_brake

        # Internal state
        self.integral = 0.0
        self.last_error = 0.0
        self.last_throttle = 0.0
        self.filtered_speed = None

        # Filters
        self.filter_alpha = filter_alpha  # Low-pass filter factor
        self.throttle_smoothing = throttle_smoothing

        # Moving average buffer
        self.moving_avg_window = []
        self.moving_avg_maxlen = 5
        self.use_moving_avg_threshold = 8.0  # [m/s] ~28.8 km/h

    def reset(self):
        self.integral = 0.0
        self.last_error = 0.0
        self.last_throttle = 0.0
        self.filtered_speed = None
        self.moving_avg_window = []

    def apply_lowpass_filter(self, new_speed):
        if self.filtered_speed is None:
            self.filtered_speed = new_speed
        else:
            self.filtered_speed = (self.filter_alpha * new_speed +
                                   (1 - self.filter_alpha) * self.filtered_speed)
        return self.filtered_speed

    def apply_moving_average(self, new_speed):
        self.moving_avg_window.append(new_speed)
        if len(self.moving_avg_window) > self.moving_avg_maxlen:
            self.moving_avg_window.pop(0)
        return sum(self.moving_avg_window) / len(self.moving_avg_window)

    def smooth_throttle(self, raw_throttle):
        smoothed = max(min(raw_throttle, self.last_throttle + self.throttle_smoothing),
                       self.last_throttle - self.throttle_smoothing)
        self.last_throttle = smoothed
        return smoothed

    def compute_control(self, current_speed, desired_speed, dt):
        # Apply appropriate filter
        if current_speed >= self.use_moving_avg_threshold:
            current_speed = self.apply_moving_average(current_speed)
        else:
            current_speed = self.apply_lowpass_filter(current_speed)

        # Calculate error
        error = desired_speed - current_speed

        # Deadband: skip small errors
        if abs(error) < self.deadband:
            self.last_throttle = 0.0
            return 0.0, 0.0, current_speed

        # PID calculations
        self.integral += error * dt
        self.integral = max(-self.max_integral, min(self.max_integral, self.integral))  # Anti-windup

        derivative = (error - self.last_error) / dt if dt > 0 else 0.0
        self.last_error = error

        control = self.Kp * error + self.Ki * self.integral + self.Kd * derivative

        # Output control
        throttle = 0.0
        brake = 0.0

        if control > 0:
            throttle = max(self.min_throttle, min(control, 1.0))
            throttle = self.smooth_throttle(throttle)
            brake = 0.0
        elif control < 0:
            brake = max(self.min_brake, min(abs(control), 1.0))
            self.last_throttle = 0.0  # Reset throttle to avoid jump on next cycle

        return throttle, brake, current_speed

    
    def compute_throttle_brake_command(self, previous_desired_speed, current_speed, desired_speed):
        """
        Compute throttle and brake values to follow a desired speed using a simple proportional controller.

        Args:
            vehicle (carla.Vehicle): The vehicle actor in CARLA.
            desired_speed (float): Target speed in meters per second (m/s).
            Kp_throttle (float): Proportional gain for throttle.
            Kp_brake (float): Proportional gain for brake.

        Returns:
            tuple: (throttle, brake), both in range [0.0, 1.0]
        """
        # Initialize control variables
        throttle = 0.0
        brake = 0.0
        current_speed =  current_speed * MPH_To_MPS
        desired_speed =  desired_speed * MPH_To_MPS
        previous_desired_speed =  previous_desired_speed * MPH_To_MPS
        # Compute speed error and changes
        speed_error = desired_speed - current_speed
        speed_change =  desired_speed - previous_desired_speed

        if desired_speed == 0 and current_speed == 0:
            throttle = 0.0
            brake = 1.0
        
        elif desired_speed > 0 and speed_error == 0:
            throttle = 0.0
            brake = 0.0
            
        elif desired_speed == 0 and current_speed <= 1.0 and speed_change < 0:
            throttle = 0.0
            brake = 1.0
            
        elif desired_speed > 0 and 0 < speed_error <= 0.25:
            throttle = 0.25
            brake = 0.0
            
        elif desired_speed > 0 and 0.25 < speed_error <= 0.5:
            throttle = 0.5
            brake = 0.0
            
        elif desired_speed > 0 and 0.5 < speed_error <= 1.0:
            throttle = 0.75
            brake = 0.0
            
        elif desired_speed > 0 and speed_error > 1.0:
            throttle = 1.0
            brake = 0.0
            
        elif speed_change < 0 and -0.25 <= speed_error < 0:
            throttle = 0.0
            brake = 0.25
            
        elif speed_change < 0 and -0.5 <= speed_error < -0.25:
            throttle = 0.0
            brake = 0.5
            
        elif speed_change < 0 and -1.0 <= speed_error < -0.5:
            throttle = 0.0
            brake = 0.75
            
        elif speed_change < 0 and speed_error < -1.0:
            throttle = 0.0
            brake = 1.0

        return throttle, brake
    
# ==============================================================================
# -------------------------- ExternalCommandListener ---------------------------
# ==============================================================================

class ExternalCommandListener(threading.Thread):
    """
    A background thread that listens for external vehicle control commands (throttle, brake, steer).
    
    It runs a TCP server that receives JSON messages containing control inputs.
    """

    def __init__(self, control_instance, vehicle=None):
        # , host="127.0.0.1", port=5005
        """
        Initializes the listener that receives control commands.

        Args:
            control_instance (KeyboardControl): The instance of KeyboardControl that applies the controls.
            host (str, optional): The IP address to bind the listener (default: "127.0.0.1").
            port (int, optional): The port to listen for external control (default: 5005).
        """
        threading.Thread.__init__(self, daemon=True)  # Make thread a daemon (auto-stops on exit)
        self.control_instance = control_instance
        self.vehicle = vehicle  # ✅ Store vehicle reference here
        
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
        
        self.host_ip = config["IPAddress"]["HostIp"]
        self.lead_controller_port = config["PortNumber"]["LeadController"]
        self.lead_controller_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.lead_controller_socket.bind((self.host_ip, self.lead_controller_port))

        self.running = True
        self.last_time = None
        self.last_steer = 0.0
        self.pid = SpeedPIDController(Kp=0.3, Ki=0.05, Kd=0.01,
                 max_integral=5.0, deadband=0.2,
                 min_throttle=0.2, min_brake=0.1,
                 filter_alpha=0.2, throttle_smoothing=0.05)
        
        way_points_file = config["VehicleInformation"]["EgoBsmLogFileName"]
        self.way_points_manager = WayPointsManager(config, way_points_file)
        
        self.log_file = open("../../log/debug/carla_lead_controller_log.csv", "w")
        log_header = ("timestamp, desired_lat, desired_lon, desired_speed, desired_heading, current_lat, current_lon, current_speed, current_heading, gps_distance, throttle, brake, steer\n")
        self.log_file.write(log_header)
        
    def get_vehicle_speed(self):
        velocity = self.vehicle.get_velocity()
        vehicle_speed = 3.6 * math.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2)  # km/h
        
        return vehicle_speed
    
    def compute_steering_angle(self, current_heading, desired_heading):
        """
        Compute a normalized steering value based on current GPS position and desired GPS waypoint.

        Args:
            current_lat (float): Current latitude
            current_lon (float): Current longitude
            desired_lat (float): Target latitude
            desired_lon (float): Target longitude
            current_heading (float): Compass heading in degrees

        Returns:
            float: Steering value in range [-1.0, 1.0]
        """
        # Compute heading error
        heading_error = desired_heading - current_heading
        heading_error = (heading_error + 180) % 360 - 180  # Normalize to [-180, 180]

        # Apply proportional control
        Kp_steer = 0.015  # Steering gain (adjustable)
        steer = Kp_steer * heading_error

        # Clamp to [-1.0, 1.0]
        steer = max(-1.0, min(1.0, steer))

        # Optional smoothing (low-pass filter)
        alpha = 1.0
        steer = alpha * steer + (1 - alpha) * self.last_steer
        self.last_steer = steer

        return steer
    
    def compute_steering_from_xy(self, current_x, current_y, current_yaw, desired_x, desired_y, Kp=0.015):
        # Compute vector from current to desired point
        dx = desired_x - current_x
        dy = desired_y - current_y

        # Compute desired yaw (in degrees)
        desired_yaw = math.degrees(math.atan2(dy, dx))

        # Normalize angles
        current_yaw = current_yaw % 360
        desired_yaw = desired_yaw % 360

        # Calculate yaw error [-180, 180]
        yaw_error = (desired_yaw - current_yaw + 180) % 360 - 180

        # Apply proportional control
        steer = Kp * yaw_error

        # Clamp to [-1.0, 1.0]
        steer = max(-1.0, min(1.0, steer))

        return steer
    
    def gps_to_carla_transform(self, lat, lon, heading):
        """
        Converts GPS coordinates to CARLA Transform using map projection.
        Assumes your map has a GeoReference (WGS84 -> CARLA).
        """
        try:
            carla_location = self.vehicle.get_world().get_map().transform_to_location(
                carla.GeoLocation(latitude=lat, longitude=lon)
            )
        except AttributeError:
            raise RuntimeError("Your CARLA map does not support GPS transformation. Use a map with geo-reference.")

        return Transform(Location(x=carla_location.x, y=carla_location.y, z=self.vehicle.get_location().z),Rotation(yaw=heading))

    def run(self):
        """
        Runs the listener that continuously receives and updates control commands.
        Works for UDP communication.
        """
        print(f"[INFO] Listening for external commands (UDP) on {self.host_ip}:{self.lead_controller_port}")
        previous_desired_speed = 0.0
        desired_speed = 0.0
        while self.running:
            try:
                self.lead_controller_socket.settimeout(5.0)  # Optional: avoid blocking forever
                data, addr = self.lead_controller_socket.recvfrom(1024)  # ✅ UDP-style receive
                if not data:
                    continue
                
                transform = self.vehicle.get_transform()
                current_location = transform.location
                current_x = current_location.x
                current_y = current_location.y
                # current_z = current_location.z
                current_yaw = transform.rotation.yaw
                
                print("Current Carla Coordinates: ", current_location)
                
                command = json.loads(data.decode())
                print(f"[DEBUG] Received command: {command}")

                desired_speed = command.get("desired_speed", 0.0) # make sure to receive in mps
                desired_speed_mph = desired_speed * MPS_To_MPH
                current_speed_kmh = self.get_vehicle_speed()
                current_speed_mps = current_speed_kmh * KPH_To_MPS #kph to mph = speed_kph * 0.621371 
                current_speed_mph = current_speed_kmh * KPH_To_MPH
                print(f"Current speed: {current_speed_mph:.2f} mph")
                
                # Get GNSS sensor readings instead, if available
                if hasattr(self.vehicle, "gnss_sensor"):
                    current_lat = self.vehicle.gnss_sensor.lat
                    current_lon = self.vehicle.gnss_sensor.lon
                if hasattr(self.vehicle, "imu_sensor"):
                    current_heading = self.vehicle.imu_sensor.compass % 360
                    
                # desired_lat, desired_lon, desired_elev, desired_heading, desired_x, desired_y, desired_yaw = self.way_points_manager.get_desired_location(current_speed_mps)
                desired_lat, desired_lon, desired_heading, desired_x, desired_y, desired_yaw = self.way_points_manager.get_next_coordinates(current_speed_mps, current_lat, current_lon, current_heading)
                # desired_lat, desired_lon, desired_heading, desired_x, desired_y, desired_yaw = self.way_points_manager.get_desired_coordinates(current_lat, current_lon, current_heading)
                now = time.time()
                dt = now - self.last_time if self.last_time is not None else 0.05
                dt = max(dt, 0.01)  # Clamp to a reasonable minimum
                self.last_time = now
                # Get throttle and brake               
                throttle, brake, current_speed_mps = self.pid.compute_control(current_speed_mps, desired_speed, dt)
                # throttle, brake = self.pid.compute_throttle_brake_command(previous_desired_speed, current_speed_mps, desired_speed)

                # Compute steer
                steer = self.compute_steering_angle(current_heading, desired_heading)
                # steer =  self.compute_steering_from_xy(current_x, current_y, current_yaw, desired_x, desired_y, Kp=0.01)

                self.control_instance.set_external_control(throttle, brake, steer)
                previous_desired_speed = desired_speed
                
                gps_distance = haversine.haversine((desired_lat, desired_lon), (current_lat, current_lon), unit=haversine.Unit.METERS)
                # print("Euclidian Distance and Haversine Distance: ", euclidian_distance, ", " , gps_distance)
                timestamp = str(time.time())
                desired_lat = str(desired_lat)
                desired_lon = str(desired_lon)
                desired_speed = str(desired_speed_mph) 
                desired_heading = str(desired_heading) 
                current_lat = str(current_lat)
                current_lon = str(current_lon) 
                current_speed_mph = str(current_speed_mph) 
                current_heading = str(current_heading)
                gps_distance = str(gps_distance)
                throttle = str(throttle) 
                brake = str(brake)
                steer = str(steer)
                
                csv_row = (timestamp + ","
                           + desired_lat + ","
                           + desired_lon + ","
                           + desired_speed + ","
                           + desired_heading + ","
                           + current_lat + ","
                           + current_lon + ","
                           + current_speed_mph + ","
                           + current_heading + ","
                           + gps_distance + ","
                           + throttle + ","
                           + brake + ","
                           + steer + "\n")
                self.log_file.write(csv_row) 

            except socket.timeout:
                print("[WARNING] No data received in the last 5 seconds...")
                continue
            except json.JSONDecodeError:
                print("[ERROR] Received invalid JSON data, ignoring.")
            except Exception as e:
                print(f"[ERROR] Unexpected error: {e}")
                break


    def stop(self):
        """
        Stops the listener and closes the socket.
        """
        self.running = False
        self.lead_controller_socket.close()
        self.log_file.close()
        self.way_points_manager.debug_log_file.close()
        self.way_points_manager.heading_log_file.close()
        print("[INFO] ExternalCommandListener stopped.")



# ==============================================================================
# -- KeyboardControl -----------------------------------------------------------
# ==============================================================================

class KeyboardControl(object):
    """
    Class that handles vehicle control using external inputs, completely removing keyboard-based control.
    
    This class listens for external throttle, brake, and steering inputs and applies them to the vehicle.
    It does not process any keyboard inputs, making it suitable for remote or AI-based vehicle control.

    Attributes:
        external_throttle (float): The throttle value received from an external source (range: [0,1]).
        external_brake (float): The brake value received from an external source (range: [0,1]).
        external_steer (float): The steering value received from an external source (range: [-1,1]).
        _control (carla.VehicleControl): The control object managing vehicle movement.
        _autopilot_enabled (bool): Whether autopilot is active.
        _lights (carla.VehicleLightState): Stores the current vehicle light state.
        listener (ExternalCommandListener): The listener that receives external control commands.

    Methods:
        set_external_control(throttle, brake, steer=0.0):
            Updates the throttle, brake, and steering values from an external source.

        _parse_external_vehicle_keys():
            Applies the externally received throttle, brake, and steering values to the vehicle.

        parse_events(client, world, clock):
            Updates vehicle control based only on external inputs.

        destroy():
            Stops the external control listener when the simulation exits.
    """
    
    def __init__(self, world, start_in_autopilot):
        """
        Initializes the external control class and starts the external input listener.

        Args:
            world (carla.World): The CARLA simulation world instance.
            start_in_autopilot (bool): Whether the vehicle starts in autopilot mode.
        """
        self._autopilot_enabled = start_in_autopilot
        self.external_throttle = 0.0  # External throttle input (range: [0,1])
        self.external_brake = 0.0  # External brake input (range: [0,1])
        self.external_steer = 0.0  # External steering input (range: [-1,1])

        if isinstance(world.player, carla.Vehicle):
            self._control = carla.VehicleControl()
            self._lights = carla.VehicleLightState.NONE
            world.player.set_autopilot(self._autopilot_enabled)
            world.player.set_light_state(self._lights)
        elif isinstance(world.player, carla.Walker):
            self._control = carla.WalkerControl()
            self._autopilot_enabled = False
            self._rotation = world.player.get_transform().rotation
        else:
            raise NotImplementedError("Actor type not supported")

        world.hud.notification("External control active (keyboard disabled).", seconds=4.0)
        
        # Start external control listener
        self.listener = ExternalCommandListener(self, vehicle=world.player)
        print("[INFO] ExternalCommandListener started")
        self.listener.start()

    def set_external_control(self, throttle, brake, steer=0.0):
        """
        Updates the vehicle's throttle, brake, and steering from an external source.

        Args:
            throttle (float): The throttle input value (range: [0,1]).
            brake (float): The brake input value (range: [0,1]).
            steer (float, optional): The steering input value (range: [-1,1]). Default is 0.0.
        """
        self.external_throttle = max(0.0, min(throttle, 1.0))  # Clamp throttle
        self.external_brake = max(0.0, min(brake, 1.0))  # Clamp brake
        self.external_steer = max(-1.0, min(steer, 1.0))  # Clamp steering

    def _parse_external_vehicle_keys(self, world):
        """
        Applies external control inputs (throttle, brake, and steering) to the vehicle.
        """
        self._control.throttle = self.external_throttle if self.external_throttle is not None else 0.0
        self._control.brake = self.external_brake if self.external_brake is not None else 0.0
        self._control.steer = self.external_steer if self.external_steer is not None else 0.0
        self._control.reverse = self._control.gear < 0
        
        # Update brake light state based on brake input
        current_lights = self._lights
        if self._control.brake > 0:
            current_lights |= carla.VehicleLightState.Brake  # Turn on brake light
        else:
            current_lights &= ~carla.VehicleLightState.Brake  # Turn off brake light

        if current_lights != self._lights:  # Only update if there's a change
            self._lights = current_lights
            world.player.set_light_state(carla.VehicleLightState(self._lights))
        
    def parse_events(self, client, world, clock):
        """
        Processes only external inputs (keyboard fully disabled).

        This function ensures that the vehicle receives input only from an external controller.
        """
        if not self._autopilot_enabled:
            if isinstance(self._control, carla.VehicleControl):
                self._parse_external_vehicle_keys(world)  # Always use external control
                world.player.apply_control(self._control)

    def destroy(self):
        """
        Stops the external listener when the simulation exits.
        """
        self.listener.stop()


# class KeyboardControl(object):
#     """Class that handles keyboard input."""
#     def __init__(self, world, start_in_autopilot):
#         self._autopilot_enabled = start_in_autopilot
#         if isinstance(world.player, carla.Vehicle):
#             self._control = carla.VehicleControl()
#             self._lights = carla.VehicleLightState.NONE
#             world.player.set_autopilot(self._autopilot_enabled)
#             world.player.set_light_state(self._lights)
#         elif isinstance(world.player, carla.Walker):
#             self._control = carla.WalkerControl()
#             self._autopilot_enabled = False
#             self._rotation = world.player.get_transform().rotation
#         else:
#             raise NotImplementedError("Actor type not supported")
#         self._steer_cache = 0.0
#         world.hud.notification("Press 'H' or '?' for help.", seconds=4.0)

#     def parse_events(self, client, world, clock):
#         if isinstance(self._control, carla.VehicleControl):
#             current_lights = self._lights
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 return True
#             elif event.type == pygame.KEYUP:
#                 if self._is_quit_shortcut(event.key):
#                     return True
#                 elif event.key == K_BACKSPACE:
#                     if self._autopilot_enabled:
#                         world.player.set_autopilot(False)
#                         world.restart()
#                         world.player.set_autopilot(True)
#                     else:
#                         world.restart()
#                 elif event.key == K_F1:
#                     world.hud.toggle_info()
#                 elif event.key == K_h or (event.key == K_SLASH and pygame.key.get_mods() & KMOD_SHIFT):
#                     world.hud.help.toggle()
#                 elif event.key == K_TAB:
#                     world.camera_manager.toggle_camera()
#                 elif event.key == K_c and pygame.key.get_mods() & KMOD_SHIFT:
#                     world.next_weather(reverse=True)
#                 elif event.key == K_c:
#                     world.next_weather()
#                 elif event.key == K_g:
#                     world.toggle_radar()
#                 elif event.key == K_BACKQUOTE:
#                     world.camera_manager.next_sensor()
#                 elif event.key == K_n:
#                     world.camera_manager.next_sensor()
#                 elif event.key == K_w and (pygame.key.get_mods() & KMOD_CTRL):
#                     if world.constant_velocity_enabled:
#                         world.player.disable_constant_velocity()
#                         world.constant_velocity_enabled = False
#                         world.hud.notification("Disabled Constant Velocity Mode")
#                     else:
#                         world.player.enable_constant_velocity(carla.Vector3D(17, 0, 0))
#                         world.constant_velocity_enabled = True
#                         world.hud.notification("Enabled Constant Velocity Mode at 60 km/h")
#                 elif event.key > K_0 and event.key <= K_9:
#                     world.camera_manager.set_sensor(event.key - 1 - K_0)
#                 elif event.key == K_r and not (pygame.key.get_mods() & KMOD_CTRL):
#                     world.camera_manager.toggle_recording()
#                 elif event.key == K_r and (pygame.key.get_mods() & KMOD_CTRL):
#                     if (world.recording_enabled):
#                         client.stop_recorder()
#                         world.recording_enabled = False
#                         world.hud.notification("Recorder is OFF")
#                     else:
#                         client.start_recorder("manual_recording.rec")
#                         world.recording_enabled = True
#                         world.hud.notification("Recorder is ON")
#                 elif event.key == K_p and (pygame.key.get_mods() & KMOD_CTRL):
#                     # stop recorder
#                     client.stop_recorder()
#                     world.recording_enabled = False
#                     # work around to fix camera at start of replaying
#                     current_index = world.camera_manager.index
#                     world.destroy_sensors()
#                     # disable autopilot
#                     self._autopilot_enabled = False
#                     world.player.set_autopilot(self._autopilot_enabled)
#                     world.hud.notification("Replaying file 'manual_recording.rec'")
#                     # replayer
#                     client.replay_file("manual_recording.rec", world.recording_start, 0, 0)
#                     world.camera_manager.set_sensor(current_index)
#                 elif event.key == K_MINUS and (pygame.key.get_mods() & KMOD_CTRL):
#                     if pygame.key.get_mods() & KMOD_SHIFT:
#                         world.recording_start -= 10
#                     else:
#                         world.recording_start -= 1
#                     world.hud.notification("Recording start time is %d" % (world.recording_start))
#                 elif event.key == K_EQUALS and (pygame.key.get_mods() & KMOD_CTRL):
#                     if pygame.key.get_mods() & KMOD_SHIFT:
#                         world.recording_start += 10
#                     else:
#                         world.recording_start += 1
#                     world.hud.notification("Recording start time is %d" % (world.recording_start))
#                 if isinstance(self._control, carla.VehicleControl):
#                     if event.key == K_q:
#                         self._control.gear = 1 if self._control.reverse else -1
#                     elif event.key == K_m:
#                         self._control.manual_gear_shift = not self._control.manual_gear_shift
#                         self._control.gear = world.player.get_control().gear
#                         world.hud.notification('%s Transmission' %
#                                                ('Manual' if self._control.manual_gear_shift else 'Automatic'))
#                     elif self._control.manual_gear_shift and event.key == K_COMMA:
#                         self._control.gear = max(-1, self._control.gear - 1)
#                     elif self._control.manual_gear_shift and event.key == K_PERIOD:
#                         self._control.gear = self._control.gear + 1
#                     elif event.key == K_p and not pygame.key.get_mods() & KMOD_CTRL:
#                         self._autopilot_enabled = not self._autopilot_enabled
#                         world.player.set_autopilot(self._autopilot_enabled)
#                         world.hud.notification(
#                             'Autopilot %s' % ('On' if self._autopilot_enabled else 'Off'))
#                     elif event.key == K_l and pygame.key.get_mods() & KMOD_CTRL:
#                         current_lights ^= carla.VehicleLightState.Special1
#                     elif event.key == K_l and pygame.key.get_mods() & KMOD_SHIFT:
#                         current_lights ^= carla.VehicleLightState.HighBeam
#                     elif event.key == K_l:
#                         # Use 'L' key to switch between lights:
#                         # closed -> position -> low beam -> fog
#                         if not self._lights & carla.VehicleLightState.Position:
#                             world.hud.notification("Position lights")
#                             current_lights |= carla.VehicleLightState.Position
#                         else:
#                             world.hud.notification("Low beam lights")
#                             current_lights |= carla.VehicleLightState.LowBeam
#                         if self._lights & carla.VehicleLightState.LowBeam:
#                             world.hud.notification("Fog lights")
#                             current_lights |= carla.VehicleLightState.Fog
#                         if self._lights & carla.VehicleLightState.Fog:
#                             world.hud.notification("Lights off")
#                             current_lights ^= carla.VehicleLightState.Position
#                             current_lights ^= carla.VehicleLightState.LowBeam
#                             current_lights ^= carla.VehicleLightState.Fog
#                     elif event.key == K_i:
#                         current_lights ^= carla.VehicleLightState.Interior
#                     elif event.key == K_z:
#                         current_lights ^= carla.VehicleLightState.LeftBlinker
#                     elif event.key == K_x:
#                         current_lights ^= carla.VehicleLightState.RightBlinker

#         if not self._autopilot_enabled:
#             if isinstance(self._control, carla.VehicleControl):
#                 self._parse_vehicle_keys(pygame.key.get_pressed(), clock.get_time())
#                 self._control.reverse = self._control.gear < 0
#                 # Set automatic control-related vehicle lights
#                 if self._control.brake:
#                     current_lights |= carla.VehicleLightState.Brake
#                 else: # Remove the Brake flag
#                     current_lights &= ~carla.VehicleLightState.Brake
#                 if self._control.reverse:
#                     current_lights |= carla.VehicleLightState.Reverse
#                 else: # Remove the Reverse flag
#                     current_lights &= ~carla.VehicleLightState.Reverse
#                 if current_lights != self._lights: # Change the light state only if necessary
#                     self._lights = current_lights
#                     world.player.set_light_state(carla.VehicleLightState(self._lights))
#             elif isinstance(self._control, carla.WalkerControl):
#                 self._parse_walker_keys(pygame.key.get_pressed(), clock.get_time(), world)
#             world.player.apply_control(self._control)

#     def _parse_vehicle_keys(self, keys, milliseconds):
#         if keys[K_UP] or keys[K_w]:
#             self._control.throttle = min(self._control.throttle + 0.01, 1)
#         else:
#             self._control.throttle = 0.0

#         if keys[K_DOWN] or keys[K_s]:
#             self._control.brake = min(self._control.brake + 0.2, 1)
#         else:
#             self._control.brake = 0

#         steer_increment = 5e-4 * milliseconds
#         if keys[K_LEFT] or keys[K_a]:
#             if self._steer_cache > 0:
#                 self._steer_cache = 0
#             else:
#                 self._steer_cache -= steer_increment
#         elif keys[K_RIGHT] or keys[K_d]:
#             if self._steer_cache < 0:
#                 self._steer_cache = 0
#             else:
#                 self._steer_cache += steer_increment
#         else:
#             self._steer_cache = 0.0
#         self._steer_cache = min(0.7, max(-0.7, self._steer_cache))
#         self._control.steer = round(self._steer_cache, 1)
#         self._control.hand_brake = keys[K_SPACE]

#     def _parse_walker_keys(self, keys, milliseconds, world):
#         self._control.speed = 0.0
#         if keys[K_DOWN] or keys[K_s]:
#             self._control.speed = 0.0
#         if keys[K_LEFT] or keys[K_a]:
#             self._control.speed = .01
#             self._rotation.yaw -= 0.08 * milliseconds
#         if keys[K_RIGHT] or keys[K_d]:
#             self._control.speed = .01
#             self._rotation.yaw += 0.08 * milliseconds
#         if keys[K_UP] or keys[K_w]:
#             self._control.speed = world.player_max_speed_fast if pygame.key.get_mods() & KMOD_SHIFT else world.player_max_speed
#         self._control.jump = keys[K_SPACE]
#         self._rotation.yaw = round(self._rotation.yaw, 1)
#         self._control.direction = self._rotation.get_forward_vector()

#     @staticmethod
#     def _is_quit_shortcut(key):
#         return (key == K_ESCAPE) or (key == K_q and pygame.key.get_mods() & KMOD_CTRL)


# ==============================================================================
# -- HUD -----------------------------------------------------------------------
# ==============================================================================


class HUD(object):
    def __init__(self, width, height):
        self.dim = (width, height)
        font = pygame.font.Font(pygame.font.get_default_font(), 20)
        font_name = 'courier' if os.name == 'nt' else 'mono'
        fonts = [x for x in pygame.font.get_fonts() if font_name in x]
        default_font = 'ubuntumono'
        mono = default_font if default_font in fonts else fonts[0]
        mono = pygame.font.match_font(mono)
        self._font_mono = pygame.font.Font(mono, 12 if os.name == 'nt' else 14)
        self._notifications = FadingText(font, (width, 40), (0, height - 40))
        self.help = HelpText(pygame.font.Font(mono, 16), width, height)
        self.server_fps = 0
        self.frame = 0
        self.simulation_time = 0
        self._show_info = True
        self._info_text = []
        self._server_clock = pygame.time.Clock()

    def on_world_tick(self, timestamp):
        self._server_clock.tick()
        self.server_fps = self._server_clock.get_fps()
        self.frame = timestamp.frame
        self.simulation_time = timestamp.elapsed_seconds

    def tick(self, world, clock):
        self._notifications.tick(world, clock)
        if not self._show_info:
            return
        t = world.player.get_transform()
        v = world.player.get_velocity()
        c = world.player.get_control()
        compass = world.imu_sensor.compass
        heading = 'N' if compass > 270.5 or compass < 89.5 else ''
        heading += 'S' if 90.5 < compass < 269.5 else ''
        heading += 'E' if 0.5 < compass < 179.5 else ''
        heading += 'W' if 180.5 < compass < 359.5 else ''
        colhist = world.collision_sensor.get_collision_history()
        collision = [colhist[x + self.frame - 200] for x in range(0, 200)]
        max_col = max(1.0, max(collision))
        collision = [x / max_col for x in collision]
        vehicles = world.world.get_actors().filter('vehicle.*')
        self._info_text = [
            'Server:  % 16.0f FPS' % self.server_fps,
            'Client:  % 16.0f FPS' % clock.get_fps(),
            '',
            'Vehicle: % 20s' % get_actor_display_name(world.player, truncate=20),
            'Map:     % 20s' % world.map.name,
            'Simulation time: % 12s' % datetime.timedelta(seconds=int(self.simulation_time)),
            '',
            'Speed:   % 15.0f km/h' % (3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2)),
            u'Compass:% 17.0f\N{DEGREE SIGN} % 2s' % (compass, heading),
            'Accelero: (%5.1f,%5.1f,%5.1f)' % (world.imu_sensor.accelerometer),
            'Gyroscop: (%5.1f,%5.1f,%5.1f)' % (world.imu_sensor.gyroscope),
            'Location:% 20s' % ('(% 5.1f, % 5.1f)' % (t.location.x, t.location.y)),
            'GNSS:% 24s' % ('(% 2.6f, % 3.6f)' % (world.gnss_sensor.lat, world.gnss_sensor.lon)),
            'Height:  % 18.0f m' % t.location.z,
            '']
        if isinstance(c, carla.VehicleControl):
            self._info_text += [
                ('Throttle:', c.throttle, 0.0, 1.0),
                ('Steer:', c.steer, -1.0, 1.0),
                ('Brake:', c.brake, 0.0, 1.0),
                ('Reverse:', c.reverse),
                ('Hand brake:', c.hand_brake),
                ('Manual:', c.manual_gear_shift),
                'Gear:        %s' % {-1: 'R', 0: 'N'}.get(c.gear, c.gear)]
        elif isinstance(c, carla.WalkerControl):
            self._info_text += [
                ('Speed:', c.speed, 0.0, 5.556),
                ('Jump:', c.jump)]
        self._info_text += [
            '',
            'Collision:',
            collision,
            '',
            'Number of vehicles: % 8d' % len(vehicles)]
        if len(vehicles) > 1:
            self._info_text += ['Nearby vehicles:']
            distance = lambda l: math.sqrt((l.x - t.location.x)**2 + (l.y - t.location.y)**2 + (l.z - t.location.z)**2)
            vehicles = [(distance(x.get_location()), x) for x in vehicles if x.id != world.player.id]
            for d, vehicle in sorted(vehicles, key=lambda vehicles: vehicles[0]):
                if d > 200.0:
                    break
                vehicle_type = get_actor_display_name(vehicle, truncate=22)
                self._info_text.append('% 4dm %s' % (d, vehicle_type))

    def toggle_info(self):
        self._show_info = not self._show_info

    def notification(self, text, seconds=2.0):
        self._notifications.set_text(text, seconds=seconds)

    def error(self, text):
        self._notifications.set_text('Error: %s' % text, (255, 0, 0))

    def render(self, display):
        if self._show_info:
            info_surface = pygame.Surface((220, self.dim[1]))
            info_surface.set_alpha(100)
            display.blit(info_surface, (0, 0))
            v_offset = 4
            bar_h_offset = 100
            bar_width = 106
            for item in self._info_text:
                if v_offset + 18 > self.dim[1]:
                    break
                if isinstance(item, list):
                    if len(item) > 1:
                        points = [(x + 8, v_offset + 8 + (1.0 - y) * 30) for x, y in enumerate(item)]
                        pygame.draw.lines(display, (255, 136, 0), False, points, 2)
                    item = None
                    v_offset += 18
                elif isinstance(item, tuple):
                    if isinstance(item[1], bool):
                        rect = pygame.Rect((bar_h_offset, v_offset + 8), (6, 6))
                        pygame.draw.rect(display, (255, 255, 255), rect, 0 if item[1] else 1)
                    else:
                        rect_border = pygame.Rect((bar_h_offset, v_offset + 8), (bar_width, 6))
                        pygame.draw.rect(display, (255, 255, 255), rect_border, 1)
                        f = (item[1] - item[2]) / (item[3] - item[2])
                        if item[2] < 0.0:
                            rect = pygame.Rect((bar_h_offset + f * (bar_width - 6), v_offset + 8), (6, 6))
                        else:
                            rect = pygame.Rect((bar_h_offset, v_offset + 8), (f * bar_width, 6))
                        pygame.draw.rect(display, (255, 255, 255), rect)
                    item = item[0]
                if item:  # At this point has to be a str.
                    surface = self._font_mono.render(item, True, (255, 255, 255))
                    display.blit(surface, (8, v_offset))
                v_offset += 18
        self._notifications.render(display)
        self.help.render(display)


# ==============================================================================
# -- FadingText ----------------------------------------------------------------
# ==============================================================================


class FadingText(object):
    def __init__(self, font, dim, pos):
        self.font = font
        self.dim = dim
        self.pos = pos
        self.seconds_left = 0
        self.surface = pygame.Surface(self.dim)

    def set_text(self, text, color=(255, 255, 255), seconds=2.0):
        text_texture = self.font.render(text, True, color)
        self.surface = pygame.Surface(self.dim)
        self.seconds_left = seconds
        self.surface.fill((0, 0, 0, 0))
        self.surface.blit(text_texture, (10, 11))

    def tick(self, _, clock):
        delta_seconds = 1e-3 * clock.get_time()
        self.seconds_left = max(0.0, self.seconds_left - delta_seconds)
        self.surface.set_alpha(500.0 * self.seconds_left)

    def render(self, display):
        display.blit(self.surface, self.pos)


# ==============================================================================
# -- HelpText ------------------------------------------------------------------
# ==============================================================================


class HelpText(object):
    """Helper class to handle text output using pygame"""
    def __init__(self, font, width, height):
        lines = __doc__.split('\n')
        self.font = font
        self.line_space = 18
        self.dim = (780, len(lines) * self.line_space + 12)
        self.pos = (0.5 * width - 0.5 * self.dim[0], 0.5 * height - 0.5 * self.dim[1])
        self.seconds_left = 0
        self.surface = pygame.Surface(self.dim)
        self.surface.fill((0, 0, 0, 0))
        for n, line in enumerate(lines):
            text_texture = self.font.render(line, True, (255, 255, 255))
            self.surface.blit(text_texture, (22, n * self.line_space))
            self._render = False
        self.surface.set_alpha(220)

    def toggle(self):
        self._render = not self._render

    def render(self, display):
        if self._render:
            display.blit(self.surface, self.pos)


# ==============================================================================
# -- CollisionSensor -----------------------------------------------------------
# ==============================================================================


class CollisionSensor(object):
    def __init__(self, parent_actor, hud):
        self.sensor = None
        self.history = []
        self._parent = parent_actor
        self.hud = hud
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.collision')
        self.sensor = world.spawn_actor(bp, carla.Transform(), attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: CollisionSensor._on_collision(weak_self, event))

    def get_collision_history(self):
        history = collections.defaultdict(int)
        for frame, intensity in self.history:
            history[frame] += intensity
        return history

    @staticmethod
    def _on_collision(weak_self, event):
        self = weak_self()
        if not self:
            return
        actor_type = get_actor_display_name(event.other_actor)
        self.hud.notification('Collision with %r' % actor_type)
        impulse = event.normal_impulse
        intensity = math.sqrt(impulse.x**2 + impulse.y**2 + impulse.z**2)
        self.history.append((event.frame, intensity))
        if len(self.history) > 4000:
            self.history.pop(0)


# ==============================================================================
# -- LaneInvasionSensor --------------------------------------------------------
# ==============================================================================


class LaneInvasionSensor(object):
    def __init__(self, parent_actor, hud):
        self.sensor = None
        self._parent = parent_actor
        self.hud = hud
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.lane_invasion')
        self.sensor = world.spawn_actor(bp, carla.Transform(), attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: LaneInvasionSensor._on_invasion(weak_self, event))

    @staticmethod
    def _on_invasion(weak_self, event):
        self = weak_self()
        if not self:
            return
        lane_types = set(x.type for x in event.crossed_lane_markings)
        text = ['%r' % str(x).split()[-1] for x in lane_types]
        self.hud.notification('Crossed line %s' % ' and '.join(text))


# ==============================================================================
# -- GnssSensor ----------------------------------------------------------------
# ==============================================================================


class GnssSensor(object):
    def __init__(self, parent_actor):
        self.sensor = None
        self._parent = parent_actor
        self.lat = 0.0
        self.lon = 0.0
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.gnss')
        self.sensor = world.spawn_actor(bp, carla.Transform(carla.Location(x=1.0, z=2.8)), attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: GnssSensor._on_gnss_event(weak_self, event))

    @staticmethod
    def _on_gnss_event(weak_self, event):
        self = weak_self()
        if not self:
            return
        self.lat = event.latitude
        self.lon = event.longitude


# ==============================================================================
# -- IMUSensor -----------------------------------------------------------------
# ==============================================================================


class IMUSensor(object):
    def __init__(self, parent_actor):
        self.sensor = None
        self._parent = parent_actor
        self.accelerometer = (0.0, 0.0, 0.0)
        self.gyroscope = (0.0, 0.0, 0.0)
        self.compass = 0.0
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.imu')
        self.sensor = world.spawn_actor(
            bp, carla.Transform(), attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(
            lambda sensor_data: IMUSensor._IMU_callback(weak_self, sensor_data))

    @staticmethod
    def _IMU_callback(weak_self, sensor_data):
        self = weak_self()
        if not self:
            return
        limits = (-99.9, 99.9)
        self.accelerometer = (
            max(limits[0], min(limits[1], sensor_data.accelerometer.x)),
            max(limits[0], min(limits[1], sensor_data.accelerometer.y)),
            max(limits[0], min(limits[1], sensor_data.accelerometer.z)))
        self.gyroscope = (
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.x))),
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.y))),
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.z))))
        self.compass = math.degrees(sensor_data.compass)


# ==============================================================================
# -- RadarSensor ---------------------------------------------------------------
# ==============================================================================


class RadarSensor(object):
    def __init__(self, parent_actor):
        self.sensor = None
        self._parent = parent_actor
        self.velocity_range = 7.5 # m/s
        world = self._parent.get_world()
        self.debug = world.debug
        bp = world.get_blueprint_library().find('sensor.other.radar')
        bp.set_attribute('horizontal_fov', str(35))
        bp.set_attribute('vertical_fov', str(20))
        self.sensor = world.spawn_actor(
            bp,
            carla.Transform(
                carla.Location(x=2.8, z=1.0),
                carla.Rotation(pitch=5)),
            attach_to=self._parent)
        # We need a weak reference to self to avoid circular reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(
            lambda radar_data: RadarSensor._Radar_callback(weak_self, radar_data))

    @staticmethod
    def _Radar_callback(weak_self, radar_data):
        self = weak_self()
        if not self:
            return
        # To get a numpy [[vel, altitude, azimuth, depth],...[,,,]]:
        # points = np.frombuffer(radar_data.raw_data, dtype=np.dtype('f4'))
        # points = np.reshape(points, (len(radar_data), 4))

        current_rot = radar_data.transform.rotation
        for detect in radar_data:
            azi = math.degrees(detect.azimuth)
            alt = math.degrees(detect.altitude)
            # The 0.25 adjusts a bit the distance so the dots can
            # be properly seen
            fw_vec = carla.Vector3D(x=detect.depth - 0.25)
            carla.Transform(
                carla.Location(),
                carla.Rotation(
                    pitch=current_rot.pitch + alt,
                    yaw=current_rot.yaw + azi,
                    roll=current_rot.roll)).transform(fw_vec)

            def clamp(min_v, max_v, value):
                return max(min_v, min(value, max_v))

            norm_velocity = detect.velocity / self.velocity_range # range [-1, 1]
            r = int(clamp(0.0, 1.0, 1.0 - norm_velocity) * 255.0)
            g = int(clamp(0.0, 1.0, 1.0 - abs(norm_velocity)) * 255.0)
            b = int(abs(clamp(- 1.0, 0.0, - 1.0 - norm_velocity)) * 255.0)
            self.debug.draw_point(
                radar_data.transform.location + fw_vec,
                size=0.075,
                life_time=0.06,
                persistent_lines=False,
                color=carla.Color(r, g, b))

# ==============================================================================
# -- CameraManager -------------------------------------------------------------
# ==============================================================================
"""
The CameraManager class is responsible for: 
    ✅ Managing different camera sensors (RGB, depth, segmentation, LiDAR, etc.)
    ✅ Attaching/detaching cameras to/from the player vehicle
    ✅ Switching between camera views
    ✅ Rendering the camera feed to the HUD
    ✅ Handling image processing (color conversion, depth maps, LiDAR visualization)
    ✅ Recording sensor data to disk
"""
class CameraManager(object):
    def __init__(self, parent_actor, hud, gamma_correction):
        """
        Initializes the CameraManager class.
            Parameters:
            parent_actor: The vehicle to which the camera is attached.
            hud: The HUD object (displays notifications and renders the camera feed).
            gamma_correction: Adjusts the brightness of the camera feed.
        """
        self.sensor = None #Stores the current camera sensor.
        self.surface = None #Stores the processed camera image.
        self._parent = parent_actor # The vehicle the camera is attached to.
        self.hud = hud # reference for displaying notifications.
        self.recording = False # Flag to track if camera data is being recorded.
        bound_y = 0.5 + self._parent.bounding_box.extent.y # Adjusts camera position based on vehicle size.
        Attachment = carla.AttachmentType # Defines how the camera is attached to the vehicle.
        """
        Stores predefined camera positions:
            Behind the vehicle (x=-5.5, z=2.5)
            First-person view (x=1.6, z=1.7)
            Side view (x=5.5, y=1.5, z=1.5)
            Overhead view (x=-8.0, z=6.0)
            Rear-view mirror position (x=-1, y=-bound_y, z=0.5)
        """
        self._camera_transforms = [
            # (carla.Transform(carla.Location(x=0.65, y=0.0, z=1.4),carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0)), Attachment.Rigid),
            (carla.Transform(carla.Location(x=-5.5, z=2.5), carla.Rotation(pitch=8.0)), Attachment.SpringArm),
            (carla.Transform(carla.Location(x=1.6, z=1.7)), Attachment.Rigid),
            (carla.Transform(carla.Location(x=5.5, y=1.5, z=1.5)), Attachment.SpringArm),
            (carla.Transform(carla.Location(x=-8.0, z=6.0), carla.Rotation(pitch=6.0)), Attachment.SpringArm),
            (carla.Transform(carla.Location(x=-1, y=-bound_y, z=0.5)), Attachment.Rigid)]
        self.transform_index = 1 #Starts with the second camera position (default is first-person view).
        self.sensors = [
            ['sensor.camera.rgb', cc.Raw, 'Camera RGB', {}],
            ['sensor.camera.depth', cc.Raw, 'Camera Depth (Raw)', {}],
            ['sensor.camera.depth', cc.Depth, 'Camera Depth (Gray Scale)', {}],
            ['sensor.camera.depth', cc.LogarithmicDepth, 'Camera Depth (Logarithmic Gray Scale)', {}],
            ['sensor.camera.semantic_segmentation', cc.Raw, 'Camera Semantic Segmentation (Raw)', {}],
            ['sensor.camera.semantic_segmentation', cc.CityScapesPalette,
                'Camera Semantic Segmentation (CityScapes Palette)', {}],
            ['sensor.lidar.ray_cast', None, 'Lidar (Ray-Cast)', {'range': '50'}],
            ['sensor.camera.dvs', cc.Raw, 'Dynamic Vision Sensor', {}],
            ['sensor.camera.rgb', cc.Raw, 'Camera RGB Distorted',
                {'lens_circle_multiplier': '3.0',
                'lens_circle_falloff': '3.0',
                'chromatic_aberration_intensity': '0.5',
                'chromatic_aberration_offset': '0'}]]
        world = self._parent.get_world()
        bp_library = world.get_blueprint_library()
        for item in self.sensors:
            bp = bp_library.find(item[0])
            if item[0].startswith('sensor.camera'):
                bp.set_attribute('image_size_x', str(hud.dim[0]))
                bp.set_attribute('image_size_y', str(hud.dim[1]))
                if bp.has_attribute('gamma'):
                    bp.set_attribute('gamma', str(gamma_correction))
                for attr_name, attr_value in item[3].items():
                    bp.set_attribute(attr_name, attr_value)
            elif item[0].startswith('sensor.lidar'):
                self.lidar_range = 50

                for attr_name, attr_value in item[3].items():
                    bp.set_attribute(attr_name, attr_value)
                    if attr_name == 'range':
                        self.lidar_range = float(attr_value)


            item.append(bp)
        self.index = None

    def toggle_camera(self):
        self.transform_index = (self.transform_index + 1) % len(self._camera_transforms)
        self.set_sensor(self.index, notify=False, force_respawn=True)

    def set_sensor(self, index, notify=True, force_respawn=False):
        index = index % len(self.sensors)
        needs_respawn = True if self.index is None else \
            (force_respawn or (self.sensors[index][2] != self.sensors[self.index][2]))
        if needs_respawn:
            if self.sensor is not None:
                self.sensor.destroy()
                self.surface = None
            self.sensor = self._parent.get_world().spawn_actor(
                self.sensors[index][-1],
                self._camera_transforms[self.transform_index][0],
                attach_to=self._parent,
                attachment_type=self._camera_transforms[self.transform_index][1])
            # We need to pass the lambda a weak reference to self to avoid
            # circular reference.
            weak_self = weakref.ref(self)
            self.sensor.listen(lambda image: CameraManager._parse_image(weak_self, image))
        if notify:
            self.hud.notification(self.sensors[index][2])
        self.index = index

    def next_sensor(self):
        self.set_sensor(self.index + 1)

    def toggle_recording(self):
        self.recording = not self.recording
        self.hud.notification('Recording %s' % ('On' if self.recording else 'Off'))

    def render(self, display):
        if self.surface is not None:
            display.blit(self.surface, (0, 0))

    @staticmethod
    def _parse_image(weak_self, image):
        self = weak_self()
        if not self:
            return
        if self.sensors[self.index][0].startswith('sensor.lidar'):
            points = np.frombuffer(image.raw_data, dtype=np.dtype('f4'))
            points = np.reshape(points, (int(points.shape[0] / 4), 4))
            lidar_data = np.array(points[:, :2])
            lidar_data *= min(self.hud.dim) / (2.0 * self.lidar_range)
            lidar_data += (0.5 * self.hud.dim[0], 0.5 * self.hud.dim[1])
            lidar_data = np.fabs(lidar_data)  # pylint: disable=E1111
            lidar_data = lidar_data.astype(np.int32)
            lidar_data = np.reshape(lidar_data, (-1, 2))
            lidar_img_size = (self.hud.dim[0], self.hud.dim[1], 3)
            lidar_img = np.zeros((lidar_img_size), dtype=np.uint8)
            lidar_img[tuple(lidar_data.T)] = (255, 255, 255)
            self.surface = pygame.surfarray.make_surface(lidar_img)
        elif self.sensors[self.index][0].startswith('sensor.camera.dvs'):
            # Example of converting the raw_data from a carla.DVSEventArray
            # sensor into a NumPy array and using it as an image
            dvs_events = np.frombuffer(image.raw_data, dtype=np.dtype([
                ('x', np.uint16), ('y', np.uint16), ('t', np.int64), ('pol', np.bool)]))
            dvs_img = np.zeros((image.height, image.width, 3), dtype=np.uint8)
            # Blue is positive, red is negative
            dvs_img[dvs_events[:]['y'], dvs_events[:]['x'], dvs_events[:]['pol'] * 2] = 255
            self.surface = pygame.surfarray.make_surface(dvs_img.swapaxes(0, 1))
        else:
            image.convert(self.sensors[self.index][1])
            array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
            array = np.reshape(array, (image.height, image.width, 4))
            array = array[:, :, :3]
            array = array[:, :, ::-1]
            self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
        if self.recording:
            image.save_to_disk('_out/%08d' % image.frame)


# ==============================================================================
# -- game_loop() ---------------------------------------------------------------
# ==============================================================================


def game_loop(args):
    pygame.init()
    pygame.font.init()
    world = None
    running = True
    carla_lock = threading.Lock()  # ✅ Thread safety
    
    try:
        client = carla.Client(args.host, args.port)
        client.set_timeout(2.0)

        display = pygame.display.set_mode(
            (args.width, args.height),
            pygame.HWSURFACE | pygame.DOUBLEBUF)

        hud = HUD(args.width, args.height)
        world = World(client.get_world(), hud, args)
        controller = KeyboardControl(world, args.autopilot)

        # ✅ Start CARLA in a separate thread
        def carla_loop(world):
            while running:
                with carla_lock:
                    try:
                        world.world.tick(timeout=2.0)
                        time.sleep(0.01)
                    except RuntimeError:
                        print("[WARNING] CARLA tick timeout!")
                        time.sleep(0.1)

        carla_thread = threading.Thread(target=carla_loop, args=(world,), daemon=True)
        carla_thread.start()
        
        clock = pygame.time.Clock()
        
        while running:
            clock.tick_busy_loop(60)

            for event in pygame.event.get():
                pygame.event.pump()
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()

            with carla_lock:
                world.hud.tick(world, clock)  # ✅ Update HUD display
                controller.parse_events(client, world, clock)
                world.render(display)
                pygame.display.flip()

    except Exception as e:
        print(f"[ERROR] Exception in game loop: {e}")
        # while True:
        #     clock.tick_busy_loop(30)
        #     if controller.parse_events(client, world, clock):
        #         return
        #     world.tick(clock)
        #     world.render(display)
        #     pygame.display.flip()

    finally:

        if (world and world.recording_enabled):
            client.stop_recorder()

        if world is not None:
            world.destroy()

        pygame.quit()


# ==============================================================================
# -- main() --------------------------------------------------------------------
# ==============================================================================


def main():
    argparser = argparse.ArgumentParser(
        description='CARLA Manual Control Client')
    argparser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='debug',
        help='print debug information')
    argparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-a', '--autopilot',
        action='store_true',
        help='enable autopilot')
    argparser.add_argument(
        '--res',
        metavar='WIDTHxHEIGHT',
        default='1280x720',
        help='window resolution (default: 1280x720)')
    argparser.add_argument(
        '--filter',
        metavar='PATTERN',
        default='vehicle.*',
        help='actor filter (default: "vehicle.*")')
    argparser.add_argument(
        '--rolename',
        metavar='NAME',
        default='hero',
        help='actor role name (default: "hero")')
    argparser.add_argument(
        '--gamma',
        default=2.2,
        type=float,
        help='Gamma correction of the camera (default: 2.2)')
    args = argparser.parse_args()

    args.width, args.height = [int(x) for x in args.res.split('x')]

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    logging.info('listening to server %s:%s', args.host, args.port)

    print(__doc__)

    try:

        game_loop(args)

    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')


if __name__ == '__main__':

    main()
