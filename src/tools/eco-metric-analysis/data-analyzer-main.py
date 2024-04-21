import json
from DataManager import DataManager


def main():

    configFile = open("configuration.json", "r")
    config = json.load(configFile)
    configFile.close()

    datamanager = DataManager(config)
    # datamanager.plotRelativeDistanceAndSpeedProfileIndividually()
    datamanager.plotRelativeDistanceAndSpeedProfileJointly()
    datamanager.plotEgoVehicleSpeedProfile()
    datamanager.analyzeDynoLog()

if __name__ == "__main__":
    main()  