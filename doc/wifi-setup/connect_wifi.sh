#!/bin/bash
sleep 5
sudo wpa_supplicant -B -c /etc/wpa_supplicant.conf -i wlan0 &
sleep 5
sudo dhclient wlan0 &
