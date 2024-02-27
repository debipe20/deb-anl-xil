#pragma once
#include <iostream>
#include <iomanip>
#include <vector>
#include <string>
#include <fstream>
#include "json/json.h"
#include "AsnJ2735Lib.h"
#include "locAware.h"
#include "dsrcConsts.h"
#include "msgEnum.h"

using std::cout;
using std::endl;
using std::fstream;
using std::ifstream;
using std::ios;
using std::ofstream;
using std::string;
using std::stringstream;
using std::vector;
using std::fixed;
using std::setprecision;
using std::showpoint;

class LeadVehicleDataManager
{
private:
    string BSMIdentifier = "0014";
    string SPaTIdentifier = "0013";
    string MAPIdentifier ="0012";
    
    
public:
    LeadVehicleDataManager();
    ~LeadVehicleDataManager();

    int getMessageType(string payload);
    string bsmDecoder(string bsmPayload);
};


