#pragma once
#include <iostream>
#include <vector>
#include <string>

using std::string;
using std::vector;

namespace TrafficControllerData
{
    struct TrafficConrtollerStatus
    {
        int phase_number{};
        string phase_status{};
        double start_time{};
        double elapsed_time{};
        double min_end_time{};
        double max_end_time{};

        void reset()
        {
            phase_number = 0;
            phase_status = "";
            start_time = 0.0;
            elapsed_time = 0.0;
            min_end_time = 0.0;
            max_end_time = 0.0;
        }
    };

    struct AvailableSpat
    {
        int intersection_id{};
        int regional_id{};
        double update_time{};
        vector<TrafficControllerData::TrafficConrtollerStatus> trafficControllerStatus{};

        void reset()
        {
            intersection_id = 0;
            regional_id = 0;
            update_time = 0.0;
        }
    };
};