

# import pandas as pd
# import re

# # Load the file
# file_path = r"C:\Users\ddas\Documents\Data\2023-Hyundai-Ioniq5\On-Road 2025-04-03 07-06-01-920000.csv"


# df = pd.read_csv(file_path)

# # Function to remove units and extract numeric values (including negative and decimal)
# def strip_units(value):
#     if pd.isnull(value):
#         return value
#     match = re.search(r'-?\d+\.?\d*', str(value))
#     return float(match.group()) if match else None

# # Identify columns with potential unit suffixes by checking for common unit patterns
# unit_keywords = ['__A', '__V', '__C', '__rpm', '__Nm', '__mOhm', '__kW', '__kWh', '__Arms', '__kph', '__per', '__m']
# columns_with_units = [col for col in df.columns if any(unit in col for unit in unit_keywords)]

# # Apply cleaning function to the relevant columns
# df_cleaned = df.copy()
# for col in columns_with_units:
#     df_cleaned[col] = df_cleaned[col].apply(strip_units)

# # Save cleaned file
# cleaned_file_path = r"C:\Users\ddas\Documents\Data\2023-Hyundai-Ioniq5\On-Road_Cleaned_NoUnits.csv"
# df_cleaned.to_csv(cleaned_file_path, index=False)

# cleaned_file_path


import pandas as pd
import re

# Load the file
file_path = r"C:\Users\ddas\Documents\Data\2023-Hyundai-Ioniq5\On-Road 2025-04-03 07-06-01-920000.csv"
df = pd.read_csv(file_path)

# Updated function: handles numbers with units like "0.0120 m/s", "41.7042560 degrees"
def strip_units(value):
    if pd.isnull(value):
        return value
    match = re.search(r'-?\d+\.?\d*', str(value))
    return float(match.group()) if match else value

# Updated unit detection: checks for any text after number
def has_unit_pattern(value):
    if pd.isnull(value):
        return False
    value_str = str(value).strip()
    return bool(re.match(r'^-?\d+\.?\d*\s+[^\d\s]+', value_str))  # number followed by space and unit

# Identify columns that contain values with units
general_unit_columns = []
for col in df.columns:
    sample = df[col].dropna().astype(str)
    if not sample.empty:
        match_ratio = sample.apply(has_unit_pattern).mean()
        if match_ratio > 0.7:  # Clean if most entries have units
            general_unit_columns.append(col)

# Apply the cleaning to those columns
df_cleaned = df.copy()
for col in general_unit_columns:
    df_cleaned[col] = df_cleaned[col].apply(strip_units)

# Save cleaned version
output_path = r"C:\Users\ddas\Documents\Data\2023-Hyundai-Ioniq5\On-Road_Cleaned_NoUnits.csv"
df_cleaned.to_csv(output_path, index=False)

print(f"Cleaned file saved to: {output_path}")
