import os
import pandas as pd
from tqdm import tqdm
from Message import Message

class Decoder:
    '''
    Utilities for decoding CAN data
    '''
    def __init__(self, csv_file_path=None, full_csv=True):
        '''
        Decoder constructor

            Parameters:
                csv_file_path (str): File path to csv log
                full_csv (bool): using the full csv file or just select signals
        '''
        self.csv_file_path = csv_file_path
        if full_csv:
            self.time_series_msg_dir = './all_time_series_msgs' 
        else:
            self.time_series_msg_dir = './time_series_msgs'
        self.msgs = []

        # get data
        # remove data (safety check buses 128, 129, and 130) from panda dataFrame
        self.all_data = pd.read_csv(self.csv_file_path)
        self.all_data.drop(self.all_data[
                (self.all_data['Bus'] == 128) |
                (self.all_data['Bus'] == 129) |
                (self.all_data['Bus'] == 130)].index, inplace=True)
        
    
    def generate_msgs(self):
        '''
        - Generates PandaCANDecoder.Message() objects for each unique message in CAN file
            - Create a DataFrame, unique_pairings with unique rows based on ['MessageID', 'PandaNum', 'Bus', 'MessageLength']
            - Generate a list of unique MessageID values in unique_msg_ids.
            - Loops through each msg_id in unique_msg_ids.
                - tqdm is used to display a progress bar for the loop, with the description "Generating messages".
                - desc="Generating messages".ljust(30) ensures the description is left-justified and takes up 30 characters for better alignment in the progress bar.
            - msg_data contains all rows from unique_pairings dataFrame with the same MessageID.
            - Gets unique PandaNum values from msg_data, sorts them, and converts them to a list.
            - Loop iterates over each panda in unique_pandas.
                - Filters msg_data for the current panda, gets the Bus column values, sorts them, and converts them to a list.
                - Adds the panda as a key to panda_buses with its associated list of buses
            - Gets the MessageLength value for the first row of msg_data.
            - Creates a new Message object with the current msg_id, panda_buses, and msg_length.
                - Appends the Message object to self.msgs, which is presumably a list that stores all message objects.
        '''
        
        unique_pairings = self.all_data.drop_duplicates(subset=['MessageID', 'PandaNum', 'Bus', 'MessageLength'])
        unique_msg_ids = unique_pairings['MessageID'].drop_duplicates().to_list()

        for msg_id in tqdm(unique_msg_ids, desc="Generating messages".ljust(30)):
            msg_data = unique_pairings[unique_pairings['MessageID'] == msg_id]

            panda_buses = {}
            unique_pandas = sorted(msg_data['PandaNum'].drop_duplicates().to_list())
            
            for panda in unique_pandas:
                buses = sorted(msg_data[msg_data['PandaNum'] == panda]['Bus'].to_list())
                panda_buses[panda] = buses

            msg_length = msg_data['MessageLength'].iloc[0]

            self.msgs.append(Message(msg_id=msg_id, panda_buses=panda_buses, msg_length=msg_length))

    
    def print_msgs(self):
        '''
        Prints messages available on each Panda and CAN bus combination.
        '''
        if not self.msgs:
            print("WARNING: No messages have been generated. Use Decoder.generate_msgs() to do so.")
            return

        print("-----------------------------------")
        print("Message ID: {Panda Number: [Buses]}")
        print("-----------------------------------")
        for msg in self.msgs:
            print(msg)

    def generate_msg_ts_data(self, full_csv=True, rewrite=False):
        '''
        Saves time series messages as uint64 numpy array to ./time_series_msgs/{msg_id}.npy

            Parameters:
                rewite (bool): If True, will overwrite existing .npy file
        '''
        if not self.msgs:
            print("WARNING: No messages have been generated. Use Decoder.generate_msgs() to do so.")
            return

        # save time series data
        os.makedirs(self.time_series_msg_dir, exist_ok=True)
        for msg in tqdm(self.msgs, desc="Generating message data".ljust(30)):
            msg.generate_ts_data(self.all_data, full_csv, rewrite)

    def calculate_signals(self, tokenization_method, signedness_method, alpha1=0.01, alpha2=0.5, gamma1=0.2):
        '''
        Calculate predicted signals for all messages
        '''
        for msg in tqdm(self.msgs, desc="Generating signals".ljust(30)):
            self.calculate_signal(msg, tokenization_method, signedness_method, alpha1, alpha2, gamma1)

    def calculate_ref_signal(self, start_bit, length, factor, offset, gamma):
        for msg in self.msgs:
            msg.msg_quantity = msg.ts_data.shape[0]
            signal_be = self._tokenize_msg_from_bits(msg, start_bit, length, factor, offset, 'be', gamma)
            signal_le = self._tokenize_msg_from_bits(msg, start_bit, length, factor, offset, 'le', gamma)

            msg.signals = signal_be + signal_le


    def calculate_signal(self, msg, tokenization_method, signedness_method, alpha1=0.01, alpha2=0.5, gamma1=0.2):
        '''
        Calculate signal using multiple methods

        To calculate signal tokenization (boundaries)
        (1) TANG method: "Unsupervised Time Series Extraction from Controller
                Area Network Payloads" by Nolan et. al.
        (2) Conditional Bit Flip method: "CAN-D: A Modular Four-Step Pipeline
                for Comprehensively Decoding Controller Area Network Data" by
                Verma et. al.

        To calculate signedness
        (3) Most Significant Bits method: "CAN-D: A Modular Four-Step Pipeline
                for Comprehensively Decoding Controller Area Network Data" by
                Verma et. al.

            Parameters:
                msg (PandaCANDecoder.Message())
                tokenization_method (str): (1)='tang', (2)='conditional_bit_flip'
                signedness_method (str): (3)='msb_classifier'
                alpha1 (float): hyperparameter for (1) and (2)
                alpha2 (float): hyperparameter for (2)
                gamma1 (float): hyperparameter for (3)
        '''
        # validate methods
        validate_tokenization_method(tokenization_method)
        validate_signedness_method(signedness_method)

        msg.calculate_probability_vectors()

        signals_be = self._tokenize_msg(msg, 'be', tokenization_method, signedness_method, alpha1, alpha2, gamma1)
        signals_le = self._tokenize_msg(msg, 'le', tokenization_method, signedness_method, alpha1, alpha2, gamma1)

        msg.signals = signals_be + signals_le
