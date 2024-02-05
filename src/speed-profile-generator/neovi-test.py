import socket
import json
import time
import struct

KPH_TO_MPS = 0.277778
    
def main():
    configFile = open("/nojournal/bin/anl-master-config.json", 'r')
    config = (json.load(configFile))
    configFile.close()

    # hostIp = config["IPAddress"]["HostIp"]
    hostIp = "169.254.137.176"
    # hostIp = "172.16.200.101"
    # port = config["PortNumber"]["SpeedProfileGenerator"]
    port = 50002
    clientIp = config["IPAddress"]["HostIp"]
    clientPort = config["PortNumber"]["BsmGenerator"]
    com_info = (hostIp, port)
    
    speedProfileGeneratorSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    speedProfileGeneratorSocket.bind(com_info)

    clientAddress = (clientIp, clientPort)
    
    previousSpeed = 6.0
    previousTime = time.time()

    logFile = open("bytes2.txt", 'w')

    while True:
        
        data, address = speedProfileGeneratorSocket.recvfrom(4096)
        print("Received data\n", data)
        logFile.write(str(data) + "\n")
        # val = data.decode()
        # print("decoded value: ", float(val))

        # byte_array = [data]
        # binary_string = b''.join(byte_array)
        # currentSpeed = struct.unpack('<d', binary_string)[0]
        # currentSpeed = struct.unpack('d', data)
        # print(currentSpeed)
        # currentSpeed = int.from_bytes(data, byteorder='big')
        currentSpeed = int.from_bytes(data, byteorder='big') * KPH_TO_MPS
  
        speedJsonString = json.dumps({
            "MsgType": "SpeedData",
            "Speed": currentSpeed
        })
        
        print("Following message will send for : \n", speedJsonString)
        # speedProfileGeneratorSocket.sendto(speedJsonString.encode(), clientAddress)
        
        
        time.sleep(0.0997)
    speedProfileGeneratorSocket.close()
    logFile.close()


if __name__ == '__main__':
    main()
