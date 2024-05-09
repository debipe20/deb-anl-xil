from PandaCANDecoder.decoder import Decoder
from diagnostic_signal import Diagnostic
"""
###Choose Signals
Choose signals for which to find a match. Each choice should be a list with the form ['arbid', 'message_start', (start_byte, end_byte), (start_bit, end_bit), scale, offset].

The arbid parameter is required. The message_start is optional, but it is helpful if one arbitration ID corresponds to different messages, e.g.  0x7DA 
corresponds to the current and the voltage of each battery. Specifying that the message begins with  04618A, filters the messages to those 
that only correspond to the current of battery 1. If there is no specific message start, input an empty string ' '.

If no starting/ending points are chosen, defaults to 0 and −1, respectively.

Bytes are indexed starting from  1, while bits are indexed starting from  0.

Choose scale and offset. Defaults to  1 and  0, respectively.
"""

# BYTES INDEXED STARTING AT 1
# BITS INDEXED STARTING AT 0
signals = [['0x245', '', (3, 3), (0, -1), 0.5, 0],
           ['7DA', '04618a', (4, 5), (0, -1), 0.01, -327.68],
           ['7DA', '0x06 61 81', (6, 7), (0, -1), 0.1, 0]]
# signals = [['7DA', '0x066181', (6, 7), (0, -1), 0.1, 0]]

known_signals = [Diagnostic(*signal) for signal in signals]
first_bits_and_lengths = [signal.get_bits() for signal in known_signals]

"""
### Import Data
Takes a path to a .csv file and creates signals based on that path. Columns for the .csv file should be 'TimeStampNs', 'PandaNum', 'MessageID', 'Bus', 'MessageLength', and 'Message'.

A .csv file downloaded directly from VSpy3 will have a lot of extra information. The vspy_processing function in panda_preprocessing.py accepts a .csv file downloaded from VSpy3 and corrects the formatting. 
It creates a new .csv file with 'processing_' prepended to the file name. By default, it deletes the original file, but setting remove=False allows the original file to remain.
"""
# all_data_path = 'can_data/processed_combined_data.csv'
all_data_path = 'can_data/2023_Hyundai_Ioniq5_processed_dat.csv'


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

# Saved as numpy `uint64` array to `./all_time_series_msgs/{msg_id}.npy` for fast reading

# force write all .npy files
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
for i, signal in enumerate(signal_decoders):
    signal.calculate_ref_signal(
        start_bit=first_bits_and_lengths[i][0],
        length=first_bits_and_lengths[i][1],
        factor=known_signals[i].scale,
        offset=known_signals[i].offset,
        gamma=0.2
    )

"""
###Reference PID Signal
This creates a bit flip probability chart for each message of interest. Each signal is represented by a different color. Signedness is represented by the shading, where shaded corresponds to twos complement and unshaded to unsigned.

It should be noted that creating these tables does take some time, somewhere around 5 seconds per plot. Most of the relevant information will also be visible when the signal matching is done, so plotting these tables can be skipped if desired.

It should also be noted that these tables separate messages based only on the message ID and not the start of the message. Thus the table will be the exact same for battery 1 voltage as for battery 2 current. That is something that may be changeable in the future.
"""

# Plot message decoding tool
# for signal in known_signals:
#     can_decoder.plot_message_from_id(signal.arbid)

"""
### Plot Signal Data
Plot the signals corresponding to the arbitration IDs chosen previously.

Note that the number at the end of the signal name for each signal changes  0
  i.e. 'SIG_BE_0', regardless of what the signal number was when plotted in the bit flip table. This does not impact anything else.
"""

# Plot signal data
ref_signals = []
for i, signal in enumerate(signal_decoders):
    ref_signal = signal.get_signal(known_signals[i].arbid, 'SIG_BE_0')
    ref_signals.append(ref_signal)
    signal.plot_signal(ref_signal, known_signals[i].message_start)

"""
###Signal Matching
This step finds signals that match the above signals beyond a specified threshold. That threshold can be adjusted by changing the value of thresh. 
Only the matches with the highest  𝑅2 values will be shown. That number can be changed as well by changing the value of num_matches.
"""

# Signal matching
matches = []
for ref_signal in ref_signals:
    print('*'*88)
    print(ref_signal)
    matches.append(can_decoder.find_signal_match(ref_signal, num_matches=3, thresh=0.95, plot=True))


"""
###Plot Message for Candidate Messages
For each match that was plotted above, the CAN message is shown. Just as before, the colors show where signals end the shaded portions are where two's complement is used.
"""

for i, match in enumerate(matches):
    if len(match) > 0:
        for submatch in match:
            print(f'Match for {submatch[1].msg.msg_id}: {submatch[0].msg.msg_id}, {submatch[0].name}')  
            can_decoder.plot_message_from_id(submatch[0].msg.msg_id)
    else:
        print(f'No matches found for {known_signals[i].arbid} {known_signals[i].message_start[2:]}')