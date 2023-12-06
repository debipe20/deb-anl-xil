
import glob
import os
import sys
import carla

import random
import time





class GpsCollector:
    def __init__(self):
        self.currentLatitude = 0.0
        self.currentLongitude = 0.0
        self.currentElevation = 0.0
        self.currentSpeed = 0.0
        self.currentHeading = 0.0
        self.bsmLogFile = open("BSM-Log.csv", 'w')
        self.bsmLogFile.write("Latitude,Longitude,Elevation,Heading\n")

    def gnss_callback(self, gnss):
        print("GNSS measure:\n"+str(gnss)+'\n')

        gnssData = str(gnss)
        splitGnssDataByComma = gnssData.split(',')
        
        self.currentLatitude = splitGnssDataByComma[2].replace('lat=', '').strip()
        self.currentLongitude = splitGnssDataByComma[3].replace('lon=', '').strip()
        self.currentElevation = splitGnssDataByComma[4].replace('alt=', '').strip(')')


    def imu_callback(self, imu):
        print("IMU measure:\n"+str(imu)+'\n')

        imuData = str(imu)
        splitImuDataByComma = imuData.split(',')

        self.currentHeading = splitImuDataByComma[8].replace('compass=', '').strip(')')

        csvRow = (str(self.currentLatitude) + "," + str(self.currentLongitude) + "," + str(self.currentElevation) + "," + str(self.currentHeading) + "\n")
        self.bsmLogFile.write(csvRow)

    def runTest(self):

        actor_list = []
        try:
            client = carla.Client('localhost', 2000)
            client.set_timeout(2.0)

            # Once we have a client we can retrieve the world that is currently running.
            world = client.get_world()

            # The world contains the list blueprints that we can use for adding new actors into the simulation.
            blueprint_library = world.get_blueprint_library()

            # Now let's filter all the blueprints of type 'vehicle' and choose one at random.
            bp = blueprint_library.filter('model3')[0]

            spawn_point = carla.Transform(carla.Location(x=-189.172150, y=-509.719635, z=41.869663), carla.Rotation(pitch=1.192223, yaw=-64.276932, roll=0.000000))
            # spawn_point = carla.Transform(carla.Location(x=-195.3, y=-508.5, z=38), carla.Rotation(pitch=0, yaw=0, roll=55))

            vehicle = world.spawn_actor(bp, spawn_point)
            vehicle.apply_control(carla.VehicleControl(throttle=0.0, steer=0.0))
            actor_list.append(vehicle)
            print(vehicle.get_location())
            print(vehicle.get_velocity())
        
            gnss_bp = world.get_blueprint_library().find('sensor.other.gnss')
            gnss_location = carla.Location(0,0,0)
            gnss_rotation = carla.Rotation(0,0,0)
            gnss_transform = carla.Transform(gnss_location,gnss_rotation)
            gnss_bp.set_attribute("sensor_tick",str(0.1))
            ego_gnss = world.spawn_actor(gnss_bp,gnss_transform,attach_to=vehicle, attachment_type=carla.AttachmentType.Rigid)
            # ego_gnss.listen(lambda gnss: self.gnss_callback(gnss))

            imu_bp = world.get_blueprint_library().find('sensor.other.imu')
            imu_location = carla.Location(0,0,0)
            imu_rotation = carla.Rotation(0,0,0)
            imu_transform = carla.Transform(imu_location,imu_rotation)
            imu_bp.set_attribute("sensor_tick",str(0.1))
            ego_imu = world.spawn_actor(imu_bp,imu_transform,attach_to=vehicle, attachment_type=carla.AttachmentType.Rigid)
            # ego_imu.listen(lambda imu: self.imu_callback(imu))
            
            # csvRow = (str(self.currentLatitude) + "," + str(self.currentLongitude) + "," + str(self.currentElevation) + "," + str(self.currentHeading) + "\n")
            # self.bsmLogFile.write(csvRow)            
            time.sleep(100)

        finally:
            self.bsmLogFile.close()
            print('destroying actors')
            for actor in actor_list:
                actor.destroy()


if __name__ == "__main__":
    try:
        sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
            sys.version_info.major,
            sys.version_info.minor,
            'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
    except IndexError:
        pass
    
    gpsCollector = GpsCollector()
    gpsCollector.runTest()
    