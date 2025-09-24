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
#include "Timestamp.h"

using std::cout;
using std::endl;
using std::begin;
using std::end;
using std::string;
using std::vector;

class SpatManager
{
private:
    int vehicle_intersection_id{};
    int timed_out_intersection_id{};
    vector<TrafficControllerData::AvailableSpat> Available_Spat_List{};
    TrafficControllerData::AvailableSpat spat_info;
    TrafficControllerData::TrafficConrtollerStatus status;

public:
    SpatManager();
    ~SpatManager();
    void manage_spat_data(string json_string);
    bool check_add_spat_data_into_available_spat_list(int spat_id);
    bool check_update_spat_data_into_available_spat_list(int spat_id);
    bool check_delete_timed_out_spat_data_from_available_spat_list();
    void delete_timed_out_spat_data_from_available_spat_list();
    void set_timed_out_intersection_id(int spat_id);
    int get_timed_out_intersection_id();
    double get_current_time_in_seconds();
    string get_signal_phase_status(int active_intersection_id, int signal_group);
};