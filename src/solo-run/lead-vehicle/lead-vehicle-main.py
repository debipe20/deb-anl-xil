import socket
import json
import time
import struct
from LeadVehicleDataManager import LeadVehicleDataManager

def main():
    configFile = open("/nojournal/bin/anl-master-config.json", "r")
    config = json.load(configFile)
    configFile.close()

    hostIp = config["IPAddress"]["HostIp"]
    port = config["PortNumber"]["LeadVehicleDataManager"]
    leadVehicleDataManagerAddress = (hostIp, port)
    
    hostVehicleDataManagerPort = config["PortNumber"]["HostVehicleDataManager"]
    hostVehicleDataManagerAddress = (hostIp, hostVehicleDataManagerPort)

    leadVehicleDataManagerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    leadVehicleDataManagerSocket.bind(leadVehicleDataManagerAddress)
    leadVehicleDataManagerSocket.settimeout(0)
    
    leadVehicleDataManager = LeadVehicleDataManager(config)
    
    timeGap = 0.1
    dataSentTime = time.time()

    while True:
        try:
            data, address = leadVehicleDataManagerSocket.recvfrom(1024)
            decodedTrafficSignalState = struct.unpack("i", data)[0]
            print("Received traffic signal state is :", decodedTrafficSignalState)
            leadVehicleDataManager.setTrafficSignalState(decodedTrafficSignalState)
            
        except:
            timeGap = time.time() - dataSentTime
            if timeGap >= 0.1:
                leadVehicleLat, leadVehicleLon, leadVehicleSpeed = leadVehicleDataManager.getLeadVehicleInformation()
                sendingData = struct.pack("ddd", leadVehicleLat, leadVehicleLon, leadVehicleSpeed)
                dataSentTime = time.time()
                
                leadVehicleDataManagerSocket.sendto(sendingData, hostVehicleDataManagerAddress)
                time.sleep(0.0998)
                
        
    leadVehicleDataManagerSocket.close()

if __name__ == "__main__":
    main()