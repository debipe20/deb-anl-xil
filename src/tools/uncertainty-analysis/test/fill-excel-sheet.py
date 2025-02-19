import os
# import sys
# sys.path.append(r"c:\Users\ddas\AppData\Roaming\Python\Python39\site-packages")
# from openpyxl import load_workbook

# def populate_ube_fre(file_path, sheet_name, ube_values, fre_values):
#     # Load the workbook and select the sheet
    
#     wb = load_workbook(file_path)
#     if sheet_name not in wb.sheetnames:
#         print(f"Sheet '{sheet_name}' not found in workbook.")
#         return
    
#     sheet = wb[sheet_name]

#     # Define column letters (adjust if needed)
#     ube_column = "UBE"  # Assuming column X for UBE
#     fre_column = "FRE"  # Assuming column Y for FRE
#     category_column = "Category"  # Assuming column A for Category
    
#     # Iterate through rows and find table boundaries
#     in_table = False
#     for row in range(1, sheet.max_row + 1):
#         print("row value is \n", row)
#         cell_value = sheet[f"{category_column}{row}"].value

#         # Detect start of a table by finding the "Category" header
#         if cell_value == "Category":
#             in_table = True  # Start of a table
#             continue

#         # If we're in a table, populate UBE and FRE based on Category values
#         if in_table:
#             category = sheet[f"{category_column}{row}"].value
#             if category is None:
#                 # End of the current table if Category column is empty
#                 in_table = False
#                 continue

#             # Populate UBE and FRE if category matches
#             if category in ube_values and category in fre_values:
#                 sheet[f"{ube_column}{row}"].value = ube_values[category]
#                 sheet[f"{fre_column}{row}"].value = fre_values[category]

#     # Save the changes
#     wb.save(file_path)
#     wb.close()

# # Example usage:
# # file_path = "2020-tesla-model3-sheet-update.xlsx"
# file_path = os.path.join("..", "Data", "Tesla-Model3", "2020-tesla-model3-sheet-update.xlsx")
# sheet_name = "72F_Cycle_Data_Hioki"
# ube_values = {
#     "1st": 100,  # Replace with actual UBE value for each category
#     "2nd": 200,
#     # Add more categories as needed
# }
# fre_values = {
#     "1st": 300,  # Replace with actual FRE value for each category
#     "2nd": 400,
#     # Add more categories as needed
# }

# populate_ube_fre(file_path, sheet_name, ube_values, fre_values)

import pandas as pd

# Load the Excel file
file_path = os.path.join("..", "Data", "Tesla-Model3", "2020-tesla-model3-sheet-update.xlsx")
sheet_name = '72F_Cycle_Data_Hioki'
data = pd.read_excel(file_path, sheet_name=sheet_name)

# Identify the index of the starting rows
def find_starting_rows(data, keyword):
    """Finds rows that contain specific keywords indicating table start."""
    for i, row in data.iterrows():
        if keyword in row.to_string():
            print("row value is \n", row)
            return i
    return None

# Identify the starting rows using known table indicators
first_table_start = find_starting_rows(data, "Category")  # Common header keyword
second_table_start = find_starting_rows(data.iloc[first_table_start + 1:], "Category") + first_table_start + 1

print(f"First table starts at row: {first_table_start}")
print(f"Second table starts at row: {second_table_start}")

