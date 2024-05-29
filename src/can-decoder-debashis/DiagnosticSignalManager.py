import os
import pandas as pd

class Diagnostic:
    def __init__(self, arbid, message_start = '', start_end_bytes = (1, -1), start_end_bits = (0, -1), scale=1, offset=0):
        self.arbid = arbid
        self.message_start = message_start
        self.start_byte = start_end_bytes[0]
        self.end_byte = start_end_bytes[1]
        self.start_bit = start_end_bits[0]
        self.end_bit = start_end_bits[1]
        self.scale = scale
        self.offset = offset
        self.data_path = None
        
        self.check_arbid()
        self.check_message_start()
        self.check_bytes_and_bits()
        
        
    def check_arbid(self):
        """Adjusts arbitration ID to be in proper format"""
        
        prefix = '0x'
        message_id = self.arbid.replace(' ', '') # replaces each space with an empty string to remove q all spaces.
        
        if self.arbid[:2] == prefix:
            message_id = message_id[2:]
        
        while message_id and message_id[0] == '0':
            message_id = message_id[1:]
        
        if len(message_id) < 2 or len(message_id) > 3:  # All message ids should be 2 or 3 characters long
            raise ValueError(f'Invalid Arbitration ID ({self.arbid})')

        self.arbid = prefix + message_id.upper()

    def check_message_start(self):
        """Ensures message_start is properly formatted"""
        
        prefix = '0x'
        message_start = self.message_start.replace(' ', '') # replaces each space with an empty string to remove q all spaces.
        
        if self.message_start[:2] == prefix: # This checks if the first two characters of self.message_start are equal to prefix.
            message_start = message_start[2:]

        self.message_start = prefix + message_start.upper()

    def check_bytes_and_bits(self):
        """Make sure bytes and bits are in range"""
        
        if type(self.start_byte) is not int or type(self.end_byte) is not int:
            raise TypeError('start_byte and end_byte must be type int')
        
        if type(self.start_bit) is not int or type(self.end_bit) is not int:
            raise TypeError('start_bit and end_bit must be type int')
        
        if self.start_byte < 1 or self.start_byte > 8:
            raise ValueError('start_byte must be between 1 and 8')
        
        if (self.end_byte < 1 and self.end_byte != -1) or self.end_byte > 8:
            raise ValueError('end_byte must be between 1 and 8, or -1')
        
        if self.start_bit < 0 or self.start_bit > 7:
            raise ValueError('start_bit must be between 0 and 7')
        
        if self.end_bit < -1 or self.end_bit > 7:
            raise ValueError('end_bit must be between 0 and 7, or -1')
        
        if self.start_byte > self.end_byte and self.end_byte != -1:
            raise ValueError('end_byte must be greater than or equal to start_byte')

    def get_bits(self):
        """Gets indices of bits in 64-bit message (bytes indexed starting at 1, bits starting at 0)"""
        
        first_bit = 8*(self.start_byte) - self.start_bit - 1
        
        if self.end_bit == -1:
            last_bit = 8*(self.end_byte)
            length = last_bit - (8*(self.start_byte - 1) + self.start_bit - 1) - 1
        
        else:
            last_bit = 8*(self.end_byte-1) + self.end_bit
            length = last_bit - (8*(self.start_byte - 1) + self.start_bit - 1) - 1
        
        return first_bit, length
    
    def set_data_path(self, data_path):
        """Sets data_path and creates csv file if necessary"""
        
        self.data_path = f'{data_path[:-4]}_{self.arbid[2:]}{self.message_start[2:]}.csv'
        
        if not os.path.isfile(self.data_path):
            self.split_message_id(data_path, self.arbid, self.message_start)
            
    # Create csv file that contains arbitration MessageID and Message starts with message_start value
    def split_message_id(self, csv_file, message_id, message_start=None):
        data = pd.read_csv(csv_file)
        # Keep only data that has correct MessageID
        id_data = data[data['MessageID'] == message_id]

        if message_start != '0x':
            id_data = id_data[id_data['Message'].str.startswith(message_start)]
            if id_data.empty:
                raise ValueError(f'No Message with MessageID {message_id} begins with {message_start}')
                
            id_data.to_csv(csv_file[:-4] + f'_{message_id[2:]}{message_start[2:]}.csv', index=False)

        else:
            id_data.to_csv(csv_file[:-4] + f'_{message_id[2:]}.csv', index=False)