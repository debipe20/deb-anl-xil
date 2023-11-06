#!/bin/bash
directory=$(cd ../ &&pwd)

extract() {
    ls *.pcap
    read -rep "Type pcap file from list: " fileName
    
    tshark -r $fileName --disable-protocol wsmp -Tfields -Eseparator=, -e data.data > output.txt
}

send() {
    python3 sender.py
}

processing() {
    extract
    send
}

processing