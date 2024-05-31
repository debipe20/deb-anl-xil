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
        
    
if __name__ == "__main__":
    main()