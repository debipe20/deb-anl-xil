import pandas as pd

# Define the file path
file_path = "Speed_Profiles_Master.xlsx"

# Load the Excel file and check available sheet names
xls = pd.ExcelFile(file_path)

# Display available sheet names
print(xls.sheet_names)


# Load the specified sheet
sheet_name = "Extra Short Time Gap"
df = pd.read_excel(file_path, sheet_name=sheet_name)

# # Select the required columns
# columns_to_print = ["Lead Speed [mps]", "Simulated Ego Spd [mps]"]
# if all(col in df.columns for col in columns_to_print):
#     print(df[columns_to_print])
# else:
#     print("One or more specified columns are not found in the sheet.")

for index, row in df.iterrows():
    lead_speed = row["Lead Speed [mps]"]
    ego_speed = row["Simulated Ego Spd [mps]"]
    print(f"Row {index}: Lead Speed = {lead_speed}, Simulated Ego Speed = {ego_speed}")
