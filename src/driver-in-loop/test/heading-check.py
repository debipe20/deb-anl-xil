import math
import haversine
def calculate_bearing(lat1, lon1, lat2, lon2):
    print("lat1, lon1:", str(lat1) + ", " + str(lon1) + "\n")
    print("lat2, lon2:", str(lat2) + ", " + str(lon2) + "\n")
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    diff_lon = math.radians(lon2 - lon1)

    x = math.sin(diff_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - \
        math.sin(lat1) * math.cos(lat2) * math.cos(diff_lon)

    bearing = math.atan2(x, y)
    bearing = math.degrees(bearing)
    bearing_to_target = (bearing + 360) % 360
    
    
    return bearing_to_target

def is_ahead_or_behind(my_heading, bearing_to_target):
    angle_diff = (bearing_to_target - my_heading + 360) % 360
    if angle_diff < 90 or angle_diff > 270:
        print("Now GPS point is Ahead\n")
        return "Ahead"
    else:
        return "Behind"

# Actual values
lat1, lon1, my_heading = 41.700842609877725, -87.99178760623737, 344.9915709017801
lat2, lon2 = 41.7008437746154, -87.9917880706466


bearing_to_target = calculate_bearing(lat1, lon1, lat2, lon2)
position = is_ahead_or_behind(my_heading, bearing_to_target)

print(f"Bearing to target: {bearing_to_target:.6f}°")
print(f"Relative to heading: {position}")
distnace_measured = haversine.haversine((lat1, lon1), (lat2, lon2), unit=haversine.Unit.METERS)
print(distnace_measured)
