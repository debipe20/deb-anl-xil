/*
 * Copyright (c) 1997-2024 Objective Systems, Inc.
 *
 * This software is furnished under a license and may be used and copied
 * only in accordance with the terms of such license and with the
 * inclusion of the above copyright notice. This software or any other
 * copies thereof may not be provided or otherwise made available to any
 * other person. No title to and ownership of the software is hereby
 * transferred.
 *
 * The information in this software is subject to change without notice
 * and should not be construed as a commitment by Objective Systems, Inc.
 *
 * PROPRIETARY NOTICE
 *
 * This software is an unpublished work subject to a confidentiality agreement
 * and is protected by copyright and trade secret law.  Unauthorized copying,
 * redistribution or other use of this work is prohibited.
 *
 * The above notice of copyright on this source code product does not indicate
 * any actual or intended publication of such source code.
 *
 *****************************************************************************/

/**
 * @file rtPrintToStream.h
 * Functions to print the output in a "name=value" format.
 */
#ifndef _RTPRINTTOSTREAM_H_
#define _RTPRINTTOSTREAM_H_
#include <stdio.h>
#include "rtsrc/asn1type.h"
#include "rtxsrc/rtxPrintStream.h"
#include "rtxsrc/rtxPrintToStream.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @defgroup valsToStream Print Values to user specified Stream
 * @ingroup cruntime
 * @{
 * These functions print the output in a "name=value" format.
 */
/** Defines the old runtime function to its new equivalent. */
#define rtPrintToStreamBoolean rtxPrintToStreamBoolean
/** Defines the old runtime function to its new equivalent. */
#define rtPrintToStreamInteger rtxPrintToStreamInteger
/** Defines the old runtime function to its new equivalent. */
#define rtPrintToStreamInt64   rtxPrintToStreamInt64
/** Defines the old runtime function to its new equivalent. */
#define rtPrintToStreamUnsigned rtxPrintToStreamUnsigned
/** Defines the old runtime function to its new equivalent. */
#define rtPrintToStreamUInt64  rtxPrintToStreamUInt64
/** Defines the old runtime function to its new equivalent. */
#define rtPrintToStreamCharStr rtxPrintToStreamCharStr
/** Defines the old runtime function to its new equivalent. */
#define rtPrintToStreamReal    rtxPrintToStreamReal
/** Defines the old runtime function to its new equivalent. */
#define rtPrintToStreamHexStr  rtxPrintToStreamHexStr
/** Defines the old runtime function to its new equivalent. */
#define rtPrintToStreamIndent  rtxPrintToStreamIndent
/** Defines the old runtime function to its new equivalent. */
#define rtPrintToStreamIncrIndent rtxPrintToStreamIncrIndent
/** Defines the old runtime function to its new equivalent. */
#define rtPrintToStreamDecrIndent rtxPrintToStreamDecrIndent
/** Defines the old runtime function to its new equivalent. */
#define rtPrintToStreamCloseBrace rtxPrintToStreamCloseBrace
/** Defines the old runtime function to its new equivalent. */
#define rtPrintToStreamOpenBrace  rtxPrintToStreamOpenBrace

/**
 * Prints an ASN.1 bit string value to a print stream.
 *
 * @param pctxt        Pointer to an ASN1 context initialized for printing.
 * @param name         The name of the variable to print.
 * @param numbits      The number of bits to be printed.
 * @param data         A pointer to the data to be printed.
 * @param conn         A pointer to the connector between the name and the
 *                       value. This points to either -> or .
 * @return             Completion status, 0 on success and -ve on failure
 */
EXTERNRT int rtPrintToStreamBitStr
(OSCTXT *pctxt, const char* name, OSSIZE numbits, const OSOCTET* data,
 const char* conn);

/**
 * Prints an ASN.1 bit string value in binary form to a print stream.
 *
 * @param pctxt        Pointer to an ASN1 context initialized for printing.
 * @param name         The name of the variable to print.
 * @param numbits      The number of bits to be printed.
 * @param data         A pointer to the data to be printed.
 * @param conn         A pointer to the connector between the name and the
 *                       value. This points to either -> or .
 * @return             Completion status, 0 on success; negative on failure
 */
EXTERNRT int rtPrintToStreamBitStrBin(OSCTXT *pctxt, const char *name,
                      OSSIZE numbits, const OSOCTET *data, const char *conn);

/**
 * This function prints the value of a bit string to a print stream as a list
 * of bit names (where applicable) and bit values.
 *
 * @param pctxt        Pointer to an ASN1 context initialized for printing.
 * @param name         The name of the variable to print.
 * @param numbits      The number of bits to be printed.
 * @param data         A pointer to the data to be printed.
 * @param conn         A pointer to the connector between the name and the
 *                       value. This points to either -> or .
 * @param namedbits    Count of how many bits have names.
 * @param positions    Array of position indicators for the positions
 *                       within the bit string that have names.
 * @param bitnames     Array of bit string names.
 */
EXTERNRT void rtPrintToStreamBitStrNamed(OSCTXT *pctxt, const char* name,
   OSSIZE numbits, const OSOCTET* data, const char* conn, OSSIZE namedbits,
   const OSUINT32 positions[], const char* bitnames[]);

/**
 * This function prints the value of a bit string to a print stream as a list
 * of bit names (where applicable) and bit values.  It includes support
 * for bit strings with extension data.
 *
 * @param pctxt        Pointer to an ASN1 context initialized for printing.
 * @param name         The name of the variable to print.
 * @param numbits      The number of bits to be printed.
 * @param data         A pointer to the data to be printed.
 * @param dataSize     Size, in bytes, of the data array.
 * @param extdata      Pointer to byte array containing extension data.
 * @param conn         A pointer to the connector between the name and the
 *                       value. This points to either -> or .
 * @param namedbits    Count of how many bits have names.
 * @param positions    Array of position indicators for the positions
 *                       within the bit string that have names.
 * @param bitnames     Array of bit string names.
 */
EXTERNRT void rtPrintToStreamBitStrNamedExt(OSCTXT *pctxt, const char* name,
   OSSIZE numbits, const OSOCTET* data, OSSIZE dataSize,
   const OSOCTET* extdata, const char* conn, OSSIZE namedbits,
   const OSUINT32 positions[], const char* bitnames[]);

/**
 * Prints an ASN.1 bit string value to a print stream.  It includes support
 * for BIT STRING's with extension data.
 *
 * @param pctxt        Pointer to an ASN1 context initialized for printing.
 * @param name         The name of the variable to print.
 * @param numbits      The number of bits to be printed.
 * @param data         A pointer to the data to be printed.
 * @param dataSize     Size, in bytes, of the data array.
 * @param extdata      Pointer to byte array containing extension data.
 * @param conn         A pointer to the connector between the name and the
 *                       value. This points to either -> or .
 * @return             Completion status, 0 on success and -ve on failure
 */
EXTERNRT int rtPrintToStreamBitStrExt(OSCTXT *pctxt, const char* name,
   OSSIZE numbits, const OSOCTET* data, OSSIZE dataSize,
   const OSOCTET* extdata, const char* conn);

/**
 * This function prints the value of a bit string to a stream in brace text
 * format.
 *
 * @param pctxt        Pointer to a context initialized for printing.
 * @param name         The name of the variable to print.
 * @param numbits      The number of bitsto be printed.
 * @param data         A pointer to the data to be printed.
 * @return             Completion status, 0 on success and -ve on failure
 */
EXTERNRT int rtPrintToStreamBitStrBraceText
(OSCTXT *pctxt, const char* name, OSSIZE numbits, const OSOCTET* data);

/**
 * This function prints the value of a bit string to a stream in brace text
 * format. It includes support for BIT STRING's with extension data.
 *
 * @param pctxt        Pointer to a context initialized for printing.
 * @param name         The name of the variable to print.
 * @param numbits      The number of bits to be printed.
 * @param data         A pointer to the data to be printed.
 * @param dataSize     Size, in bytes, of the data array.
 * @param extdata      Pointer to byte array containing extension data.
 * @return             Completion status, 0 on success and -ve on failure
 */
EXTERNRT int rtPrintToStreamBitStrBraceTextExt(OSCTXT *pctxt, const char* name,
   OSSIZE numbits, const OSOCTET* data, OSSIZE dataSize,
   const OSOCTET* extdata);

/**
 * @param pctxt        Pointer to a context initialized for printing.
 * @param name         The name of the variable to print.
 * @param numocts      The number of octets to be printed.
 * @param data         A pointer to the data to be printed.
 */
EXTERNRT int rtPrintToStreamIpv4Addr(OSCTXT *pctxt, const char* name,
                            OSSIZE numocts, const OSOCTET* data);

/**
 * @param pctxt        Pointer to a context initialized for printing.
 * @param name         The name of the variable to print.
 * @param numocts      The number of octets to be printed.
 * @param data         A pointer to the data to be printed.
 */
EXTERNRT int rtPrintToStreamIpv6Addr(OSCTXT *pctxt, const char* name,
                            OSSIZE numocts, const OSOCTET* data);

/**
 * @param pctxt        Pointer to a context initialized for printing.
 * @param name         The name of the variable to print.
 * @param numocts      The number of octets to be printed.
 * @param data         A pointer to the data to be printed.
 */
EXTERNRT int rtPrintToStreamTBCDStr(OSCTXT *pctxt, const char* name,
                            OSSIZE numocts, const OSOCTET* data);

/**
 * @param pctxt        Pointer to a context initialized for printing.
 * @param name         The name of the variable to print.
 * @param pDateTime    Pointer to date/time structure to be printed.
 */
EXTERNRT int rtPrintToStreamDateTime(OSCTXT *pctxt, const char* name,
                            OSNumDateTime *pDateTime);

/**
 * @param pctxt        Pointer to a context initialized for printing.
 * @param name         The name of the variable to print.
 * @param numocts      The number of octets to be printed.
 * @param data         A pointer to the data to be printed.
 */
EXTERNRT int rtPrintToStreamText(OSCTXT *pctxt, const char* name,
                            OSSIZE numocts, const OSOCTET* data);

/**
 * @param pctxt        Pointer to an ASN1 context initialized for printing.
 * @param name         The name of the variable to print.
 * @param numocts      The number of octets to be printed.
 * @param data         A pointer to the data to be printed.
 * @param conn         A pointer to the connector between the name and the
 *                       value. This points to either -> or .
 *
 * @return             Completion status, 0 on success and -ve on failure
 */
EXTERNRT int rtPrintToStreamOctStr
(OSCTXT *pctxt, const char* name, OSSIZE numocts, const OSOCTET* data,
 const char* conn);

/**
 * Prints a 16-bit (Unicode) character string value to a print stream.
 *
 * @param pctxt        Pointer to an ASN1 context initialized for printing.
 * @param name         The name of the variable to print.
 * @param bstring      A pointer to the bit string to be printed.
 * @param conn         A pointer to the connector between the name and the
 *                       value. This points to either -> or .
 *
 * @return             Completion status, 0 on success and -ve on failure
 */
EXTERNRT int rtPrintToStream16BitCharStr
(OSCTXT *pctxt, const char* name, const Asn116BitCharString* bstring,
 const char* conn);

/**
 * Prints a 32-bit (Universal) character string value to a print stream.
 *
 * @param pctxt        Pointer to an ASN1 context initialized for printing.
 * @param name         The name of the variable to print.
 * @param bstring      A pointer to the bit string to be printed.
 * @param conn         A pointer to the connector between the name and the
 *                       value. This points to either -> or .
 *
 * @return             Completion status, 0 on success and -ve on failure
 */
EXTERNRT int rtPrintToStream32BitCharStr
(OSCTXT *pctxt, const char* name, const Asn132BitCharString* bstring,
 const char* conn);

/**
 * This function prints the value of an object identifier to the stream.
 *
 * @param pctxt        Pointer to an ASN1 context initialized for printing.
 * @param name         The name of the variable to print.
 * @param pOID         A pointer to the OID to be printed.
 *
 * @return             Completion status, 0 on success and -ve on failure
 */
EXTERNRT int rtPrintToStreamOID
(OSCTXT *pctxt, const char* name, const ASN1OBJID* pOID);

/**
 * This function prints the value of an object identifier to the stream.
 * Only the value is printed, not the name.
 *
 * @param pctxt        Pointer to an ASN1 context initialized for printing.
 * @param pOID         A pointer to the OID to be printed.
 *
 * @return             Completion status, 0 on success and -ve on failure
 */
EXTERNRT int rtPrintToStreamOIDValue (OSCTXT *pctxt, const ASN1OBJID* pOID);


/**
 * This function prints the value of an object identifier to the stream.
 * Only the value is printed, not the name.
 *
 * @param pctxt        Pointer to an ASN1 context initialized for printing.
 * @param name         The name of the variable to print.
 * @param pOID         A pointer to the OID to be printed.
 *
 * @return             Completion status, 0 on success and -ve on failure
 */
EXTERNRT int rtPrintToStreamOIDStr(OSCTXT* pctxt, const char* name,
                                    const char* pOID);


/**
 * This function prints the value of an object identifier to the stream.
 * This version allows the number of sub-identifiers and array of
 * subidentifiers to be passed in separately allowing it to be used
 * for both static and dynamic OID structures.
 *
 * @param pctxt        Pointer to an ASN1 context initialized for printing.
 * @param name         The name of the variable to print.
 * @param numids       Number of sub-identifiers
 * @param subidArray   Pointer to array of sub-identifiers.
 * @return             Completion status, 0 on success and -ve on failure
 */
EXTERNRT int rtPrintToStreamOID2
(OSCTXT *pctxt, const char* name, OSSIZE numids, const OSUINT32* subidArray);

/**
 * This function prints the value of an object identifier to the stream.
 * Only the value is printed, not the name.
 *
 * This version allows the number of sub-identifiers and array of
 * subidentifiers to be passed in separately allowing it to be used
 * for both static and dynamic OID structures.
 *
 * @param pctxt        Pointer to an ASN1 context initialized for printing.
 * @param numids       Number of sub-identifiers
 * @param subidArray   Pointer to array of sub-identifiers.
 * @return             Completion status, 0 on success and -ve on failure
 */
EXTERNRT int rtPrintToStreamOIDValue2
(OSCTXT *pctxt, OSSIZE numids, const OSUINT32* subidArray);

/**
 * @param pctxt        Pointer to an ASN1 context initialized for printing.
 * @param name         The name of the variable to print.
 * @param pOID         A pointer to the OID to be printed.
 *
 * @return             Completion status, 0 on success and -ve on failure
 */
EXTERNRT int rtPrintToStreamOID64
(OSCTXT *pctxt, const char* name, const ASN1OID64* pOID);

/**
 * @param pctxt        Pointer to an ASN1 context initialized for printing.
 * @param pOID         A pointer to the OID to be printed.
 *
 * @return             Completion status, 0 on success and -ve on failure
 */
EXTERNRT int rtPrintToStreamOID64Value (OSCTXT *pctxt, const ASN1OID64* pOID);

/**
 * @param pctxt        Pointer to an ASN1 context initialized for printing.
 * @param name         The name of the variable to print.
 * @param numocts      The number of octets to be printed.
 * @param data         The pointer to the data to be printed.
 * @param conn         A pointer to the connector between the name and the
 *                       value. This points to either -> or .
 *
 * @return             Completion status, 0 on success and -ve on failure
 */
EXTERNRT int rtPrintToStreamOpenType
(OSCTXT *pctxt, const char* name, OSSIZE numocts, const OSOCTET* data,
 const char* conn);

/**
 * @param pctxt        Pointer to an ASN1 context initialized for printing.
 * @param name         The name of the variable to print.
 * @param pElemList    A pointer to an element of a list.
 *
 * @return             Completion status, 0 on success and -ve on failure
 */
EXTERNRT int rtPrintToStreamOpenTypeExt
(OSCTXT *pctxt, const char* name, const OSRTDList* pElemList);

/**
 * This function prints a Universal string to stream output.  Characters
 * in the string that are within the normal Ascii range are printed as
 * single characters.  Characters outside the Ascii range are printed
 * as 8-byte hex codes (0xnnnnnnnn).
 * @param pctxt        Pointer to an ASN1 context initialized for stream
 *                     printing.
 * @param name         The name of the variable to print.
 * @param bstring      A pointer to the bit string to be printed.
 */
EXTERNRT int rtPrintToStreamUnivCharStr
   (OSCTXT *pctxt, const char* name, const Asn132BitCharString* bstring);

/**
 * This function prints a Unicode string to stream output.  Characters
 * in the string that are within the normal Ascii range are printed as
 * single characters.  Characters outside the Ascii range are printed
 * as 4-byte hex codes (0xnnnn).
 * @param pctxt        Pointer to an ASN1 context initialized for stream
 *                     printing.
 * @param name         The name of the variable to print.
 * @param bstring      A pointer to the bit string to be printed.
 */
EXTERNRT int rtPrintToStreamUnicodeCharStr
   (OSCTXT *pctxt, const char* name, const Asn116BitCharString* bstring);

/**
 * This function prints the value of an open type extension in brace
 * text format to stream.
 * @param pctxt        Pointer to an ASN1 context initialized for stream
 *                     printing.
 * @param name         The name of the variable to print.
 * @param pElemList    A pointer to an element of a list.
 */
EXTERNRT int rtPrintToStreamOpenTypeExtBraceText
   (OSCTXT *pctxt, const char* name, const OSRTDList* pElemList);

/**
 * These macro definitions provide backward compatible definitions for
 * ASN1C v5.xx applications.
 */
/** Defines the old runtime function to its new equivalent. */
#define rtPrintCallback  rtxPrintCallback
/** Defines the old runtime function to its new equivalent. */
#define rtSetPrintStream rtxSetPrintStream
/** Defines the old runtime function to its new equivalent. */
#define rtSetGlobalPrintStream rtxSetGlobalPrintStream
/** Defines the old runtime function to its new equivalent. */
#define rtPrintToStream rtxPrintToStream
/** Defines the old runtime function to its new equivalent. */
#define rtDiagToStream  rtxDiagToStream
/** Defines the old runtime function to its new equivalent. */
#define rtPrintStreamRelease rtxPrintStreamRelease

/**
 * @} valsToStream
 */
#ifdef __cplusplus
}
#endif
#endif
