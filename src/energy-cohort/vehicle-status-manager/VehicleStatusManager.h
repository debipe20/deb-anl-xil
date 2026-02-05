/*
**********************************************************************************

VehicleStatusManager.h
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************

Description:
------------
This script:


**********************************************************************************
*/


#pragma once

#include <iostream>
#include <iomanip>
#include <fstream>
#include "Timestamp.h"
#include "json/json.h"
#include "locAware.h"
#include "msgEnum.h"
#include "BasicVehicle.h"
#include "MapManager.h"
#include "SpatManager.h"

using std::cout;
using std::endl;
using std::fixed;
using std::setprecision;
using std::showpoint;
using std::string;
using std::vector;
using std::ofstream;
using std::ifstream;


class VehicleStatusManager
{
private:
    vector<Map::ActiveMap> activeMapList;
    bool activeMapStatus{false};
    int temporaryVehicleID{};
    int vehicleLaneID{};
    int vehicleAprroachID{};
    int intersectionID{};
    int regionalID{};
    int signalGroup{};
    int vehicleIntersectionStatus{};
    double vehicleSpeed{};
    double vehicleDistanceFromStopBar{};
    double minTimeToChange{};
    double maxTimeToChange{};
    string activeIntersectionName{};
    string trafficSignalState{};
    
public:
    VehicleStatusManager();
    ~VehicleStatusManager();
    vector<Map::AvailableMap> availableMapList;
    
    void setIntersectionID(int vehicleNearByIntersectionId);
    void setRegionalID(int vehicleNearByRegionalId);
    void setVehicleID(BasicVehicle basicVehicle);
    void setVehicleSpeed(BasicVehicle basicVehicle);
    void setLaneID(int laneId);
    void setApproachID(int approachID);
    void setSignalGroup(int phaseNo);
    void setVehicleIntersectionStatus(int vehIntersectionStatus);
    void setVehicleDistanceFromStopBar(double vehDistanceFromStopBar);
    void setTrafficSignalState(SpatManager spatManager);
    int getMessageType(string jsonString);
    void getVehicleInformationFromMAP(MapManager mapManager, BasicVehicle basicVehicle);
    vector<Map::ActiveMap> getActiveMapList(MapManager mapManager);
    int getIntersectionID();
    int getRegionalID();
    int getVehicleID();
    double getVehicleSpeed();
    int getLaneID();
    int getApproachID();
    int getSignalGroup();
    int getVehicleIntersectionStatus();
    int getVehicleDistanceFromStopBar();
    string getActiveIntersectionName();
    string getTrafficSignalState();
    double getMinTimeToChange();
    double getMaxTimeToChange();
    vector<Map::AvailableMap> manageMapStatusInAvailableMapList(MapManager mapManager);    
    string createJsonStringForAutomatedDrving();
    bool checkSendUpdateToAutomatedDrving();
};


