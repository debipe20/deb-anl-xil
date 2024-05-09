#%%
import pandas as pd
import numpy as np
import pickle
import sys
import os.path

sys.path.insert(0, '../data_analysis_scion_iq/')

from canData_post_processing import dataProcessing, get_all_data

# Edit csv file to be in PandaCANDecoder-friendly format
def vspy_processing(csv_file, save_file_path='./can_data/processed_data.csv', remove=True):
    """Converts .csv file downloaded from VSpy3 to a format that can be used with PandaCANDecoder. 
        IMPORTANT: Before downloading a .csv file from VSpy3, make sure that 'DW CAN 01' was selected 
        as the network in VSpy. If this is not selected, the processing takes much longer and sometimes 
        the output files have the wrong information"""
    # Read in csv file from location
    data = pd.read_csv(csv_file, skiprows=148)
    data = data.drop(['Line', 'Rel Time (Sec)', 'Status', 'Er', 'Tx', 'Description', 'Node', 'Trgt', 'Src', 'Value', 'Trigger', 'Signals'], axis=1)
    rename_columns = {'Abs Time(Sec)' : 'TimeStampNs', 'Network' : 'PandaNum', 'PT' : 'MessageID'}
    data = data.rename(columns=rename_columns)

    # Edit columns to be in format readable by PandaCANDecoder
    can_data = data.drop(np.where(data['PandaNum']=='neoVI')[0])
    can_data['PandaNum'] = can_data['PandaNum'].replace('DW CAN 01', 0)
    can_data['Bus'] = 0
    can_data['MessageLength'] = 0
    can_data['Message'] = '0x'
    can_data['MessageID'] = can_data['MessageID'].apply(lambda x: f'0x{x}')
    can_data['TimeStampNs'] = can_data['TimeStampNs'] * 1e9

    # Convert individual byte columns into single column containing full message
    byte_list = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8']

    can_data[byte_list] = can_data[byte_list].astype(str)
    can_data[byte_list] = can_data[byte_list].apply(lambda x: x.str.zfill(2))
    can_data['MessageLength'] += (can_data[byte_list] != 'nan').sum(axis=1)
    can_data['MessageID'] = can_data['MessageID'].str.replace('.00E+0', 'E', regex=False)

    def join_bytes(row):
        return ''.join(row)

    can_data['Message'] = can_data[byte_list].apply(join_bytes, axis=1)
    can_data['Message'] = can_data['Message'].str.replace('nan', '')
    can_data['Message'] = '0x' + can_data['Message']

    # Remove the individual byte columns
    processed_can_data = can_data.drop(byte_list, axis=1)

    # Save processed data as csv file
    processed_can_data.to_csv(save_file_path, index=False)

    if remove:
        os.remove(csv_file)

def pickle_processing(pickle_file, save_file_path):
    if not os.path.isfile(save_file_path[:-3] + 'p'):
        pickle_data = decode_raw_can(pickle_file)
        pickle.dump(pickle_data, open(save_file_path[:-3] + 'p', 'wb'))
    else:
        pickle_data = pd.read_pickle(save_file_path[:-3] + 'p')
    # Remove unnecessary columns + rename remaining columns
    use_data = pickle_data[['can_msgs', 'arb_id', 'time_s']]
    use_data = use_data.dropna(axis=1) # Remove extra 'timestamp' column
    rename_columns = {'can_msgs':'Message', 'arb_id':'MessageID', 'time_s':'TimeStampNs'}
    processed_data = use_data.rename(columns=rename_columns)

    # Remove spaces from Message
    processed_data['Message'] = processed_data['Message'].str.replace(' ', '')

    def remove_id(row):
        return '0x' + row[4:]

    processed_data['Message'] = processed_data['Message'].apply(remove_id)

    # Add hex prefix to MessageID
    def remove_leading_zeros(row):
        if row[0] == '0':
            return '0x' + row[1:]
        else:
            return '0x' + row

    processed_data['MessageID'] = processed_data['MessageID'].apply(remove_leading_zeros)
    processed_data['Bus'] = 0
    processed_data['PandaNum'] = 0
    processed_data['MessageLength'] = (processed_data['Message'].str.len() - 2) // 2

    processed_data = processed_data[['TimeStampNs', 'PandaNum', 'MessageID', 'Bus', 'MessageLength', 'Message']]

    processed_data.to_csv(save_file_path, index=False)

def decode_raw_can(file):
    can_data = pd.read_pickle(file)
    all_data, phone_data, combined_data = get_all_data(can_data, can_length=62)
    processed_data = dataProcessing(61, len(all_data), combined_data)
    print('\nData collection done!')

    return processed_data

# Create csv files for battery 1 and battery 2 current and voltage
def split_batteries(csv_file):
    data = pd.read_csv(csv_file)
    # Keep only data that has correct MessageID
    bat_data = data[data['MessageID'] == '0x7DA']

    # Filter and save battery 1 data
    bat1_c_data = bat_data[bat_data['Message'].str.contains('0x04618A')]
    bat1_c_data.to_csv(csv_file[:-4] + '_bat1_c.csv', index=False)
    bat1_v_data = bat_data[bat_data['Message'].str.contains('0x066181')]
    bat1_v_data.to_csv(csv_file[:-4] + '_bat1_v.csv', index=False)

    # Filter and save battery 2 data
    bat2_c_data = bat_data[bat_data['Message'].str.contains('0x04618B')]
    bat2_c_data.to_csv(csv_file[:-4] + '_bat2_c.csv', index=False)
    bat2_v_data = bat_data[bat_data['Message'].str.contains('0x066183')]
    bat2_v_data.to_csv(csv_file[:-4] + '_bat2_v.csv', index=False)

# Create csv file for state of charge
def split_soc(csv_file):
    data = pd.read_csv(csv_file)
    # Keep only data that has correct MessageID
    soc_data = data[data['MessageID'] == '0x74F']
    soc_data.to_csv(csv_file[:-4] + '_soc.csv', index=False)

# Create csv file containing arbitrary MessageID
def split_message_id(csv_file, message_id, message_start=None):
    data = pd.read_csv(csv_file)
    # Keep only data that has correct MessageID
    id_data = data[data['MessageID'] == message_id]

    if message_start != '0x':
        id_data = id_data[id_data['Message'].str.contains(message_start)]
        if id_data.empty:
            raise ValueError(f'No Message with MessageID {message_id} begins with {message_start}')
            
        id_data.to_csv(csv_file[:-4] + f'_{message_id[2:]}{message_start[2:]}.csv', index=False)

    else:
        id_data.to_csv(csv_file[:-4] + f'_{message_id[2:]}.csv', index=False)

if __name__=='__main__':
    pickle_processing('../data_analysis_scion_iq/data/20231030_scion0676_Data.p', './can_data/processed_pickle.csv')
