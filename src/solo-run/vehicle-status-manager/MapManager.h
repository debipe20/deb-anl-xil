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
#include "Map.h"
#include "json/json.h"
#include "Timestamp.h"
#include "BasicVehicle.h"
#include "Position3D.h"
#include "locAware.h"
#include "geoUtils.h"
#include "msgEnum.h"

using std::cout;
using std::endl;
using std::ifstream;
using std::ofstream;
using std::string;
using std::stringstream;
using std::vector;

class MapManager
{
private:
  int intersectinID{};
  string mapPayload{};
  string intersectionMapName{};
  vector<Map::ActiveMap> activeMapList{};

public:
  MapManager();
  ~MapManager();

  vector<Map::AvailableMap> availableMapList{};

  void json2MapPayload(string jsonString);
  void writeMAPPayloadInFile();
  bool addToMapInList();
  bool updateMapPayLoadList();
  void maintainAvailableMapList();
  void deleteMapPayLoadFromList();
  void setActiveMapList(BasicVehicle basicVehicle);
  void deleteActiveMapfromList();
  void updateMapAge();
  vector<Map::ActiveMap> getActiveMapList();
  vector<Map::AvailableMap> getAvailableMapList();
  // void loggingData(string logString);
  // void displayConsoleData(string consoleString);
  void printAvailableMapList();
};
