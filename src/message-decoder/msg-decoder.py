import socket
import json
import binascii
from osys import v2x

def getMessageType(jsonString):
    messageType = ""

    if(jsonString["messageId"]) == 18:
        messageType = "MAP"

    elif (jsonString["messageId"]) == 19:
        messageType = "SPaT"

    elif(jsonString["messageId"]) == 20:
        messageType = "BSM"    

    return messageType

def main():
    configFile = open("/nojournal/bin/anl-master-config.json", 'r')
    config = (json.load(configFile))
    configFile.close()
    
    hostIp = config["HostIp"]
    port = config["PortNumber"]["MessageDecoder"]
    com_info = (hostIp, port)
    
    msgDecoderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msgDecoderSocket.bind(com_info)
    

    while True:
        data, address = msgDecoderSocket.recvfrom(1024)
        data = binascii.unhexlify(data)
        receivedJsonString = v2x.MessageFrame.to_json(data,len(data))
        receivedJsonString = json.loads(receivedJsonString)
        print(receivedJsonString)
    
    msgDecoderSocket.close()
if __name__ == '__main__':
    main()