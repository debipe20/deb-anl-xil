#!/usr/bin/env python3

import argparse
import random
import sys
import os
import math

import pygame  # for keyboard input
import importlib.util

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

    if args.dest:
        dest_loc = carla.Location(x=args.dest[0], y=args.dest[1], z=args.dest[2])
        print(f">>> Setting route destination to {dest_loc}")
        agent.set_destination(dest_loc)
        # Initial target speed in kph = args.speed_limit
        agent.set_target_speed(float(args.speed_limit))
        autopilot_active = True
    else:
        print(">>> No destination provided; route autopilot inactive, manual control expected.")

    return agent, autopilot_active

# -------------------------------------------------------------------------
# Method to get lead vehicle headway
# -------------------------------------------------------------------------
def get_speed_mps(vehicle: carla.Actor) -> float:
    vel = vehicle.get_velocity()
    speed_mps = math.sqrt(vel.x**2 + vel.y**2 + vel.z**2)
    
    return speed_mps

def get_vehicle_ahead(ego_vehicle, world, max_distance=80.0, lane_width=3.6):
    """
    Find the closest vehicle ahead of the ego vehicle within a lateral corridor.

    The function iterates over vehicles in the simulation world, keeps only those
    that are in front of the ego vehicle (positive projection onto the ego's
    forward direction), rejects vehicles that are too far laterally (outside the
    current lane/corridor), and returns the nearest remaining candidate within max_distance.

    Args:
        ego_vehicle:
            The ego vehicle actor (must provide CARLA get_transform()).
        world:
            Simulation world object used to retrieve vehicle actors.
        max_distance (float, optional):
            Maximum distance (meters) to search ahead. Defaults to 80.0.
        lane_width (float, optional):
            Maximum allowed lateral offset (meters) from the ego's forward axis
            to still be considered "ahead in the same lane/corridor". Defaults to 3.6.

    Returns:
        tuple:
            (lead_vehicle, distance_m, lead_speed_mps, lead_speed_mph), where:

            - lead_vehicle: Closest vehicle ahead, or None if not found.
            - distance_m: Distance to the lead vehicle in meters, or None.
            - lead_speed_mps: Lead vehicle speed in m/s, or None.
            - lead_speed_mph: Lead vehicle speed in mph, or None.

        If no valid lead vehicle is found, returns (None, None, None, None).

    Notes:
        - "Ahead" is determined using the ego vehicle's forward direction.
        - Lateral offset is computed in the ground plane to approximate lane alignment.
        - Vehicle speed is computed via an external helper (e.g., get_speed_mps).
    """
    
    vehicles = world.get_actors().filter('vehicle.*')

    ego_tf = ego_vehicle.get_transform() #the transform (position + rotation) of the ego vehicle.
    ego_loc = ego_tf.location #3D position of ego
    ego_forward = ego_tf.get_forward_vector()  # carla.Vector3D, a unit vector pointing in the direction the car is facing (its heading)

    closest_vehicle = None
    closest_dist = max_distance

    for v in vehicles:
        if v.id == ego_vehicle.id:
            continue

        loc = v.get_transform().location
        rel = loc - ego_loc  # Relative Vector Distance, Vector from ego to this vehicle

        # Longitudinal component along ego heading (dot product)
        longitudinal = (
            rel.x * ego_forward.x +
            rel.y * ego_forward.y +
            rel.z * ego_forward.z
        )

        # Ignore vehicles behind or exactly at ego longitudinally
        if longitudinal <= 0.0:
            continue

        # Lateral offset using 2D cross product magnitude
        lateral = abs(rel.x * ego_forward.y - rel.y * ego_forward.x)
        if lateral > lane_width:
            # Too far to the side -> likely another lane
            continue

        dist = ego_loc.distance(loc) #3D Euclidean distance between ego and that car, in meters.
        if dist < closest_dist:
            closest_dist = dist
            closest_vehicle = v

    if closest_vehicle is None:
        return None, None, None, None

    lead_speed_mps = get_speed_mps(closest_vehicle)
    lead_speed_mph = lead_speed_mps * 2.23694

    return closest_vehicle, closest_dist, lead_speed_mps, lead_speed_mph

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

def run_loop(world, vehicle, agent, autopilot_active, args):
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
    train_mode = False

    # Simple longitudinal control for train mode
    train_throttle = 0.0
    train_brake = 0.0
    # PID controller for speed in train mode
    speed_pid = SpeedPIDController(Kp=0.6, Ki=0.1, Kd=0.0, max_integral=10.0, deadband=0.2,
        min_throttle=0.2, min_brake=0.1, filter_alpha=0.3, throttle_smoothing=0.05)
    
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
                if agent.done():
                    print(">>> Route completed")
                    autopilot_active = False
                    continue

                # Your modified BehaviorAgent.run_step(manual_speed_limit=...)
                control = agent.run_step(manual_speed_limit=manual_speed_value)

                if train_mode:
                    manual_speed_value = 50 #kph
                    # TRAIN MODE: BehaviorAgent steers, PID controls throttle/brake
                    throttle_pid, brake_pid, pid_raw = speed_pid.compute_control(
                        current_speed=ego_speed_mps,
                        desired_speed=desired_speed_mps,
                        dt=dt,
                    )

                    # Hard safety override if extremely close to lead vehicle
                    if lead_vehicle is not None and lead_distance is not None and lead_distance <= 5.0:
                        throttle_pid = 0.0
                        brake_pid = 1.0

                    control.throttle = throttle_pid
                    control.brake = brake_pid
                    control.hand_brake = 0
                else:
                    # Not in train mode -> reset PID to avoid stale integral
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
            rect_status7 = status6.get_rect(center=(150, 250))

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
        except Exception as e:
            print(f"Failed to disable autopilot cleanly: {e}")



# -------------------------------------------------------------------------
# Entry point
# -------------------------------------------------------------------------

def main():
    args = parse_args()
    world, carla_map = get_world_and_map(args.host, args.port)
    vehicle = setup_vehicle(world, carla_map, args)
    agent, autopilot_active = setup_agent(vehicle, args)
    run_loop(world, vehicle, agent, autopilot_active, args)


if __name__ == '__main__':
    main()
