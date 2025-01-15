"""
**********************************************************************************

HiokiCANAnalyzer.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************

Description:
------------
The `HiokiCANAnalyzer` class is responsible for generating and embedding visualizations for uncertainty and energy analysis into an Excel workbook. It integrates seamlessly with the summary data from MCT drive cycles and provides functionality to:


Methods:
--------

"""

import os
import platform
from nptdms import TdmsFile

class HiokiCANAnalyzer:
    def __init__(self):
        """
        Initialize the HiokiCANAnalyzer class.

        Parameters:
        hioki_data (dict): Dictionary containing Hioki data with keys like 'voltage', 'current', 'power', etc.
        can_data (dict): Dictionary containing CAN data with keys like 'voltage', 'current', 'power', etc.
        """
        self.test_id_list = [62005016]
        self.get_files()
        self.manage_linear_fit_analysis(self.test_id_list)

    def get_files(self):
        current_os = platform.system()

        if current_os == "Linux":
            self.tdms_data_directory = os.path.join(os.path.expanduser("~"), "Documents", "Data", "AMTL-Test-Data")
        
        elif current_os == "Windows":  
            self.tdms_data_directory = os.path.join(os.path.expanduser("~"), "Documents", "Data", "AMTL-Test-Data")
        
        else:
            raise OSError(f"Unsupported operating system: {current_os}")

    def manage_linear_fit_analysis(self, test_id_list):
        
        for test_id in test_id_list:
            self.tdms_file_path = self.tdms_data_directory + f"/{test_id} Test Data.tdms"
            print(f"Conducting Linear Fit Analysis for '{self.tdms_file_path}' TDMS file")
            self.tdms_file = TdmsFile.read(self.tdms_file_path, memmap_dir=None)
            group_data = self.tdms_file["Data"]
            self.time_data = group_data['DAQ_Time[s]']
            self.get_groups_channels_name()

    def get_groups_channels_name(self):
        # Get all groups in the TDMS file
        groups = self.tdms_file.groups()

        # Iterate over groups and print their names and channels
        for group in groups:
            print(f"Group: {group.name}")

            # Get all channels in the current group
            channels = group.channels()
            
            # Iterate over channels in the group and print their names
            for channel in channels:
                print(f"  Channel: {channel.name}")

    def get_voltage_data(self):
        pass
    
'''##############################################
                   Unit testing
##############################################'''
if __name__ == "__main__":
    hioki_CAN_analyzer = HiokiCANAnalyzer()
