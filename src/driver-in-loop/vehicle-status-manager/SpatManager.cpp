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

const double TIME_GAP_BETWEEN_RECEIVING_SPaT = 10;

SpatManager::SpatManager()
{
}

void SpatManager::manage_spat_data(string json_string)
{
    int spat_id{};
    spat_info.reset();

    int minute_of_the_year{};
    int ms_of_minute{};
    double start_time{};
    double min_end_time{};
    double max_end_time{};

    Json::Value jsonObject;
    Json::CharReaderBuilder builder;
    Json::CharReader *reader = builder.newCharReader();
    std::string errors{};

    const bool check_json = reader->parse(json_string.c_str(), json_string.c_str() + json_string.size(), &jsonObject, &errors);
    delete reader;

    if (!check_json)
    {
        std::cerr << "SPaT JSON parse error: " << errors << std::endl;
        return;
    }

    spat_id = (jsonObject["Spat"]["intersectionState"]["intersectionID"]).asInt();
    minute_of_the_year = (jsonObject["Spat"]["minuteOfYear"]).asInt();
    ms_of_minute = (jsonObject["Spat"]["msOfMinute"]).asInt();

    if (check_add_spat_data_into_available_spat_list(spat_id))
    {
        spat_info.intersection_id = spat_id;
        spat_info.regional_id = (jsonObject["Spat"]["intersectionState"]["regionalID"]).asInt();
        spat_info.update_time = get_current_time_in_seconds();

        // Parse phaseState and store in trafficControllerStatus
        const Json::Value &phaseState = jsonObject["Spat"]["phaseState"];
        if (phaseState.isArray())
        {
            spat_info.trafficControllerStatus.clear();
            spat_info.trafficControllerStatus.reserve(phaseState.size()); // Pre-reserve space in vector for efficiency

            for (const auto &phase : phaseState)
            {
                controller_status.reset();

                start_time = phase.get("startTime", 0.0).asDouble();
                min_end_time = phase.get("minEndTime", 0.0).asDouble();
                max_end_time = phase.get("maxEndTime", 0.0).asDouble();
                // elasped_time = phase.get("elaspedTime", 0.0).asInt();

                get_min_max_elapsed_time_in_seconds(minute_of_the_year, ms_of_minute, start_time, min_end_time, max_end_time);

                controller_status.phase_number = phase.get("phaseNo", 0).asInt();
                controller_status.phase_status = phase.get("currState", "").asString();
                // controller_status.start_time = phase.get("startTime", 0.0).asDouble();
                // controller_status.min_end_time = phase.get("minEndTime", 0.0).asDouble();
                // controller_status.max_end_time = phase.get("maxEndTime", 0.0).asDouble();
                // controller_status.elapsed_time = 0.0; // If you need to calculate this, do it here

                controller_status.start_time = start_time_s;
                controller_status.min_end_time = min_end_time_s;
                controller_status.max_end_time = max_end_time_s;
                controller_status.elapsed_time = elasped_time_s;

                // Push the phase status into the trafficControllerStatus vector
                spat_info.trafficControllerStatus.push_back(std::move(controller_status));
            }
        }
        Available_Spat_List.push_back(spat_info);
    }

    else if (check_update_spat_data_into_available_spat_list(spat_id))
    {
        vector<TrafficControllerData::AvailableSpat>::iterator find_intersection_id_in_list = std::find_if(std::begin(Available_Spat_List), std::end(Available_Spat_List),
                                                                                                           [&](TrafficControllerData::AvailableSpat const &p)
                                                                                                           { return p.intersection_id == spat_id; });

        find_intersection_id_in_list->update_time = get_current_time_in_seconds();
        // Parse phaseState and replace in trafficControllerStatus
        const Json::Value &phaseState = jsonObject["Spat"]["phaseState"];
        if (phaseState.isArray())
        {
            find_intersection_id_in_list->trafficControllerStatus.clear();
            spat_info.trafficControllerStatus.reserve(phaseState.size()); // Pre-reserve space in vector for efficiency

            for (const auto &phase : phaseState)
            {
                controller_status.reset();

                start_time = phase.get("startTime", 0.0).asDouble();
                min_end_time = phase.get("minEndTime", 0.0).asDouble();
                max_end_time = phase.get("maxEndTime", 0.0).asDouble();
                // elasped_time = phase.get("elaspedTime", 0.0).asDouble();

                get_min_max_elapsed_time_in_seconds(minute_of_the_year, ms_of_minute, start_time, min_end_time, max_end_time);

                controller_status.phase_number = phase.get("phaseNo", 0).asInt();
                controller_status.phase_status = phase.get("currState", "").asString();
                // controller_status.start_time = phase.get("startTime", 0.0).asDouble();
                // controller_status.min_end_time = phase.get("minEndTime", 0.0).asDouble();
                // controller_status.max_end_time = phase.get("maxEndTime", 0.0).asDouble();
                // controller_status.elapsed_time = 0.0; // If you need to calculate this, do it here

                controller_status.start_time = start_time_s;
                controller_status.min_end_time = min_end_time_s;
                controller_status.max_end_time = max_end_time_s;
                controller_status.elapsed_time = elasped_time_s;

                find_intersection_id_in_list->trafficControllerStatus.push_back(controller_status);
            }
        }
    }
}

/*
    -Check whether spat_id has to be added in the available spat list or not
        --If Available_Spat_List is empty, spat_id has to be added in the Available_Spat_List
        --If avilableSpatList is not empty but spat_id is not in the Available_Spat_List, spat_id has to be added in the Available_Spat_List
*/
bool SpatManager::check_add_spat_data_into_available_spat_list(int spat_id)
{
    bool add_spat_id{false};

    vector<TrafficControllerData::AvailableSpat>::iterator find_spat_id_in_list = std::find_if(begin(Available_Spat_List), end(Available_Spat_List),
                                                                                               [&](TrafficControllerData::AvailableSpat const &p)
                                                                                               { return p.intersection_id == spat_id; });
    if (Available_Spat_List.empty())
        add_spat_id = true;

    else if (!Available_Spat_List.empty() && find_spat_id_in_list == Available_Spat_List.end())
        add_spat_id = true;

    return add_spat_id;
}

/*
    - The following boolean method will determine whether the received spat is required to update in the Available Spat List
    - If spat/intersection ID is present in the Available Spat List the method will return true.
*/
bool SpatManager::check_update_spat_data_into_available_spat_list(int spat_id)
{
    bool update_spat_id{false};

    vector<TrafficControllerData::AvailableSpat>::iterator find_spat_id_in_list = std::find_if(begin(Available_Spat_List), end(Available_Spat_List),
                                                                                               [&](TrafficControllerData::AvailableSpat const &p)
                                                                                               { return p.intersection_id == spat_id; });

    if (Available_Spat_List.empty())
        update_spat_id = false;

    else if (!Available_Spat_List.empty() && find_spat_id_in_list != Available_Spat_List.end())
        update_spat_id = true;

    else if (!Available_Spat_List.empty() && find_spat_id_in_list == Available_Spat_List.end())
        update_spat_id = false;

    return update_spat_id;
}

/*
    - The following boolean method will determine whether received spat is required to delete from the Available Spat List
    - If SPaT is not received from an intersection for more than predefined time(10sec),the method will return true.
    - The method will set the timed out intersection ID
*/
bool SpatManager::check_delete_timed_out_spat_data_from_available_spat_list()
{
    bool delete_spat_info{false};

    if (!Available_Spat_List.empty())
    {
        for (size_t i = 0; i < Available_Spat_List.size(); i++)
        {
            if (get_current_time_in_seconds() - Available_Spat_List[i].update_time > TIME_GAP_BETWEEN_RECEIVING_SPaT)
            {
                delete_spat_info = true;
                set_timed_out_intersection_id(Available_Spat_List[i].intersection_id);
                break;
            }
        }
    }

    return delete_spat_info;
}

/*
    - Method for deleting the timed out SPaT information.
    - The method will find the SPaT information object in Available SPaT List for timed out intersection ID and delete that object.
*/
void SpatManager::delete_timed_out_spat_data_from_available_spat_list()
{
    int spat_id{};

    if (check_delete_timed_out_spat_data_from_available_spat_list())
    {
        spat_id = get_timed_out_intersection_id();

        vector<TrafficControllerData::AvailableSpat>::iterator find_spat_id_in_list = std::find_if(begin(Available_Spat_List), end(Available_Spat_List),
                                                                                                   [&](TrafficControllerData::AvailableSpat const &p)
                                                                                                   { return p.intersection_id == spat_id; });

        if (find_spat_id_in_list != Available_Spat_List.end())
            Available_Spat_List.erase(find_spat_id_in_list);
    }
}

/*
    - Setter for timed out intersection id
*/
void SpatManager::set_timed_out_intersection_id(int spat_id)
{
    timed_out_intersection_id = spat_id;
}

/*
    - Getter for timed out intersection id
*/
int SpatManager::get_timed_out_intersection_id()
{
    return timed_out_intersection_id;
}

/*
    - Method to obtain current time
*/
double SpatManager::get_current_time_in_seconds()
{
    double currentTime = getPosixTimestamp();

    return currentTime;
}

/*
    - Method to obtain phase status for a requested signal group of an intersection
*/
string SpatManager::get_signal_phase_status(int active_intersection_id, int signal_group)
{
    string signal_phase_status{"unknown"};

    vector<TrafficControllerData::AvailableSpat>::iterator find_spat_id_in_list = std::find_if(begin(Available_Spat_List), end(Available_Spat_List),
                                                                                               [&](TrafficControllerData::AvailableSpat const &p)
                                                                                               { return p.intersection_id == active_intersection_id; });
    if (find_spat_id_in_list != Available_Spat_List.end())
    {
        for (size_t i = 0; i < find_spat_id_in_list->trafficControllerStatus.size(); i++)
        {
            if (find_spat_id_in_list->trafficControllerStatus[i].phase_number == signal_group)
            {
                signal_phase_status = find_spat_id_in_list->trafficControllerStatus[i].phase_status;
                break;
            }
        }
    }

    else
    {
        signal_phase_status = "unknown";
    }

    return signal_phase_status;
}

void SpatManager::print_available_spat_list()
{
    double timeStamp = getPosixTimestamp();

    if (!Available_Spat_List.empty())
    {
        for (size_t i = 0; i < Available_Spat_List.size(); i++)
        {
            const auto &spat = Available_Spat_List[i];
            for (size_t j = 0; j < spat.trafficControllerStatus.size(); j++)
            {
                const auto &status = spat.trafficControllerStatus[j];
                cout << spat.intersection_id << "  "
                     << status.phase_number << "  "
                     << status.phase_status << "  "
                     << status.start_time << "  "
                     << status.elapsed_time << "  "
                     << status.min_end_time << "  "
                     << status.max_end_time << "  "
                     << spat.update_time << endl;
            }
        }
    }

    else
        cout << "[" << fixed << showpoint << setprecision(2) << timeStamp << "] Vehicle Availabale Spat List is empty" << endl;
}

/*
    
*/
void SpatManager::get_min_max_elapsed_time_in_seconds(int minute_of_the_year, int ms_of_minute, double start_time, double min_end_time, double max_end_time)
{
    // Small epsilon (1 ms) so values at the exact threshold don't flicker to negative due to jitter
    const double EPS = 1e-3;

    // Current time in seconds since start of the hour
    double now_sec = (minute_of_the_year % 60) * 60.0 + (ms_of_minute / 1000.0);

    // Convert tenths of a second to seconds (inputs are in 0.1s per J2735)
    double min_end_abs = min_end_time / 10.0;
    double max_end_abs = max_end_time / 10.0;

    // Remaining times (never negative), with small epsilon for stability
    min_end_time_s = std::max(0.0, (min_end_abs - now_sec) + EPS);
    max_end_time_s = std::max(0.0, (max_end_abs - now_sec) + EPS);

    // Start and elapsed
    if (start_time >= 0.0 && start_time != 36001.0) 
    {
        start_time_s = start_time / 10.0;

        // Hour wrap: if start appears after "now", assume it began in the previous hour
        if (start_time_s > now_sec)
            start_time_s -= 3600.0;

        elasped_time_s = std::max(0.0, now_sec - start_time_s);
    } 
    
    else 
    {
        start_time_s   = -1.0;
        elasped_time_s = -1.0;
    }
}

SpatManager::~SpatManager()
{
}