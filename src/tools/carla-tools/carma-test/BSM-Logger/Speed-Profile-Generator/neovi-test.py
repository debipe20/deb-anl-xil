import socket
import json
import time


    
def main():
    configFile = open("../anl-master-config.json", 'r')
    config = (json.load(configFile))
    configFile.close()

    hostIp = config["HostIp"]
    port = config["PortNumber"]["SpeedProfileGenerator"]
    clientIp = config["HostIp"]
    clientPort = config["PortNumber"]["BsmGenerator"]
    com_info = (hostIp, port)
    
    speedProfileGeneratorSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    speedProfileGeneratorSocket.bind(com_info)

    clientAddress = (clientIp, clientPort)
    
    previousSpeed = 6.0
    previousTime = time.time()
    count = 0
    while True:
        
        data, address = speedProfileGeneratorSocket.recvfrom(4096)
        print("Received data\n", data)
        currentSpeed = int.from_bytes(data, byteorder='big')
        count= count +1
        if count == 100:
            count = 1
        speedJsonString = json.dumps({
            "MsgType": "SpeedData",
            "Speed": currentSpeed
        })
        
        print("Following message will send for : \n",count, speedJsonString)
        speedProfileGeneratorSocket.sendto(speedJsonString.encode(), clientAddress)
        
        
        time.sleep(0.0997)
    speedProfileGeneratorSocket.close()


if __name__ == '__main__':
    main()
