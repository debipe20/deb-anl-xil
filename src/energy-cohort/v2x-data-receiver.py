import socket
import time
import json
import binascii
from osys import v2x
from datetime import datetime

GPS_CONVERSION = 10_000_000          # 1e-7 degrees
ELEVATION_CONVERSION = 10            # decimeters → meters
HEADING_CONVERSION = 0.0125          # degrees
SPEED_CONVERSION = 0.02              # m/s
SECOND_MILLISECOND_CONVERSION = 1000

# -----------------------------
# Mapping rules
# -----------------------------

EVENT_STATE_MAP = {
    "stop-And-Remain": "red",
    "protected-Movement-Allowed": "protected_green",
    "permissive-Movement-Allowed": "permissive_green",
    "clearance": "yellow"
}


def normalize_hex_id(value) -> str:
    """
    Normalize a vehicle ID to lowercase hex without '0x'.
    Accepts hex string or int.
    """
    if isinstance(value, int):
        return format(value, "x")

    if isinstance(value, str):
        v = value.strip().lower()
        return v[2:] if v.startswith("0x") else v

    raise ValueError(f"Unsupported vehicle ID type: {type(value)}")


def build_bsm_json(input_msg):
    core = input_msg["value"]["coreData"]

    latitude = core["lat"] / GPS_CONVERSION
    longitude = core["long"] / GPS_CONVERSION
    elevation = core["elev"] / ELEVATION_CONVERSION

    heading_deg = core["heading"] * HEADING_CONVERSION
    speed_mps = core["speed"] * SPEED_CONVERSION
    sec_mark_seconds = core["secMark"] / SECOND_MILLISECOND_CONVERSION

    width_cm = core["size"]["width"] * 10
    length_cm = core["size"]["length"] * 100
    
    tmp_id = core["id"]
    temporary_id = int(tmp_id, 16) if isinstance(tmp_id, str) else int(tmp_id)

    now = datetime.utcnow()

    output_msg = {
        "MsgType": "BSM",
        "Timestamp_posix": now.timestamp(),
        "Timestamp_verbose": now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        "BasicVehicle": {
            "heading_Degree": heading_deg,
            "position": {
                "elevation_Meter": elevation,
                "latitude_DecimalDegree": latitude,
                "longitude_DecimalDegree": longitude
            },
            "secMark_Second": sec_mark_seconds,
            "size": {
                "length_cm": length_cm,
                "width_cm": width_cm
            },
            "speed_MeterPerSecond": speed_mps,
            "temporaryID": temporary_id,
            "type": "0"
        }
    }

    return json.dumps(output_msg, indent=4)


import json

def build_map_json(map_json: dict, hexstring: str) -> str:
    # Extract intersection ID (MAP usually contains one intersection)
    intersection = map_json["value"]["intersections"][0]
    intersection_id = intersection["id"]["id"]

    output = {
        "MsgType": "MAP",
        "IntersectionName": f"Map{intersection_id}",
        "MapPayload": hexstring,
        "IntersectionID": intersection_id
    }

    return json.dumps(output, indent=4)


def build_spat_json(decoded_spat: dict) -> dict:
    intersection = decoded_spat["value"]["intersections"][0]

    phase_states = []

    for state in intersection["states"]:
        signal_group = state["signalGroup"]
        sts_list = state.get("state-time-speed", [])
        if not sts_list:
            continue
        sts = sts_list[0]

        event_state = sts["eventState"]
        timing = sts["timing"]

        phase_states.append({
            "currState": EVENT_STATE_MAP.get(event_state, "unknown"),
            "maxEndTime": timing.get("maxEndTime"),
            "minEndTime": timing.get("minEndTime"),
            "phaseNo": signal_group,
            "startTime": timing.get("maxEndTime", 0) + 1
        })

    # Timestamps
    ts_posix = time.time()
    ts_verbose = datetime.fromtimestamp(ts_posix).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    output = {
        "MsgType": "SPaT",
        "Spat": {
            "intersectionState": {
                "intersectionID": intersection["id"]["id"],
                "regionalID": 0
            },
            "minuteOfYear": intersection.get("moy"),
            "msOfMinute": intersection.get("timeStamp"),
            "msgCnt": intersection.get("revision", 0),
            "phaseState": phase_states,
            "status": intersection.get("status", "")
        },
        "Timestamp_posix": ts_posix,
        "Timestamp_verbose": ts_verbose
    }

    return json.dumps(output, indent=4)

def main():
    configFile = open("../../config/anl-master-config.json", "r")
    config = json.load(configFile)
    configFile.close()

    # host_ip = config["IPAddress"]["HostIp"]
    host_ip = "127.0.0.1"
    port = config["PortNumber"]["V2XDataReceiver"]
    com_info = (host_ip, port)

    client_port = config["PortNumber"]["VehicleStatusManager"]
    client_info = (host_ip,client_port)

    msg_receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msg_receiver_socket.bind(com_info)


    ego_vehicle_id = config["VehicleInformation"]["EgoVehicleId"]

    try: 
        while True:
            data, address = msg_receiver_socket.recvfrom(8192)
            timestamp = str(round(time.time(),4))

            try:
                receivedJsonString = v2x.MessageFrame.to_json(data, len(data))          
                receivedJsonString = json.loads(receivedJsonString)
        
                
                if receivedJsonString["messageId"] == 18: # MAP

                    hex_payload = data.hex()
                    sending_json_string = build_map_json(receivedJsonString, hex_payload)
                    msg_receiver_socket.sendto(sending_json_string.encode("utf-8"), client_info)
                    
                elif receivedJsonString["messageId"] == 19: # SPaT
                    sending_json_string = build_spat_json(receivedJsonString)
                    msg_receiver_socket.sendto(sending_json_string.encode("utf-8"), client_info)
                    
                elif receivedJsonString["messageId"] == 20: # BSM
                    rx_id = normalize_hex_id(receivedJsonString["value"]["coreData"]["id"])
                    ego_id = normalize_hex_id(ego_vehicle_id)

                    if rx_id == ego_id:
                    # if receivedJsonString["value"]["coreData"]["id"] == ego_vehicle_id:
                        sending_json_string = build_bsm_json(receivedJsonString)
                        msg_receiver_socket.sendto(sending_json_string.encode("utf-8"), client_info)

                    
                else: 
                    print(("\n[{}]".format(timestamp) + " Unknown message type" ))
                    
            except Exception as e:

                print(f"\n[{timestamp}] Failed to decode/process message: {e}")

    except KeyboardInterrupt:
        print("\nShutdown requested (Ctrl+C)")

    finally:
        print(f"\n[{round(time.time(),4)}] Closing UDP socket")
        msg_receiver_socket.close()

if __name__ == '__main__':
    main()
    
    
# 001425003c0eb596271026a5e0a59f125427880080000000200019cb7e7d07d07f7fff8000020010 

# 0013264059360180000800000059369e1a0200204342d9b2d9b001823216be96be80101190b5f4b5f4 

# 0013264059360180001000000059369e1a0200204342d9b2d9b002023216be96be80201190b5f4b5f4 

# 00131f4059360180001800000059369e1a0100204342d9b2d9b000023216be96be80 

# 0013264059360180002000000059369e1a0200204342d9b2d9b002023216be96be80201190b5f4b5f4 

# 0013264059360180002800000059369e1a0200204342d9b2d9b002023216be96be80201190b5f4b5f4 

# 0013264059360180003000000059369e1a0200204342d9b2d9b002023216be96be80201190b5f4b5f4 

# 00131f4059360180003800000059369e1a0100204342d9b2d9b000023216be96be80 

# 0013264059360180004000000059369e1a0200204342d9b2d9b001823216be96be80101190b5f4b5f4 

# 0012811238053020200010154d4bbf403e248c7b0ff602dc06580228000005000298f89221966a5defc18f89218666a5dedc18f8920f466a5debd18f89204b26a5deb598f891fa6e6a5decf18f891f05e6a5df0a98f891e8666a5df5d02c0e0000804b0085000000c000531f12440d4d4bbf4131f124323cd4bbf0d31f1241d14d4bbec531f12407ecd4bbecf31f123f5a4d4bbf0031f123e444d4bbf5731f123d38cd4bbffa058240001008c01910000010000663e24913c9a977e4e63e2492e19a977e96e3e2495b59a977f0804fb18f89265ee6a5dfed98f89273da6a5e0198c02110000010000663e2490d19a97810a63e2492b99a97814a63e2495579a9781a6e3e2499529a97824004fb18f89272ea6a5e0b98 

# 001425003c0eb58da71026a5f7199f11e92f08000000000030000b707e7d07d07f7fff8000020008 

# 001425003c0eb596271026a5e0a59f125427880080000000200019cb7e7d07d07f7fff8000020010 

# 001425003c0eb58da71026a5f7199f11e92f08000000000030000b707e7d07d07f7fff8000020008 

# 0013264059360180000800000059369e7e0200204342d9b2d9b001823216be96be80101190b5f4b5f4 

# 0013264059360180001000000059369e7e0200204342d9b2d9b002023216be96be80201190b5f4b5f4 

# 00131f4059360180001800000059369e7e0100204342d9b2d9b000023216be96be80 

# 0013264059360180002000000059369e7e0200204342d9b2d9b002023216be96be80201190b5f4b5f4 

# 0013264059360180002800000059369e7e0200204342d9b2d9b002023216be96be80201190b5f4b5f4 

# 0013264059360180003000000059369e7e0200204342d9b2d9b002023216be96be80201190b5f4b5f4 

# 00131f4059360180003800000059369e7e0100204342d9b2d9b000023216be96be80 

# 0013264059360180004000000059369e7e0200204342d9b2d9b001823216be96be80101190b5f4b5f4 

# 0012811338063000200002194d4bd7223e227a25104602dc06580428000004000218f889d2466a5ebc318f889cc666a5ebcb18f889c4f66a5ebf418f889bb026a5ec5398f889b24e6a5eca918f889aa726a5ed0082c120000804b0045000000a000431f113a48cd4bd63c31f11399a4d4bd64c31f1138984d4bd6a331f113752cd4bd76231f11363ccd4bd80731f1135154d4bd8bc0581c0001008802110000000a63e227e489a97affa63e227fc69a97b00e63e22819c9a97b02463e22835d9a97b03863e2285769a97b04263e2287b69a97b05663e228a5c9a97b062200644000000218f889f9726a5eb5998f88a039e6a5eb6698f88a0c1a6a5eb6918f88a15026a5eb7098f88a1fce6a5eb7898f88a293a6a5eb7b0