/*
**********************************************************************************

SpatManager.h
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
#include <string>
#include <algorithm>
#include "Spat.h"
#include "json/json.h"

using std::cout;
using std::endl;
using std::string;
using std::vector;

class SpatManager
{
private:
    int vehicle_intersection_id{};
    vector<TrafficControllerData::AvailableSpat> available_spat_List{};

public:
    SpatManager();
    ~SpatManager();
    void manage_spat_data(string json_string);
    bool check_add_spat_data_into_List(int spat_id);
};