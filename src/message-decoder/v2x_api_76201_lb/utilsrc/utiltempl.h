/**
 * This header provides a class template for defining utility classes that
 * can simply convert messages between binary and text formats.
 */
#include <cstdio>

/* Runtime sources needed for encoding/decoding. */
#include "rtxsrc/rtxFile.h"
#include "rtxsrc/rtxPrint.h"
#include "rtxsrc/OSRTInputStream.h"
#include "rtxsrc/OSRTFileInputStream.h"
#include "rtxsrc/OSRTMemoryInputStream.h"
#include "rtxmlsrc/OSXMLDecodeBuffer.h"
#include "rtjsonsrc/OSJSONDecodeBuffer.h"
#include "rtxmlsrc/OSXMLEncodeBuffer.h"
#include "rtjsonsrc/OSJSONEncodeBuffer.h"
#include "rtpersrc/asn1PerCppTypes.h"

/**
 * The decode template function takes three parameters: a Data class, Control
 * class, and a decode Buffer; as an example, the three parameters could be
 * specified by ASN1T_MessageFrame, ASN1C_MessageFrame, and
 * OSJSONDecodeBuffer.  Such a configuration would produce a JSON decoder for
 * the MessageFrame PDU type.
 *
 * N.b., this function expects that the input data is actually the JSON or XML
 * to be decoded, and not a filename.
 *
 * @param str The null-terminated text to be converted to UPER.
 * @param dat Receives the UPER data. This array will need to be freed by the
 *    caller when finished with it.
 * @param len Receives the length of dat.
 * @param errmsg Receives the error message text if there is an error.
 * @param verbose Controls whether verbose output is produced.
 * @returns success (0) or error code (<0)
 */
template<typename Data, typename Control, typename Buffer>
int from_text(const char* str, char** dat, size_t* len, char** errmsg,
               bool verbose) 
{
   Data data;
   Control control(data);
   int stat = 0;

   char *outbuf;

   *dat = 0;
   *len = 0;
   *errmsg = 0;
   
   /* The PER encode buffer.  We turn on debugging information by default, but
    * the release libraries won't do anything with it. */
   ASN1PEREncodeBuffer encodeBuffer(FALSE);
   if ( verbose ) {
      encodeBuffer.setTrace(TRUE);
      encodeBuffer.setDiag(TRUE);
   }

   OSRTMemoryInputStream strm(reinterpret_cast<const OSOCTET*>(str),
         strlen(str));
   Buffer decodeBuffer(strm); 

   stat = control.DecodeFrom(decodeBuffer);

   if (stat != 0) {
      /* Make a copy of the error text, because it won't survive context
         destruction.
      */
      char* errtxt = rtxErrGetText(decodeBuffer.getCtxtPtr(), 0, 0);
      size_t bufsiz = strlen(errtxt) + 1;
      *errmsg = new char[bufsiz];
      #ifdef _MSC_VER
         strcpy_s(*errmsg, bufsiz, errtxt);
      #else
         strcpy(*errmsg, errtxt);
      #endif
      return stat;
   }

   stat = control.EncodeTo(encodeBuffer);

   if (verbose) encodeBuffer.binDump("data");

   if (stat != 0) {
      /* Make a copy of the error text, because it won't survive context
         destruction.
      */
      char* errtxt = rtxErrGetText(encodeBuffer.getCtxtPtr(), 0, 0);
      size_t bufsiz = strlen(errtxt) + 1;
      *errmsg = new char[bufsiz];
      #ifdef _MSC_VER
         strcpy_s(*errmsg, bufsiz, errtxt);
      #else
         strcpy(*errmsg, errtxt);
      #endif
      return stat;
   }

   *len = encodeBuffer.getMsgLen();
   outbuf = new char[*len];
   void *ptr = memcpy((void *)outbuf, encodeBuffer.getMsgPtr(), *len);
   *dat = outbuf;
   return 0;
}

/**
 * The encode template function takes three parameters: a Data class, Control
 * class, and a decode Buffer; as an example, the three parameters could be
 * specified by ASN1T_MessageFrame, ASN1C_MessageFrame, and
 * OSJSONEncodeBuffer.  Such a configuration would produce a JSON encoder for
 * the MessageFrame PDU type.
 *
 * N.b., this function expects that the input data is binary, not a filename
 * or hexadecimal text. 
 * @param dat The binary input data
 * @param len The length of dat.
 * @param txt Receives the resulting text.  This memory will need to be
 *       freed by the caller when they are finished with it.
 * @param errmsg Receives the error message text if there is an error.
 * @param verbose Controls whether verbose output is enabled or not.
 * @returns success (0) or error code (<0)
 */
template<typename Data, typename Control, typename Buffer>
int to_text(const char* dat, size_t len, char** txt, char** errmsg, 
            bool verbose) 
{
   int stat = 0;

   const OSOCTET *msgbuf = reinterpret_cast<const OSOCTET *>(dat);
   char* outbuf;

   *txt = 0;
   *errmsg = 0;

   /* The PER decode buffer.  We turn on debugging information by default, but
    * the release libraries won't do anything with it. */
   /* TODO: address options for alignment, et c. */
   ASN1PERDecodeBuffer decodeBuffer(msgbuf, len, FALSE);

   Data data;
   Control control(decodeBuffer, data);

   Buffer encodeBuffer; 

   if ( verbose ) {
      decodeBuffer.setTrace(TRUE);
      decodeBuffer.setDiag(TRUE);
   }

   stat = control.Decode();

   if (verbose) decodeBuffer.binDump("data");
   
   if (stat != 0) {
      /* Make a copy of the error text, because it won't survive context
         destruction.
      */
      char* errtxt = rtxErrGetText(control.getCtxtPtr(), 0, 0);
      size_t bufsiz = strlen(errtxt) + 1;
      *errmsg = new char[bufsiz];
      #ifdef _MSC_VER
         strcpy_s(*errmsg, bufsiz, errtxt);
      #else
         strcpy(*errmsg, errtxt);
      #endif
      return stat;
   }

   stat = control.EncodeTo(encodeBuffer);

   if (stat != 0) {      
      /* Make a copy of the error text, because it won't survive context
         destruction.
      */
      char* errtxt = rtxErrGetText(encodeBuffer.getCtxtPtr(), 0, 0);
      size_t bufsiz = strlen(errtxt) + 1;
      *errmsg = new char[bufsiz];
      #ifdef _MSC_VER
         strcpy_s(*errmsg, bufsiz, errtxt);
      #else
         strcpy(*errmsg, errtxt);
      #endif
      return stat;
   }

   /* A subtle issue here: the JSON and XML encoders don't actually implement
    * a getMsgCopy() function: this isn't immediately obvious because the OSys
    * runtimes don't throw exceptions.  So we copy the data out ourselves and
    * clean up after. */
   size_t txt_len = encodeBuffer.getMsgLen();
   outbuf = new char[txt_len + 1];
   void *ptr = memcpy((void *)outbuf, encodeBuffer.getMsgPtr(), txt_len);
   outbuf[txt_len] = 0;
   *txt = outbuf;
   return 0;
}


