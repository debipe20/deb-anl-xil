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


