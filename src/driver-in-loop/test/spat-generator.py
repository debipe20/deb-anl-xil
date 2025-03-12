import asn1tools
import time
import random

# Load the ASN.1 schema
schema = asn1tools.compile_files("j2735.asn", "uper")

EVENT_STATE_MAP = {
    0: "unknown",
    1: "dark",
    2: "stop-And-Remain",
    3: "permissive-Movement-Allowed",
    4: "protected-Movement-Allowed",
    5: "permissive-clearance",
    6: "protected-clearance",
    7: "caution-Conflicting-Traffic"
}

def generate_spat_uper(intersection_id=101, num_phases=4):
    """
    Generates a J2735 SPaT message wrapped inside a MessageFrame for proper validation.
    """
    current_time = int(time.time() * 1000) % (24 * 60 * 60 * 1000)

    # Construct Intersection State
    intersection_state = {
        "region": 0,
        "id": intersection_id,
        "status": 0,  # Normal operation
        "moy": current_time // 60000,  # Minute of the year
        "timeStamp": current_time % 60000  # Milliseconds within the current minute
    }

    # Generate random phases
    valid_states = [2, 3, 4, 5, 6]  # (stop-And-Remain, permissive, protected, etc.)
    phases = []
    for phase_id in range(1, num_phases + 1):
        min_end_time = random.randint(5, 30)
        max_end_time = min_end_time + random.randint(3, 10)

        event_state_int = random.choice(valid_states)
        event_state_str = EVENT_STATE_MAP[event_state_int]  # Convert to string

        phase_state = {
            "id": phase_id,
            "eventState": event_state_str,
            "minEndTime": min_end_time,
            "maxEndTime": max_end_time
        }
        phases.append(phase_state)

    # Construct SPaT message
    spat_message = {
        "msgID": 19,  # SPaT message ID
        "intersectionState": intersection_state,
        "phases": phases
    }

    # Wrap SPaT inside a MessageFrame
    message_frame = {
        "msgID": 19,  # MessageFrame for SPaT
        "value": ("SPAT", spat_message)  # Encapsulated SPaT data
    }

    # Encode MessageFrame in UPER format
    uper_encoded_message = schema.encode("MessageFrame", message_frame)

    return uper_encoded_message

if __name__ == "__main__":
    spat_uper = generate_spat_uper()
    print("Encoded MessageFrame (UPER, Hex Format):", spat_uper.hex())  # Print hex format
