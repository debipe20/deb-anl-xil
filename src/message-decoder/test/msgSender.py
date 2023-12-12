'''
  msgSender.py  
  Created by: Debashis Das
  Argonne National Laboratory
    Transportation and Power Systems Division

  This code was developed under the supervision of Professor Larry Head
  in the Systems and Industrial Engineering Department.

  Revision History:
  1. This is the initial revision developed for testing the messageDecoder.py
'''

import socket
import json
import time

map = "001282953808302030ce162148dbba702927d34f2bf802dc051870a96008a000001480082d95d4a6788902c01414cdece02c02829b67ab002c050a1344b80d19a1441bc05050a44a0001922c4000c58042800000400010b786fd9bc9470166050f3326480840a0a6727103f814140911800062c0314000002000045ca7514de9c680cc028a1b4c11016605050244200018b010500000050001173648433b2e814c0a0a1f096122290b40001482880008c0291000001000002e5962f6dbd5401c81428300c4400000400000ba95279b6f0b003c050a0c0391000001000002eb836e6dba63fd70142858106800000120000e9186e41c1940e60907200082c093400000200008724d3759214121edb01a4b59204fb1200d34b8122d0001058146800000200000e18a6eb243004890244100020602d0800000800001bcc4dea486647b32c0f5400000140004436adc0d52348097027d867537e90a459000152202000a5818a8000005200288a18b01aa181012e04fb10f368291849241c404fb30ede819409f6602c6ff3813ec31103fcc520f0000490b200022c0d5400000200018449a87ed5e8c8039027d8875c40b0c3a160c9027d88575c12ec2a4a065027d983c1c01a04fb0c58900d04834000116072a0000010000a22085b96af75c003013ec43e3e07e61cd9045013ec43c120bd61e09032813ecd50e58019027d8120b000043020c40000040000085aacadaa62efeec04fb0c08b100000100000214abf56a9953fed013ec3024c40000040000084df56daa661002604fb1609ba0000004800035db663c6f74f848244880010b051d000000800031b6bf31047dd3d9b2bfef5d5536007378b809f623fcfc550242e00010b055d000000400001bcab31047c3f4e80482a00020c0b41000001000003878e5bcafc8944400"
spat = "001380820018800001F58300001D4C1C3510B001043C00190032004B001023600258032003E800C10F001F4025802BC0080878015E019001C2005043C00E100FA011300302360089809600A2801C10F00514057805DC010087802EE0320035200A048C01A901C201DB006021E00ED80FA0106803812300834089808FC0200878047E04B004E2"
bsm = "001425007C0EB58400AF266E8B019EA6BC5F128CFFFFFFFFF0D890EAFDFA1FA1007FFF8000962580"

def Main():
    configFile = open("/nojournal/bin/anl-master-config.json", 'r')
    config = (json.load(configFile))
    configFile.close()
    
    hostIp = config["HostIp"]
    port = 10001
    receiverPort = config["PortNumber"]["MessageDecoder"]
    com_info = (hostIp, port)
    receiver = (hostIp, receiverPort)

    msgSenderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msgSenderSocket.bind(com_info)
  
    message = spat # Type the name of file containing the message. This message must be formatted as per RSU4.1 Specifications.
    frequency = 0.1
    msgCount = 1

    msgSenderSocket.sendto(message.encode(), receiver)
    # while True:
    #     msgSenderSocket.sendto(message.encode(), receiver) # Send the data to receiver
    #     print("Sent message# " + str(msgCount) + " to " + str(hostIp) + ":" + str(receiverPort))
    #     msgCount = msgCount + 1
    #     time.sleep(frequency) 

    msgSenderSocket.close() # Close the socket


if __name__ == "__main__":
    Main()
