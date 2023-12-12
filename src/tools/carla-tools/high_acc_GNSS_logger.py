#!/usr/bin/python3
#encoding:utf-8
import rospy
from typing import Optional
from std_msgs.msg import String
from novatel_oem7_msgs.msg import BESTPOS
from docutils.nodes import topic

import rosbag, sys, csv
import time
import string
import os #for file management make directory
import shutil #for file management, copy file

# ==================================================================
if_header  = False
deli       = "\t"
filename   = "/home/carma/autoware.ai/CUSTOMIZED/DATA/highacc_GNSS_coord.csv"
write_file = open(filename,'a')

def callback(Frame):
    rospy.loginfo("\n READING %s, \n lat %s, lon %s", Frame.header,Frame.lat,Frame.lon)
    time = str( Frame.header.stamp.secs) +"."+ str( Frame.header.stamp.nsecs)
    with open(filename,  'a', newline='') as f:
         writer = csv.writer(f)
         writer.writerow([time,Frame.lat,Frame.lon,Frame.hgt,Frame.lat_stdev,Frame.lon_stdev,Frame.hgt_stdev])    
 
def listener():
    rospy.init_node('POS_LOGGER', anonymous= True)
    rospy.Subscriber("/novatel/oem7/bestpos",BESTPOS,callback)
if __name__ == '__main__':
   # Now let'.s form a csv file.
   rospy.init_node('POS_LOGGER',anonymous=True)
   rospy.Subscriber("/novatel/oem7/bestpos", BESTPOS, callback)
   rospy.spin()
