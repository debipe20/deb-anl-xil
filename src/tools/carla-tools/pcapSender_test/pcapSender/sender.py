# Send replay raw PCAP using UDP
import socket
import signal, sys
from binascii import unhexlify, hexlify
from time import sleep

def signal_handler(sig, frame):
    print('\nExiting')
    sys.exit(0)  

# send Hex string to IP + port
ip = input('Enter IP Address to send to: ')
port = input('Enter Port to send to: ')
sk = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

payload = input('Insert payload: ')
## open and read from file, then close file
# f = open('output.txt', 'r')
# Lines = f.readlines()
# f.close()

print('Sending.\nPress Ctrl+C to exit')
## block for sending payload from file
# sleep(1)
# while(1):
#     for line in Lines:
#         data = line.strip('\n')     # removes any new line characters
#         print(data)                # uncomment to view stream 
#         # send Hex string to port
#         unhexed = unhexlify(data)
#         sk.sendto(unhexed,(ip,int(port)))
#         sleep(0.1) # 0.1 for BSM or SPAT or a pre-recorded message with multiple message types, 1 for ONLY Map

# block for sending single payload
unhexed = unhexlify(payload)
print('Sending.\nPress Ctrl+C to exit')
sleep(2)
while(1):
    sk.sendto(unhexed,(ip,int(port)))
    sleep(0.1) # 0.1 for BSM or SPAT, 1 for MAP


signal.signal(signal.SIGINT, signal_handler)
signal.pause()