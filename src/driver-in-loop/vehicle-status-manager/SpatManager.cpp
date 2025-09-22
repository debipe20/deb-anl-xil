/*
**********************************************************************************

SpatManager.cpp
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************

Description:
------------
This script:


**********************************************************************************
*/

#include "SpatManager.h"

SpatManager::SpatManager()
{
}

void SpatManager::manage_spat_data(string json_string)
{
    int spat_intersection_id{};
    Json::Value jsonObject;
    Json::CharReaderBuilder builder;
    Json::CharReader *reader = builder.newCharReader();
    std::string errors{};

    reader->parse(json_string.c_str(), json_string.c_str() + json_string.size(), &jsonObject, &errors);
    delete reader;

    spat_intersection_id = (jsonObject["Spat"]["IntersectionState"]["intersectionID"]).asInt();
}

/*
    -Check whether spat_id has to be added in the available spat list or not
        --If available_spat_List is empty, spat_id has to be added in the available_spat_List
        --If avilableSpatList is not empty but spat_id is not in the available_spat_List, spat_id has to be added in the available_spat_List
*/
bool SpatManager::check_add_spat_data_into_List(int spat_id)
{
    bool add_spat_id{false};
    
    vector<TrafficControllerData::AvailableSpat>::iterator find_spat_id_in_list = std::find_if(std::begin(available_spat_List), std::end(available_spat_List),
                                                                                               [&](TrafficControllerData::AvailableSpat const &p)
                                                                                               { return p.intersection_id == spat_id; });
    if (available_spat_List.empty())
        add_spat_id = true;

    else if (!available_spat_List.empty() && find_spat_id_in_list == available_spat_List.end())
        add_spat_id = true;

    return add_spat_id;
}

SpatManager::~SpatManager()
{
}