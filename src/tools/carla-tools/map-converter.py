import glob
import os
import sys

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

import random
import time



# # Read the .osm data
# f = open("/home/carma/Downloads/map.osm", 'r')
f = open("/home/carma/Downloads/keanery.osm", 'r')
osm_data = f.read()
f.close()

# # Define the desired settings. In this case, default values.
# settings = carla.Osm2OdrSettings()
# # Set OSM road types to export to OpenDRIVE
# settings.set_osm_way_types(["motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link", "secondary", "secondary_link", "tertiary", "tertiary_link", "unclassified", "residential"])
# # enable traffic light generation from OSM data
# settings.generate_traffic_lights = True
# # Convert to .xodr
# xodr_data = carla.Osm2Odr.convert(osm_data, settings)

# Define the desired settings. In this case, default values.
settings = carla.Osm2OdrSettings()
settings.generate_traffic_lights = True
# Convert to .xodr
xodr_data = carla.Osm2Odr.convert(osm_data, settings)

# save opendrive file
# f = open("/home/carma/Downloads/map.xodr", 'w')
f = open("/home/carma/Downloads/keanery.xodr", 'w')
f.write(xodr_data)
f.close()