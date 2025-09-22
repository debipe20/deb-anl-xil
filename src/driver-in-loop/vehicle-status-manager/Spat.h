#pragma once
#include <iostream>
#include <vector>

using std::vector;

namespace TrafficControllerData
{
    struct TrafficConrtollerStatus
    {
        int phase_number{};
        int phase_status{};
        double start_time{};
        double elapsed_green{};
        double min_end_time{};
        double max_end_time{};
    };
    
    
    struct AvailableSpat
    {
        int intersection_id{};
        int regional_id{};
        vector<TrafficControllerData::TrafficConrtollerStatus> trafficControllerStatus{};
    };
};