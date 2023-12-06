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
lattitude = 0.0
lon = 0.0
elev = 0.0
heading  = 0.0

def setData(lat1, lon1, elev1):

    lat = lat1
    lon = lon1
    elev = elev1


def gnss_callback(gnss):
    print("GNSS measure:\n"+str(gnss)+'\n')

    gnssData = str(gnss)
    splitGnssDataByComma = gnssData.split(',')
    
    lat = splitGnssDataByComma[2].replace('lat=', '').strip()
    lon = splitGnssDataByComma[3].replace('lon=', '').strip()
    elev = splitGnssDataByComma[4].replace('alt=', '').strip(')')
    lattitude = lat
    # elev = elev.replace(')', '').strip()
   
    print("Elevation is ", str(elev))

    # csvRow = (lat + "," + lon + "," + elev + "\n")
    # bsmLogFile.write(csvRow)
    setData(str(lat), str(lon), str(elev)) 

def imu_callback(imu):
    print("IMU measure:\n"+str(imu)+'\n')

    imuData = str(imu)
    splitImuDataByComma = imuData.split(',')

    heading = splitImuDataByComma[8].replace('compass=', '').strip(')')
    # print("Heading is", heading)
    print("Lattitude is ", lattitude)
    print("elevation is ", str(elev))
    csvRow = (str(lattitude) + "," + str(lon) + "," + str(elev) + "," + str(heading) + "\n")
    bsmLogFile.write(csvRow)
    # return str(heading)  

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
        gnss_bp.set_attribute("sensor_tick",str(0.1))
        ego_gnss = world.spawn_actor(gnss_bp,gnss_transform,attach_to=vehicle, attachment_type=carla.AttachmentType.Rigid)
        ego_gnss.listen(lambda gnss: gnss_callback(gnss))


        imu_bp = world.get_blueprint_library().find('sensor.other.imu')
        imu_location = carla.Location(0,0,0)
        imu_rotation = carla.Rotation(0,0,0)
        imu_transform = carla.Transform(imu_location,imu_rotation)
        imu_bp.set_attribute("sensor_tick",str(0.1))
        ego_imu = world.spawn_actor(imu_bp,imu_transform,attach_to=vehicle, attachment_type=carla.AttachmentType.Rigid)
        ego_imu.listen(lambda imu: imu_callback(imu))

        # csvRow = (str(lattitude) + "," + str(longitude) + "," + str(elevation) + "," + str(heading) + "\n")
        # bsmLogFile.write(csvRow)
        
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
