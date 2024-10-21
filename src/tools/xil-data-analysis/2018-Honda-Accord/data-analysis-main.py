import json
from DataManager import DataManager

def main():
    # Read the config file into a json object:
    configFile = open("config-files/configuration.json", 'r')
    config = (json.load(configFile))
    configFile.close()

    data_manager = DataManager(config)
    data_manager.generate_plots()

if __name__ == "__main__":
    main() 