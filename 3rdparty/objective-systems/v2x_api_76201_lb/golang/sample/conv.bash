#!/bin/bash
# Run the sample program using test data and doing many of the possible
# conversions.

if [[ ! -d temp ]]
then
   mkdir temp
fi

export ROOT=${PWD}/../..
export LIBROOT=${ROOT}/debug/lib
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${LIBROOT}


#  BasicSafetyMessage and JSON
./v2xconv bin2json MessageFrame data/BasicSafetyMessage/message.dat temp/bm.json
./v2xconv json2bin MessageFrame temp/bm.json temp/bm_json.dat
./v2xconv json2bin -hex MessageFrame temp/bm.json temp/bm_json.hex
./v2xconv bin2json -hex MessageFrame temp/bm_json.hex temp/bm_hex.json

# BasicSafetyMessage and XML
./v2xconv bin2xml MessageFrame data/BasicSafetyMessage/message.dat temp/bm.xml
./v2xconv xml2bin MessageFrame temp/bm.xml temp/bm_xml.dat
./v2xconv xml2bin -hex MessageFrame temp/bm.xml temp/bm_xml.hex
./v2xconv bin2xml -hex MessageFrame temp/bm_xml.hex temp/bm_hex.xml

# CAM and JSON
./v2xconv bin2json CAM data/CAMMessage/message.dat temp/cam.json
./v2xconv json2bin CAM temp/cam.json temp/cam_json.dat
./v2xconv json2bin -hex CAM temp/cam.json temp/cam_json.hex
./v2xconv bin2json -hex CAM temp/cam_json.hex temp/cam_hex.json

# CAM and XML
./v2xconv bin2xml CAM data/CAMMessage/message.dat temp/cam.xml
./v2xconv xml2bin CAM temp/cam.xml temp/cam_xml.dat
./v2xconv xml2bin -hex CAM temp/cam.xml temp/cam_xml.hex
./v2xconv bin2xml -hex CAM temp/cam_xml.hex temp/cam_hex.xml

# DENM and JSON
./v2xconv bin2json DENM data/DENMMessage/message.dat temp/denm.json
./v2xconv json2bin DENM temp/denm.json temp/denm_json.dat
./v2xconv json2bin -hex DENM temp/denm.json temp/denm_json.hex
./v2xconv bin2json -hex DENM temp/denm_json.hex temp/denm_hex.json

# DENM and XML
./v2xconv bin2xml DENM data/DENMMessage/message.dat temp/denm.xml
./v2xconv xml2bin DENM temp/denm.xml temp/denm_xml.dat
./v2xconv xml2bin -hex DENM temp/denm.xml temp/denm_xml.hex
./v2xconv bin2xml -hex DENM temp/denm_xml.hex temp/denm_hex.xml