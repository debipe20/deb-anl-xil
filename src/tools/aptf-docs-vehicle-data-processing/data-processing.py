import copy
import pandas as pd
import json
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

udds_dictionary = {}
HWY_Dictionary = {}
US06_Dictionary = {}
SSS_65_mph_Dictionary = {}



# Define a function to identify description rows
def is_description_row(row):
    return pd.isna(row['Test Time']) and pd.isna(row['Date'])

def dict_to_df(dictionary):
    data_list = []
    for key, entries in dictionary.items():
        for entry in entries:
            data_entry = {k: v[0] for k, v in entry.items()}
            data_entry['Category'] = key
            data_list.append(data_entry)
    df = pd.DataFrame(data_list)
    # Reorder columns to place 'Category' at the start
    columns = ['Category'] + [col for col in df.columns if col != 'Category']
    df = df[columns]
    return df
     
        
# Function to merge cells in the 'Category' column
def merge_category_cells(df, start_row, sheet):
    current_category = None
    start_merge = None
    for idx, row in df.iterrows():
        category = row['Category']
        row_num = start_row + idx
        if category == current_category:
            continue
        if current_category is not None:
            end_merge = row_num
            sheet.merge_cells(start_row=start_merge, start_column=1, end_row=end_merge, end_column=1)
        current_category = category
        start_merge = row_num + 1
    # Merge the last group
    if start_merge is not None:
        sheet.merge_cells(start_row=start_merge, start_column=1, end_row=row_num + 1, end_column=1)


def update_dict(key, value, dictionary, dictionary_name):
        """
        Method to update msg_count_dictionary
        """
        if key in dictionary:
            dictionary[key].append(value)
        else:
            dictionary[key] = [value]
            
        # print(f"Data in {dictionary_name} is:\n{dictionary}")
        
def populate_dictionary(config, df, index_list, desired_subcycle_name, sub_phase_number, iteration_key, dictionary, dictionary_name):
    lists_dict = {f"{field}": [] for field in config['DataFields']}
    
    for index in index_list:
        # print(df.loc[index, 'Cycle'])
        if df.loc[index, 'Cycle'] == desired_subcycle_name:
            for field in config['DataFields']:
                if field in df.columns:
                    lists_dict[f"{field}"].append(df.loc[index, field])
                else:
                    print(f"Field '{field}' does not exist in the dataframe. Skipping this field.")
                
            lists_dict["Sub-Phase"].append(sub_phase_number)
                
    
    update_dict(iteration_key, lists_dict, dictionary, dictionary_name)           
    
    # print("UDDS Dictionary is:", udds_dictionary)
            

def matching_rows(config, df):
    
    
    cycle_type_dicts = {}

    for cycle_type in config["CycleTypes"]:
        for cycle_type_key, cycle_type_value in cycle_type.items():
            dict_name = f"{cycle_type_key}_dictionary" 
            cycle_type_dicts[dict_name] = {}                

   
    sub_cycle_names =  config["SubCycleNames"]
    iteration_keys = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"]
    sub_phase_number = 1
    cycle_name_counter = 0
    iteration_index = 0
    counter_status = True
    cycle_name_completion_status = False
    desired_index_list  =[]
    
    for index, row in df.loc[:].iterrows():
        temp_index_list = []

        if row['Cycle'] == sub_cycle_names[cycle_name_counter]:
            # print(f"Match found at index: {index}")
            
            cycle_name_counter = cycle_name_counter + 1
            counter_status = True
            
            # if row['Cycle'] == ("UDDS 1 , Combined" or "UDDS 2, combined" or "UDDS 3, combined" or "UDDS 4, combined" or "US06 1, combined" or "US06 2, combined" or "SSS 65mph depletion"): 
            # if row['Cycle'] == ("UDDS 1 , Combined" or "UDDS 2, combined" or "UDDS 3, combined" or "UDDS 4, combined"): 
                
            if row['Cycle'] in config["CycleNames"]:
            
                temp_index_list.append(index)
                desired_index_list.append(index)
            
        else: counter_status = False
        
        if counter_status and cycle_name_counter == len(sub_cycle_names):
            counter_status = False
            cycle_name_completion_status = True
            
    
            
            # for dictionary_index, ((dict_name, dictionary), cycle_type) in enumerate(zip(cycle_type_dicts.items(), config["CycleTypes"])):
            for (dict_name, dictionary), cycle_type in zip(cycle_type_dicts.items(), config["CycleTypes"]):
                for key, values in cycle_type.items():
                    for sub_cycle_name in values:
                        if sub_phase_number > 2:
                            sub_phase_number = 1
                        if iteration_index < len(iteration_keys):
                            populate_dictionary(config, df, desired_index_list, sub_cycle_name, sub_phase_number, iteration_keys[iteration_index], dictionary, dict_name)
                        else:
                            print("Not enough iteration keys for all cycle types")
                            break
                        sub_phase_number += 1
            iteration_index += 1
                        
            
            
            
        if not(counter_status)  and cycle_name_counter > 1:
            cycle_name_counter = 0
            desired_index_list.clear()
        
    return cycle_type_dicts
    

def main():
    
    # Read the config file into a json object:
    configFile = open("configuration.json", 'r')
    config = (json.load(configFile))
    configFile.close()
    
    df = pd.read_excel(config["FileName"], sheet_name = config['SheetName'],  skiprows = config["NoOfSkipRows"])


    # Apply the filter to exclude description rows
    filtered_df = df[~df.apply(is_description_row, axis=1)]

    # Printing rows 80-100
    # print(filtered_df.iloc[60:90])

    cycle_type_dicts = matching_rows(config, filtered_df)
    
    # for dictionary_name, dictionary in cycle_type_dicts.items():
    #     print(f"Data in {dictionary_name} is:\n{dictionary}")
    
    # Define the path to save the new file
    output_file_path = 'test_data_with_titles.xlsx'
   
    
    # Create a Pandas Excel writer using openpyxl as the engine
    with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
        start_row = 0
        for dict_name, dictionary in cycle_type_dicts.items():
            # Convert dictionary to DataFrame
            df = dict_to_df(dictionary)
            
            # Add dictionary name before DataFrame
            worksheet = writer.book.create_sheet('Sheet1') if start_row == 0 else writer.sheets['Sheet1']
            worksheet.append([dict_name.split('_')[0].upper()]) if start_row == 0 else worksheet.cell(row=start_row + 1, column=1, value=dict_name.split('_')[0].upper())
            
            # Write the DataFrame to the sheet starting at the next row
            df.to_excel(writer, sheet_name='Sheet1', startrow=start_row + 1, index=False)
            
            # Update start_row for the next dictionary
            start_row += len(df) + 3

    # Load the workbook and access the sheet
    workbook = load_workbook(output_file_path)
    sheet = workbook['Sheet1']
    
    # Merge cells in 'Category' column for each DataFrame
    start_row = 2
    for dict_name, dictionary in cycle_type_dicts.items():
        df = dict_to_df(dictionary)
        merge_category_cells(df, start_row, sheet)
        start_row += len(df) + 3

    # Save the updated workbook
    workbook.save(output_file_path)

    print(f"File created successfully: {output_file_path}")


if __name__ == "__main__":
    main()  

