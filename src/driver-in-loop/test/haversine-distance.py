import haversine
# Start Point
ego_lat, ego_lon = 41.7008249863636,-87.9917813124293
# lead_lat, lead_lon = 41.7008912469787,-87.9918045699135
lead_lat, lead_lon = 41.7009509863219,-87.9918152849739

# #End Point
# ego_lat, ego_lon = 41.7202207899173,-87.9923974646193
# lead_lat, lead_lon = 41.7202433364726,-87.9924725355009

relative_distance = haversine.haversine((lead_lat, lead_lon), (ego_lat, ego_lon), unit=haversine.Unit.METERS)
print(relative_distance)

# start_lat, start_lon = 41.70082498636364,-87.99178131242928
# end_lat, end_lon = 41.72019112326953,-87.99234783922897

# map_length = haversine.haversine((start_lat, start_lon), (end_lat, end_lon), unit=haversine.Unit.METERS)
# print(map_length)
lat1, lon1 = 41.7201378804944, -87.9923287650774
lat2, lon2 = 41.7057974355923, -87.991922442096
distnace_measured = haversine.haversine((lat1, lon1), (lat2, lon2), unit=haversine.Unit.METERS)
print(distnace_measured)

carla_lead_lat, carla_lead_lon = 41.700828, -87.991782
carla_distance = haversine.haversine((lead_lat, lead_lon), (carla_lead_lat, carla_lead_lon), unit=haversine.Unit.METERS)
print(carla_distance)