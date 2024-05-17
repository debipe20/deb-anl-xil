# Software Component Description: Lead-Vehicle-Manager
The Lead-Vehicle-Manager software component is responsible for generating lead vehicle speed profile.

## Work-flow
The Lead-Vehicle-Manager composed of oneclass- (1) LeadVehicleDataManager. Lead-Vehicle-Manager generates lead vehicle speed and gps coordinates considering intersection traffic signal state information receives from the Dyno-Vehicle-Manager software component.

### Lead Vehicle Data Manager Class
LeadVehicleDataManager has the functionality to generate speed profile for lead vehicle (virtual vehicle) based on vehicle speed and waypoints. It estimates vehicle's next gps coordinates based on vehicle's travel distance. The distance between two waypoints may greater than the actual distance travel by the vehicle. This class has the capability to take that into consideration while estimating vehicle's gps coordinates. It also has the capability to consider SPaT data while generating speed profile.


## Console output and logging
The Dyno-Vehicle-Manager can store lead vehicle BSM (Uper Hex) and display important messages.

## Requirements
- None

## Configuration
In the `anl-master-config.json` (config) file following keys need to be assigned with appropriate values:
- `config["IPAddress"]["HostIp"]`: IP address of the host computer
- `config["PortNumber"][["LeadVehicleDataManager"]]`: UDP port number (integer) of the lead-vehicle-manager software
- `config["PortNumber"]["HostVehicleDataManager"]`:  UDP port number (integer) of the dyno-vehicle-manager software
- `config["VehicleInformation"]["LeadVehicleId"]`: Lead vehicle Id

## Known issues/limitations
- None

