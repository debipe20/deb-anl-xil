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
#include <vector>
#include <string>
#include"Map.h"

using std::cout;
using std::endl;
using std::string;
using std::vector;

class MapManager
{
private:
    int intersectinID{};
    string mapPayload{};
    string intersectionMapName{};

public:
    MapManager();
    ~MapManager();

    vector<Map::AvailableMap> availableMapList{};

    void json2MapPayload(string jsonString);
    bool addToMapInList();
    bool updateMapPayLoadList();
    bool deleteMapPayLoadFromList();
};
