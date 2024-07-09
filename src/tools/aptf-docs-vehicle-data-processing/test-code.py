
#Code to create two tables in two excel sheets

# import pandas as pd

# # Create the first DataFrame (Table 1)
# data1 = {
#     'Column1': [1, 2, 3],
#     'Column2': [4, 5, 6],
#     'Column3': [7, 8, 9]
# }
# df1 = pd.DataFrame(data1)

# # Create the second DataFrame (Table 2)
# data2 = {
#     'A': ['foo', 'bar', 'baz'],
#     'B': [10, 20, 30],
#     'C': [100, 200, 300]
# }
# df2 = pd.DataFrame(data2)

# # Define the path to save the new file
# output_file_path = 'two_tables.xlsx'

# # Create a Pandas Excel writer using XlsxWriter as the engine
# with pd.ExcelWriter(output_file_path, engine='xlsxwriter') as writer:
#     # Write each DataFrame to a specific sheet
#     df1.to_excel(writer, sheet_name='Table1', index=False)
#     df2.to_excel(writer, sheet_name='Table2', index=False)

# print(f"File created successfully: {output_file_path}")


######### Code to create two tables in one excel sheet

# import pandas as pd

# # Create the first DataFrame (Table 1)
# data1 = {
#     'Column1': [1, 2, 3],
#     'Column2': [4, 5, 6],
#     'Column3': [7, 8, 9]
# }
# df1 = pd.DataFrame(data1)

# # Create the second DataFrame (Table 2)
# data2 = {
#     'A': ['foo', 'bar', 'baz'],
#     'B': [10, 20, 30],
#     'C': [100, 200, 300]
# }
# df2 = pd.DataFrame(data2)

# # Define the path to save the new file
# output_file_path = 'two_tables_one_sheet.xlsx'

# # Create a Pandas Excel writer using openpyxl as the engine
# with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
#     # Write the first DataFrame to the sheet starting at cell A1
#     df1.to_excel(writer, sheet_name='Sheet1', startrow=0, index=False)
    
#     # Write the second DataFrame to the sheet starting at cell A6 (below the first table)
#     df2.to_excel(writer, sheet_name='Sheet1', startrow=len(df1) + 2, index=False)

# print(f"File created successfully: {output_file_path}")


##### Code to create variables dynamically

# Initialize an empty dictionary to hold the lists
lists_dict = {}

# Create and initialize the lists dynamically
for i in range(1, 6):
    list_name = f"list{i}"
    lists_dict[list_name] = []

# Append data to the lists dynamically
for i in range(1, 6):
    list_name = f"list{i}"
    lists_dict[list_name].append(i * 10)  # Example data to append

# Print the lists
for list_name, data in lists_dict.items():
    print(f"{list_name}: {data}")
