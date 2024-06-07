import pandas as pd
import json
# Function to create groups based on start and end indices
def create_groups(df, start_indices, end_indices):
    group = 0
    groups = []
    in_group = False
    
    for i in df.index:
        if i in start_indices:
            in_group = True
        if in_group:
            groups.append(group)
        else:
            groups.append(None)
        if i in end_indices:
            in_group = False
            group += 1
            
    return groups

def main():
    configFile = open("configuration.json", "r")
    config = json.load(configFile)
    configFile.close()
    signals = []
    signalInfoList = []
    signalInfoDictionary = {}
    for signalInfo in config["SignalInformation"]:
        signals.append([signalInfo['arbid'], signalInfo['message_start'], (signalInfo['start_byte'], signalInfo['end_byte']), (signalInfo['start_bit'], signalInfo['end_bit']), signalInfo['scale'], signalInfo['offset']])
        # signalInfoList.append([signalInfo['arbid'], signalInfo['message_start'], (signalInfo['start_byte'], signalInfo['end_byte']), (signalInfo['start_bit'], signalInfo['end_bit']), signalInfo['scale'], signalInfo['offset'], signalInfoList['multiframe']])

        signalInfoDictionary = json.dumps({
            "MessageID": signalInfo['arbid'],
            "MultiFrameInfo":{
                "status": signalInfo['multiframe']['status'],
                "startBits": signalInfo['multiframe']['startBits'],
                "endBits": signalInfo['multiframe']['endBits'],
                "discardBitsList": signalInfo['multiframe']['discardBits']
            }
        })
    
    print(signalInfoDictionary)

    all_data_path = config["FileName"]
    df = pd.read_csv(all_data_path)

    # Identify start and end indices
    start_indices = df[df['Message'].str.contains("0x10", case=False)].index
    end_indices = df[df['Message'].str.contains("0x28", case=False)].index

    

    # Add groups column
    df['Group'] = create_groups(df, start_indices, end_indices)

    # Drop rows that are not part of any group
    df_grouped = df.dropna(subset=['Group'])

    # Group by the new column and merge the Message column
    merged_df = df_grouped.groupby('Group').agg({
        'TimeStampNs': 'first',      # You can choose how to aggregate other columns
        'PandaNum': 'first',
        'MessageID': 'first',
        'Bus': 'first',
        'MessageLength': 'sum',     # Or any other aggregation function you need
        'Message': ''.join         # Merge the Message column
    }).reset_index(drop=True)

    print(merged_df)
if __name__ == "__main__":
    main()