from nptdms import TdmsFile
import os
def get_groups_channels_name(tdms_file_path):
    tdms_file = TdmsFile.read(tdms_file_path, memmap_dir=None)
    # Get all groups in the TDMS file
    groups = tdms_file.groups()

    # Iterate over groups and print their names and channels
    for group in groups:
        print(f"Group: {group.name}")

        # Get all channels in the current group
        channels = group.channels()
        
        # Iterate over channels in the group and print their names
        for channel in channels:
            print(f"Channel: {channel.name}")

def main():

    directory = r"C:\Users\ddas\Documents\Data\AMTL-Test-Data"  # Use raw string

    if os.path.isdir(directory):
        print("Directory exists")

    tdms_file_path = r"C:\Users\ddas\Documents\Data\AMTL-Test-Data\62005016 Test Data.tdms"
    get_groups_channels_name(tdms_file_path)
    

if __name__ == "__main__":
    main()  