import glob
import os
import sys
import carla

import random
import time

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

# client = carla.Client('localhost', 2000)
# client.set_timeout(2.0)

# # Once we have a client we can retrieve the world that is currently
# # running.
# world = client.get_world()

# def draw_waypoints(waypoints, road_id=None, life_time=50.0):

#     for waypoint in waypoints:

#         if (waypoint.road_id == road_id):
#             world.debug.draw_string(waypoint.transform.location, 'O', draw_shadow=False,
#                                     color=carla.Color(r=0, g=255, b=0), life_time=life_time,
#                                     persistent_lines=True)

bsmLogFile = open("BSM-Log.csv", 'w')
bsmLogFile.write("Latitude,Longitude,Elevation\n")

def gnss_callback(gnss):
    print("enter in the function")
    print(type(gnss))
    print("GNSS measure:\n"+str(gnss)+'\n')
    # print(gnss.lat)
    # print("type is ", type(gnss))
    line = str(gnss)
    splitByComma=line.split(',')
    # print(splitByComma[2])
    # fValue = splitByComma[2].replace('lat=', '').strip()
    # print(fValue)    
    
    lat = splitByComma[2].replace('lat=', '').strip()
    lon = splitByComma[3].replace('lon=', '').strip()
    elev = splitByComma[4].replace('alt=', '').strip()
    elev = elev.replace(')', '').strip()
    csvRow = (lat + "," + lon + "," + elev + "\n")
    bsmLogFile.write(csvRow)

def main():

    actor_list = []
    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(2.0)

        # Once we have a client we can retrieve the world that is currently
        # running.
        world = client.get_world()

        # The world contains the list blueprints that we can use for adding new
        # actors into the simulation.
        blueprint_library = world.get_blueprint_library()

        # Now let's filter all the blueprints of type 'vehicle' and choose one
        # at random.
        # bp = random.choice(blueprint_library.filter('vehicle'))
        bp = blueprint_library.filter('model3')[0]
        print(bp)
        # spawn_point = random.choice(world.get_map().get_spawn_points())
        # spawn_point = carla.Transform(carla.Location(x=-189.9,y=-508.5, z=38),carla.Rotation(pitch=0.0, yaw=0.0, roll=0.000000))
        spawn_point = carla.Transform(carla.Location(x=-189.172150, y=-509.719635, z=41.869663), carla.Rotation(pitch=1.192223, yaw=-64.276932, roll=0.000000))
        # spawn_point = carla.Transform(carla.Location(x=-195.3, y=-508.5, z=38), carla.Rotation(pitch=0, yaw=0, roll=55))
        print("spawn point is:\n", spawn_point)
        vehicle = world.spawn_actor(bp, spawn_point)
        vehicle.apply_control(carla.VehicleControl(throttle=0.0, steer=0.0))
        actor_list.append(vehicle)
        print(vehicle.get_location())
        
        gnss_bp = world.get_blueprint_library().find('sensor.other.gnss')
        gnss_location = carla.Location(0,0,0)
        gnss_rotation = carla.Rotation(0,0,0)
        gnss_transform = carla.Transform(gnss_location,gnss_rotation)
        # gnss = world.spawn_actor(gnss_bp,gnss_transform,attach_to=vehicle, attachment_type=carla.AttachmentType.Rigid)

        # actor_list.append(gnss)
        ego_gnss = world.spawn_actor(gnss_bp,gnss_transform,attach_to=vehicle, attachment_type=carla.AttachmentType.Rigid)
        # print("GNSS data: ", world.gnss_sensor.latitude)
        ego_gnss.listen(lambda gnss: gnss_callback(gnss))

        
        time.sleep(100)
        # transform = random.choice(world.get_map().get_spawn_points())
        # # So let's tell the world to spawn the vehicle.
        # vehicle = world.spawn_actor(bp, transform)

        # actor_list.append(vehicle)
        # print('created %s' % vehicle.type_id)

        # # to move it a bit forward.
        # location = vehicle.get_location()
        # print("vehicle location: ", location)
        
        # # waypoints = client.get_world().get_map().generate_waypoints(distance=1.0)
        # # # print("WayPoints", waypoints)
        # # draw_waypoints(waypoints, road_id=10, life_time=20)
        
        # spawn_point ="-182.6, -511.5, 38, 0, 0, 18"
        # vehicle = client.get_world().spawn_actor(bp, spawn_point)
        


    finally:
        bsmLogFile.close()
        print('destroying actors')
        for actor in actor_list:
            actor.destroy()


if __name__ == '__main__':

    main()
