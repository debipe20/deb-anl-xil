#https://scapy.readthedocs.io/en/latest/usage.html
#https://subscription.packtpub.com/book/security/9781784399771/8/ch08lvl1sec48/reading-and-writing-to-pcap-files
#https://www.youtube.com/watch?v=gOcT5r0spVM&t=10s&ab_channel=danscourses
#https://stackoverflow.com/questions/5649407/how-to-convert-hexadecimal-string-to-bytes-in-python
from scapy.all import *
import json
import binascii
from osys import v2x
filename='/home/carma/Downloads/constant-drive-trace/const_speed_msg_fwd.pcap'
p = rdpcap(filename)

pkt = p[100]

data = raw(pkt)
print(data)
# print("hexadecimal dump",hexdump(pkt))
data = binascii.hexlify(data)


data = str(data, encoding='utf-8')
index = data.find('0014')
print("index is:", index)
data = data[index:]
print("payload is:\n", data)
# data = b'001468427298b345a441a76dbbdd9cb32bd78ca18505000071388238fd7d07d0007fff00004f89d00104c0c10a0e405af02203b0115e7c06b705222b2114cec06d704c22c610f5cbec0502a5bb610d43be5e301a5c9210c95bdebd0165d2010c0abda110165d84b53bc600'
data = binascii.unhexlify(data)
receivedJsonString = v2x.MessageFrame.to_json(data,len(data))
receivedJsonString = json.loads(receivedJsonString)
print(receivedJsonString)


