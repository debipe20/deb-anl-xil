
import os, platform

class DataManager:
    def __init__(self, config):
        self.config = config
        self.vehicle_name = self.config['VehicleName']
        
        
    def get_data_directory(self):
        """
            Method to get the Data directory irrespective of operating system
        """
        current_os = platform.system()

        if current_os == "Linux":
            data_directory = os.path.join(os.path.expanduser("~"), "Downloads", self.vehicle_name)
        elif current_os == "Windows":
            data_directory = os.path.join("C:\\", "Users", "ddas", "Documents", "Data", self.vehicle_name)
        else:
            raise OSError(f"Unsupported operating system: {current_os}")
        
        return data_directory
        
'''##############################################
                   Unit testing
##############################################'''
if __name__ == "__main__":
    import json
    configFile = open("config-files/configuration.json", 'r')
    config = (json.load(configFile))
    configFile.close()
    data_manager = DataManager(config)