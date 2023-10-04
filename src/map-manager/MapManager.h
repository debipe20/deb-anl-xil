/*
**********************************************************************************

**********************************************************************************
  MapManager.h
  Created by: Debashis Das
  Argonne National Laboratory
  Transportation and Power Systems Division

  Revision History:
  1. This script is header file for MapManager.cpp
*/

#pragma once
#include <iostream>
#include <iomanip>
#include <vector>
#include <string>
#include <fstream>
#include"Map.h"
#include "json/json.h"
#include "BasicVehicle.h"
#include "Position3D.h"
#include "locAware.h"

using std::cout;
using std::endl;
using std::string;
using std::vector;
using std::ofstream;
using std::ifstream;
using std::stringstream;

class MapManager
{
private:
    int intersectinID{};
    string mapPayload{};
    string intersectionMapName{};
    vector<Map::ActiveMap> activeMapList{};
    LocAware *plocAwareLib;

public:
    MapManager();
    ~MapManager();

    vector<Map::AvailableMap> availableMapList{};
    
    int getMessageType(string jsonString);
    void json2MapPayload(string jsonString);
    void writeMAPPayloadInFile();
    bool addToMapInList();
    bool updateMapPayLoadList();
    void maintainAvailableMapList();
    void deleteMapPayLoadFromList();
    void createActiveMapList(BasicVehicle basicVehicle);
    void deleteActiveMapfromList();
    void updateMapAge();
    // void loggingData(string logString);
    // void displayConsoleData(string consoleString);
    void printAvailableMapList();
};
