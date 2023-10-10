#include "MessageFrame.h"
#include "BasicSafetyMessage.h"
#include "Common.h"
#include "AddGrpB.h"
#include "AddGrpC.h"

#include "rtxsrc/rtxFile.h"
#include "rtxsrc/rtxPrint.h"
#include "rtxsrc/OSRTFileInputStream.h"
#include "rtxmlsrc/OSXMLDecodeBuffer.h"
#include "rtjsonsrc/OSJSONDecodeBuffer.h"

int main (int argc, char** argv)
{
   int        i, stat;
   OSSIZE     len;
   OSBOOL     trace = TRUE;
   OSBOOL     verbose = FALSE;
   const char* filename = "message.dat";
   const char* infilename = 0;
   const OSOCTET* msgptr;

   /* Process command line arguments */
   if (argc > 1) {
      for (i = 1; i < argc; i++) {
         if (!strcmp (argv[i], "-v")) verbose = TRUE;
         else if (!strcmp (argv[i], "-o")) filename = argv[++i];
         else if (!strcmp (argv[i], "-i")) infilename = argv[++i];
         else if (!strcmp (argv[i], "-notrace")) trace = FALSE;
         else {
            printf ("usage: writer [-v] [-o <filename>]  [-notrace]\n");
            printf ("   -v  verbose mode: print trace info\n");
            printf ("   -o <filename>  write encoded msg to <filename>\n");
            printf ("   -i <filename>  read XER or JSON data from file\n");
            printf ("   -notrace  do not display trace info\n");
            return 1;
         }
      }
   }

   /* Create an instance of the compiler generated class.
      This example uses a dynamic message buffer..*/
   ASN1PEREncodeBuffer encodeBuffer (FALSE);
   encodeBuffer.setTrace (trace);
   encodeBuffer.setDiag (verbose);

   ASN1T_MessageFrame messageFrameData;
   ASN1C_MessageFrame messageFramePDU (messageFrameData);

   if (0 != infilename) {
      // check extension
      const char* extptr = strrchr (infilename, '.');
      if (0 != extptr) {
         if (strcmp (extptr, ".xml") == 0) {
            // XER (XML) file
            OSRTFileInputStream xmlfis (infilename);
            OSXMLDecodeBuffer xerDecStrm (xmlfis);

            stat = xerDecStrm.getStatus();
            if (0 == stat) {
               stat = messageFramePDU.DecodeFrom (xerDecStrm);
            }
            if (0 != stat) {
               printf ("XER decode of MessageFrame failed.\n");
               xerDecStrm.printErrorInfo();
               return stat;
            }
         }
         else if (strcmp (extptr, ".json") == 0) {
            // JSON file
            OSRTFileInputStream jsonfis (infilename);
            OSJSONDecodeBuffer jsonDecStrm (jsonfis);

            stat = messageFramePDU.DecodeFrom (jsonDecStrm);
            if (0 != stat) {
               printf ("JSON decode of MessageFrame failed.\n");
               jsonDecStrm.printErrorInfo();
               return stat;
            }
         }
         else extptr = 0;
      }
      if (0 == extptr) {
         printf ("Input file extension must be .xml or .json\n");
         return -1;
      }
      if (0 == stat) {
         stat = messageFramePDU.EncodeTo(encodeBuffer);
      }
   }
   else {
      ASN1T_BasicSafetyMessage bsm;
      bsm.coreData = new_ASN1T_BSMcoreData(messageFramePDU);
      bsm.coreData->msgCnt = 0;

      const OSOCTET tempID[] = { 0x00, 0x00, 0x00, 0x02 };
      memcpy (bsm.coreData->id.data, tempID, 4);

      bsm.coreData->secMark = 14800;

      bsm.coreData->lat = 0;
      bsm.coreData->long_ = 0;
      bsm.coreData->elev = 0;

      bsm.coreData->accuracy.semiMajor = 255;
      bsm.coreData->accuracy.semiMinor = 255;
      bsm.coreData->accuracy.orientation = 65535;

      bsm.coreData->transmission = TransmissionState::forwardGears;

      bsm.coreData->speed = 716;
      bsm.coreData->heading = 6774;
      bsm.coreData->angle = -1;

      bsm.coreData->accelSet.long_ = 0;
      bsm.coreData->accelSet.lat = 0;
      bsm.coreData->accelSet.vert = 0;
      bsm.coreData->accelSet.yaw = 0;

      ASN1C_BrakeAppliedStatus basC 
         (encodeBuffer, bsm.coreData->brakes.wheelBrakes);
      basC.clear();

      bsm.coreData->brakes.traction = TractionControlStatus::unavailable;
      bsm.coreData->brakes.abs_ = AntiLockBrakeStatus::unavailable;
      bsm.coreData->brakes.scs = StabilityControlStatus::unavailable;
      bsm.coreData->brakes.brakeBoost = BrakeBoostApplied::unavailable;
      bsm.coreData->brakes.auxBrakes = AuxiliaryBrakeStatus::unavailable;

      bsm.coreData->size.width = 230;
      bsm.coreData->size.length = 600;
   
      // Add part II element
      bsm.m.partIIPresent = 1;
      ASN1C_BasicSafetyMessage_partII part2 (encodeBuffer, bsm.partII);
      ASN1T_BasicSafetyMessage_partII_element* pElem = part2.NewElement();
      pElem->partII_Id = 0;
      pElem->partII_Value.t = BSMpartIIExtension::T_vehicleSafetyExt;
      ASN1T_VehicleSafetyExtensions vsExtns;
      vsExtns.m.eventsPresent = 1;
      vsExtns.events.numbits = 2;
      vsExtns.events.data[0] = 0xC0;
      vsExtns.events.data[1] = 0x00;
      pElem->partII_Value.u._BSMpartIIExtension_vehicleSafetyExt = &vsExtns;
      part2.Append (pElem);

      messageFrameData.messageId = ASN1V_basicSafetyMessage;
      messageFrameData.value.t = MessageTypes::T_basicSafetyMessage;
      messageFrameData.value.u._MessageTypes_basicSafetyMessage = &bsm;

      /* Encode */
      stat = messageFramePDU.EncodeTo(encodeBuffer);
   }

   if (0 == stat) {
      if (trace) {
         printf ("Encoding was successful\n");
         printf ("Hex dump of encoded record:\n");
         encodeBuffer.hexDump ();
         printf ("Binary dump:\n");
         encodeBuffer.binDump ("Data");
      }
      msgptr = encodeBuffer.getMsgPtr ();
      len = encodeBuffer.getMsgLen ();
   }
   else
   {
      printf ("Encoding failed\n");
      encodeBuffer.printErrorInfo ();
      return (-1);
   }
   /* Write the encoded message out to the output file */
   stat = rtxFileWriteBinary (filename, msgptr, len);
   if (stat < 0) {
      printf ("Write to file failed, status = %d\n", stat);
      return stat;
   }

   /* Write hex text of encoded message to .hex file for comparisons */
   stat = rtxHexDumpToNamedFile ("message.hex", msgptr, len);
   if (stat < 0) {
      printf ("Write hex text to file message.hex failed, "
              "status = %d\n", stat);
   }

   return stat;
}
