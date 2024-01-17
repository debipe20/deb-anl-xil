import socket
import json
import time
import struct


hostIp = "169.254.137.176"
port = 50002
com_info = (hostIp, port)

speedProfileGeneratorSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
speedProfileGeneratorSocket.bind(com_info)

encoded_bytes = struct.pack('f', 4.6)
print(encoded_bytes)


speedProfileGeneratorSocket.close()