import socket
import json
import struct
import random
import time

def getSpeed(previousSpeed):

    currentSpeed = previousSpeed * (random.randint(80,130)/100)
    
    if(currentSpeed > 8.0):
        currentSpeed = 6.0

            
    return currentSpeed

def main():
    configFile = open("/nojournal/bin/anl-master-config.json", 'r')
    config = (json.load(configFile))
    configFile.close()

    hostIp = config["IPAddress"]["HostIp"]
    # port = config["PortNumber"]["VehicleController"]
    port = 50001
    hostAddress = (hostIp, port)

    clientIp = config["IPAddress"]["HostIp"]
    clinetPort = config["PortNumber"]["LeadVehicleDataManager"]
    clientAddress = (clientIp, clinetPort)
    
    speedDataSenderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    speedDataSenderSocket.bind(hostAddress)
    
    counter = 0.0
    previousSpeed = 1.0
    previousTime = time.time()

    while True:
        currentSpeed = getSpeed(previousSpeed)
        previousSpeed = currentSpeed
        counter = counter + 1.0
        
        encodedCounter = struct.pack("d", counter)
        encodedSpeed = struct.pack("d", currentSpeed)

        sendingData =  encodedCounter + encodedSpeed
        speedDataSenderSocket.sendto(sendingData, clientAddress)
        print("Sent following speed data : ", currentSpeed)
        time.sleep(0.0997)

    speedDataSenderSocket.close()

if __name__ == '__main__':
    main()