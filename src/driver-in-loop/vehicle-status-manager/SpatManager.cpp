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
    

    Json::Value jsonObject;
    Json::CharReaderBuilder builder;
    Json::CharReader *reader = builder.newCharReader();
    std::string errors{};

    reader->parse(json_string.c_str(), json_string.c_str() + json_string.size(), &jsonObject, &errors);
    delete reader;

    spat_id = (jsonObject["Spat"]["IntersectionState"]["intersectionID"]).asInt();

    if(check_add_spat_data_into_available_spat_list(spat_id))
    {
        spat_info.intersection_id = spat_id;
        spat_info.regional_id = (jsonObject["Spat"]["IntersectionState"]["regionalID"]).asInt();
        spat_info.update_time = get_current_time_in_seconds();
        // spat_info.trafficControllerStatus = 

        // Parse phaseState and store in trafficControllerStatus
        const Json::Value& phaseState = jsonObject["Spat"]["phaseState"];
        if (phaseState.isArray())
        {
            spat_info.trafficControllerStatus.reserve(phaseState.size());  // Pre-reserve space in vector for efficiency

            for (const auto& phase : phaseState)
            {
                status.reset();

                status.phase_number = phase.get("phaseNo", 0).asInt();
                status.phase_status = phase.get("currState", "").asString();
                status.start_time = phase.get("startTime", 0.0).asDouble();
                status.min_end_time = phase.get("minEndTime", 0.0).asDouble();
                status.max_end_time = phase.get("maxEndTime", 0.0).asDouble();
                status.elapsed_time = 0.0;  // If you need to calculate this, do it here

                // Push the phase status into the trafficControllerStatus vector
                spat_info.trafficControllerStatus.push_back(std::move(status));
            }
        }
    }
}

// void SpatManager::set_intersection_controller_staus():
// {

// }

/*
    -Check whether spat_id has to be added in the available spat list or not
        --If Available_Spat_List is empty, spat_id has to be added in the Available_Spat_List
        --If avilableSpatList is not empty but spat_id is not in the Available_Spat_List, spat_id has to be added in the Available_Spat_List
*/
bool SpatManager::check_add_spat_data_into_available_spat_list(int spat_id)
{
    bool add_spat_id{false};

    vector<TrafficControllerData::AvailableSpat>::iterator find_spat_id_in_list = std::find_if(begin(Available_Spat_List),end(Available_Spat_List),
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

    vector<TrafficControllerData::AvailableSpat>::iterator find_spat_id_in_list = std::find_if(begin(Available_Spat_List),end(Available_Spat_List),
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

        vector<TrafficControllerData::AvailableSpat>::iterator find_spat_id_in_list = std::find_if(begin(Available_Spat_List),end(Available_Spat_List),
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

SpatManager::~SpatManager()
{
}