import socket
import json
import struct

KPH_TO_MPS = 0.35
MPH_TO_MPS = 0.44704

def main():
    configFile = open("/nojournal/bin/anl-master-config.json", 'r')
    config = (json.load(configFile))
    configFile.close()

    hostIp = config["IPAddress"]["HostIp"]
    port = config["PortNumber"]["VehicleController"]
    hostAddress = (hostIp, port)

    clientIp = config["IPAddress"]["HostIp"]
    clinetPort = config["PortNumber"]["HostVehicleDataManager"]
    clientAddress = (clientIp, clinetPort)
    
    msgSenderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msgSenderSocket.bind(hostAddress)
    

    while True:
        data, address = msgSenderSocket.recvfrom(2048)
        relativeDistance, relativeSpeed, counter, leadVehicleSpeed  = struct.unpack("dddd", data)

        print("Received data is following:\n Relative Distance, Relative Speed, Speed \n", relativeDistance, relativeSpeed, leadVehicleSpeed)

        if relativeDistance <= 10.0:
            leadVehicleSpeed = 0.0
        
        # else: leadVehicleSpeed = leadVehicleSpeed * KPH_TO_MPS
        
        leadVehicleSpeed = leadVehicleSpeed * MPH_TO_MPS
            
        encodedCounter = struct.pack("d", counter)
        encodedSpeed = struct.pack("d", leadVehicleSpeed)

        sendingData =  encodedCounter + encodedSpeed
        msgSenderSocket.sendto(sendingData, clientAddress)

    msgSenderSocket.close()

if __name__ == '__main__':
    main()