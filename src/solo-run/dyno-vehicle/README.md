# Software Component Description: Dyno-Vehicle-Manager
The Dyno-Vehicle-Manager software component is responsible for managing ego vehicle data, host vehicle data, and SPaT data receive from vehicle controller, Lead Vehicle Data Manager, and VOICES J2735 Adapter, respectively.

## Work-flow
The Dyno-Vehicle-Manager composed of two class- (1) BSMGenerator (2) SpaTManager. Dyno-Vehicle-Manager is an API to manage instance of both of these two class. It receives ego vehicle's speed from Vehicle Controller in real-time and forwards to the BSMGenerator to generate BSM. It also receives lead vehicle information from Lead-Vehicle-Data-Manager software. Based on ego and lead vehicle information it estimates relative distance and relative speed between two vehicles and forwards the information to the vehicle controller. It manages messages received from VOICES J2735 adapter and forwards them to SPaTManager to obtain signal timing and phase information of desired intersection. It forwards signal phase infromation to the Lead-Vehicle-Data-Manager component.

### BSMGenerator Class
BSMGenerator has the functionality to generate BSMs for ego vehicle (dyno vehicle) based on vehicle speed and waypoints. It estimates vehicle's next gps coordinates based on vehicle's travel distance and creates J2735 formatted BSM json string using Objective Systems API. The distance between two waypoints may greater than the actual distance travel by the vehicle. This class has the capability to take that into consideration while estimating vehicle's gps coordinates.

### SPaTManager Class
SPaTanager has the functionality to decode J2735 SPaT messages using Objective Systems API and obtain required information. It can match intersection id of the decoded SPaT's with desired intersection id and discard other V2X messages and non-standard messages coming through the VOICES J2735 adapter. It finds desired signal group information to forward to the Lead-Vehicle-Data-Manager component.


## Console output and logging
The Dyno-Vehicle-Manager can store important information like- ego and lead vehicle speed, gps coordinates, BSM (Uper Hex), etc. and display important messages.

## Requirements
- None

## Configuration
In the `anl-master-config.json` (config) file following keys need to be assigned with appropriate values:
- `config["IPAddress"]["HostIp"]`: IP address of the host computer
- `config["IPAddress"]["VehicleControllerIp"]`: IP address of the vehicle controller
- `config["IPAddress"]["V2XHubIp"]`: IP address of the vehicle controller
- `config["PortNumber"]["HostVehicleDataManager"]`:  UDP port number (integer) of the dyno-vehicle-manager software
- `config["PortNumber"]["VehicleController"]`: UDP port number (integer) of the vehicle controller
- `config["PortNumber"][["LeadVehicleDataManager"]]`: UDP port number (integer) of the lead-vehicle-manager software
- `config["PortNumber"]["MessageReceiver"]`: UDP port number (integer) of the V2X-Hub MessageReceiver component
- `config["SignalControllerInformation"]["DesiredSignalGroup"]`: Signal Group
- `config["SignalControllerInformation"]["IntersectionId"]`: Intersection Id

## Known issues/limitations
- None

