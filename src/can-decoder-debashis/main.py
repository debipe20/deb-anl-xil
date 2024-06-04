import json
from DiagnosticSignalManager import Diagnostic
from Decoder import Decoder

def main():
    # BYTES INDEXED STARTING AT 1
    # BITS INDEXED STARTING AT 0
    signals = [['0x245', '', (3, 3), (0, -1), 0.5, 0],
            ['7DA', '04618a', (4, 5), (0, -1), 0.01, -327.68],
            ['7DA', '0x06 61 81', (6, 7), (0, -1), 0.1, 0]]


    known_signals = [Diagnostic(*signal) for signal in signals]
    first_bits_and_lengths = [signal.get_bits() for signal in known_signals]

    """
    ### Import Data
    Takes a path to a .csv file and creates signals based on that path. Columns for the .csv file should be 'TimeStampNs', 'PandaNum', 'MessageID', 'Bus', 'MessageLength', and 'Message'.

    A .csv file downloaded directly from VSpy3 will have a lot of extra information. The vspy_processing function in panda_preprocessing.py accepts a .csv file downloaded from VSpy3 and corrects the formatting. 
    It creates a new .csv file with 'processing_' prepended to the file name. By default, it deletes the original file, but setting remove=False allows the original file to remain.
    """
    all_data_path = 'can_data/processed_combined_data.csv'
    # all_data_path = 'can_data/2023_Hyundai_Ioniq5_processed_dat.csv'
    for signal in known_signals:
        signal.set_data_path(all_data_path)

    can_decoder = Decoder(all_data_path, full_csv=True) # Keep full_csv=True here

    signal_decoders = [Decoder(signal.data_path, full_csv=False) for signal in known_signals] # Set full_csv False
    # Generate message objects
    can_decoder.generate_msgs()
    for signal in signal_decoders:
        signal.generate_msgs()

    # Print messages
    # can_decoder.print_msgs()
    for signal in signal_decoders:
        signal.print_msgs()    

    """
    ### Generate Time Series Data
    can_decoder.generate_msg_ts_data will generate message time series data for all message IDs. These get saved as numpy uint64 arrays to the directory ./all_time_series_msgs/{msg_id}.npy for fast reading. 
    If the data needs to be saved for the first time, this step should take about 8 seconds. If the data has been saved previously, the rewrite argument should be set to False.

    signal.generate_msg_ts_data will generate message time series data only for the message IDs chosen above. This should be fast regardless regardless of whether or not the data has already been saved previously.

    """

    can_decoder.generate_msg_ts_data(rewrite=False)
    print('*'*88)
    for signal in signal_decoders:
        signal.generate_msg_ts_data(full_csv=False, rewrite=True) 

    # # Calculate predicted signals
    can_decoder.calculate_signals(
            tokenization_method='conditional_bit_flip',
            signedness_method='msb_classifier',
            alpha1=0.01,
            alpha2=0.5,
            gamma1=0.2)  

        
if __name__ == "__main__":
    main()