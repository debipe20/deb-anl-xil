import socket
import struct
import time

def main():
    # hostIp = "192.168.26.102"
    hostIp = "127.0.0.1"
    port = 50002
    com_info = (hostIp, port)

    msgReceiverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msgReceiverSocket.bind(com_info)

    while True:
        data, address = msgReceiverSocket.recvfrom(1024)
        counter, vehicleSpeed = struct.unpack("dd", data) 

        timestamp = str(round(time.time(),4))
        print(("\n[{}]".format(timestamp) + " " + "Message no " + str(counter) + " is received containing vehicle speed " + str(vehicleSpeed)))
        
    msgReceiverSocket.close()

if __name__ == '__main__':
    main()