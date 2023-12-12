import socket
import json
import time
import binascii
from osys import v2x
from scapy.all import *

OneByTenMicroDegree_To_Degree = 10000000
Deca_Conversion = 10
SECOND_MILISECOND_CONVERSION = 1000

bsmLogFile = open("BSM-Log.csv", 'w')
bsmLogFile.write(
    "timestamp_posix,msgCount,temporaryId,latitude,longitude,elevation,speed,heading,length,width\n")


def bsm_json_to_csv(jsonData):

    timestamp_posix = str(time.time())
    msgCount = str(jsonData["value"]["coreData"]["msgCnt"])
    temporaryId = str(jsonData["value"]["coreData"]["id"])
    latitude = str(jsonData["value"]["coreData"]["lat"] / OneByTenMicroDegree_To_Degree)
    longitude = str(jsonData["value"]["coreData"]["long"] / OneByTenMicroDegree_To_Degree)
    elevation = str(jsonData["value"]["coreData"]["elev"] / Deca_Conversion)
    speed = str(jsonData["value"]["coreData"]["speed"] * 0.2)
    heading = str(jsonData["value"]["coreData"]["heading"] * 0.0125)
    length = str(jsonData["value"]["coreData"]["size"]["length"])
    width = str(jsonData["value"]["coreData"]["size"]["width"])

    csvRow = (timestamp_posix + ","
              + msgCount + ","
              + temporaryId + ","
              + latitude + ","
              + longitude + ","
              + elevation + ","
              + speed + ","
              + heading + ","
              + length + ","
              + width + "\n")

    bsmLogFile.write(csvRow)


def main():
    configFile = open("/nojournal/bin/anl-master-config.json", 'r')
    config = (json.load(configFile))
    configFile.close()

    hostIp = config["HostIp"]
    port = config["PortNumber"]["MessageDecoder"]
    com_info = (hostIp, port)

    msgDecoderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msgDecoderSocket.bind(com_info)

    pcapFilename = '/home/carma/Downloads/constant-drive-trace/const_speed_msg_fwd.pcap'

    pcapPackets = rdpcap(pcapFilename)

    for pkt in pcapPackets:
        packet = raw(pkt)
        print(packet)
        hexPacket = binascii.hexlify(packet)
        packetString = str(hexPacket, encoding='utf-8')
        bsmIdentifier = packetString.find('0014')
        bsmPayload = packetString[bsmIdentifier:]
        print("payload is:\n", bsmPayload)

        bsmBytes = binascii.unhexlify(bsmPayload)
        receivedJsonString = v2x.MessageFrame.to_json(bsmBytes, len(bsmBytes))
        receivedJsonString = json.loads(receivedJsonString)
        
        bsm_json_to_csv(receivedJsonString)


if __name__ == '__main__':
    main()
