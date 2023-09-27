#include "MapManager.h"
#include "json/json.h"

const double TIME_GAP_BETWEEN_RECEIVING_MAPPAYLOAD = 300.0;

MapManager::MapManager()
{
}


/*
    -Get uper hex string payload from the received json string
*/
void MapManager::json2MapPayload(string jsonString)
{
    Json::Value jsonObject;
    Json::CharReaderBuilder builder;
    Json::CharReader * reader = builder.newCharReader();
    string errors{};
    bool parsingSuccessful = reader->parse(jsonString.c_str(), jsonString.c_str() + jsonString.size(), &jsonObject, &errors);
    
    if(parsingSuccessful)
    {    
        mapPayload = (jsonObject["MapPayload"]).asString();
        intersectionMapName = (jsonObject["IntersectionName"]).asString();
        intersectinID = (jsonObject["IntersectionID"]).asInt();
    }
    delete reader;
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
                                                                                  [&](Map::AvailableMap const &p) { return p.availableMapPayload == mapPayload; });

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
                                                                           [&](Map::AvailableMap const &p) { return p.availableMapPayload == mapPayload; });

    if (availableMapList.empty())
        updateMapList = false;

    else if (findMapPayLoad != availableMapList.end())
        updateMapList = true;

    return updateMapList;
}


/*
    -Check whether mapPayload has to be deleted in the available map list or not
        --If time difference between last time mapPpayload has been received and elapsed time is atleast 5minutes delete that map.
*/
bool MapManager::deleteMapPayLoadFromList()
{
    bool deleteMapPayload{false};

    if (!availableMapList.empty())
    {
        for (size_t i = 0; i < availableMapList.size(); i++)
        {
            if (availableMapList[i].mapAge >= TIME_GAP_BETWEEN_RECEIVING_MAPPAYLOAD) //If year changed getMapPayloadReceivedTime() will less than availableMapList[i].minuteOfYear. Thus, abs() is used.
            {
                deleteMapPayload = true;
                setTimedOutMapPayLoad(availableMapList[i].availableMapPayload);
                break;
            }
        }
    }

    return deleteMapPayload;
}

MapManager::~MapManager()
{
}