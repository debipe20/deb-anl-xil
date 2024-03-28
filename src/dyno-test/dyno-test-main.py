import socket
import json
import binascii
import struct
import haversine
import time, datetime
from osys import v2x
from BsmGenerator import BsmGenerator
from LeadVehicleDataManager import LeadVehicleDataManager

SpeedDataLength = 16
initializationTimestamp = ('{:%m%d%Y_%H%M%S}'.format(datetime.datetime.now()))
hostVehicleLogFile = open("/nojournal/bin/log/eco-driving/host_vehicle_log_" + initializationTimestamp + ".csv", "w")
leadVehicleLogFile = open("/nojournal/bin/log/eco-driving/lead_vehicle_log_" + initializationTimestamp + ".csv", "w")
bsmLog = open("/nojournal/bin/log/eco-driving/bsm_hex_log_" + initializationTimestamp + ".log","w")

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
            + str(round(leadVehicleSpeed, 2)) +  ","
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


def main():
    configFile = open("/nojournal/bin/anl-master-config.json", "r")
    config = json.load(configFile)
    configFile.close()

    hostIp = config["IPAddress"]["HostIp"]
    port = config["PortNumber"]["HostVehicleDataManager"]
    hostAddress = (hostIp, port)

    MessageReceiverIp = config["IPAddress"]["V2XHubIp"]
    MessageReceiverPort = config["PortNumber"]["MessageReceiver"]
    MessageReceiverAddress = (MessageReceiverIp, MessageReceiverPort)

    # vehicleControllerIp = config["IPAddress"]["VehicleControllerIp"]
    vehicleControllerIp = config["IPAddress"]["HostIp"]
    vehicleControllerPort = config["PortNumber"]["VehicleController"]
    vehicleControllerAddress = (vehicleControllerIp, vehicleControllerPort)

    dynoTestDataManagerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dynoTestDataManagerSocket.bind(hostAddress)
    # dynoTestDataManagerSocket.settimeout(0)

    bsmGenerator = BsmGenerator(config)
    leadVehicleDataManager = LeadVehicleDataManager(config)

    hostVehicleLat, hostVehicleLon, hostVehicleSpeed = 0.0, 0.0, 0.0
    leadVehicleLat, leadVehicleLon, leadVehicleSpeed = 0.0, 0.0, 0.0
    relativeDistance, relativeSpeed, counter = 10.0, 0.0, 0.0
    leadVehicleDataReceivedTime = time.time()
    # msgSendingTime = time.time()
    
    sendingData =  struct.pack("dddd", relativeDistance, relativeSpeed, counter, leadVehicleSpeed)
    # checkCounter = 1

    while True:
        # try:
        data, address = dynoTestDataManagerSocket.recvfrom(2048)
        # print("Received data is following:\n", data)

        dataLength = len(data)

        if dataLength == SpeedDataLength:
            decodedCounter, decodedSpeed = struct.unpack("dd", data)            
            hostVehicleLat, hostVehicleLon, hostVehicleSpeed, bsmJsonString = (bsmGenerator.getBsmJsonString(decodedSpeed))
            
            encodedBsm = v2x.MessageFrame.from_json(bsmJsonString)
            dynoTestDataManagerSocket.sendto(encodedBsm, MessageReceiverAddress)
            
            bsmHex = binascii.hexlify(encodedBsm)
            bsmLog.write(str(bsmHex) + "\n") 
            logHostVehicleData(decodedCounter, decodedSpeed)
            print("Decoded data is: ", decodedSpeed, " and counter is: ", decodedCounter)
            
            if time.time() - leadVehicleDataReceivedTime > 1.0:
                while relativeDistance > 10:
                    relativeDistance, relativeSpeed, counter, leadVehicleSpeed = getSafeDynoOperationData(counter, relativeDistance)
                    sendingData =  struct.pack("dddd", relativeDistance, relativeSpeed, counter, leadVehicleSpeed)

                    dynoTestDataManagerSocket.sendto(sendingData, vehicleControllerAddress)
                    
                    logLeadVehicleData(counter, relativeDistance, relativeSpeed, leadVehicleSpeed, hostVehicleSpeed)
                    print("Sending relative distance & speed, counter, and lead and host vehicle speed for safe operation:", relativeDistance, relativeSpeed, counter, leadVehicleSpeed, hostVehicleSpeed)

        else:

            hexPacket = binascii.hexlify(data)
            packetString = str(hexPacket, encoding="utf-8")
            bsmIdentifier = packetString.find("0014")

            if bsmIdentifier >= 0:
                leadVehicleInformationStatus, leadVehicleLat, leadVehicleLon, leadVehicleSpeed = (leadVehicleDataManager.getLeadVehicleInformation(data))
                
                if leadVehicleInformationStatus == True:
                    relativeDistance = haversine.haversine((leadVehicleLat, leadVehicleLon), (hostVehicleLat, hostVehicleLon), unit=haversine.Unit.METERS)
                    
                    if relativeDistance >= 80.0:
                        relativeDistance = 10.0
                        
                    leadVehicleDataReceivedTime = time.time()
                    # msgSendingTime = time.time()
                    relativeSpeed = leadVehicleSpeed - hostVehicleSpeed
                    counter = counter + 1.0
                    # checkCounter = 1
                    
                    sendingData =  struct.pack("dddd", relativeDistance, relativeSpeed, counter, leadVehicleSpeed)
                    
                    
                    dynoTestDataManagerSocket.sendto(sendingData, vehicleControllerAddress)
                    logLeadVehicleData(counter, relativeDistance, relativeSpeed, leadVehicleSpeed, hostVehicleSpeed)
                    print("Sending relative distance & speed, counter, and lead and host vehicle speed: ",
                        relativeDistance, relativeSpeed, counter, leadVehicleSpeed, hostVehicleSpeed)

            # else:
            #     continue
        # except:
        #     timeGap = time.time() - msgSendingTime
        #     if timeGap >= 0.01:
        #         msgSendingTime = time.time()
        #         dynoTestDataManagerSocket.sendto(sendingData, vehicleControllerAddress)
        #         checkCounter = checkCounter + 1
        #         print("[ " + str(time.time()) + " ]: at time gap: " + str(timeGap) + " Check counter value is ", checkCounter)
        #         if checkCounter == 10:
        #             checkCounter = 1
                
    dynoTestDataManagerSocket.close()
    hostVehicleLogFile.close()
    leadVehicleLogFile.close()
    bsmLog.close()


if __name__ == "__main__":
    main()
