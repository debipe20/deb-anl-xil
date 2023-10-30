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
        data, address = spatManagerSocket.recvfrom(2048)
        data = data.decode()
        receivedMessage = json.loads(data)
        print("Decoded Json Message is :\n",receivedMessage)
        if receivedMessage["MsgType"] == "SignalGroupDataRequest":
            requestedSignalGroupData = spatManager.getRequestedSignalGroupData()
            spatManagerSocket.sendto(requestedSignalGroupData.encode(), vehicleStatusManagerAddress)
        
        #  ''' if msg-decoder is run using mmitss'''

        elif receivedMessage["MsgType"] == "SPaT":
            spatManager.manageSpatData(receivedMessage)
        
        #''' if msg-decoder is run using objective-systems'''
        # elif receivedMessage["MsgType"] == "SPaT":
        #     spatPayload = receivedMessage["SpatPayload"]
        #     print("Received Payload is", spatPayload)
        #     spatBytes = binascii.unhexlify(spatPayload)
        #     receivedJsonString = v2x.MessageFrame.to_json(spatBytes, len(spatBytes))
        #     receivedJsonString = json.loads(receivedJsonString)

        #     spatManager.manageSpatData(receivedJsonString)



    spatManagerSocket.close()

if __name__ == '__main__':
    main()