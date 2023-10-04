/**
 * Sample program that reads and decodes a DSRC BasicSafetyMessage from 
 * a file.  The contents are then output in JSON and XER formats.
 */
#include "MessageFrame.h"
#include "AddGrpB.h"
#include "AddGrpC.h"
#include "rtxsrc/rtxCharStr.h"
#include "rtxsrc/rtxPrintStream.h"
#include "rtxsrc/OSRTFileOutputStream.h"
#include "rtxmlsrc/OSXMLEncodeStream.h"
#include "rtjsonsrc/OSJSONEncodeStream.h"

int main (int argc, char** argv)
{
   OSBOOL       aligned = !TRUE;
   OSBOOL       trace = TRUE, verbose = FALSE;
   const char*  filename = "message.dat";
   const char*  hexstr = 0;
   int          i, stat;

   // Process command line arguments
   if (argc > 1) {
      for (i = 1; i < argc; i++) {
         if (!strcmp (argv[i], "-v")) verbose = TRUE;
         else if (!strcmp (argv[i], "-i")) filename = argv[++i];
         else if (!strcmp (argv[i], "-hex")) hexstr = argv[++i];
         else if (!strcmp (argv[i], "-notrace")) trace = FALSE;
         else {
            printf ("usage: reader [-v] [-i <filename>] [-hex <string>] "
                    "[-notrace]\n");
            printf ("   -v  verbose mode: print trace info\n");
            printf ("   -i <filename> read encoded msg from <filename>\n");
            printf ("   -hex <string> hex string containing encoded msg\n");
            printf ("   -notrace  do not display trace info\n");
            return 1;
         }
      }
   }

   OSOCTET* msgbuf = 0;
   size_t nbytes = 0;
   if (0 != hexstr) {
      stat = rtxHexCharsToBinCount (hexstr, strlen(hexstr));
      if (stat < 0) {
         printf ("hex string conversion failed, status = %d\n", stat);
         return stat;
      }
      else nbytes = (size_t)stat;

      msgbuf = new OSOCTET [nbytes];
      if (0 == msgbuf) return RTERR_NOMEM;

      stat = rtxHexCharsToBin (hexstr, strlen(hexstr), msgbuf, nbytes);
      if (stat < 0) {
         printf ("hex string conversion failed, status = %d\n", stat);
         return stat;
      }
   }
   
   ASN1PERDecodeBuffer decodeBuffer (aligned);
   ASN1T_MessageFrame data;
   ASN1C_MessageFrame MessageFramePDU (decodeBuffer, data);
   decodeBuffer.setDiag (verbose);
   if (0 != msgbuf) {
      stat = decodeBuffer.setBuffer (msgbuf, nbytes);
      if (stat < 0) {
         printf("Error setting message buffer\n");
         decodeBuffer.printErrorInfo();
         return stat;
      }
   }
   else {
      decodeBuffer.readBinaryFile (filename);
      if (decodeBuffer.getStatus() != 0) {
         printf("Error opening %s for read access\n", filename);
         decodeBuffer.printErrorInfo();
         return -1;
      }
   }
   decodeBuffer.SetTrace (trace);
   stat = MessageFramePDU.Decode ();
   if (stat != 0) {
      printf ("decode MessageFrame failed\n");
      decodeBuffer.PrintErrorInfo ();
      return stat;
   }

   if (trace) {
      printf ("Dump of decoded bit fields:\n");
      decodeBuffer.BinDump ("Data");
      printf ("\n");
      printf ("Decode MessageFrame data was successful\n");
      printf ("Decoded record:\n");
      MessageFramePDU.setPrintStream (rtxPrintStreamToStdoutCB, 0);
      MessageFramePDU.toStream();
   }

   delete [] msgbuf;

   // Output decoded data to XER (XML) format

   OSRTFileOutputStream xerfos ("message.xml");
   OSXMLEncodeStream xerEncStrm (xerfos);

   stat = MessageFramePDU.EncodeTo (xerEncStrm);
   if (stat != 0) {
      printf ("encode MessageFrame to XER failed\n");
      xerEncStrm.printErrorInfo ();
      return stat;
   }

   // Output decoded data to JSON format

   OSRTFileOutputStream jsonfos ("message.json");
   OSJSONEncodeStream jsonEncStrm (jsonfos);

   stat = MessageFramePDU.EncodeTo (jsonEncStrm);
   if (stat != 0) {
      printf ("encode MessageFrame to JSON failed\n");
      jsonEncStrm.printErrorInfo ();
      return stat;
   }

   return 0;
}
