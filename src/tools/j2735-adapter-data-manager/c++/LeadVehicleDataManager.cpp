#include "LeadVehicleDataManager.h"
#include "BasicVehicle.h"
#include "Timestamp.h"

const double KPH_TO_MPS_CONVERSION = 0.277778;

LeadVehicleDataManager::LeadVehicleDataManager()
{
}

/*
    - Get the message type based on the received json string
*/
int LeadVehicleDataManager::getMessageType(string payload)
{
    int messageType{};
    string subPayload = payload.substr(0, 4);
    std::vector<string> MessageIdentifier{};

    MessageIdentifier = {BSMIdentifier, SPaTIdentifier, MAPIdentifier};

    if (MessageIdentifier.at(0).compare(subPayload) == 0)
        messageType = MsgEnum::DSRCmsgID_bsm;

    else if (MessageIdentifier.at(1).compare(subPayload) == 0)
        messageType = MsgEnum::DSRCmsgID_spat;

    else if (MessageIdentifier.at(2).compare(subPayload) == 0)
        messageType = MsgEnum::DSRCmsgID_map;

    return messageType;
}

string LeadVehicleDataManager::bsmDecoder(string bsmPayload)
{
    BasicVehicle basicVehicle;
    string jsonString{};

    /// buffer to hold message payload
    size_t bufSize = DsrcConstants::maxMsgSize;
    std::vector<uint8_t> buf(bufSize, 0);
    /// dsrcFrameOut to store UPER decoding result
    Frame_element_t dsrcFrameOut;

    string output;
    size_t cnt = bsmPayload.length() / 2;

    for (size_t i = 0; cnt > i; ++i)
    {
        uint32_t s = 0;
        std::stringstream ss;
        ss << std::hex << bsmPayload.substr(i * 2, 2);
        ss >> s;
        output.push_back(static_cast<unsigned char>(s));
    }

    size_t index = 0;
    for (std::vector<uint8_t>::iterator it = buf.begin(); it != buf.end() && index < output.size(); ++it)
    {
        *it = output[index];
        index++;
    }
    size_t payload_size = output.size();
    if (payload_size > 0 && (AsnJ2735Lib::decode_msgFrame(&buf[0], payload_size, dsrcFrameOut) > 0) && (dsrcFrameOut.dsrcMsgId == MsgEnum::DSRCmsgID_bsm))
    {
        BSM_element_t &bsmOut = dsrcFrameOut.bsm;
        basicVehicle.setTemporaryID(bsmOut.id);
        basicVehicle.setSecMark_Second((bsmOut.timeStampSec) / 1000.0);
        basicVehicle.setPosition(DsrcConstants::damega2unit<int32_t>(bsmOut.latitude), DsrcConstants::damega2unit<int32_t>(bsmOut.longitude), DsrcConstants::deca2unit<int32_t>(bsmOut.elevation));
        basicVehicle.setSpeed_MeterPerSecond(round(DsrcConstants::unit2kph<uint16_t>(bsmOut.speed) * KPH_TO_MPS_CONVERSION));
        basicVehicle.setHeading_Degree(round(DsrcConstants::unit2heading<uint16_t>(bsmOut.heading)));
        basicVehicle.setType("0");
        basicVehicle.setLength_cm(bsmOut.vehLen);
        basicVehicle.setWidth_cm(bsmOut.vehWidth);
        jsonString = basicVehicle.basicVehicle2Json();
    }

    return jsonString;
}


LeadVehicleDataManager::~LeadVehicleDataManager()
{
}