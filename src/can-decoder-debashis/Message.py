import os
import numpy as np

class Message:
    '''
    CAN message

        Attributes:
            msg_id (string): hex value
            pandas (dict{int: list[int]})
            buses (list[int])
            msg_length (int): bytes
            msg_quantity (int)
            tang (np.array[int])
            msg_ts_data (np.array[uint64])
            signal_boundaries (list[int])
    '''
    time_series_msg_dir = './time_series_msgs' # TODO: change
    all_time_series_msgs_dir = './all_time_series_msgs'

    def __init__(self, msg_id, panda_buses, msg_length):
        self.msg_id = msg_id
        self.panda_buses = panda_buses
        self.msg_length = msg_length # bytes
        self.msg_quantity = None

        self.bf_probability_be = None
        self.bf_probability_le = None

        self.conditional_bf_probability_be = None
        self.conditional_bf_probability_le = None

        self.name = ""
        self.signals = None

        self.ts_data = None

    def __repr__(self):
        '''
        Override print string
        '''
        return f"Message {self.msg_id}: {self.panda_buses}"
    

    def generate_ts_data(self, all_data, full_csv=True, rewrite=False):
        '''
        Generate time series message data and set to self.ts_data. Save data to
        numpy file for easy recall if it does not exist

        Parameters:
            all_data (Pandas.DataFrame)
        '''
        if full_csv:
            data_path = os.path.join(self.all_time_series_msgs_dir, self.msg_id + '.npy')
        else:
            data_path = os.path.join(self.time_series_msg_dir, self.msg_id + '.npy')

        # if data file does not exist or rewrite is True
        if not os.path.exists(data_path) or rewrite:
            panda = list(self.panda_buses.keys())[0]
            bus = self.panda_buses[panda][0]

            time_series_msg = all_data[
                (all_data['PandaNum'] == panda) &
                (all_data['Bus'] == bus) &
                (all_data['MessageID'] == self.msg_id)][['TimeStampNs', 'Message']]

            # Print memory usage of DataFrame
            # print("DataFrame Memory Usage (Before Conversion):")
            # print(time_series_msg.memory_usage())

            # Convert hexadecimal strings to integers
            time_series_msg['Message'] = time_series_msg['Message'].apply(lambda x: int(x, 16))

            # Save as object dtype to handle larger integers
            np.save(data_path, time_series_msg.to_numpy(dtype=object))

        self.ts_data = np.load(data_path, allow_pickle=True)
