This script is intended to UDP-forward the contents of any pcap file to any specified IPv4 Address and Port.
To use, move the desired pcap file into this directory. Run the script and input the file name. 
The following two prompts will request the IP/Port to send to. 

Note: The script is currently set to send each payload at a rate of 10Hz. This is reconfigurable in line 40.

Prerequisites: 
python3 # https://www.python.org/downloads/ 
tshark  # sudo apt-get install tshark

To use:
1. Run: bash pcapSender.sh
2. Follow the prompts
3. To stop script: <Ctrl-C>
