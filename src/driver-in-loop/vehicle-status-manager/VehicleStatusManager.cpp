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


#include "AsnJ2735Lib.h"
#include "geoUtils.h"
#include "VehicleStatusManager.h"
#include <algorithm>

using namespace GeoUtils;
using namespace MsgEnum;

VehicleStatusManager::VehicleStatusManager()
{
}

void VehicleStatusManager::setIntersectionID(int vehicleNearByIntersectionId)
{
	intersectionID = vehicleNearByIntersectionId;
}

void VehicleStatusManager::setRegionalID(int vehicleNearByRegionalId)
{
	regionalID = vehicleNearByRegionalId;
}

void VehicleStatusManager::setVehicleID(BasicVehicle basicVehicle)
{
	temporaryVehicleID = basicVehicle.getTemporaryID();
}

void VehicleStatusManager::setVehicleSpeed(BasicVehicle basicVehicle)
{
	vehicleSpeed = basicVehicle.getSpeed_MeterPerSecond();
}

void VehicleStatusManager::setLaneID(int laneId)
{
	vehicleLaneID = laneId;
}

void VehicleStatusManager::setApproachID(int approachID)
{
	vehicleAprroachID = approachID;
}

void VehicleStatusManager::setSignalGroup(int phaseNo)
{
	signalGroup = phaseNo;
}

/*
	-obtain vehicle location in the map-  whether it is in inBound or in intersectionBox or in outBound
*/
void VehicleStatusManager::setVehicleIntersectionStatus(int vehIntersectionStatus)
{
	vehicleIntersectionStatus = vehIntersectionStatus;
}

void VehicleStatusManager::setTrafficSignalState(string jsonString)
{
	Json::Value jsonObject;
	Json::CharReaderBuilder builder;
	Json::CharReader *reader = builder.newCharReader();
	string errors{};

	bool parsingSuccessful = reader->parse(jsonString.c_str(), jsonString.c_str() + jsonString.size(), &jsonObject, &errors);
	delete reader;

	if (parsingSuccessful)
	{
		trafficSignalState = (jsonObject["LightState"]).asString();

		cout << " Set traffic light state is " << trafficSignalState << " for signal group " << signalGroup << endl;
	}
}

/*
	-Get the message type based on the received json string from Transceiver
*/
int VehicleStatusManager::getMessageType(string jsonString)
{
	int messageType{};
	Json::Value jsonObject;
	Json::CharReaderBuilder builder;
	Json::CharReader *reader = builder.newCharReader();
	string errors{};

	bool parsingSuccessful = reader->parse(jsonString.c_str(), jsonString.c_str() + jsonString.size(), &jsonObject, &errors);
	delete reader;

	if (parsingSuccessful)
	{
		if ((jsonObject["MsgType"]).asString() == "MAP")
			messageType = MsgEnum::DSRCmsgID_map;

		else if ((jsonObject["MsgType"]).asString() == "BSM")
			messageType = MsgEnum::DSRCmsgID_bsm;

		else if ((jsonObject["MsgType"]).asString() == "SPaT")
			messageType = MsgEnum::DSRCmsgID_spat;

		else if ((jsonObject["MsgType"]).asString() == "CarlaTrafficLightStatus")
			messageType = static_cast<int>(msgType::carlaTrafficLightStatus);
	}

	return messageType;
}

/*
	-If there is active map, based on the bsm data this function will locate vehicle on the map and obtain inBoundLaneID, inBoundApproachID, distance from the stop-bar and time requires to reach the stop-bar
*/
void VehicleStatusManager::getVehicleInformationFromMAP(MapManager mapManager, BasicVehicle basicVehicle)
{

	string fmap{};
	string intersectionName{};
	bool singleFrame{false}; /// TRUE to encode speed limit in lane, FALSE to encode in approach

	//If active map list is empty, look for active map
	if (activeMapList.empty())
	{
		mapManager.createActiveMapList(basicVehicle);
		getActiveMapList(mapManager);
	}

	//If active map List is not empty, locate vehicle on the map and obtain inBoundLaneID, inBoundApproachID, distance from the stop-bar and time requires to reach the stop-bar
	if (!activeMapList.empty())
	{
		activeMapStatus = true; //This variables will be used by while checking if vehicle needs to send srm or not. If there is active map the value of this variable will true.
		fmap = activeMapList.front().activeMapFileDirectory;
		intersectionName = activeMapList.front().activeMapFileName;

		//initialize mapengine library
		LocAware *plocAwareLib = new LocAware(fmap, singleFrame);

		uint32_t referenceId = plocAwareLib->getIntersectionIdByName(intersectionName);
		uint16_t regionalId = static_cast<uint16_t>((referenceId >> 16) & 0xFFFF);
		uint16_t intersectionId = static_cast<uint16_t>(referenceId & 0xFFFF);

		//get the vehicle data from bsm
		double vehicle_Latitude = basicVehicle.getLatitude_DecimalDegree();
		double vehicle_Longitude = basicVehicle.getLongitude_DecimalDegree();
		double vehicle_Elevation = basicVehicle.getElevation_Meter();
		setVehicleSpeed(basicVehicle);
		double vehicle_Heading = basicVehicle.getHeading_Degree();
		//initialize all the struct require to locate vehicle in Map.
		struct geoPoint_t geoPoint_t_1 = {vehicle_Latitude, vehicle_Longitude, vehicle_Elevation};
		struct motion_t motion_t_1 = {vehicleSpeed, vehicle_Heading};
		struct intersectionTracking_t intersectionTracking_t_1 = {mapLocType::onInbound, 0, 0, 0};
		struct point2D_t point2D_t_1 = {0, 0};
		struct point2D_t point2D_t_2 = {0, 0};
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


		//If vehicle is on Map, update all the information
		if (plocAwareLib->locateVehicleInMap(connectedVehicle_t_1, vehicleTracking_t_1) == true && unsigned(vehicleTracking_t_1.intsectionTrackingState.vehicleIntersectionStatus) == static_cast<int>(MsgEnum::mapLocType::onInbound))
		{
			setVehicleIntersectionStatus(unsigned(vehicleTracking_t_1.intsectionTrackingState.vehicleIntersectionStatus));
			setIntersectionID(intersectionId);
			setRegionalID(regionalId);
			setLaneID(plocAwareLib->getLaneIdByIndexes(unsigned(vehicleTracking_t_1.intsectionTrackingState.intersectionIndex), unsigned(vehicleTracking_t_1.intsectionTrackingState.approachIndex), unsigned(vehicleTracking_t_1.intsectionTrackingState.laneIndex)));
			setApproachID(plocAwareLib->getApproachIdByLaneId(regionalId, intersectionId, (unsigned char)((unsigned)getLaneID())));
			setSignalGroup(plocAwareLib->getControlPhaseByIds(static_cast<uint16_t>(regionalID), static_cast<uint16_t>(intersectionID), static_cast<uint8_t>(vehicleAprroachID), static_cast<uint8_t>(vehicleLaneID))); //Method for obtaining signal group based on vehicle laneID and approachID using MapEngine Library.
			plocAwareLib->getPtDist2D(vehicleTracking_t_1, point2D_t_2);
			vehicleDistanceFromStopBar = unsigned(point2D_t_1.distance2pt(point2D_t_2)); //unit of centimeters
			setVehicleID(basicVehicle); //Vehicle change its ID on a regular basis. Need to check the vehicle id.
			activeIntersectionName = plocAwareLib->getIntersectionNameById(regionalId, intersectionId);
			
			cout << "Intersection Name is: " << activeIntersectionName << endl;
			cout << "Vehicle is on map: " << vehicleIntersectionStatus << endl;
			cout << "Lane id is: " << vehicleLaneID << endl;
			cout << "Approach id is: " << vehicleAprroachID << endl;
			cout << "Signal Group is: " << signalGroup << endl;
 		}
		//If vehicle is not on Map, clear the active map related information
		else
		{
			mapManager.deleteActiveMapfromList();
			activeMapList.clear();
			setIntersectionID(0);
			setSignalGroup(0);
			setLaneID(0);
			setApproachID(0);
			activeMapStatus = false;
		}

		delete plocAwareLib;
	}
	else
		activeMapStatus = false;
}

vector<Map::ActiveMap> VehicleStatusManager::getActiveMapList(MapManager mapManager)
{
	activeMapList = mapManager.getActiveMapList();

	return activeMapList;
}

int VehicleStatusManager::getIntersectionID()
{
	return intersectionID;
}

int VehicleStatusManager::getRegionalID()
{
	return regionalID;
}

int VehicleStatusManager::getVehicleID()
{
	return temporaryVehicleID;
}

double VehicleStatusManager::getVehicleSpeed()
{
	return vehicleSpeed;
}

int VehicleStatusManager::getLaneID()
{
	return vehicleLaneID;
}

int VehicleStatusManager::getApproachID()
{
	return vehicleAprroachID;
}

int VehicleStatusManager::getSignalGroup()
{
	return signalGroup;
}

int VehicleStatusManager::getVehicleDistanceFromStopBar()
{
    return static_cast<int>(std::round(vehicleDistanceFromStopBar / 100));
}

/*
	-Methods for updating map status for HMI
	-If vehicle in on Map then for the active map, activeMapStatus will be true for the active map
	-If vehicle is leaving the map (either leaving the intersection or going to parking lot) then activeMapStatus will be false for all available map
*/
vector<Map::AvailableMap> VehicleStatusManager::manageMapStatusInAvailableMapList(MapManager mapManager)
{
	mapManager.updateMapAge();
	mapManager.deleteMap();
	if (!activeMapList.empty())
	{
		vector<Map::AvailableMap>::iterator findActiveMap = std::find_if(std::begin(mapManager.availableMapList), std::end(mapManager.availableMapList),
																		 [&](Map::AvailableMap const &p)
																		 { return p.availableMapFileName == activeMapList.front().activeMapFileName; });

		if (findActiveMap != availableMapList.end())
			findActiveMap->activeMapStatus = "True";

		availableMapList = mapManager.availableMapList;
	}

	else
	{
		for (size_t i = 0; i < availableMapList.size(); i++)
			availableMapList[i].activeMapStatus = "False";

		availableMapList = mapManager.availableMapList;
	}

	return availableMapList;
}

string VehicleStatusManager::getActiveIntersectionName()
{
	return activeIntersectionName;
}

string VehicleStatusManager::getSignalState()
{
	return trafficSignalState;
}

double VehicleStatusManager::getMinTimeToChange()
{
	return minTimeToChange;
}

double VehicleStatusManager::getMaxTimeToChange()
{
	return maxTimeToChange;
}

string VehicleStatusManager::createJsonStringForDriverInLoopTestManager()
{
	string jsonString{};
	
	Json::Value jsonObject;
	Json::StreamWriterBuilder builder;
	builder["commentStyle"] = "None";
	builder["indentation"] = "";

	jsonObject["MsgType"] = "MapSPaTData";
	jsonObject["Map-SPat-Data"]["IntersectionName"] = getActiveIntersectionName();
	jsonObject["Map-SPat-Data"]["IntersectionDistance"] = getVehicleDistanceFromStopBar();
	jsonObject["Map-SPat-Data"]["SignalGroup"] = getSignalGroup();
	jsonObject["Map-SPat-Data"]["SignalState"] = getSignalState();
	jsonObject["Map-SPat-Data"]["MinTimeToChange"] = getMinTimeToChange();
	jsonObject["Map-SPat-Data"]["MaxTimeToChange"] = getMaxTimeToChange();
	jsonObject["Map-SPat-Data"]["ApproachID"] = getApproachID();
	jsonObject["Map-SPat-Data"]["LaneID"] = getLaneID();		

	jsonString = Json::writeString(builder, jsonObject);
	cout << "Map-SPaT Data is following: \n" << jsonString << endl;
	return jsonString;
}

VehicleStatusManager::~VehicleStatusManager()
{
}