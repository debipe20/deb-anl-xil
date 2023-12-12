import json
import socket

configFile = open("/nojournal/bin/mmitss-phase3-master-config.json", 'r')
config = json.load(configFile)
configFile.close()

host = (config["HostIp"], config["PortNumber"]["MessageDistributor"])
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(host)

bsmLogFile = open("BSM-Log.csv", 'w')
bsmLogFile.write(
            "timestamp_verbose,timestamp_posix,msgCount,temporaryId,secMark,latitude,longitude,elevation,speed,heading,type,length,width\n")

def bsm_json_to_csv(jsonData):

    timestamp_verbose = str(jsonData["Timestamp_verbose"])
    
    timestamp_posix = str(jsonData["Timestamp_posix"])
    msgCount = str(jsonData["BasicVehicle"]["msgCount"])
    temporaryId = str(jsonData["BasicVehicle"]["temporaryID"])
    secMark = str(jsonData["BasicVehicle"]["secMark_Second"])
    latitude = str(jsonData["BasicVehicle"]["position"]
                ["latitude_DecimalDegree"])
    longitude = str(jsonData["BasicVehicle"]
                    ["position"]["longitude_DecimalDegree"])
    elevation = str(jsonData["BasicVehicle"]["position"]["elevation_Meter"])
    speed = str(jsonData["BasicVehicle"]["speed_MeterPerSecond"])
    heading = str(jsonData["BasicVehicle"]["heading_Degree"])
    vehType = str(jsonData["BasicVehicle"]["type"])
    length = str(jsonData["BasicVehicle"]["size"]["length_cm"])
    width = str(jsonData["BasicVehicle"]["size"]["width_cm"])

    csvRow = (timestamp_verbose + ","
        + timestamp_posix + ","
        + msgCount + ","
        + temporaryId + ","
        + secMark + ","
        + latitude + ","
        + longitude + ","
        + elevation + ","
        + speed + ","
        + heading + ","
        + vehType + ","
        + length + ","
        + width + "\n")
    
    bsmLogFile.write(csvRow)


while True:
    data, addr = s.recvfrom(1024)
    msg = json.loads(data.decode())
    # print(str(msg["Timestamp_posix"]))
    # print(str(msg["BasicVehicle"]["size"]["width_cm"]))
    bsm_json_to_csv(msg)
    
bsmLogFile.close()
s.close()

if __name__ == "__main__":
    main()