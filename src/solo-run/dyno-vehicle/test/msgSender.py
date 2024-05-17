import socket
import json
import struct



def main():
    configFile = open("../../../../config/anl-master-config.json", 'r')
    config = (json.load(configFile))
    configFile.close()

    hostIp = config["IPAddress"]["HostIp"]
    port = config["PortNumber"]["VehicleController"]
    hostAddress = (hostIp, port)

    clientIp = config["IPAddress"]["HostIp"]
    clientPort = config["PortNumber"]["HostVehicleDataManager"]
    clientAddress = (clientIp, clientPort)
    
    msgSenderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msgSenderSocket.bind(hostAddress)
    

    while True:
        data, address = msgSenderSocket.recvfrom(2048)
        decodedDistance, decodedSpeed, decodedCounter, decodedSpeedOriginal  = struct.unpack("dddd", data)

        print("Received data is following:\n Relative Distance, Relative Speed, Speed \n", decodedDistance, decodedSpeed,  decodedSpeedOriginal)

        encodedCounter = struct.pack("d", decodedCounter)
        encodedSpeed = struct.pack("d", decodedSpeedOriginal)

        sendingData =  encodedCounter + encodedSpeed
        msgSenderSocket.sendto(sendingData, clientAddress)

    msgSenderSocket.close()

if __name__ == '__main__':
    main()