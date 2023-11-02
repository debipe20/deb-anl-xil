/*
**********************************************************************************

**********************************************************************************
  BsmManger.cpp
  Created by: Debashis Das
  Argonne National Laboratory
  Transportation and Power Systems Division

  Revision History:
  1. This script is main class for BsmManger. It contains definition of the methods.
*/

#include "BsmManager.h"

using namespace GeoUtils;
using namespace MsgEnum;

BsmManager::BsmManager()
{
}

void BsmManager::getVehicleInformationFromMAP(MapManager mapManager, BasicVehicle basicVehicle)
{
    string fmap{};
	string intersectionName{};
	bool singleFrame{false}; /// TRUE to encode speed limit in lane, FALSE to encode in approach


    // If active map list is empty, look for active map
    if (activeMapList.empty())
    {
        mapManager.setActiveMapList(basicVehicle);
        getActiveMapList(mapManager);
    }

    // If active map List is not empty, locate vehicle on the map and obtain inBoundLaneID, inBoundApproachID, distance from the stop-bar and time requires to reach the stop-bar
    if (!activeMapList.empty())
    {
        fmap = activeMapList.front().activeMapFileDirectory;
        intersectionName = activeMapList.front().activeMapFileName;

        //initialize mapengine library
		LocAware *plocAwareLib = new LocAware(fmap, singleFrame);

        uint32_t referenceId = plocAwareLib->getIntersectionIdByName(intersectionName);
        uint16_t regionalId = static_cast<uint16_t>((referenceId >> 16) & 0xFFFF);
        uint16_t intersectionId = static_cast<uint16_t>(referenceId & 0xFFFF);
        setVehicleIntersectionId(intersectionId);

        // get the vehicle data from bsm
        double vehicleLatitude = basicVehicle.getLatitude_DecimalDegree();
        double vehicleLongitude = basicVehicle.getLongitude_DecimalDegree();
        double vehicleElevation = basicVehicle.getElevation_Meter();
        double vehicleSpeed = basicVehicle.getSpeed_MeterPerSecond();
        double vehicleHeading = basicVehicle.getHeading_Degree();
        // initialize all the struct require to locate vehicle in Map.
        struct geoPoint_t geoPoint_t_1 = {vehicleLatitude, vehicleLongitude, vehicleElevation};
        struct motion_t motion_t_1 = {vehicleSpeed, vehicleHeading};
        struct intersectionTracking_t intersectionTracking_t_1 = {mapLocType::onInbound, 0, 0, 0};
        struct projection_t projection_t_1 = {0.0, 0.0, 0.0};
        struct laneProjection_t laneProjection_t_1 = {0, projection_t_1};
        struct vehicleTracking_t vehicleTracking_t_1 = {intersectionTracking_t_1, laneProjection_t_1};
        std::bitset<4> maneuvers;
        struct dist2go_t dist2go_t_1 = {0.0, 0.0};
        struct connectTo_t connectTo_t_1 = {0, 0, 0, maneuverType::straightAhead};
        vector<connectTo_t> connect2go1;
        connect2go1.push_back(connectTo_t_1);
        struct locationAware_t locationAware_t_1 = {0, 0, 0, 0, 0.0, maneuvers, dist2go_t_1, connect2go1};
        struct signalAware_t signalAware_t_1 = {phaseColor::dark, phaseState::redLight, unknown_timeDetail, unknown_timeDetail, unknown_timeDetail};
        struct connectedVehicle_t connectedVehicle_t_1 = {0, 0, 0, geoPoint_t_1, motion_t_1, vehicleTracking_t_1, locationAware_t_1, signalAware_t_1};

        // If vehicle is on Map, update all the information
        if (plocAwareLib->locateVehicleInMap(connectedVehicle_t_1, vehicleTracking_t_1) == true && unsigned(vehicleTracking_t_1.intsectionTrackingState.vehicleIntersectionStatus) == static_cast<int>(MsgEnum::mapLocType::onInbound))
        {
            cout << "Vehicle on Map" << endl;
            int vehicleLaneID = plocAwareLib->getLaneIdByIndexes(unsigned(vehicleTracking_t_1.intsectionTrackingState.intersectionIndex), unsigned(vehicleTracking_t_1.intsectionTrackingState.approachIndex), unsigned(vehicleTracking_t_1.intsectionTrackingState.laneIndex));
            int vehicleApproachID = plocAwareLib->getApproachIdByLaneId(regionalId, intersectionId, static_cast<uint8_t>(vehicleLaneID));
            vehicleSignalGroup = plocAwareLib->getControlPhaseByIds(regionalId, intersectionId, static_cast<uint8_t>(vehicleApproachID), static_cast<uint8_t>(vehicleLaneID));

        }
        // If vehicle is not on Map, clear the active map related information
        else
        {
            mapManager.deleteActiveMapfromList();
            activeMapList.clear();
            vehicleIntersectionId = 0;
            vehicleSignalGroup = 0;
        }
        delete plocAwareLib;
    }
}

void BsmManager::setVehicleIntersectionId(int intersection_id)
{
    vehicleIntersectionId = intersection_id;
}

int BsmManager::getVehicleIntersectionId()
{
    return vehicleIntersectionId;
}

int BsmManager::getVehicleSignalGroup()
{
	return vehicleSignalGroup;
}

vector<Map::ActiveMap> BsmManager::getActiveMapList(MapManager mapManager)
{
    activeMapList = mapManager.getActiveMapList();

    return activeMapList;
}

BsmManager::~BsmManager()
{
}