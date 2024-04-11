import json
from DataManager import DataManager


def main():

    configFile = open("configuration-file.json", "r")
    config = json.load(configFile)
    configFile.close()

    datamanager = DataManager(config)
    datamanager.plotRelativeDistanceAndSpeedProfile()

if __name__ == "__main__":
    main()  