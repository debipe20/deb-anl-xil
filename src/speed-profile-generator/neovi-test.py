import socket
import json
import time

KPH_TO_MPS = 0.277778
    
def main():
    configFile = open("/nojournal/bin/anl-master-config.json", 'r')
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

    while True:
        
        data, address = speedProfileGeneratorSocket.recvfrom(4096)
        print("Received data\n", data)
        currentSpeed = int.from_bytes(data, byteorder='big') * KPH_TO_MPS
  
        speedJsonString = json.dumps({
            "MsgType": "SpeedData",
            "Speed": currentSpeed
        })
        
        print("Following message will send for : \n", speedJsonString)
        speedProfileGeneratorSocket.sendto(speedJsonString.encode(), clientAddress)
        
        
        time.sleep(0.0997)
    speedProfileGeneratorSocket.close()


if __name__ == '__main__':
    main()
