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
#include <iomanip> 
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
using std::fixed;
using std::showpoint;
using std::setprecision;

class SpatManager
{
private:
    int timed_out_intersection_id{};
    double start_time_s{};
    double min_end_time_s{};
    double max_end_time_s{};
    double elasped_time_s{};
    
    TrafficControllerData::AvailableSpat spat_info;
    TrafficControllerData::TrafficConrtollerStatus controller_status;

public:
    SpatManager();
    ~SpatManager();
    vector<TrafficControllerData::AvailableSpat> Available_Spat_List{};
    void manage_spat_data(string json_string);
    bool check_add_spat_data_into_available_spat_list(int spat_id);
    bool check_update_spat_data_into_available_spat_list(int spat_id);
    bool check_delete_timed_out_spat_data_from_available_spat_list();
    void delete_timed_out_spat_data_from_available_spat_list();
    void set_timed_out_intersection_id(int spat_id);
    int get_timed_out_intersection_id();
    double get_current_time_in_seconds();
    string get_signal_phase_status(int active_intersection_id, int signal_group);
    void print_available_spat_list();
    void get_min_max_elapsed_time_in_seconds(int minute_of_the_year, int ms_of_minute, double start_time, double min_end_time, double max_end_time);
};