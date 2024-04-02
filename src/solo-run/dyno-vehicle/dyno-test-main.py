import socket
import json
import binascii
import struct
import haversine
import time,datetime
from osys import v2x
from BsmGenerator import BsmGenerator
from SpatManager import SpatManager

SpeedDataLength = 16
LEAD_VEHICLE_DATA_LENGTH = 24
initializationTimestamp = ('{:%m%d%Y_%H%M%S}'.format(datetime.datetime.now()))

hostVehicleLogFile = open("/nojournal/bin/log/solo-run/host_vehicle_log_" + initializationTimestamp + ".csv", "w")
leadVehicleLogFile = open("/nojournal/bin/log/solo-run/lead_vehicle_log_" + initializationTimestamp + ".csv", "w")
bsmLog = open("/nojournal/bin/log/solo-run/bsm_hex_log_" + initializationTimestamp + ".log","w")

hostHeader = ("TimeStamp, Counter, HostVehicleSpeed\n")
leadHeader = ("TimeStamp, Counter, RelativeDistance, RelativeSpeed, LeadVehicleSpeed, HostVehicleSpeed\n")

hostVehicleLogFile.write(hostHeader)
leadVehicleLogFile.write(leadHeader)

def logLeadVehicleData(counter, relativeDistance, relativeSpeed, leadVehicleSpeed, hostVehicleSpeed):
    csvrow = (
            str(round(time.time(), 4)) + ","
            + str(round(counter, 0))  + ","
            + str(round(relativeDistance, 3)) + ","
            + str(round(relativeSpeed, 2)) + ","
            + str(round(leadVehicleSpeed, 2)) + ","
            + str(round(hostVehicleSpeed, 2)) + "\n")
    leadVehicleLogFile.write(csvrow)
    
def logHostVehicleData(counter, decodedSpeed):
    csvrow = (str(round(time.time(), 4)) + "," 
            + str(round(counter, 0)) + "," 
            + str(round(decodedSpeed, 2)) + "\n")
    hostVehicleLogFile.write(csvrow)

def getSafeDynoOperationData(counter, relativeDistance):
    
    relativeDistance = relativeDistance - 5.0
    relativeSpeed, leadVehicleSpeed = 0.0, 0.0
    counter = counter + 1.0        
    
    return relativeDistance, relativeSpeed, counter, leadVehicleSpeed


def getMessageType(string):
    messageType = ""

    if (string[:4]) == "0012":
        messageType = "MAP"

    elif (string[:4]) == "0013":
        messageType = "SPaT"

    elif (string[:4]) == "0014":
        messageType = "BSM"
        
    else: messageType = "Unknown"

    return messageType

def main():
    configFile = open("/nojournal/bin/anl-master-config.json", "r")
    config = json.load(configFile)
    configFile.close()

    hostIp = config["IPAddress"]["HostIp"]
    port = config["PortNumber"]["HostVehicleDataManager"]
    hostAddress = (hostIp, port)

    messageReceiverIp = config["IPAddress"]["V2XHubIp"]
    messageReceiverPort = config["PortNumber"]["MessageReceiver"]
    messageReceiverAddress = (messageReceiverIp, messageReceiverPort)

    vehicleControllerIp = config["IPAddress"]["VehicleControllerIp"]
    # vehicleControllerIp = config["IPAddress"]["HostIp"]
    vehicleControllerPort = config["PortNumber"]["VehicleController"]
    vehicleControllerAddress = (vehicleControllerIp, vehicleControllerPort)
    
    leadVehicleDataManagerPort = config["PortNumber"]["LeadVehicleDataManager"]
    leadVehicleDataManagerAddress = (hostIp, leadVehicleDataManagerPort)

    hostVehicleDataManagerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hostVehicleDataManagerSocket.bind(hostAddress)

    bsmGenerator = BsmGenerator(config)
    spatManager = SpatManager(config)

    hostVehicleLat, hostVehicleLon, hostVehicleSpeed = 42.3025391192385, -83.69779345760013, 0.0
    leadVehicleLat, leadVehicleLon, leadVehicleSpeed = 42.30245402283134, -83.69784540965374, 0.0
    relativeDistance, relativeSpeed, counter = 10.0, 0.0, 0.0
    leadVehicleDataReceivedTime = time.time()

    while True:
        data, address = hostVehicleDataManagerSocket.recvfrom(2048)
        # print("Received data is following:\n", data)

        dataLength = len(data)

        if dataLength == SpeedDataLength:
            decodedCounter, decodedSpeed = struct.unpack("dd", data)            
            hostVehicleLat, hostVehicleLon, hostVehicleSpeed, bsmJsonString = (bsmGenerator.getBsmJsonString(decodedSpeed))
            
            encodedBsm = v2x.MessageFrame.from_json(bsmJsonString)
            # print("Encoded Bsm is: \n ", encodedBsm)
            hostVehicleDataManagerSocket.sendto(encodedBsm, messageReceiverAddress)
            
            bsmHex = binascii.hexlify(encodedBsm)
            bsmLog.write(str(bsmHex) + "\n")
            logHostVehicleData(decodedCounter, decodedSpeed)
            print("Decoded data is: ", decodedSpeed, " and counter is: ", decodedCounter)
            
            if time.time() - leadVehicleDataReceivedTime > 1.0:
                while relativeDistance > 10:
                    relativeDistance, relativeSpeed, counter, leadVehicleSpeed = getSafeDynoOperationData(counter, relativeDistance)
                    sendingData =  struct.pack("dddd", relativeDistance, relativeSpeed, counter, leadVehicleSpeed)

                    hostVehicleDataManagerSocket.sendto(sendingData, vehicleControllerAddress)
                    
                    # logLeadVehicleData(counter, relativeDistance, relativeSpeed, leadVehicleSpeed, hostVehicleSpeed)
                    print("Sending relative distance & speed, counter, and lead and host vehicle speed for safe operation: ", relativeDistance, relativeSpeed, counter, leadVehicleSpeed, hostVehicleSpeed)

        elif dataLength == LEAD_VEHICLE_DATA_LENGTH:
            leadVehicleLat, leadVehicleLon, leadVehicleSpeed = struct.unpack("ddd", data)
            print("Received lead vehicle data is following: \n", leadVehicleLat, leadVehicleLon, leadVehicleSpeed)
            relativeDistance = haversine.haversine((leadVehicleLat, leadVehicleLon), (hostVehicleLat, hostVehicleLon), unit=haversine.Unit.METERS)
 
            leadVehicleDataReceivedTime = time.time()
            relativeSpeed = leadVehicleSpeed - hostVehicleSpeed
            counter = counter + 1.0
            sendingData =  struct.pack("dddd", relativeDistance, relativeSpeed, counter, leadVehicleSpeed)
            
            hostVehicleDataManagerSocket.sendto(sendingData, vehicleControllerAddress)
            logLeadVehicleData(counter, relativeDistance, relativeSpeed, leadVehicleSpeed, hostVehicleSpeed)
            print("Sending relative distance & speed, counter, and lead and host vehicle speed: ",
                relativeDistance, relativeSpeed, counter, leadVehicleSpeed, hostVehicleSpeed)

        else:

            hexPacket = binascii.hexlify(data)
            packetString = str(hexPacket, encoding="utf-8")
            msgIdentifier = packetString.find('001')
            payload = packetString[msgIdentifier:].strip()
            msgType = getMessageType(payload)

            if msgType == "SPaT":
                trafficSignalState = spatManager.getDesiredSignalGroupState(payload)
                sendingData =  struct.pack("i", trafficSignalState)
                hostVehicleDataManagerSocket.sendto(sendingData, leadVehicleDataManagerAddress)
                print("Sent traffic signal state", trafficSignalState)
                
                
    hostVehicleDataManagerSocket.close()
    hostVehicleLogFile.close()
    leadVehicleLogFile.close()
    bsmLog.close()


if __name__ == "__main__":
    main()
