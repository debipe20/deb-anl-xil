from nptdms import TdmsFile


tdms_file = TdmsFile.read("62404016 Test Data.tdms")

groups = tdms_file.groups()

# Iterate over groups and print their names and channels
for group in groups:
    print(f"Group: {group.name}")

    # Get all channels in the current group
    channels = group.channels()
    
    # Iterate over channels in the group and print their names
    for channel in channels:
        print(f"  Channel: {channel.name}")