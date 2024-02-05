import socket
import json

def main():
    configFile = open("/nojournal/bin/anl-master-config.json", 'r')
    config = (json.load(configFile))
    configFile.close()

    hostIp = config["IPAddress"]["HostIp"]
    port = config["PortNumber"]["LeadVehicleDataManager"]
    clientIp = config["IPAddress"]["VehicleControllerIp"]
    clientPort = config["PortNumber"]["VehicleController"]
    com_info = (hostIp, port)
    clientAddress = (clientIp, clientPort)
    
    leadVehicleDataManagerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    leadVehicleDataManagerSocket.bind(com_info)

    while True:
        data, address = leadVehicleDataManagerSocket.recvfrom(2048)
        print("Received data:", data)

    leadVehicleDataManagerSocket.close()

if __name__ == '__main__':
    main()