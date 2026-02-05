import glob
import os
import sys



import random
import time

carla_egg_path = os.environ.get("CARLA_EGG_PATH")

try:
    sys.path.append(glob.glob(carla_egg_path + '/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass


import carla

def main():
    actor_list = []
    
    try:
        # First of all, we need to create the client that will send the requests
        # requests in the localhost at port 2000.
        client = carla.Client('localhost', 2000)
        client.set_timeout(2.0)
        
        # Once we have a client we can retrieve the world that is currently running.
        world = client.get_world()
        
        # light_manager = world.get_lightmanager()
        # lights = light_manager.get_all_lights()
        # for light in lights:
        #     position = light.location
        #     print(position)
        
        # tmp_map = world.get_map()
        # for landmark in tmp_map.get_all_landmarks_of_type('1000001'):
        #     traffic_light = world.get_traffic_light(landmark)
        #     print(traffic_light)
        
        # The world contains the list blueprints that we can use for adding new actors into the simulation.
        blueprint_library = world.get_blueprint_library()

        # Now let's filter all the blueprints of type 'vehicle' and choose one at random.
        bp = random.choice(blueprint_library.filter('vehicle'))
        
        if bp.has_attribute('color'):
            color = random.choice(bp.get_attribute('color').recommended_values)
            bp.set_attribute('color', color)
            
        #Spwan vehicle    
        # transform = random.choice(world.get_map().get_spawn_points())
        # print("spawn point is:\n", transform)
        # vehicle = world.spawn_actor(bp, transform)
        
        # spawn_point = carla.Transform(carla.Location(x=-189.172150, y=-509.719635, z=41.869663), carla.Rotation(pitch=1.192223, yaw=-64.276932, roll=0.000000))
        spawn_point = carla.Transform(carla.Location(x=24.0, y=1070, z=231.780380), carla.Rotation(pitch=0, yaw=-105, roll=0))
        print("spawn point is:\n", spawn_point)
        vehicle = world.spawn_actor(bp, spawn_point)
        
        actor_list.append(vehicle)
        print('created %s' % vehicle.type_id)

        # Let's put the vehicle to drive around.
        vehicle.set_autopilot(True)
        
        time.sleep(10)
        
    
    finally:

        print('destroying actors')

        # camera.destroy()
        # client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
        print('done.')
    
if __name__ == '__main__':

    main()