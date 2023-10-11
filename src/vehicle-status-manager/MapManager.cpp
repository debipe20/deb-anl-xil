/*
**********************************************************************************

**********************************************************************************
  MapManager.h
  Created by: Debashis Das
  Argonne National Laboratory
  Transportation and Power Systems Division

  Revision History:
  1. This script is main class for MapManager. It contains definition of the methods.
*/
#include <algorithm>
#include <sys/types.h>
#include <sys/stat.h>
#include "MapManager.h"
#include "Timestamp.h"

using namespace GeoUtils;
using namespace MsgEnum;

const double TIME_GAP_BETWEEN_RECEIVING_MAPPAYLOAD = 300.0;

MapManager::MapManager()
{
    const char *path = "/nojournal/bin/map";
    struct stat sb;

    if (stat(path, &sb) != 0)
        mkdir(path, 0777);
}

/*
	-Get the message type based on the received json string
*/
int MapManager::getMessageType(string jsonString)
{
	int messageType{};
	Json::Value jsonObject;
	Json::CharReaderBuilder builder;
	Json::CharReader *reader = builder.newCharReader();
	string errors{};

	bool parsingSuccessful = reader->parse(jsonString.c_str(), jsonString.c_str() + jsonString.size(), &jsonObject, &errors);
	delete reader;

	if (parsingSuccessful == true)
	{
		if ((jsonObject["MsgType"]).asString() == "MAP")
			messageType = MsgEnum::DSRCmsgID_map;

		else if ((jsonObject["MsgType"]).asString() == "BSM")
			messageType = MsgEnum::DSRCmsgID_bsm;
	}

	return messageType;
}


/*
    -Get uper hex string payload from the received json string
*/
void MapManager::json2MapPayload(string jsonString)
{
    Json::Value jsonObject;
    Json::CharReaderBuilder builder;
    Json::CharReader *reader = builder.newCharReader();
    string errors{};
    bool parsingSuccessful = reader->parse(jsonString.c_str(), jsonString.c_str() + jsonString.size(), &jsonObject, &errors);

    if (parsingSuccessful)
    {
        mapPayload = (jsonObject["MapPayload"]).asString();
        intersectionMapName = (jsonObject["IntersectionName"]).asString();
        intersectinID = (jsonObject["IntersectionID"]).asInt();
    }
    delete reader;
}

/*
    - Method to write the mapPayload in a file based on structure require for map Engine Library.
*/
void MapManager::writeMAPPayloadInFile()
{
    const char *path = "/nojournal/bin/map";    
    stringstream ss{};
    ss << path;
    string pathDirectory{};
    ss >> pathDirectory;
    ofstream outputfile;

    outputfile.open(pathDirectory + "/" + intersectionMapName + ".map.payload");
    outputfile << "payload" << " " << intersectionMapName << " " << mapPayload << endl;
    outputfile.close();
}

/*
    -Check whether mapPayload has to be added in the available map list or not
        --If availableMapList is empty, mapPayload has to be added in the availableMapList
        --If availableMapList is not empty but mapPayload is not in the availableMapList, mapPayload has to be added in the availableMapList
*/
bool MapManager::addToMapInList()
{
    bool addInList{false};
    std::vector<Map::AvailableMap>::iterator findVehicleMapPayLoad = std::find_if(std::begin(availableMapList), std::end(availableMapList),
                                                                                  [&](Map::AvailableMap const &p)
                                                                                  { return p.availableMapPayload == mapPayload; });

    if (mapPayload.size() > 0 && intersectinID > 0)
    {
        if (availableMapList.empty())
            addInList = true;

        else if (findVehicleMapPayLoad == availableMapList.end())
            addInList = true;
    }

    return addInList;
}

/*
    -Check whether mapPayload information has to be updated in the available map list or not
        --If availableMapList is not empty and mapPayload is in the availableMapList, map information will be in the availableMapList
*/
bool MapManager::updateMapPayLoadList()
{
    bool updateMapList{false};
    std::vector<Map::AvailableMap>::iterator findMapPayLoad = std::find_if(std::begin(availableMapList), std::end(availableMapList),
                                                                           [&](Map::AvailableMap const &p)
                                                                           { return p.availableMapPayload == mapPayload; });

    if (availableMapList.empty())
        updateMapList = false;

    else if (findMapPayLoad != availableMapList.end())
        updateMapList = true;

    return updateMapList;
}

/*
    - Check whether mapPayload has to be added in the availableMapList or updated the received time of mapPayload
*/
void MapManager::maintainAvailableMapList() // check Map.h
{
    Map::AvailableMap availableMap;

    if (addToMapInList())
    {
        string mapFileDirectory = "/nojournal/bin/map/" + intersectionMapName + ".map.payload";

        writeMAPPayloadInFile();
        availableMap.availableMapPayload = mapPayload;
        availableMap.availableMapFileName = intersectionMapName;
        availableMap.availableMapFileDirectory = mapFileDirectory;
        availableMap.mapIntersectionID = intersectinID;
        availableMap.mapAge = 1;
        availableMap.mapReceivingTime = getPosixTimestamp();
        availableMap.activeMapStatus = "False";
        availableMapList.insert(availableMapList.begin(), availableMap);
    }

    else if (updateMapPayLoadList())
    {
        vector<Map::AvailableMap>::iterator findMapPayLoad = std::find_if(std::begin(availableMapList), std::end(availableMapList),
                                                                          [&](Map::AvailableMap const &p)
                                                                          { return p.availableMapPayload == mapPayload; });

        findMapPayLoad->availableMapPayload = mapPayload;
        findMapPayLoad->mapAge = 1.0;
        findMapPayLoad->mapReceivingTime = getPosixTimestamp();
    }
}

/*
    -Check whether mapPayload has to be deleted in the available map list or not
        --If time difference between last time mapPayload has been received and elapsed time is atleast 5minutes delete that map.
*/
void MapManager::deleteMapPayLoadFromList()
{

    if (!availableMapList.empty())
    {
        for (size_t i = 0; i < availableMapList.size(); i++)
        {
            if (availableMapList[i].mapAge >= TIME_GAP_BETWEEN_RECEIVING_MAPPAYLOAD)
            {

                vector<Map::AvailableMap>::iterator findMapFileName = std::find_if(std::begin(availableMapList), std::end(availableMapList),
                                                                                   [&](Map::AvailableMap const &p)
                                                                                   { return p.availableMapFileName == availableMapList[i].availableMapFileName; });

                remove(findMapFileName->availableMapFileDirectory.c_str());
                availableMapList.erase(findMapFileName);
                i--;
            }
        }
    }
}

/*
    - This function is for maintaining active map list based on the available map list.
*/
void MapManager::setActiveMapList(BasicVehicle basicVehicle)
{
    Map::ActiveMap activeMap;
    bool singleFrame{false}; /// TRUE to encode speed limit in lane, FALSE to encode in approach
    string fmap{};
    string intersectionName{};

    if (activeMapList.empty() && !availableMapList.empty())
    {
        for (size_t i = 0; i < availableMapList.size(); i++)
        {
            fmap = availableMapList[i].availableMapFileDirectory;
            intersectionName = availableMapList[i].availableMapFileName;
            
            //Initialize mapengine library.
            LocAware *plocAwareLib = new LocAware(fmap, singleFrame);
            // Obtain vehicle information from bsm
            double vehicle_Latitude = basicVehicle.getLatitude_DecimalDegree();
            double vehicle_Longitude = basicVehicle.getLongitude_DecimalDegree();
            double vehicle_Elevation = basicVehicle.getLongitude_DecimalDegree();
            double vehicle_Speed = basicVehicle.getSpeed_MeterPerSecond();
            double vehicle_Heading = basicVehicle.getHeading_Degree();
            // Initialize all struct require to locate vehicle in map by mapengine library.
            struct geoPoint_t geoPoint_t_1 = {vehicle_Latitude, vehicle_Longitude, vehicle_Elevation};
            struct motion_t motion_t_1 = {vehicle_Speed, vehicle_Heading};
            struct intersectionTracking_t intersectionTracking_t_1 = {mapLocType::outside, 0, 0, 0};
            struct projection_t projection_t_1 = {0.0, 0.0, 0.0};
            struct laneProjection_t laneProjection_t_1 = {0, projection_t_1};
            struct vehicleTracking_t vehicleTracking_t_1 = {intersectionTracking_t_1, laneProjection_t_1};
            std::bitset<4> maneuvers;
            struct dist2go_t dist2go_t_1 = {0.0, 0.0};
            struct connectTo_t connectTo_t_1 = {0, 0, 0, maneuverType::straightAhead};
            std::vector<connectTo_t> connect2go1;
            connect2go1.push_back(connectTo_t_1);
            struct locationAware_t locationAware_t_1 = {0, 0, 0, 0, 0.0, maneuvers, dist2go_t_1, connect2go1};
            struct signalAware_t signalAware_t_1 = {phaseColor::dark, phaseState::redLight, unknown_timeDetail, unknown_timeDetail, unknown_timeDetail};
            struct connectedVehicle_t connectedVehicle_t_1 = {0, 0, 0, geoPoint_t_1, motion_t_1, vehicleTracking_t_1, locationAware_t_1, signalAware_t_1};

            if (plocAwareLib->locateVehicleInMap(connectedVehicle_t_1, vehicleTracking_t_1) == true && unsigned(vehicleTracking_t_1.intsectionTrackingState.vehicleIntersectionStatus) == static_cast<int>(MsgEnum::mapLocType::onInbound))
            {
                activeMap.activeMapFileName = intersectionName;
                activeMap.activeMapFileDirectory = fmap;
                activeMapList.push_back(activeMap);
                cout << "Active map is " << intersectionName << endl;
                break;
            }
            delete plocAwareLib;
        }
    }
}

/*
	-If vehicle is out of the intersection, activeMapList has to cleared.
*/
void MapManager::deleteActiveMapfromList()
{
    activeMapList.clear();
}

/*
    - Method to increment the map age based on the current time and the time when map was received
*/
void MapManager::updateMapAge()
{
    for (size_t i = 0; i < availableMapList.size(); i++)
        availableMapList[i].mapAge = availableMapList[i].mapAge + (getPosixTimestamp() - availableMapList[i].mapReceivingTime);
}

/*
    - Getters for Active map List
*/
    vector<Map::ActiveMap> MapManager::getActiveMapList()
{
    return activeMapList;
}

/*
	- Getters for Available map List
*/
vector<Map::AvailableMap> MapManager::getAvailableMapList()
{
    return availableMapList;
}


// /*
// 	- Method for logging data in a file
// */
// void MapManager::loggingData(string logString)
// {
// 	double timeStamp = getPosixTimestamp();

// 	if (logging)
// 	{
// 		logFile << "\n[" << fixed << showpoint << setprecision(4) << timeStamp << "] ";
// 		logFile << logString << endl;
// 	}
// }

// /*
// 	- Method for displaying console output
// */
// void MapManager::displayConsoleData(string consoleString)
// {
// 	double timestamp = getPosixTimestamp();

// 	if (consoleOutput)
// 	{
// 		cout << "\n[" << fixed << showpoint << setprecision(4) << timestamp << "] ";
// 		cout << consoleString << endl;
// 	}
// }

/*
    - This function is for printing availableMapList.
*/
void MapManager::printAvailableMapList()
{
    for (size_t i = 0; i < availableMapList.size(); i++)
        cout << availableMapList[i].availableMapFileName << " " << availableMapList[i].availableMapFileDirectory << " " << availableMapList[i].activeMapStatus << endl;
}

MapManager::~MapManager()
{
}