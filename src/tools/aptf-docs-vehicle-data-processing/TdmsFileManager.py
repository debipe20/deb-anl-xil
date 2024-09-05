
import os
import openpyxl
import pandas as pd
from nptdms import TdmsFile


class TdmsFileManager:
    def __init__(self, config):
        self.config = config
        self.output_file_path = self.config["OutputFileName"]
        # Define the path to your TDMS file using a raw string literal (r"...")
        self.tdms_data_directory = os.path.expanduser("~") + "/Nissan-Leaf-Data"
        self.test_ID_list = [62007023]
        
    def get_tdm_file_path(self):
        # Loop through each test ID in the list
        for test_id in self.test_ID_list:
            
            self.tdms_file_path = self.tdms_data_directory + f"/{test_id} Test Data.tdms"
            
            print(self.tdms_file_path)
            tdms_file = TdmsFile.read(self.tdms_file_path, memmap_dir=None)
            # Print all groups and their channels
            # for group in tdms_file.groups():
            #     print(f"Group: {group.name}")
            #     for channel in group.channels():
            #         print(f"  Channel: {channel.name}")
            
            
            group_channel_dataframe = self.get_data_group_channel_dataframe(tdms_file)
            # Open the Excel file and create a new sheet with the specified name
            with pd.ExcelWriter(self.output_file_path, engine='openpyxl', mode='a') as writer:
                # Write DataFrame to a new sheet in the existing Excel file
                sheet_name = "wh_cal_" + str(test_id)
                group_channel_dataframe.to_excel(writer, sheet_name=sheet_name, index=False)

            print(f"Data successfully written to sheet '{sheet_name}' in {self.output_file_path}")

    def get_data_group_channel_dataframe(self, tdms_file):
            
        group_channel_dataframe = pd.DataFrame()
        # Access the 'Data' group
        group_data = tdms_file["Data"]

        # Read the DAQ_Time[s] and P2 channels
        daq_time = group_data["DAQ_Time[s]"].data
        p2_data = group_data["P2"].data
        exhaust_bag = group_data["Exhaust_Bag"].data
        no_cycle = [p2_data[i] if exhaust_bag[i] == 0 else 0 for i in range(len(p2_data))] 
        
        # Prepare a DataFrame with the values for easy export to Excel
        group_channel_dataframe = pd.DataFrame({
            "DAQ_Time[s]": daq_time,
            "P2": p2_data,
            "Exhaust_Bag": exhaust_bag,
            "No_cycle": no_cycle
        })
            
        return group_channel_dataframe