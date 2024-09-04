from nptdms import TdmsFile

# Define the path to your TDMS file using a raw string literal (r"...")
file_path = r"C:\Users\ddas\Documents\62007023 Test Data.tdms"

# Load the TDMS file with memory mapping disabled
tdms_file = TdmsFile.read(file_path, memmap_dir=None)

# Print all groups and their channels
for group in tdms_file.groups():
    print(f"Group: {group.name}")
    for channel in group.channels():
        print(f"  Channel: {channel.name}")
