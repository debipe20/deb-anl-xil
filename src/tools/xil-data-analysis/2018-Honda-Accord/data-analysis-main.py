import json
from nptdms import TdmsFile

def main():
    # Read the config file into a json object:
    configFile = open("config-files/configuration.json", 'r')
    config = (json.load(configFile))
    configFile.close()

if __name__ == "__main__":
    main() 