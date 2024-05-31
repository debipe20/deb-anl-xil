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
