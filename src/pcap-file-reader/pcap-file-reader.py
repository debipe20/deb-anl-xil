#https://scapy.readthedocs.io/en/latest/usage.html
#https://subscription.packtpub.com/book/security/9781784399771/8/ch08lvl1sec48/reading-and-writing-to-pcap-files
#https://www.youtube.com/watch?v=gOcT5r0spVM&t=10s&ab_channel=danscourses
#https://stackoverflow.com/questions/5649407/how-to-convert-hexadecimal-string-to-bytes-in-python
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
