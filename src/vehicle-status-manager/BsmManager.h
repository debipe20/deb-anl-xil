/*
**********************************************************************************

**********************************************************************************
  BsmManger.h
  Created by: Debashis Das
  Argonne National Laboratory
  Transportation and Power Systems Division

  Revision History:
  1. This script is header file for BsmManger.cpp
*/

#pragma once
#include "MapManager.h"

class BsmManager
{
private:
    int vehicleSignalGroup{};
    vector<Map::ActiveMap> activeMapList;


public:
    BsmManager();
    ~BsmManager();

    void getVehicleInformationFromMAP(MapManager mapManager, BasicVehicle basicVehicle);
    int getSignalGroup();
    vector<Map::ActiveMap> getActiveMapList(MapManager mapManager);
};


