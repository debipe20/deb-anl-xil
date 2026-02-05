#!/usr/bin/env python3

import argparse
import random
import sys
import os
import math
import socket
import json
import pygame  # for keyboard input
import importlib.util
import time

from find_carla_egg import find_carla_egg

# -------------------------------------------------------------------------
# Locate CARLA egg and add CARLA to sys.path
# -------------------------------------------------------------------------

carla_egg_file = find_carla_egg()
print(f"Found carla egg(s): {carla_egg_file}")

# Add egg so `import carla` works
sys.path.append(carla_egg_file)

# Get /home/.../CARLA/PythonAPI from egg path
# carla_pythonapi_root = os.path.dirname(os.path.dirname(os.path.dirname(carla_egg_file)))
# print(f"Using CARLA PythonAPI root: {carla_pythonapi_root}")

# Add PythonAPI root so we can load agent sources from there
# sys.path.append(carla_pythonapi_root)

import carla

# -------------------------------------------------------------------------
# Load BehaviorAgent directly from its file path
# -------------------------------------------------------------------------

def load_behavior_agent_class():
    # Try both common layouts:
    candidates = [
        os.path.join(carla_pythonapi_root, "agents", "navigation", "behavior_agent.py"),
        os.path.join(carla_pythonapi_root, "carla", "agents", "navigation", "behavior_agent.py"),
    ]

    behavior_agent_path = None
    for path in candidates:
        if os.path.isfile(path):
            behavior_agent_path = path
            break

    if behavior_agent_path is None:
        raise RuntimeError(
            "Could not find behavior_agent.py under PythonAPI. "
            f"Tried: {candidates}"
        )

    print(f"Loading BehaviorAgent from: {behavior_agent_path}")

    spec = importlib.util.spec_from_file_location(
        "carla_behavior_agent", behavior_agent_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.BehaviorAgent


# BehaviorAgent = load_behavior_agent_class()

from agents.navigation.behavior_agent import BehaviorAgent
from speed_pid_controller import SpeedPIDController

# -------------------------------------------------------------------------
# Argument parser
# -------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description='CARLA manual vehicle with optional route-based autopilot'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='debug',
        help='print debug information')
    parser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    parser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    parser.add_argument(
        '--filter',
        metavar='PATTERN',
        default='vehicle.*',
        help='actor filter (default: "vehicle.*")')
    parser.add_argument(
        '--rolename',
        metavar='NAME',
        default='hero',
        help='actor role name for spawned vehicle (default: "hero")')
    parser.add_argument(
        '--follow_vehicle',
        default="TFHRC-MANUAL-1",
        help='Vehicle role_name to use if it already exists in the world')
    parser.add_argument(
        '-s', '--speed_limit',
        metavar='S',
        default=50,
        type=int,
        help='Speed limit for vehicle in kph (default: 50 kph)')
    parser.add_argument(
        '--x', type=float,
        help='x coordinate of the spawn point in CARLA left handed coordinate system')
    parser.add_argument(
        '--y', type=float,
        help='y coordinate of the spawn point in CARLA left handed coordinate system')
    parser.add_argument(
        '--z', type=float,
        help='z coordinate of the spawn point in CARLA left handed coordinate system')
    parser.add_argument(
        '--roll', type=float, default=0.0,
        help='roll angle in degrees (CARLA left handed coordinate system)')
    parser.add_argument(
        '--pitch', type=float, default=0.0,
        help='pitch angle in degrees (CARLA left handed coordinate system)')
    parser.add_argument(
        '--yaw', type=float, default=0.0,
        help='yaw angle in degrees (CARLA left handed coordinate system)')
    parser.add_argument(
        '--dest',
        metavar=('DX', 'DY', 'DZ'),
        type=float,
        nargs=3,
        help='Destination coordinate for route autopilot (DX DY DZ)')
    
    parser.add_argument(
        '--show_route',
        action='store_true',
        help='Display the planned route waypoints on the HUD/World')
        
    return parser.parse_args()


# -------------------------------------------------------------------------
# World & vehicle helpers
# -------------------------------------------------------------------------

def get_world_and_map(host, port):
    client = carla.Client(host, port)
    client.set_timeout(10.0)
    world = client.get_world()
    return world, world.get_map()


def find_existing_vehicle(world, follow_role_name):
    carla_vehicles = world.get_actors().filter('vehicle.*')
    for vehicle in carla_vehicles:
        current_attributes = vehicle.attributes
        print("Checking vehicle:", current_attributes.get("role_name", "<no-role>"))
        if current_attributes.get("role_name") == follow_role_name:
            print(f">>> Selected existing vehicle with role_name={follow_role_name}")
            return vehicle
    return None


def spawn_vehicle(world, carla_map, args):
    bp_lib = world.get_blueprint_library()
    bp_candidates = bp_lib.filter(args.filter)
    if not bp_candidates:
        raise RuntimeError(f"No blueprints found with filter {args.filter}")
    bp = bp_candidates[0]

    if bp.has_attribute('role_name'):
        bp.set_attribute('role_name', args.rolename)

    if args.x is not None and args.y is not None and args.z is not None:
        spawn_transform = carla.Transform(
            carla.Location(x=args.x, y=args.y, z=args.z),
            carla.Rotation(
                roll=args.roll,
                pitch=args.pitch,
                yaw=args.yaw
            )
        )
    else:
        spawn_points = carla_map.get_spawn_points()
        if not spawn_points:
            raise RuntimeError("No spawn points available in this map")
        spawn_transform = random.choice(spawn_points)

    print(f">>> Spawning vehicle with role_name={args.rolename} at {spawn_transform}")
    vehicle = world.try_spawn_actor(bp, spawn_transform)
    if vehicle is None:
        raise RuntimeError("Failed to spawn vehicle at requested transform")
    return vehicle


def setup_vehicle(world, carla_map, args):
    # Try existing vehicle first
    vehicle = find_existing_vehicle(world, args.follow_vehicle)
    if vehicle is None:
        print(f">>> No vehicle with role_name={args.follow_vehicle} found, spawning a new one")
        vehicle = spawn_vehicle(world, carla_map, args)

    # Make sure Traffic Manager autopilot is OFF – we are using BehaviorAgent
    vehicle.set_autopilot(False)

    return vehicle


# -------------------------------------------------------------------------
# BehaviorAgent setup (route-based autopilot)
# -------------------------------------------------------------------------

def setup_agent(vehicle, args):
    agent = BehaviorAgent(vehicle, behavior="normal")
    autopilot_active = False
    dest_loc = None  # >>> ADDED >>> keep destination for replanning

    if args.dest:
        dest_loc = carla.Location(x=args.dest[0], y=args.dest[1], z=args.dest[2])
        print(f">>> Setting route destination to {dest_loc}")
        agent.set_destination(dest_loc)
        # Initial target speed in kph = args.speed_limit
        agent.set_target_speed(float(args.speed_limit))
        autopilot_active = True
    else:
        print(">>> No destination provided; route autopilot inactive, manual control expected.")

    return agent, autopilot_active, dest_loc  # >>> CHANGED >>> return dest_loc
# -------------------------------------------------------------------------
# >>> ADDED >>> On-road / off-road detection and recovery control
# -------------------------------------------------------------------------
def is_on_driving_lane(carla_map, location: carla.Location) -> bool:
    """
    Returns True only if the current location maps to a DRIVING waypoint
    without projection (i.e., truly on-road/drivable lane).
    """
    wp = carla_map.get_waypoint(
        location,
        project_to_road=False,
        lane_type=carla.LaneType.Driving
    )
    return wp is not None
def clamp(x, lo, hi):
    return max(lo, min(hi, x))
def normalize_angle_deg(a):
    # Normalize to [-180, 180]
    while a > 180.0:
        a -= 360.0
    while a < -180.0:
        a += 360.0
    return a
def recover_to_road_control(vehicle: carla.Vehicle, carla_map, desired_speed_mps=3.8) -> carla.VehicleControl:
    """
    Simple recovery policy:
      - Find nearest drivable waypoint (project_to_road=True),
      - steer towards it,
      - keep a low desired speed until back on road.
    """
    ego_tf = vehicle.get_transform()
    ego_loc = ego_tf.location
    ego_yaw = ego_tf.rotation.yaw
    wp = carla_map.get_waypoint(
        ego_loc,
        project_to_road=True,
        lane_type=carla.LaneType.Driving
    )
    control = carla.VehicleControl()
    control.hand_brake = False
    control.manual_gear_shift = False
    if wp is None:
        # Worst case: no waypoint found; stop safely
        control.throttle = 0.0
        control.brake = 1.0
        control.steer = 0.0
        return control
    target_loc = wp.transform.location
    dx = target_loc.x - ego_loc.x
    dy = target_loc.y - ego_loc.y
    target_yaw = math.degrees(math.atan2(dy, dx))
    yaw_err = normalize_angle_deg(target_yaw - ego_yaw)
    steer_cmd = clamp(yaw_err / 45.0, -1.0, 1.0)  # 45 deg error -> full steer
    # Simple speed hold (very coarse): throttle if slow, brake if fast
    v = vehicle.get_velocity()
    speed_mps = math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z)
    if speed_mps < desired_speed_mps:
        control.throttle = 0.35
        control.brake = 0.0
    else:
        control.throttle = 0.0
        control.brake = 0.25
    control.steer = float(steer_cmd)
    return control
# -------------------------------------------------------------------------
# >>> ADDED >>> Replanning logic (early-stop detection + replan)
# -------------------------------------------------------------------------
def maybe_replan(agent, carla_map, dest_loc, arrive_dist_m=4.0, low_plan_len=8) -> bool:
    """
    Replan if:
      - destination exists,
      - not within arrive_dist_m,
      - local plan is depleted or very short OR agent.done() is True.
    Returns True if replanned.
    """
    if dest_loc is None:
        return False
    ego_loc = agent._vehicle.get_location()
    dist_to_goal = ego_loc.distance(dest_loc)
    if dist_to_goal <= arrive_dist_m:
        return False  # arrived
    # Check remaining plan length
    try:
        plan_len = len(list(agent.get_local_planner().get_plan()))
    except Exception:
        plan_len = 0
    if (plan_len > low_plan_len) and (not agent.done()):
        return False
    # Build plan from current pose to destination (snap endpoints to Driving waypoints)
    start_wp = carla_map.get_waypoint(
        ego_loc,
        project_to_road=True,
        lane_type=carla.LaneType.Driving
    )
    end_wp = carla_map.get_waypoint(
        dest_loc,
        project_to_road=True,
        lane_type=carla.LaneType.Driving
    )
    if start_wp is None or end_wp is None:
        print(">>> Replan skipped: could not project start/dest to Driving waypoint.")
        return False
    route = agent.trace_route(start_wp, end_wp)
    if route is None or len(route) == 0:
        print(">>> Replan failed: trace_route returned empty route.")
        return False
    agent.set_global_plan(route, stop_waypoint_creation=True, clean_queue=True)
    print(f">>> Replanned route (dist_to_goal={dist_to_goal:.1f} m, new_route_len={len(route)})")
    return True


# -------------------------------------------------------------------------
# Method to get lead vehicle headway
# -------------------------------------------------------------------------
def get_speed_mps(vehicle: carla.Actor) -> float:
    vel = vehicle.get_velocity()
    speed_mps = math.sqrt(vel.x**2 + vel.y**2 + vel.z**2)
    
    return speed_mps

def get_vehicle_ahead(ego_vehicle, world, max_distance=80.0, lane_width=3.2):
    """
    Returns:
        lead_vehicle       (carla.Actor or None)
        distance_to_lead   (float or None)
        lead_speed_mps     (float or None)
        lead_speed_mph     (float or None)
    for the closest vehicle in front of the ego vehicle within lane_width,
    or (None, None, None, None) if no one is ahead.
    """
    
    all_vehicles = world.get_actors().filter('vehicle.*')

    ego_transform = ego_vehicle.get_transform()  # the transform (position + rotation) of the ego vehicle
    ego_position = ego_transform.location  # 3D position of ego
    ego_forward_direction = ego_transform.get_forward_vector()  # direction the ego vehicle is facing

    closest_vehicle = None
    closest_distance = max_distance  # start with the maximum distance allowed

    for vehicle in all_vehicles:
        if vehicle.id == ego_vehicle.id:
            continue  # skip the ego vehicle itself

        vehicle_position = vehicle.get_transform().location
        relative_position = vehicle_position - ego_position  # vector from ego to this vehicle

        # Longitudinal component along ego vehicle's heading (dot product)
        longitudinal_distance = (
            relative_position.x * ego_forward_direction.x +
            relative_position.y * ego_forward_direction.y +
            relative_position.z * ego_forward_direction.z
        )

        # Ignore vehicles behind the ego vehicle (longitudinally) or exactly at the same position
        if longitudinal_distance <= 0.0:
            continue

        # Calculate lateral distance (perpendicular distance to ego's forward direction)
        lateral_distance = abs(relative_position.x * ego_forward_direction.y - relative_position.y * ego_forward_direction.x)
        if lateral_distance > lane_width *0.5:
            # If the vehicle is too far off to the side, it's likely in another lane
            continue

        # Calculate the 3D Euclidean distance between the ego vehicle and this vehicle
        distance_to_vehicle = ego_position.distance(vehicle_position)
        if distance_to_vehicle < closest_distance:
            closest_distance = distance_to_vehicle
            closest_vehicle = vehicle

    if closest_vehicle is None:
        return None, None, None, None

    lead_vehicle_speed_mps = get_speed_mps(closest_vehicle)
    lead_vehicle_speed_mph = lead_vehicle_speed_mps * 2.23694  # convert m/s to mph

    return closest_vehicle, closest_distance, lead_vehicle_speed_mps, lead_vehicle_speed_mph


def compute_desired_speed_mps(ego_speed_mps, lead_distance_m, lead_speed_mps, speed_limit_mph, min_gap_m = 10.0, time_headway_s=1.5, gap_gain=0.5) -> float:
    """
    Compute a desired speed (m/s) for the ego vehicle using a simple
    time-headway rule.

    - If there is no lead vehicle: track the speed limit.
    - If there is a lead vehicle: follow its speed while trying to keep
      a safe distance (min_gap_m + time_headway_s * ego_speed_mps).
    """

    # Convert road speed limit from mph to m/s
    speed_limit_mps = (speed_limit_mph or 0.0) * 0.44704

    # No usable lead info -> just follow the speed limit
    if lead_distance_m is None or lead_speed_mps is None:
        return speed_limit_mps

    # Desired following distance (meters)
    # desired_gap = min_gap + time_headway * ego_speed
    ego_speed_for_gap_mps = max(ego_speed_mps, 0.0)
    desired_gap_m = min_gap_m + time_headway_s * ego_speed_for_gap_mps

    # Gap error: positive = too far, negative = too close
    gap_error_m = lead_distance_m - desired_gap_m

    # Reference speed = lead speed plus a correction based on gap error
    desired_speed_mps = lead_speed_mps + gap_gain * gap_error_m

    # Clamp between 0 and the road speed limit
    desired_speed_mps = max(0.0, min(speed_limit_mps, desired_speed_mps))
    return desired_speed_mps


# -------------------------------------------------------------------------
# Main loop with keyboard speed control (SPACE / UP / DOWN)
# -------------------------------------------------------------------------

def run_loop(world, carla_map, vehicle, agent, autopilot_active, dest_loc, args):  # >>> CHANGED >>> carla_map + dest_loc
    """
    Main synchronous control loop for the ego vehicle.

    This loop advances the CARLA simulation (`world.tick()`), computes perception-derived
    longitudinal targets (lead-vehicle following + speed limit), and applies either
    BehaviorAgent control (autopilot) or manual/assisted control depending on runtime flags.

    Key behaviors when `autopilot_active` is True
    ---------------------------------------------
    1) Route following / lateral control:
       - `agent.run_step(...)` is called to produce a base `carla.VehicleControl`.
       - In train mode, this base control is used primarily for steering (lateral control).

    2) Replanning / completion logic:
       - `maybe_replan(...)` is invoked to rebuild the global plan when the plan is short,
         depleted, or `agent.done()` becomes True before reaching the destination.
       - If the agent is truly done (within ARRIVE_DIST_M to destination), autopilot is disabled.

    3) Off-road recovery (highest-level mode switch):
       - If the ego vehicle leaves a drivable lane (`is_on_driving_lane(...) == False`),
         the loop enters `recovery_mode`.
       - During recovery, agent control and PID/UDP logic are skipped; a simple controller
         (`recover_to_road_control`) steers toward the nearest drivable waypoint and holds a low speed.
       - When back on-road, recovery exits and a replan is attempted.

    Longitudinal control priority in train mode (override order)
    ------------------------------------------------------------
    In `train_mode == True`, throttle/brake are NOT taken from BehaviorAgent; they are produced
    and overridden in the following strict order each tick:

      (A) PID baseline (lowest priority)
          - `SpeedPIDController.compute_control(current_speed, desired_speed, dt)` computes
            `throttle_pid` and `brake_pid` to track `desired_speed_mps`.

      (B) UDP Map-SPaT override (medium priority; only if a valid packet is received)
          - A non-blocking UDP read attempts to parse JSON containing "Map-SPat-Data".
          - Example rule: if signal is red and intersection distance <= 200 m:
                throttle_pid = 0.0
                brake_pid = max(brake_pid, 0.5)

      (C) Lead-vehicle safety hard stop (highest priority)
          - If a lead vehicle is detected within 5 m:
                throttle_pid = 0.0
                brake_pid = 1.0
          - This overrides BOTH PID output and any UDP-based override.

    Desired speed computation
    -------------------------
    - `get_vehicle_ahead(...)` finds the closest vehicle ahead in-lane and returns its distance/speed.
    - `compute_desired_speed_mps(...)` applies a simple time-headway / min-gap policy:
        * No lead vehicle: desired speed tracks the (manual or configured) speed limit.
        * Lead vehicle present: desired speed follows lead speed plus a correction based on gap error.

    Inputs / UI
    -----------
    - Pygame is used for keyboard input and HUD-like status rendering.
    - Keys:
        * SPACE: stop/resume target speed
        * UP/DOWN: adjust manual target speed
        * E: toggle manual speed limiting
        * T: toggle train mode
        * W/S: manual throttle/brake commands (only meaningful if you implement them; PID currently dominates in train mode)

    Networking
    ----------
    - A UDP socket is bound to the configured host/port and set to non-blocking mode.
    - At most one datagram is processed per tick; absence of data is non-fatal.

    Parameters
    ----------
    world : carla.World
        CARLA world instance used for ticking and debug drawing.
    carla_map : carla.Map
        Map used for waypoint queries (on-road detection, replanning, recovery).
    vehicle : carla.Vehicle
        Ego vehicle actor to be controlled.
    agent : BehaviorAgent
        Route-following agent used when autopilot is active.
    autopilot_active : bool
        Enables agent-based route control and recovery/replanning logic.
    dest_loc : carla.Location or None
        Destination location for route autopilot/replanning. If None, autopilot is typically inactive.
    args : argparse.Namespace
        CLI arguments (speed limit, route display, etc.).

    Notes
    -----
    - If `recovery_mode` is active, this loop applies recovery control and continues to the next tick,
      bypassing agent.run_step() and PID/UDP logic for that iteration.
    - When exiting (exception or quit), the function attempts to disable autopilot and close sockets cleanly.
    """
    
    # Pygame setup for keyboard events
    pygame.init()
    screen = pygame.display.set_mode((300, 300))  # tiny window just to grab focus
    pygame.display.set_caption("Control Window")

    font = pygame.font.SysFont(None, 24, bold=True)

    # Track target speed in km/h (this is what BehaviorAgent expects)
    if args.speed_limit > 0:
        target_speed_kph = float(args.speed_limit)
    else:
        target_speed_kph = 0.0

    prev_target_speed_kph = 0.0

    print(f">>> Initial target speed = {target_speed_kph:.1f} kph")

    manual_speed_limit_enabled = True
    train_mode = True
    target_speed_kph = 0.0

    # Simple longitudinal control for train mode
    train_throttle = 0.0
    train_brake = 0.0
    # PID controller for speed in train mode
    speed_pid = SpeedPIDController(Kp=0.6, Ki=0.1, Kd=0.0, max_integral=10.0, deadband=0.2,
        min_throttle=0.2, min_brake=0.1, filter_alpha=0.3, throttle_smoothing=0.05)
    
    INITIAL_PLAN = False
    # >>> ADDED >>> Recovery mode state
    recovery_mode = False
    recovery_ticks = 0
    MAX_RECOVERY_TICKS = 250  # ~5 seconds if 20 FPS, adjust as needed
    # >>> ADDED >>> thresholds
    ARRIVE_DIST_M = 4.0
    LOW_PLAN_LEN = 8
    
    configFile = open("../../config/anl-master-config.json", "r")
    config = json.load(configFile)
    configFile.close()

    host_ip = config["IPAddress"]["HostIp"]
    port = config["PortNumber"]["EgoController"]
    com_info = (host_ip, port)

    ego_controller_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ego_controller_socket.bind(com_info)
    # ego_controller_socket.settimeout(0.01)  # 10 ms
    ego_controller_socket.setblocking(False)  # non-blocking (no settimeout)
    
    last_spat = {"signal": None, "dist": None, "t": -1e9}
    SPAT_HOLD_S = 0.5
    
    try:
        while True:
            world.tick()
            snapshot = world.get_snapshot()
            dt = snapshot.timestamp.delta_seconds

            # -----------------------------
            # Lead vehicle detection (object + distance)
            # -----------------------------
            lead_vehicle, lead_distance, lead_speed_mps, lead_speed_mph = get_vehicle_ahead(vehicle, world)
            ego_speed_mps = get_speed_mps(vehicle)
            
            if lead_vehicle is not None:
                rel_speed_mps = lead_speed_mps - ego_speed_mps
                rel_speed_mph = rel_speed_mps * 2.23694
                print(
                    f"Lead vehicle id={lead_vehicle.id}, "
                    f"distance={lead_distance:.2f} m, "
                    f"speed={lead_speed_mph:.2f} mph,"
                    f"rel_speed={rel_speed_mph:.2f} mph"
                )
                
                lead_text_str  = f"Lead Speed: {lead_speed_mph:.1f} mph"
                relative_dist_text_str = f"Relative Distance: {lead_distance:.1f} m"
                # relative_spd_text_str = f"Relative Speed ={rel_speed_mph:.1f} mph"      
                                
            else:
                lead_text_str = "Lead Speed: NA"
                relative_dist_text_str = "Relative Distance: NA"
                print("Lead vehicle None")

            # -----------------------------
            # Choose desired speed for PID (lead-following vs speed limit)
            # -----------------------------
            # Base speed limit coming from UI/args
            if manual_speed_limit_enabled:
                cruise_speed_mph = target_speed_kph * 0.621371
            else:
                cruise_speed_mph = float(args.speed_limit) *0.621371

            desired_speed_mps = compute_desired_speed_mps(
                ego_speed_mps=ego_speed_mps,
                lead_distance_m=lead_distance,
                lead_speed_mps=lead_speed_mps,
                speed_limit_mph=cruise_speed_mph,
            )

                
            # -----------------------------
            # Keyboard handling
            # -----------------------------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

                if event.type == pygame.KEYDOWN:
                    # SPACE: stop / resume previous target speed
                    if event.key == pygame.K_SPACE:
                        if target_speed_kph not in (0.0, None):
                            prev_target_speed_kph = target_speed_kph
                            target_speed_kph = 0.0
                            print(">>> SPACE pressed: target speed set to 0.0 kph")
                        else:
                            # Restore previous target speed (only if manual speed is enabled)
                            if manual_speed_limit_enabled and prev_target_speed_kph is not None:
                                target_speed_kph = prev_target_speed_kph
                            print(f">>> SPACE pressed: returning target speed to {target_speed_kph} kph")

                    # UP: increase target speed by 5 kph
                    elif event.key == pygame.K_UP:
                        if manual_speed_limit_enabled:
                            # If we were in "auto" (None), start from 0
                            if target_speed_kph is None:
                                target_speed_kph = 0.0
                            target_speed_kph += 5.0
                            print(f">>> UP pressed: target speed = {target_speed_kph:.1f} kph")

                    # DOWN: decrease target speed by 5 kph (not below zero)
                    elif event.key == pygame.K_DOWN:
                        if manual_speed_limit_enabled:
                            if target_speed_kph is None:
                                target_speed_kph = 0.0
                            target_speed_kph = max(0.0, target_speed_kph - 5.0)
                            print(f">>> DOWN pressed: target speed = {target_speed_kph:.1f} kph")

                    # E: toggle manual speed limiting on/off
                    elif event.key == pygame.K_e:
                        manual_speed_limit_enabled = not manual_speed_limit_enabled
                        print(f">>> E pressed: toggling manual_speed_limit: {manual_speed_limit_enabled}")

                    # T: toggle train mode (agent steers, user does throttle/brake)
                    elif event.key == pygame.K_t:
                        train_mode = not train_mode
                        # Reset longitudinal when toggling
                        train_throttle = 0.0
                        train_brake = 0.0
                        print(f">>> T pressed: toggling train mode: {train_mode}")

                    # W: throttle (only in train mode)
                    elif event.key == pygame.K_w:
                        if train_mode:
                            train_throttle = 1.0   # full throttle
                            train_brake = 0.0
                            print(">>> W pressed (train mode): throttle=1.0, brake=0.0")

                    # S: brake (only in train mode)
                    elif event.key == pygame.K_s:
                        if train_mode:
                            train_throttle = 0.0
                            train_brake = 1.0   # full brake
                            print(">>> S pressed (train mode): throttle=0.0, brake=1.0")

                # When key is released, stop applying throttle/brake in train mode
                if event.type == pygame.KEYUP:
                    if train_mode and event.key in (pygame.K_w, pygame.K_s):
                        train_throttle = 0.0
                        train_brake = 0.0
                        print(">>> W/S released (train mode): throttle=0.0, brake=0.0")

            # If we disabled manual speed, pass None down to the agent
            manual_speed_value = target_speed_kph if manual_speed_limit_enabled else None

            # -----------------------------
            # Autopilot / agent control
            # -----------------------------
            if autopilot_active:
                # >>> ADDED >>> Off-road detection
                on_road = is_on_driving_lane(carla_map, vehicle.get_location())
                if not on_road:
                    if not recovery_mode:
                        print(">>> Off-road detected: entering recovery mode.")
                        recovery_mode = True
                        recovery_ticks = 0

                # >>> ADDED >>> Recovery behavior (bring vehicle back on road)
                if recovery_mode:
                    recovery_ticks += 1
                    control = recover_to_road_control(vehicle, carla_map, desired_speed_mps=3.0)

                    # Optionally respect your lead-vehicle hard stop in recovery mode too
                    if lead_vehicle is not None and lead_distance is not None and lead_distance <= 10.0:
                        control.throttle = 0.0
                        control.brake = 1.0

                    vehicle.apply_control(control)

                    # Exit recovery mode if back on-road, then replan immediately
                    if is_on_driving_lane(carla_map, vehicle.get_location()):
                        print(">>> Recovery success: back on drivable lane. Replanning.")
                        recovery_mode = False
                        maybe_replan(agent, carla_map, dest_loc, arrive_dist_m=ARRIVE_DIST_M, low_plan_len=LOW_PLAN_LEN)
                    elif recovery_ticks >= MAX_RECOVERY_TICKS:
                        print(">>> Recovery timeout: stopping vehicle for safety.")
                        stop = carla.VehicleControl(throttle=0.0, brake=1.0, steer=0.0)
                        vehicle.apply_control(stop)
                        recovery_mode = False
                    continue  # skip agent control during recovery

                # >>> CHANGED >>> Replan if plan depleted/too short before destination
                replanned = maybe_replan(agent, carla_map, dest_loc, arrive_dist_m=ARRIVE_DIST_M, low_plan_len=LOW_PLAN_LEN)

                # If the agent says done and we did NOT replan, treat as arrived and stop autopilot
                if agent.done() and not replanned:
                    if dest_loc is not None and vehicle.get_location().distance(dest_loc) > ARRIVE_DIST_M:
                        # Defensive: sometimes done() is true even though not arrived; force a replan attempt
                        forced = maybe_replan(agent, carla_map, dest_loc, arrive_dist_m=ARRIVE_DIST_M, low_plan_len=999999)
                        if forced:
                            print(">>> Forced replan because done() but not within arrival distance.")
                        else:
                            print(">>> Route ended but cannot replan; disabling autopilot.")
                            autopilot_active = False
                            continue
                    else:
                        print(">>> Route completed")
                        autopilot_active = False
                        continue

                # Your modified BehaviorAgent.run_step(manual_speed_limit=...)
                # control = agent.run_step(manual_speed_limit=manual_speed_value)
                ### Adding code block to display the route
                control = agent.run_step(debug=args.show_route, manual_speed_limit=manual_speed_value)
 
                # if args.show_route:
                #     # Draw the next few waypoints from the local planner
                #     plan = agent.get_local_planner().get_plan()
                #     for i, (wp, _) in enumerate(plan):
                #         if i >= 50: break # Limit to 50 points to avoid lag
                #         loc = wp.transform.location + carla.Location(z=0.5)
                #         world.debug.draw_point(loc, size=0.1, color=carla.Color(0, 255, 0), life_time=0.1)
                
                if args.show_route:
                    # Draw the next few waypoints from the local planner
                    plan = agent.get_local_planner().get_plan()
                    if not INITIAL_PLAN:
                        for i, (wp, _) in enumerate(plan):
                            loc = wp.transform.location + carla.Location(z=0.5)
                            world.debug.draw_point(loc, size=0.1, color=carla.Color(0, 255, 0), life_time=10)
                            INITIAL_PLAN = True
                    else:
                        for i, (wp, _) in enumerate(plan):
                            if i >= 50: break # Limit to 50 points to avoid lag
                            loc = wp.transform.location + carla.Location(z=0.5)
                            world.debug.draw_point(loc, size=0.1, color=carla.Color(0, 255, 0), life_time=0.1)

                
                if train_mode:
                    # 1) Always compute PID first
                    # TRAIN MODE: BehaviorAgent steers, PID controls throttle/brake
                    throttle_pid, brake_pid, pid_raw = speed_pid.compute_control(
                        current_speed=ego_speed_mps,
                        desired_speed=desired_speed_mps,
                        dt=dt,
                    )

                    # 2) Try to read one UDP packet (non-fatal if none)
                    # Try to read one UDP packet; if none, keep PID output
                    now = time.time()
                    try:
                        data, addr = ego_controller_socket.recvfrom(2048)
                        decoded_data = data.decode("utf-8", errors="replace")
                        parsed_json = json.loads(decoded_data)
                        print(f"[{now}] Received Map-SPaT data:\n{parsed_json}")

                        map_spat_data = parsed_json.get("Map-SPaT-Data", {})
                        signal_state = (map_spat_data.get("SignalState") or "").lower()
                        intersection_distance = map_spat_data.get("IntersectionDistance", None)

                        # Convert distance to float if possible
                        try:
                            intersection_distance = float(intersection_distance)
                        except (TypeError, ValueError):
                            intersection_distance = None

                        # Update latch
                        last_spat.update({"signal": signal_state, "dist": intersection_distance, "t": now})
                    except (BlockingIOError, json.JSONDecodeError):
                        pass
                    
                    # 2) Use latched SPaT for a short time window (the key missing piece)
                    use_spat = (now - last_spat["t"]) <= SPAT_HOLD_S
                    sig = last_spat["signal"] if use_spat else None
                    dist = last_spat["dist"] if use_spat else None
                    
                    # 3) Apply override based on latched values
                    if sig == "red" and dist is not None:
                        if dist <= 5:
                            throttle_pid = 0.0
                            brake_pid = 1.0
                        elif dist <= 15:
                            throttle_pid = 0.0
                            brake_pid = max(brake_pid, 0.2)
                        elif dist <= 25:
                            throttle_pid = min(throttle_pid, 0.1)
                            brake_pid = max(brake_pid, 0.15)
                                                    
                    

                    # 4) Hard safety override has highest priority
                    if lead_vehicle is not None and lead_distance is not None and lead_distance <= 5.0:
                        throttle_pid = 0.0
                        brake_pid = 1.0
                        
                    # Debug what will be applied (based on latch)
                    print(f"APPLY ctrl: thr={throttle_pid:.2f} brk={brake_pid:.2f} sig={sig} dist={dist}")

                    control.throttle = throttle_pid
                    control.brake = brake_pid
                    control.hand_brake = False
                else:
                    speed_pid.reset()

                vehicle.apply_control(control)
                
            # -----------------------------
            # Prepare speed debug text (ego & desired)
            # -----------------------------
            ego_speed_mph = ego_speed_mps * 2.23694
            desired_speed_mph = desired_speed_mps * 2.23694

            ego_speed_text = f"Ego Speed: {ego_speed_mph:.1f} mph"
            desired_speed_text = f"Desired Speed: {desired_speed_mph:.1f} mph"

            # -----------------------------
            # Draw HUD text in the pygame window
            # -----------------------------
            screen.fill((0, 0, 0))  # black background

            # Static title text
            title1 = font.render("CLICK HERE", True, (255, 0, 0))
            title2 = font.render("TO CONTROL", True, (255, 0, 0))

            # Dynamic status text
            manual_text = f"Manual: {'ON' if manual_speed_limit_enabled else 'OFF'}"
            if manual_speed_value is None:
                speed_text = "Mannual Speed Limit: AUTO"
            else:
                speed_text = f"Mannual Speed Limit: {manual_speed_value:.1f} kph"

            train_text = f"Train: {'ON' if train_mode else 'OFF'}"
            lead_text = lead_text_str  # from detection step above
            relative_distance_text = relative_dist_text_str
            
            status1 = font.render(manual_text, True, (255, 255, 255))
            status2 = font.render(speed_text, True, (255, 255, 255))
            status3 = font.render(train_text, True, (255, 255, 0))
            status4 = font.render(lead_text, True, (0, 255, 255))
            status5 = font.render(ego_speed_text, True, (255, 255, 255))
            status6 = font.render(desired_speed_text, True, (255, 255, 255))
            status7 = font.render(relative_distance_text, True, (255, 255, 255))

            # Positioning
            rect_title1 = title1.get_rect(center=(150, 30))
            rect_title2 = title2.get_rect(center=(150, 60))
            rect_status1 = status1.get_rect(center=(150, 110))
            rect_status2 = status2.get_rect(center=(150, 140))
            rect_status3 = status3.get_rect(center=(150, 170))
            rect_status4 = status4.get_rect(center=(150, 190))
            rect_status5 = status5.get_rect(center=(150, 210))
            rect_status6 = status6.get_rect(center=(150, 230))
            rect_status7 = status7.get_rect(center=(150, 250))

            # Blit and flip
            screen.blit(title1, rect_title1)
            screen.blit(title2, rect_title2)
            screen.blit(status1, rect_status1)
            screen.blit(status2, rect_status2)
            screen.blit(status3, rect_status3)
            screen.blit(status4, rect_status4)
            screen.blit(status5, rect_status5)
            screen.blit(status6, rect_status6)
            screen.blit(status7, rect_status7)
            pygame.display.flip()

    finally:
        print(">>> Exiting loop; ensuring autopilot is OFF.")
        try:
            vehicle.set_autopilot(False)
            ego_controller_socket.close()
        except Exception as e:
            print(f"Failed to disable autopilot cleanly: {e}")

# -------------------------------------------------------------------------
# Entry point
# -------------------------------------------------------------------------

def main():
    args = parse_args()
    world, carla_map = get_world_and_map(args.host, args.port)
    vehicle = setup_vehicle(world, carla_map, args)
    agent, autopilot_active, dest_loc = setup_agent(vehicle, args)  # >>> CHANGED >>>

    run_loop(world, carla_map, vehicle, agent, autopilot_active, dest_loc, args)  # >>> CHANGED >>>



if __name__ == '__main__':
    main()
