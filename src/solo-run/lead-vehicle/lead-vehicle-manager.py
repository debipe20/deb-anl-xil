import socket
import json
import time

def main():
    configFile = open("/nojournal/bin/anl-master-config.json", "r")
    config = json.load(configFile)
    configFile.close()

    hostIp = config["IPAddress"]["HostIp"]
    port = config["PortNumber"]["LeadVehicleDataManager"]
    hostAddress = (hostIp, port)

    leadVehicleDataManagerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    leadVehicleDataManagerSocket.bind(hostAddress)

    while True:
        data, address = leadVehicleDataManagerSocket.recvfrom(1024)

        leadVehicleDataManagerSocket.close()

if __name__ == "__main__":
    main()