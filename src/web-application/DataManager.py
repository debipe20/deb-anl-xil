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

import time, datetime

Time_Gap = 300.0

class DataManager:
    def __init__(self) -> None:
                
        self.log_file = open("/log/msg_count_log_.csv", "w")        

        self.simulation_msg_count = 0.0
        self.faulty_simulation_msg_count = 0.0
        self.simulation_msg_count_cumulative = 0.0
        
        self.msg_count_dictionary = {}
        
        self.msg_update_time = time.time()
        self.log_file.write("Time,Message,Count,Cumulative,Type\n")
        
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
            self.simulation_msg_count = self.simulation_msg_count + 1
            self.simulation_msg_count_cumulative = self.simulation_msg_count_cumulative + 1
            
            valueList.append(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")), "Simulation", self.simulation_msg_count, self.simulation_msg_count_cumulative, transmission_type)
            self.update_dict("simulation", valueList)
            
            
        elif msg_type == "fauly-simulation":
            self.faulty_simulation_msg_count = self.faulty_simulation_msg_count + 1
            self.simulation_msg_count_cumulative = self.simulation_msg_count_cumulative + 1
            
            valueList.append(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")), "Faulty-Simulation", self.simulation_msg_count, self.simulation_msg_count_cumulative, transmission_type)
            self.update_dict("simulation", valueList)
        
    def write_msg_count(self):
        """
        Method to write the csv file based on the msg_count_dictionary
            - Method will check the time gap between two consecutive file writing
        """
        
        if time.time() - self.msg_update_time >= Time_Gap:
            for lists in self.msg_count_dictionary.values():
                for list_value in lists:
                    self.log_file.writerow(list_value)                  
            
            
            self.simulation_msg_count_cumulative = 0.0
            self.msg_update_time = time.time()
            
            
    def __del__(self):
        # self.logger.consoleDisplay("Closing BSM Generator Application")
        pass