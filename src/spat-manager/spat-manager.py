import socket
import json
import binascii
from osys import v2x
from SpatManager import SpatManager


def main():

    configFile = open("/nojournal/bin/anl-master-config.json", 'r')
    config = (json.load(configFile))
    configFile.close()
    
    hostIp = config["HostIp"]
    port = config["PortNumber"]["SpatManager"]
    com_info = (hostIp, port)
    
    spatManagerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    spatManagerSocket.bind(com_info)

    vehicleStatusManagerAddress = (hostIp, config["PortNumber"]["VehicleStatusManager"])
    
    spatManager = SpatManager()

    while True:
        data, address = spatManagerSocket.recvfrom(4096)
        data = data.decode()
        # print("Received data:\n", data)
        receivedMessage = json.loads(data)
        # print("Decoded Json Message is :\n",receivedMessage)
        
        if receivedMessage["MsgType"] == "SignalGroupDataRequest":
            requestedSignalGroupData = spatManager.getRequestedSignalGroupData(receivedMessage)
            print(requestedSignalGroupData)
            spatManagerSocket.sendto(requestedSignalGroupData.encode(), vehicleStatusManagerAddress)

        elif receivedMessage["MsgType"] == "SPaT":
            spatManager.manageSpatData(receivedMessage)

    spatManagerSocket.close()

if __name__ == '__main__':
    main()