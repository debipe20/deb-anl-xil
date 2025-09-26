import socket
import struct
import time

def main():
    # hostIp = "192.168.26.101"
    # hostIp = "127.0.0.1"
    hostIp = "10.0.0.230"
    port = 50001
    # clientIp = "192.168.26.102"
    # clientIp = "127.0.0.1"
    clientIp = "10.0.0.101"
    clientPort = 50002
    com_info = (hostIp, port)
    clientAddress = (clientIp, clientPort)

    msgSenderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msgSenderSocket.bind(com_info)

    counter = 0
    vehicleSpeed = 4.5

    while True:        
        counter += 1
        encodedCounter = struct.pack("d", counter)
        encodedSpeed = struct.pack("d", vehicleSpeed)

        sendingData =  encodedCounter + encodedSpeed
        msgSenderSocket.sendto(sendingData, clientAddress)

        timestamp = str(round(time.time(),4))
        print(("\n[{}]".format(timestamp) + " " + "Message no " + str(counter) + " is sent containing vehicle speed " + str(vehicleSpeed)))
        time.sleep(0.099)
        
    msgSenderSocket.close()

if __name__ == '__main__':
    main()