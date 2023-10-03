from scapy.all import *
import json
import binascii
from osys import v2x
filename='/home/debashis/Downloads/constant-drive-trace/const_speed_msg_fwd.pcap'
p = rdpcap(filename)
# print(p)
# print(len(p))
# packets = rdpcap("/home/debashis/Downloads/constant-drive-trace/const_speed_msg_fwd.pcap")
# print(packet.summary())
# print(p.summary())
pkt = p[100]
# print(pkt)
# print(type(pkt))
# print(dir(pkt))
# print(hexdump(pkt))
# print(pkt.show())
# pkts = []
# for packet in p:
#     if packet.haslayer('Other'):
#       pkts.append(packet)
# print(pkts)
data = raw(pkt)
print(data)
# print("hexadecimal dump",hexdump(pkt))
data = binascii.unhexlify(data.strip())
receivedJsonString = v2x.MessageFrame.to_json(data,len(data))
receivedJsonString = json.loads(receivedJsonString)
print(receivedJsonString)
