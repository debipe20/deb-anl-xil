"""
**********************************************************************************

DataManager.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************
  
Description:
------------
The methods available from this class are the following:
- getLeadVehicleInformation(data): Method to decode messages 
********
"""

import time
from datetime import datetime
# import csv

Time_Gap = 300.0

class DataManager:
    def __init__(self) -> None:
                
               

        self.simulation_msg_count = 0.0
        self.faulty_simulation_msg_count = 0.0
        self.simulation_msg_count_cumulative = 0.0
        self.faulty_simulation_msg_count_cumulative = 0.0
        
        self.mabx_msg_count = 0.0
        self.faulty_mabx_msg_count = 0.0
        self.mabx_msg_count_cumulative = 0.0
        self.faulty_mabx_msg_count_cumulative = 0.0
        
        self.facilities_msg_count = 0.0
        self.faulty_facilities_msg_count = 0.0
        self.facilities_msg_count_cumulative = 0.0
        self.faulty_facilities_msg_count_cumulative = 0.0
        
        self.trasmitted_simulation_msg_count = 0.0
        self.trasmitted_mabx_msg_count = 0.0
        self.trasmitted_facilities_msg_count = 0.0
        
        self.trasmitted_simulation_msg_count_cumulative = 0.0
        self.trasmitted_mabx_msg_count_cumulative = 0.0
        self.trasmitted_facilities_msg_count_cumulative = 0.0
        
        self.msg_count_dictionary = {}
        
        self.msg_update_time = time.time()
        
        
    def update_dict(self,key, value):
        """
        Method to update msg_count_dictionary
        """
        if key in self.msg_count_dictionary:
            self.msg_count_dictionary[key].append(value)
        else:
            self.msg_count_dictionary[key] = [value]
        
    def manageMsgInformation(self, msg_type, transmission_type):
        
        """
        Method to append values into msg_count_dictionary based on msg type and trasmission type
        """
        valueList = []
        if msg_type == "simulation":
            self.simulation_msg_count += 1
            self.simulation_msg_count_cumulative += 1
            self.trasmitted_simulation_msg_count += 1
            self.trasmitted_simulation_msg_count_cumulative += 1

        elif msg_type == "faulty-simulation":
            self.faulty_simulation_msg_count = self.faulty_simulation_msg_count + 1
            self.faulty_simulation_msg_count_cumulative = self.faulty_simulation_msg_count_cumulative + 1

        elif msg_type == "mabx":
            self.mabx_msg_count = self.mabx_msg_count + 1
            self.mabx_msg_count_cumulative = self.mabx_msg_count_cumulative + 1
            self.trasmitted_mabx_msg_count += 1
            self.trasmitted_mabx_msg_count_cumulative += 1
            
        elif msg_type == "faulty-mabx":
            self.faulty_mabx_msg_count += 1
            self.faulty_mabx_msg_count_cumulative += 1
            
        elif msg_type == "facilities":
            self.facilities_msg_count += 1
            self.facilities_msg_count_cumulative += 1
            self.trasmitted_facilities_msg_count += 1
            self.trasmitted_facilities_msg_count_cumulative += 1
            
        elif msg_type == "faulty-facilities":
            self.faulty_facilities_msg_count += 1
            self.faulty_facilities_msg_count_cumulative += 1
            
            # valueList.append(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")), "Faulty-Facilities", self.faulty_facilities_msg_count, self.faulty_facilities_msg_count_cumulative, transmission_type)
            # self.update_dict("facilities", valueList)
            # self.reset_msg_count(self.faulty_facilities_msg_count)
        
    def write_msg_count(self):
        """
        Method to write the csv file based on the msg_count_dictionary
            - Method will check the time gap between two consecutive file writing
        """

        log_file = open("../log/msg_count_log_.csv", "w") 
        log_file.write("Time,Message,Count,Cumulative,Type\n")
        
        log_file.write(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")) + "," + "Simulation" + "," + str(self.simulation_msg_count) + "," + str(self.simulation_msg_count_cumulative) + "," + "Received" + "\n")
        log_file.write(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")) + "," + "MabX" + "," + str(self.mabx_msg_count) + "," + str(self.mabx_msg_count_cumulative) + "," + "Received" + "\n")
        log_file.write(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")) + "," + "Facilities" + "," + str(self.facilities_msg_count) + "," + str(self.facilities_msg_count_cumulative) + "," + "Received" + "\n")
        
        if self.faulty_simulation_msg_count > 0.0:
            log_file.write(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")) + "," + "Faulty-Simulation" + "," + str(self.faulty_simulation_msg_count) + "," + str(self.faulty_simulation_msg_count_cumulative) + "," + "Received" + "\n")
        
        if self.faulty_mabx_msg_count > 0.0:
            log_file.write(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")) + "," + "Faulty-MabX" + "," + str(self.faulty_mabx_msg_count) + "," + str(self.faulty_mabx_msg_count_cumulative) + "," + "Received" + "\n")
        
        if self.faulty_facilities_msg_count > 0.0:
            log_file.write(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")) + "," + "Faulty-Facilities" + "," + str(self.faulty_facilities_msg_count) + "," + str(self.faulty_facilities_msg_count_cumulative) + "," + "Received" + "\n")
        
        log_file.write(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")) + "," + "Simulation" + "," + str(self.trasmitted_simulation_msg_count) + "," + str(self.trasmitted_simulation_msg_count_cumulative) + "," + "Transmitted" + "\n")
        log_file.write(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")) + "," + "MabX" + "," + str(self.trasmitted_mabx_msg_count) + "," + str(self.trasmitted_mabx_msg_count_cumulative) + "," + "Transmitted" + "\n")
        log_file.write(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")) + "," + "Facilities" + "," + str(self.trasmitted_facilities_msg_count) + "," + str(self.trasmitted_facilities_msg_count_cumulative) + "," + "Transmitted" + "\n")
        
        log_file.close()
        
        self.simulation_msg_count = 0.0
        self.faulty_simulation_msg_count = 0.0
        self.mabx_msg_count = 0.0
        self.faulty_mabx_msg_count = 0.0
        self.facilities_msg_count = 0.0
        self.faulty_facilities_msg_count = 0.0
        self.trasmitted_simulation_msg_count = 0.0
        self.trasmitted_mabx_msg_count = 0.0
        self.trasmitted_facilities_msg_count = 0.0
            
    
    def reset_msg_count(self, msg_count_attr):
        """
        Method to reset a particular type message count after updating the dictionary
        """
        setattr(self, msg_count_attr, 0.0)           
            
    # def __del__(self):
        # self.logger.consoleDisplay("Closing BSM Generator Application")
        # self.log_file.close()
