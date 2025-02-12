import json
from DataManager import DataManager
from AccelerationEnvelopeManager import AccelerationEnvelopeManager

def main():
    # Read the config file into a json object:
    configFile = open("config-files/configuration.json", 'r')
    config = (json.load(configFile))
    configFile.close()

    data_manager = DataManager(config)
    # acceleration_envelope_manager = AccelerationEnvelopeManager(config)
    data_manager.generate_plots()
    # acceleration_envelope_manager.manage_test_data()

if __name__ == "__main__":
    main() 