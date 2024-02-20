import random
import socket
import json
import time

# speedProfileLogFile = open("Speed-Profile-Log.csv", 'w')
# speedProfileLogFile.write("TimeStamp,TimeStep,Speed\n")

def getSpeed(previousSpeed):

    currentSpeed = previousSpeed * (random.randint(80,130)/100)
    
    if(currentSpeed > 8.0):
        currentSpeed = 6.0

    # currentSpeed = 3.0
            
    return currentSpeed
    
def main():
    configFile = open("/nojournal/bin/anl-master-config.json", 'r')
    config = (json.load(configFile))
    configFile.close()

    hostIp = config["IPAddress"]["HostIp"]
    port = config["PortNumber"]["SpeedProfileGenerator"]
    clientIp = config["IPAddress"]["HostIp"]
    clientPort = config["PortNumber"]["BsmGenerator"]
    com_info = (hostIp, port)
    
    speedProfileGeneratorSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    speedProfileGeneratorSocket.bind(com_info)

    clientAddress = (clientIp, clientPort)
    
    previousSpeed = 1.0
    previousTime = time.time()

    while True:
        currentSpeed = getSpeed(previousSpeed)
        previousSpeed = currentSpeed
    
        speedJsonString = json.dumps({
            "MsgType": "SpeedData",
            "Speed": currentSpeed
        })
        
        print("Following message will send:\n", speedJsonString)
        speedProfileGeneratorSocket.sendto(speedJsonString.encode(), clientAddress)
        
        # currentTime = time.time()
        # timeStep = currentTime - previousTime
        # previousTime = currentTime
        
        # csvRow = (str(currentTime) + "," + str(timeStep) + "," + str(currentSpeed) + "\n")
        # speedProfileLogFile.write(csvRow)
        
        time.sleep(0.0997)
    speedProfileGeneratorSocket.close()
    # speedProfileLogFile.close()


if __name__ == '__main__':
    main()
