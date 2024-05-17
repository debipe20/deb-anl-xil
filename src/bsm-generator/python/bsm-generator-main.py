import socket
import json
# import pandas as pdgit 
import binascii
import sys
import argparse
import os
import signal
import struct
from pathlib import Path
from osys import v2x
import time
from BsmGenerator import BsmGenerator

def main():
    configFile = open("/nojournal/bin/anl-master-config.json", 'r')
    config = (json.load(configFile))
    configFile.close()

    hostIp = config["IPAddress"]["HostIp"]
    port = config["PortNumber"]["BsmGenerator"]
    clientIp = config["IPAddress"]["V2XHubIp"]
    clientPort = config["PortNumber"]["MessageReceiver"]
    com_info = (hostIp, port)
    clientAddress = (clientIp, clientPort)
    
    bsmGeneratorSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    bsmGeneratorSocket.bind(com_info)
    
    # currentSpeed, currentTime = 10.1, time.time()
    bsmGenerator = BsmGenerator(config)

    # bsmJsonString =  bsmGenerator.getBsmJsonString(currentSpeed, currentTime)
    receivingTime = time.time()
    counter =  0
    while True:
        data, address = bsmGeneratorSocket.recvfrom(2048)
        # # print("Received data:", data)
        # data = data.decode()
        # # print("Decoded data:", data)
        # receivedMessage = json.loads(data)
        
        # if receivedMessage["MsgType"]=="SpeedData":
        #     bsmJsonString =  bsmGenerator.getBsmJsonString(receivedMessage["Speed"])


        #     encodedBsm = v2x.MessageFrame.from_json(bsmJsonString)

        #     print("Encoded BSM is Following:\n", encodedBsm)

        #     bsmGeneratorSocket.sendto(encodedBsm, clientAddress)
        counter = counter + 1
        
        if counter == 10:
            timeGap = time.time() - receivingTime
            receivingTime = time.time()
            counter = 0
            decodedCounter, decodedSpeed = struct.unpack("dd", data) 
            print("Received speed data at timeGap: ", timeGap, " ", decodedSpeed)
            bsmJsonString =  bsmGenerator.getBsmJsonString(decodedSpeed*0.277778)
            encodedBsm = v2x.MessageFrame.from_json(bsmJsonString)
            print("Encoded BSM is Following:\n", encodedBsm)
            bsmGeneratorSocket.sendto(encodedBsm, clientAddress)
        
        else: continue
            

    bsmGeneratorSocket.close()
    
if __name__ == '__main__':
    main()
