import socket
import json
import pandas as pd
import haversine
import binascii

import sys
import time
import socket
import argparse
import os
import signal
from pathlib import Path
from osys import v2x

from BsmGenerator import BsmGenerator

def main():
    configFile = open("/nojournal/bin/anl-master-config.json", 'r')
    config = (json.load(configFile))
    configFile.close()

    hostIp = config["HostIp"]
    port = config["PortNumber"]["BsmGenerator"]
    clientIp = config["V2XHubIp"]
    clientPort = config["PortNumber"]["MessageReceiver"]
    com_info = (hostIp, port)
    clientAddress = (clientIp, clientPort)
    
    bsmGeneratorSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    bsmGeneratorSocket.bind(com_info)
    
    # currentSpeed, currentTime = 10.1, time.time()
    bsmGenerator = BsmGenerator(config)
    
    # bsmJsonString =  bsmGenerator.getBsmJsonString(currentSpeed, currentTime)

    while True:
        data, address = bsmGeneratorSocket.recvfrom(2048)
        # print("Received data:", data)
        data = data.decode()
        # print("Decoded data:", data)
        receivedMessage = json.loads(data)
        
        if receivedMessage["MsgType"]=="SpeedData":
            bsmJsonString =  bsmGenerator.getBsmJsonString(receivedMessage["Speed"])
            # print(type(bsmJsonString))
            # bsmJsonString = json.loads(bsmJsonString)
            # print(type(bsmJsonString))
            # print("BSM Json is following:\n", bsmJsonString)
            encodedBsm = v2x.MessageFrame.from_json(bsmJsonString)
            print(type(encodedBsm))
            encodedBsm = binascii.hexlify(encodedBsm)
            print("Encoded BSM is Following:\n", encodedBsm)

            bsmGeneratorSocket.sendto(encodedBsm, clientAddress)
            
    bsmGeneratorSocket.close()

if __name__ == '__main__':
    main()
