
import os
import openpyxl
import pandas as pd
from nptdms import TdmsFile
from openpyxl.styles import Border, Side

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
            
            
            group_channel_dataframe, summary_data = self.get_data_group_channel_dataframe(tdms_file)
            # Open the Excel file and create a new sheet with the specified name
            with pd.ExcelWriter(self.output_file_path, engine='openpyxl', mode='a') as writer:
                # Write DataFrame to a new sheet in the existing Excel file
                sheet_name = "wh_cal_" + str(test_id)
                group_channel_dataframe.to_excel(writer, sheet_name=sheet_name, index=False)

            print(f"Data successfully written to sheet '{sheet_name}' in {self.output_file_path}")
            # Add the summary table to the same sheet
            self.add_summary_table(sheet_name, summary_data)

    def fill_cumulative_list(self, source_list):
        cumulative_list = []
        for i in range(len(source_list)):
            if i == 0:
                cumulative_list.append((source_list[i] * 0.1) / 3600)
            else:
                cumulative_list.append(cumulative_list[i-1] + (source_list[i] * 0.1) / 3600)
        return cumulative_list

    def get_data_group_channel_dataframe(self, tdms_file):
            
        group_channel_dataframe = pd.DataFrame()
        no_cycle_wh, udds1_wh, udds2_wh, highway_wh, us06_wh = ([] for i in range(5))
        # Access the 'Data' group
        group_data = tdms_file["Data"]

        # Read the DAQ_Time[s] and P2 channels
        daq_time = group_data["DAQ_Time[s]"].data
        p2_data = group_data["P2"].data
        exhaust_bag = group_data["Exhaust_Bag"].data

        no_cycle = [p2_data[i] if exhaust_bag[i] == 0 else 0 for i in range(len(p2_data))]
        udds1_w =  [p2_data[i] if (exhaust_bag[i] == 1 or exhaust_bag[i] == 2) else 0 for i in range(len(p2_data))]
        udds2_w =  [p2_data[i] if (exhaust_bag[i] == 4 or exhaust_bag[i] == 5) else 0 for i in range(len(p2_data))]
        highway_w = [p2_data[i] if exhaust_bag[i] == 3 else 0 for i in range(len(p2_data))]
        us06_w = [p2_data[i] if (exhaust_bag[i] == 6 or exhaust_bag[i] == 7) else 0 for i in range(len(p2_data))]
        
        no_cycle_wh = self.fill_cumulative_list(no_cycle)
        udds1_wh = self.fill_cumulative_list(udds1_w)
        udds2_wh = self.fill_cumulative_list(udds2_w)
        highway_wh = self.fill_cumulative_list(highway_w)
        us06_wh = self.fill_cumulative_list(us06_w)
        # [no_cycle_wh.append((no_cycle[i] * 0.1) / 3600 if i == 0 else no_cycle_wh[i-1] + (no_cycle[i] * 0.1) / 3600) for i in range(len(p2_data))]
        # [udds1_wh.append(udds1_w[i]*0.1)/3600 if i == 0 else (udds1_wh[i-1] + (udds1_w[i]*0.1/3600)) for i in range(len(p2_data))]
        # [udds2_wh.append(udds2_w[i]*0.1)/3600 if i == 0 else (udds2_wh[i-1] + (udds2_w[i]*0.1/3600)) for i in range(len(p2_data))]
        # [highway_wh.append(highway_w[i]*0.1)/3600 if i == 0 else (highway_wh[i-1] + (highway_w[i]*0.1/3600)) for i in range(len(p2_data))]
        # [us06_wh.append(us06_w[i]*0.1)/3600 if i == 0 else (us06_wh[i-1] + (us06_w[i]*0.1/3600)) for i in range(len(p2_data))]

        u_p_no_cycle = [0 if no_cycle[i] == 0 else ((0.0035 * no_cycle[i]) + 54) for i in range(len(p2_data))]
        u_p_no_cycle_percentage = [0 if no_cycle[i] == 0 else (u_p_no_cycle[i] / no_cycle[i]) for i in range(len(p2_data))]
        u_p_udds1 = [0 if udds1_w[i] == 0 else ((0.0035 * udds1_w[i]) + 54) for i in range(len(p2_data))]
        u_p_udds1_percentage = [0 if udds1_w[i] == 0 else (u_p_udds1[i] / udds1_w[i]) for i in range(len(p2_data))]
        u_p_udds2 = [0 if udds2_w[i] == 0 else ((0.0035 * udds2_w[i]) + 54) for i in range(len(p2_data))]
        u_p_udds2_percentage = [0 if udds2_w[i] == 0 else (u_p_udds2[i] / udds2_w[i]) for i in range(len(p2_data))]
        u_p_highway = [0 if highway_w[i] == 0 else ((0.0035 * highway_w[i]) + 54) for i in range(len(p2_data))]
        u_p_highway_percentage = [0 if highway_w[i] == 0 else (u_p_highway[i] / highway_w[i]) for i in range(len(p2_data))]
        u_p_us06 = [0 if us06_w[i] == 0 else ((0.0035 * us06_w[i]) + 54) for i in range(len(p2_data))]
        u_p_us06_percentage = [0 if us06_w[i] == 0 else (u_p_us06[i] / us06_w[i]) for i in range(len(p2_data))]
        
        # Prepare a DataFrame with the values for easy export to Excel
        group_channel_dataframe = pd.DataFrame({
            "DAQ_Time[s]": daq_time,
            "P2": p2_data,
            "Exhaust_Bag": exhaust_bag,
            "No_cycle": no_cycle,
            "UDDS1_[W]": udds1_w,
            "UDDS2_[W]": udds2_w,
            "Highway_[W]": highway_w,
            "US06_[W]": us06_w,
            "No_cycle_[Wh]": no_cycle_wh,
            "UDDS1_[Wh]": udds1_wh,
            "UDDS2_[Wh]": udds2_wh,
            "Highway_[Wh]": highway_wh,
            "US06_[Wh]": us06_wh,
            "u(P)_no_cycle": u_p_no_cycle,  
            "u(P)_no_cycle_[%]": u_p_no_cycle_percentage,
            "u(P)_UDDS1": u_p_udds1,  
            "u(P)_UDDS1_[%]": u_p_udds1_percentage,
            "u(P)_UDDS2": u_p_udds2,  
            "u(P)_UDDS2_[%]": u_p_udds2_percentage,
            "u(P)_Highway": u_p_highway,  
            "u(P)_Highway_[%]": u_p_highway_percentage,
            "u(P)_US06": u_p_us06,  
            "u(P)_US06_[%]": u_p_us06_percentage   
        })
        
        summary_data = [
            ["SUMMARY (cycle totals)", "No-cycle", "UDDS 1", "UDDS 2", "Highway", "US06", "Tot"],
            ["Energy [Wh]", group_channel_dataframe['No_cycle_[Wh]'].dropna().iloc[-1], 1486.30, 1349.77, 1954.71, 2032.24, 6883.75],
            ["u (Energy)", 11.44, 25.85, 25.33, 18.30, 16.11, 85.59],
            ["u (Energy) [%]", "18.8%", "1.74%", "1.88%", "0.94%", "0.79%", "1.24%"],
            ["u (Energy)", 0.13, 0.24, 0.24, 0.22, 0.28, 0.99],
            ["u (Energy) [%]", "0.22%", "0.02%", "0.02%", "0.01%", "0.01%", "0.01%"]
        ]
        
            
        return group_channel_dataframe, summary_data
    
    def add_summary_table(self, sheet_name, summary_data):
        wb = openpyxl.load_workbook(self.output_file_path)
        sheet = wb[sheet_name]

        # Border style
        thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

        
        # Find the first empty row in the sheet
        start_row = sheet.max_row + 2
        
        # Write the summary data to the sheet
        for row_idx, row_data in enumerate(summary_data, start=start_row):
            for col_idx, cell_value in enumerate(row_data, start=1):
                cell = sheet.cell(row=row_idx, column=col_idx, value=cell_value)
                cell.border = thin_border
        # Save workbook
        wb.save(self.output_file_path)
        wb.close()

    
    