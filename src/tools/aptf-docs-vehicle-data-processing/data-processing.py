import pandas as pd


# Define a function to identify description rows
def is_description_row(row):
    return pd.isna(row['Test Time']) and pd.isna(row['Date'])


def matching_rows(df):
    # Define the list of cycle names to check
    cycle_names = [
        "UDDS 1 , 505", "UDDS 1 ", "UDDS 1 , Combined", "HWY 1", "UDDS 2, 505", "UDDS 2", "UDDS 2, combined",
        "US06 1, city", "US06 1, hwy", "US06 1, combined", "SSS 65mph depletion", "US06 2, city", "US06 2, hwy",
        "US06 2, combined", "UDDS 3, 505", "UDDS 3", "UDDS 3, combined", "HWY", "UDDS 4, 505", "UDDS 4",
        "UDDS 4, combined", "SSS 65mph depletion", "Charge L2 23C"
    ]

    cycle_name_counter = 0
    counter_status = True
    cycle_name_completion_status = False
    
        
    for index, value in df['Cycle'].items():
        if value == cycle_names[cycle_name_counter]:
            print(f"Match found at index: {index}")
            
            cycle_name_counter = cycle_name_counter + 1
            counter_status = True
            
        else: counter_status = False
        
        if counter_status and cycle_name_counter > len(cycle_names):
            counter_status = False
            cycle_name_completion_status = True
            
        
        if not(counter_status)  and cycle_name_counter > 1:
            cycle_name_counter = 0
        
    


sheet_name = 'TestSummary'
df=  pd.read_excel('2020_Chevrolet_Bolt_TestPlanInstru_MasterSummary_201005.xlsm', sheet_name = sheet_name,  skiprows=6)


# Apply the filter to exclude description rows
filtered_df = df[~df.apply(is_description_row, axis=1)]

# Display the filtered data
# print(filtered_df.head(100))
# Printing rows 80-100
print(filtered_df.iloc[60:90])

matching_rows(filtered_df)


