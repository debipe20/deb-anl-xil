import socket
import signal, sys
from binascii import unhexlify, hexlify
from time import sleep

hostIP = "192.168.26.101"
port = 60001
com_info =(hostIP,port)
payloadSenderSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
payloadSenderSocket.bind(com_info)
clientAddress = ("192.168.26.100",26789)
payLoadLogFile = open("BSM-Payload.log", 'r')

payload = "001425007C0EB5840019266E8AE61EA6BC0D928CFFFFFFFFF00012B6FDFA1FA1007FFF8000962580"

unhexed = unhexlify(payload)

while(True):
    for line in payLoadLogFile:
        payload = line.strip()
        print(payload)
        unhexed = unhexlify(payload)
        print("Unhexed Message is following:\n", unhexed)
        payloadSenderSocket.sendto(unhexed,clientAddress)
        sleep(0.1)
    
payloadSenderSocket.close()