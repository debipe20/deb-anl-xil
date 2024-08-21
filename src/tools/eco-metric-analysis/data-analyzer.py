"""
**********************************************************************************

data-analyzer.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************
  
Description:
------------
  1. This script contains API of DataAnalyzer class to generate plots based on VOICES data log.
"""

import json
from DataAnalyzer import DataAnalyzer

def main():

    configFile = open("configuration.json", "r")
    config = json.load(configFile)
    configFile.close()

    dataAnalyzer = DataAnalyzer(config)
    # dataAnalyzer.plotRelativeDistanceAndSpeedProfileIndividually()
    dataAnalyzer.plotRelativeDistanceAndSpeedProfileJointly()
    dataAnalyzer.plotEgoVehicleSpeedProfile()
    dataAnalyzer.analyzeDynoLog()

if __name__ == "__main__":
    main()  