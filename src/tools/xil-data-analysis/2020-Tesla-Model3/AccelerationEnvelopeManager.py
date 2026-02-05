import pandas as pd
import re
import os
import platform
from nptdms import TdmsFile
from PlotManager import PlotManager

g_value = 9.80665

class AccelerationEnvelopeManager:
    def __init__(self, config):
        self.config = config
        self.acc_override_test_file_list = self.config['AccOverrideTestFileList']
        self.stock_acc_test_file_list = self.config['StockAccTestFileList']
        self.acc_override_acceleration = []
        self.acc_override_speed_mps = []
        self.acc_override_speed_mph = []
        self.stock_acc_acceleration = []
        self.stock_acc_speed_mps = []
        self.stock_acc_speed_mph = []

        self.plot_manager = PlotManager(config)

    def get_data_directory(self):
        """
            Method to get the Data directory irrespective of operating system
        """
        current_os = platform.system()

        if current_os == "Linux":
            data_directory = os.path.join(os.path.expanduser("~"), "Downloads", "2020-Tesla-Model3")
        elif current_os == "Windows":
            data_directory = os.path.join("C:\\", "Users", "ddas", "Documents", "Data", "2020-Tesla-Model3")
        else:
            raise OSError(f"Unsupported operating system: {current_os}")
        
        return data_directory

    def get_groups_channels(self):

        self.group_data = self.tdms_file["Data"]

        self.time_channel = self.group_data['Time[s]']
        self.speed_channel_mph = self.group_data['veh_speed'] * 0.621371

        self.time_data = self.time_channel[:]
        self.speed_data_mph = self.speed_channel_mph[:]
        self.speed_data_mps = self.speed_channel_mph[:] * 0.44704
        
    def get_speed_accel_data_from_csv_file(self, file_path):
        """
            Extracts speed data from the CSV file
        """
        calculated_accel = 0
        speed_mph = []
        speed_mps = []
        acceleration_g = []
        accel_list = []
        df = pd.read_csv(file_path)
        # print(df.columns.tolist())
        # df.columns[df.columns.str.contains("Speed", case=False)]

        num_rows = df.shape[0]
        self.time_data = [round(0.1 * i, 1) for i in range(num_rows)]

        # self.time_data = self.time_channel[:]

        # self.speed_data_mps = df['Q5GPS_Speed']
        # self.speed_data_mph = df['Q5GPS_Speed'] * 2.23694    
        self.speed_data_kph = df['wheel_spd_1__rpm']
        self.speed_data_mps = df['wheel_spd_1__rpm'] * 0.277778
        self.speed_data_mph = df['wheel_spd_1__rpm'] * 0.621371   
          
        
        for i in range(1, len(self.speed_data_mps)):
            previous_calculated_accel = calculated_accel
            calculated_accel = (self.speed_data_mps[i] - self.speed_data_mps[i-1]) / (self.time_data[i] - self.time_data[i-1])
            
            # if (calculated_accel > 4):
            #     print("calculated_accel, speed, previous speed, time, previous time, and index: ", calculated_accel, ", ", self.speed_data_mps[i], ", ", self.speed_data_mps[i-1], ", ", self.time_data[i], ", ", self.time_data[i-1], ", ", i)
            
            if (abs(calculated_accel-previous_calculated_accel) >= 0.1):
                speed_mph.append(self.speed_data_mph[i])
                speed_mps.append(self.speed_data_mps[i])
                accel_list.append(calculated_accel)
                acceleration_g.append(calculated_accel / g_value)
        # print("accel_list max: ", max(accel_list))
        return speed_mph, speed_mps, acceleration_g

    def get_acc_data(self):
        """
            Extracts speed and acceleration data
        """
        calculated_accel = 0
        speed_mph = []
        speed_mps = []
        acceleration_g = []

        for i in range(1, len(self.speed_data_mps)):
            previous_calculated_accel = calculated_accel
            calculated_accel = (self.speed_data_mps[i] - self.speed_data_mps[i-1]) / (self.time_data[i] - self.time_data[i-1])
            
            if (abs(calculated_accel-previous_calculated_accel) >= 0.1):
                speed_mph.append(self.speed_channel_mph[i])
                speed_mps.append(self.speed_data_mps[i])
                acceleration_g.append(calculated_accel / g_value)

        return speed_mph, speed_mps, acceleration_g

    def manage_test_data(self):
        data = pd.DataFrame()
        data_directory = self.get_data_directory()
        
        for test_file_name in self.acc_override_test_file_list:
            tdms_file_path = os.path.join(data_directory, test_file_name)

            # Check if the file exists
            if not os.path.isfile(tdms_file_path):
                raise FileNotFoundError(f"No such file: {tdms_file_path}")
            
            self.tdms_file = TdmsFile.read(tdms_file_path)
            self.get_groups_channels()
            speed_mph, speed_mps, acceleration_g = self.get_acc_data()
            self.acc_override_speed_mph.extend(speed_mph)
            self.acc_override_speed_mps.extend(speed_mps)
            self.acc_override_acceleration.extend(acceleration_g)

        for test_file_name in self.stock_acc_test_file_list:
            # tdms_file_path = os.path.join(data_directory, test_file_name)

            # # Check if the file exists
            # if not os.path.isfile(tdms_file_path):
            #     raise FileNotFoundError(f"No such file: {tdms_file_path}")
            
            # self.tdms_file = TdmsFile.read(tdms_file_path)
            # self.get_groups_channels()
            csv_file_path = os.path.join(data_directory, test_file_name)
            # self.csv_file = self.generate_cleaned_csv_file(csv_file_path)
            speed_mph, speed_mps, acceleration_g = self.get_speed_accel_data_from_csv_file(csv_file_path)
      
            self.stock_acc_speed_mph.extend(speed_mph)
            self.stock_acc_speed_mps.extend(speed_mps)
            self.stock_acc_acceleration.extend(acceleration_g)

        self.plot_manager.generate_vehicle_envelope_scatter_plot(self.acc_override_speed_mph, self.acc_override_acceleration, self.stock_acc_speed_mph, self.stock_acc_acceleration)


    def generate_cleaned_csv_file(self, file_path):
        """
            Generates a cleaned CSV file after removing units from the data
            Load a CSV, detect columns with numeric values followed by units, 
            and strip units to retain only numeric values.
            
            Parameters:
                input_path (str): Path to the original CSV file.
                output_path (str): Path to save the cleaned CSV.
                threshold (float): Proportion of unit-pattern values needed to clean a column.
            
            Returns:
                None    
        """
    
        df = pd.read_csv(file_path)

        # Updated function: handles numbers with units like "0.0120 m/s", "41.7042560 degrees"
        def strip_units(value):
            """
            Extract the numeric portion from a string containing a value with units.
            
            Parameters:
                value (str or float): The cell value to clean.
            
            Returns:
                float or original value: The extracted float if a number is found, otherwise the original value.
            """
            if pd.isnull(value):
                return value
            match = re.search(r'-?\d+\.?\d*', str(value))
            return float(match.group()) if match else value

        # Updated unit detection: checks for any text after number
        def has_unit_pattern(value):
            """
            Check whether a value string includes a numeric value followed by a unit.
            
            Parameters:
                value (str): The cell value to evaluate.
            
            Returns:
                bool: True if the pattern matches "number + unit", else False.
            """
            if pd.isnull(value):
                return False
            value_str = str(value).strip()
            return bool(re.match(r'^-?\d+\.?\d*\s+[^\d\s]+', value_str))  # number followed by space and unit

        # Identify columns that contain values with units
        general_unit_columns = []
        for col in df.columns:
            sample = df[col].dropna().astype(str)
            if not sample.empty:
                match_ratio = sample.apply(has_unit_pattern).mean()
                if match_ratio > 0.7:  # Clean if most entries have units
                    general_unit_columns.append(col)

        # Apply the cleaning to those columns
        df_cleaned = df.copy()
        for col in general_unit_columns:
            df_cleaned[col] = df_cleaned[col].apply(strip_units)
    
        df_cleaned.to_csv(file_path, index=False)

        print(f"Cleaned file saved to: {file_path}")

        

'''##############################################
                   Unit testing
##############################################'''
if __name__ == "__main__":
    import json
    configFile = open("config-files/configuration.json", 'r')
    config = (json.load(configFile))
    configFile.close()
    acceleration_envelope_manager = AccelerationEnvelopeManager(config)
    acceleration_envelope_manager.manage_test_data()
    
