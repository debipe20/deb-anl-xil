/*
 * Copyright (c) 2019-2022 Objective Systems, Inc.
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

/*! \mainpage C JSON Runtime Library Functions
 *
 * The <b>C run-time JSON library</b> contains functions used to encode/decode
 * data in Javascript object notation (JSON).  These functions are identified
 * by their <i>rtJson</i> prefixes.
 *
 */
/**
 * @file osrtjson.h
 * JSON low-level C encode/decode functions.
 */
#ifndef _OSRTJSON_H_
#define _OSRTJSON_H_

#include "rtxsrc/osMacros.h"
#include "rtxsrc/osSysTypes.h"
#include "rtxsrc/rtxCommon.h"
#include "rtxsrc/rtxError.h"
#include "rtxsrc/rtxBuffer.h"
#include "rtxsrc/rtxMemory.h"
#include "rtxsrc/rtxText.h"

#include "rtjsonsrc/rtJsonExternDefs.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum
{
   OSJSONNOCOMMA,  // Do not write comma to output (end of arrays, etc)
   OSJSONNORMAL,   // Element is not SEQOF/SETOF (use '{', '}')
   OSJSONSEQOF,    // If current element is SEQOF or SETOF (use '[', ']')
   OSJSONRAW,      // Write raw value (no type name)
   OSJSONARRAYEDGE // Begin or end of array element
} OSJSONState;

/* JSON specific context flags */

#define OSJSONNOWS      OSNOWHITESPACE  /* encode with NO WhiteSpace */
#define OSJSONATTR      0x00008000  /* encode string value as attribute */

/* JSON macros */

#define OSJSONPUTCOMMA(pctxt) \
if ((pctxt)->lastChar != '{' && (pctxt)->lastChar != ',' \
    && (pctxt)->lastChar != '\0' && (pctxt)->lastChar != '[') \
    OSRTSAFEPUTCHAR (pctxt, ',');

/* Other definitions if needed */

#ifndef DEFAULT_DOUBLE_PRECISION
#define DEFAULT_DOUBLE_PRECISION 11
#endif

#ifndef DEFAULT_FLOAT_PRECISION
#define DEFAULT_FLOAT_PRECISION 6
#endif

#ifndef OSUPCASE
/** The upper-case flag:  if set, hex strings will be encoded in upper case. */
#define OSUPCASE 0x00008000
#endif


/* run-time JSON function prototypes */

/**
 * @defgroup rtJsonEnc JSON encode functions.
 * @{
 */

/**
 * This function encodes a list of OSAnyAttr attributes in which
 * the name and value are given as a UTF-8 string.
 *
 * @param pctxt        Pointer to context block structure.
 * @param pvalue       List of attributes.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncAnyAttr (OSCTXT* pctxt, const OSRTDList* pvalue);

/**
 * This function encodes a variable of the XSD integer type.
 *
 * @param pctxt        Pointer to context block structure.
 * @param value        Value to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
#define rtJsonEncIntValue rtxTxtWriteInt

/**
 * This function encodes a variable of the XSD integer type. This version
 * of the function is used for 64-bit integer values.
 *
 * @param pctxt        Pointer to context block structure.
 * @param value        Value to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
#define rtJsonEncInt64Value rtxTxtWriteInt64

/**
 * This function encodes a variable of the XSD base64Binary type.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nocts        Number of octets in the value string.
 * @param value        Value to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncBase64StrValue (OSCTXT* pctxt, OSSIZE nocts,
                            const OSOCTET* value);

/**
 * This function encodes a variable of the XSD boolean type.
 *
 * @param pctxt        Pointer to context block structure.
 * @param value        Boolean value to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncBoolValue (OSCTXT* pctxt, OSBOOL value);

/**
 * This function encodes a numeric gYear value into a JSON string
 * representation.
 *
 * @param pctxt        Pointer to context block structure.
 * @param pvalue       Pointer to value to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncGYear (OSCTXT* pctxt, const OSXSDDateTime* pvalue);

/**
 * This function encodes a numeric gYearMonth value into a JSON string
 * representation.
 *
 * @param pctxt        Pointer to context block structure.
 * @param pvalue       Pointer to value to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncGYearMonth (OSCTXT* pctxt, const OSXSDDateTime* pvalue);

/**
 * This function encodes a numeric gMonth value into a JSON string
 * representation.
 *
 * @param pctxt        Pointer to context block structure.
 * @param pvalue       Pointer to value to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncGMonth (OSCTXT* pctxt, const OSXSDDateTime* pvalue);

/**
 * This function encodes a numeric gMonthDay value into a JSON string
 * representation.
 *
 * @param pctxt        Pointer to context block structure.
 * @param pvalue       Pointer to value to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncGMonthDay (OSCTXT* pctxt, const OSXSDDateTime* pvalue);

/**
 * This function encodes a numeric gDay value into a JSON string
 * representation.
 *
 * @param pctxt        Pointer to context block structure.
 * @param pvalue       Pointer to value to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncGDay (OSCTXT* pctxt, const OSXSDDateTime* pvalue);

/**
 * This function encodes a variable of the XSD 'date' type as a
 * string. This version of the function is used to encode an OSXSDDateTime
 * value into CCYY-MM-DD format.
 *
 * @param pctxt        Pointer to context block structure.
 * @param pvalue       OSXSDDateTime type pointer points to a OSXSDDateTime
 *                     value to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncDate (OSCTXT* pctxt, const OSXSDDateTime* pvalue);

/**
 * This function encodes a variable of the XSD 'time' type as a JSON
 * string.
 *
 * @param pctxt        Pointer to context block structure.
 * @param pvalue       OSXSDDateTime type pointer points to a OSXSDDateTime
 *                     value to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncTime (OSCTXT* pctxt, const OSXSDDateTime* pvalue);

/**
 * This function encodes a numeric date/time value into a string
 * representation.
 *
 * @param pctxt        Pointer to context block structure.
 * @param pvalue       Pointer to value to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncDateTime (OSCTXT* pctxt, const OSXSDDateTime* pvalue);

/**
 * This function encodes a value of the XSD decimal type.
 *
 * @param pctxt        Pointer to context block structure.
 * @param value        Value to be encoded.
 * @param pFmtSpec     Pointer to format specification structure.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncDecimalValue (OSCTXT* pctxt, OSREAL value,
                        const OSDecimalFmt* pFmtSpec);

/**
 * This function encodes a value of the XSD double or float type.
 *
 * @param pctxt        Pointer to context block structure.
 * @param value        Value to be encoded.
 * @param pFmtSpec     Pointer to format specification structure.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncDoubleValue (OSCTXT* pctxt, OSREAL value,
                        const OSDoubleFmt* pFmtSpec);

/**
 * This function encodes a variable of the XSD float type.
 *
 * @param pctxt        Pointer to context block structure.
 * @param value        Value to be encoded.
 * @param pFmtSpec     Pointer to format specification structure.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncFloatValue (OSCTXT* pctxt, OSREAL value,
                        const OSDoubleFmt* pFmtSpec);

/**
 * This function encodes the given data as a JSON string, using a hexadecimal
 * representation of the data.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nocts        Number of octets in the value string.
 * @param data         Value to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncHexStr (OSCTXT* pctxt, OSSIZE nocts,
                                const OSOCTET* data);

/**
 * This function encodes the given data as a sequence of hexadecimal characters.
 * Unlike rtJsonHexStr, it does not encode quotation marks.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nocts        Number of octets in the value string.
 * @param data         Value to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncHexValue (OSCTXT* pctxt, OSSIZE nocts,
                                const OSOCTET* data);

/**
 * This function encodes a variable of the ASN.1 Bit string type.
 * This provides ObjSys-specific behavior that predates ITU-T X.697.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nbits        Number of bits in the value string.
 * @param data         Value to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncBitStrValueV72 (OSCTXT* pctxt, OSSIZE nbits,
                         const OSOCTET* data);

/**
 * This function encodes a variable of the ASN.1 Bit string type.
 * It handles bit strings with extdata member present.
 * This provides ObjSys-specific behavior that predates ITU-T X.697.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nbits        Number of bits in the value string.
 * @param data         Value to be encoded.
 * @param dataSize     Size of data member.
 * @param extData      Value of extdata to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncBitStrValueExtV72(OSCTXT* pctxt, OSSIZE nbits,
                        const OSOCTET* data, OSSIZE dataSize,
                        const OSOCTET* extData);


/**
 * This function encodes a variable of the ASN.1 Bit string type as a JSON
 * object, as required by X.697 for a BIT STRING without a fixed length.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nbits        Number of bits in the value string.
 * @param data         Value to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncBitStrValue (OSCTXT* pctxt, OSSIZE nbits,
                         const OSOCTET* data);

/**
 * This function encodes a variable of the ASN.1 Bit string type as a JSON
 * string, as required by X.697 for a BIT STRING with a fixed length.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nbits        Number of bits in the value string.
 * @param data         Value to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncFixedBitStrValue (OSCTXT* pctxt, OSSIZE nbits,
                         const OSOCTET* data);

/**
 * This function encodes a variable of the ASN.1 Bit string type as a JSON
 * object, as required by X.697 for a BIT STRING without a fixed length.
 * It handles bit strings with extdata member present.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nbits        Number of bits in the value string.
 * @param data         Value to be encoded.
 * @param dataSize     Size of data member.
 * @param extData      Value of extdata to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncBitStrValueExt(OSCTXT* pctxt, OSSIZE nbits,
                        const OSOCTET* data, OSSIZE dataSize,
                        const OSOCTET* extData);

/**
 * This function:
 *    - Writes a comma unless OSJSONNOCOMMA is set or the previous character
 *       is a comma, null terminator, {, or [ character.
 *    - Writes a newline and indentation unless OSNOWHITEPSACE is set.
 *
 * The amount of indentation to add is determined by the indent member
 * variable in the context structure.
 *
 * @param pctxt        Pointer to context block structure.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncIndent (OSCTXT* pctxt);

/**
 * This decreases the indentation level set in the given context by
 * updating the indent member.
 *
 * @param pctxt        Pointer to context block structure.
 */
#define rtJsonEncDecrIndent rtxIndentDecr

/**
 * This increases the indentation level set in the given context by
 * updating the indent member.
 *
 * @param pctxt        Pointer to context block structure.
 */
#define rtJsonEncIncrIndent rtxIndentIncr

/**
 * This resets the indentation level in the given context to zero.
 *
 * @param pctxt        Pointer to context block structure.
 */
#define rtJsonEncResetIndent rtxIndentReset


/**
 * This returns the number of levels of indentation rtJsonEncIndent is
 * using.
 *
 * @param pctxt        Pointer to context block structure.
 */
#define rtJsonGetIndentLevels rtxGetIndentLevels


/**
 * This function encodes a JSON object containing a string value.
 *
 * @param pctxt        Pointer to context block structure.
 * @param name         Name token to be encoded.
 * @param value        Value as a character string to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncStringObject (OSCTXT* pctxt,
                        const OSUTF8CHAR* name, const OSUTF8CHAR* value);

/**
 * This function encodes a JSON object containing a string value.
 *
 * @param pctxt        Pointer to context block structure.
 * @param name         Name token to be encoded.
 * @param nameLen      Length of the name token to be encoded.
 * @param value        Value as a character string to be encoded.
 * @param valueLen     Length of the value to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncStringObject2 (OSCTXT* pctxt,
                        const OSUTF8CHAR* name, size_t nameLen,
                        const OSUTF8CHAR* value, size_t valueLen);

/**
 * This function encodes a name/value pair. The value is a character string.
 *
 * @param pctxt        Pointer to context block structure.
 * @param name         Name token to be encoded.
 * @param value        Value as a character string to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncStringPair (OSCTXT* pctxt,
                        const OSUTF8CHAR* name, const OSUTF8CHAR* value);

/**
 * This function encodes a name/value pair. The value is a character string.
 *
 * @param pctxt        Pointer to context block structure.
 * @param name         Name token to be encoded.
 * @param nameLen      Length of the name token to be encoded.
 * @param value        Value as a character string to be encoded.
 * @param valueLen     Length of the value to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncStringPair2 (OSCTXT* pctxt,
                        const OSUTF8CHAR* name, size_t nameLen,
                        const OSUTF8CHAR* value, size_t valueLen);

/**
 * This function encodes a UTF8 string value.
 *
 * @param pctxt        Pointer to context block structure.
 * @param value        XML string value to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncStringValue (OSCTXT* pctxt, const OSUTF8CHAR* value);

/**
 * This function encodes a UTF8 string value.
 *
 * @param pctxt        Pointer to context block structure.
 * @param value        XML string value to be encoded.
 * @param valueLen     Length of the XML string to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncStringValue2 (OSCTXT* pctxt,
                        const OSUTF8CHAR* value, size_t valueLen);

/**
 * This function encodes the given number of characters from a character
 * string value as a JSON string.
 *
 * @param pctxt        Pointer to context block structure.
 * @param value        Character string value to be encoded.
 * @param valueLen     Length of the XML string to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncChars
(OSCTXT* pctxt, const char* value, OSSIZE valueLen);

/**
 * This function encodes a character string value as a JSON string.
 *
 * @param pctxt        Pointer to context block structure.
 * @param value        Character string value to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncCharStr (OSCTXT* pctxt, const char* value);

/**
 * This function encodes an asn.1 NULL type as string.
 *
 * @param pctxt        Pointer to context block structure.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncStringNull(OSCTXT* pctxt);

/**
 * This function encodes a raw string without any quotation.
 *
 * @param pctxt        Pointer to context block structure.
 * @param value        String value to be written.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncStringRaw(OSCTXT* pctxt, const OSUTF8CHAR* value);

/**
 * This function encodes a variable that contains UCS-2 / UTF-16 characters.
 *
 * @param pctxt        Pointer to context block structure.
 * @param value        UCS-2 characters to be encoded.
 * @param nchars       Number of Unicode characters to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncUnicodeData (OSCTXT* pctxt, const OSUNICHAR* value,
      OSSIZE nchars);

/**
 * This function encodes a variable that contains UCS-4 / UTF-32 characters.
 *
 * @param pctxt        Pointer to context block structure.
 * @param value        UCS-4 characters to be encoded.
 * @param nchars       Number of characters to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncUCS4Data (OSCTXT* pctxt, const OS32BITCHAR* value,
      OSSIZE nchars);


/**
 * This function encodes a variable of the XSD unsigned integer type.
 *
 * @param pctxt        Pointer to context block structure.
 * @param value        Value to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
#define rtJsonEncUIntValue rtxTxtWriteUInt

/**
 * This function encodes a variable of the XSD integer type. This version
 * of the function is used when constraints cause an unsigned 64-bit integer
 * variable to be used.
 *
 * @param pctxt        Pointer to context block structure.
 * @param value        Value to be encoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
#define rtJsonEncUInt64Value rtxTxtWriteUInt64

/**
 * This function encodes the beginning of a JSON object.
 *
 * @param pctxt        Pointer to context block structure.
 * @param name         Object name token to be encoded.
 * @param noComma      If TRUE do not print comma at end of line in output.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncStartObject(OSCTXT* pctxt, const OSUTF8CHAR* name,
                                    OSBOOL noComma);

/**
 * This function encodes the end of a JSON object.
 *
 * @param pctxt        Pointer to context block structure.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncEndObject(OSCTXT* pctxt);

/**
 * This function encodes the characters separating the JSON name and value.
 *
 * @param pctxt        Pointer to context block structure.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonEncBetweenObject(OSCTXT* pctxt);

/**
 * @}
 */

/**
 * @defgroup rtJsonDec JSON decode functions.
 * @{
 */

/**
 * This function decodes an arbitrary block of JSON-encoded data into
 * a string variable.  In this case, the expected format is element name
 * : JSON encoded data.
 *
 * @param pctxt        A pointer to a context structure. This provides a
 *                       storage area for the function to store all working
 *                       variables that must be maintained between function
 *                       calls.
 * @param ppvalue      A pointer to a variable to receive the decoded
 *                       JSON text.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecAnyElem (OSCTXT* pctxt, OSUTF8CHAR** ppvalue);

/**
 * This version of rtJsonDecAnyElem assumes the element name has been
 * pushed on the element name stack in the context.  This will be the
 * case if rtJsonGetElemIdx is called prior to calling this function.
 *
 * @param pctxt        A pointer to a context structure. This provides a
 *                       storage area for the function to store all working
 *                       variables that must be maintained between function
 *                       calls.
 * @param ppvalue      A pointer to a variable to receive the decoded
 *                       JSON text.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecAnyElem2 (OSCTXT* pctxt, OSUTF8CHAR** ppvalue);

/**
 * This function decodes an arbitrary block of JSON-encoded data into
 * a string variable.  In this case, the expected format is a complete
 * JSON encoded data fragment.
 *
 * @param pctxt        A pointer to a context structure. This provides a
 *                       storage area for the function to store all working
 *                       variables that must be maintained between function
 *                       calls.
 * @param ppvalue      A pointer to a variable to receive the decoded
 *                       JSON text.  You may pass null if not interested in
 *                       receiving the decoded text.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecAnyType (OSCTXT* pctxt, OSUTF8CHAR** ppvalue);

/**
 * This function decodes a contents of a Base64-encode binary string into a
 * static memory structure. The octet string must be Base64 encoded. This
 * function call is used to decode a sized base64Binary string production.
 *
 * @param pctxt        A pointer to a context structure. This provides a
 *                       storage area for the function to store all working
 *                       variables that must be maintained between function
 *                       calls.
 * @param pvalue       A pointer to a variable to receive the decoded bit
 *                       string. This is assumed to be a static array large
 *                       enough to hold the number of octets specified in the
 *                       bufsize input parameter.
 * @param pnocts       A pointer to an integer value to receive the decoded
 *                       number of octets.
 * @param bufsize      The size (in octets) of
 *                       the sized octet string. An error will occur if
 *                       the number of octets in the decoded string is larger
 *                       than this value.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecBase64Str (OSCTXT* pctxt,
                        OSOCTET* pvalue, OSUINT32* pnocts,
                        size_t bufsize);

/**
 * This function is identical to rtJsonDecBase64Str except that it supports
 * lengths up to 64-bits in size on 64-bit machines.
 *
 * @param pctxt        A pointer to a context structure. This provides a
 *                       storage area for the function to store all working
 *                       variables that must be maintained between function
 *                       calls.
 * @param pvalue       A pointer to a variable to receive the decoded bit
 *                       string. This is assumed to be a static array large
 *                       enough to hold the number of octets specified in the
 *                       bufsize input parameter.
 * @param pnocts       A pointer to an integer value to receive the decoded
 *                       number of octets.
 * @param bufsize      The size (in octets) of
 *                       the sized octet string. An error will occur if
 *                       the number of octets in the decoded string is larger
 *                       than this value.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 * @see rtJsonDecBase64Str
 */
EXTERNJSON int rtJsonDecBase64Str64 (OSCTXT* pctxt,
                        OSOCTET* pvalue, OSSIZE* pnocts,
                        size_t bufsize);

/**
 * This function decodes a contents of a Base64-encode binary string.
 * The octet string must be Base64 encoded. This
 * function will allocate dynamic memory to store the decoded result.
 *
 * @param pctxt        A pointer to a context structure. This provides a
 *                       storage area for the function to store all working
 *                       variables that must be maintained between function
 *                       calls.
 * @param pvalue       A pointer to a dynamic octet string structure to receive
 *                       the decoded octet string. Dynamic memory is allocated
 *                       for the string using the ::rtxMemAlloc function.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecDynBase64Str (OSCTXT* pctxt, OSDynOctStr* pvalue);


/**
 * This function is identical to rtJsonDecDynBase64Str64 except that it
 * supports 64-bit integer lengths on 64-bit systems.
 *
 * @param pctxt        A pointer to a context structure. This provides a
 *                       storage area for the function to store all working
 *                       variables that must be maintained between function
 *                       calls.
 * @param pvalue       A pointer to a dynamic octet string structure to receive
 *                       the decoded octet string. Dynamic memory is allocated
 *                       for the string using the ::rtxMemAlloc function.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecDynBase64Str64 (OSCTXT* pctxt, OSDynOctStr64* pvalue);

/**
 * This function decodes a variable of the boolean type.
 *
 * @param pctxt        Pointer to context block structure.
 * @param pvalue       Pointer to a variable to receive the decoded boolean
 *                       value.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecBool (OSCTXT* pctxt, OSBOOL* pvalue);

/**
 * This function will attempt to decode a boolean variable at the current
 * buffer or stream position.  If the attempt fails, the decode cursor is
 * reset to the position it was at when the function was called and an
 * RTERR_IDNOTFOU status is returned.  The error is not logged in the context.
 *
 * @param pctxt        Pointer to context block structure.
 * @param pvalue       Pointer to a variable to receive the decoded boolean
 *                       value.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - RTERR_IDNOTFOU = not boolean value (not logged)
 *                       - negative return value if other error (logged)
 */
EXTERNJSON int rtJsonTryDecBool (OSCTXT* pctxt, OSBOOL* pvalue);

/**
 * This function decodes a variable of the XSD 'date' type.
 * Input is expected to be a string of characters returned
 * by a JSON parser. The string should have CCYY-MM-DD format.
 *
 * @param pctxt        Pointer to context block structure.
 * @param pvalue       OSXSDDateTime type pointer points to a OSXSDDateTime
 *                     value to receive decoded result.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecDate (OSCTXT* pctxt, OSXSDDateTime* pvalue);

/**
 * This function decodes a variable of the XSD 'time' type.
 * Input is expected to be a string of characters returned
 * by a JSON parser. The string should have one of following formats:
 *
 *                    (1) hh-mm-ss.ss  used if tz_flag = false
 *                    (2) hh-mm-ss.ssZ used if tz_flag = false and tzo = 0
 *                    (3) hh-mm-ss.ss+HH:MM if tz_flag = false and tzo > 0
 *                    (4) hh-mm-ss.ss-HH:MM-HH:MM
 *                                          if tz_flag = false and tzo < 0
 *
 * @param pctxt        Pointer to context block structure.
 * @param pvalue       OSXSDDateTime type pointer points to a OSXSDDateTime
 *                     value to receive decoded result.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecTime (OSCTXT* pctxt, OSXSDDateTime* pvalue);

/**
 * This function decodes a variable of the XSD 'dateTime' type.
 * Input is expected to be a string of characters returned
 * by an JSON parser.
 *
 * @param pctxt        Pointer to context block structure.
 * @param pvalue       OSXSDDateTime type pointer points to a OSXSDDateTime
 *                     value to receive decoded result.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecDateTime (OSCTXT* pctxt, OSXSDDateTime* pvalue);

/**
 * This function decodes a variable of the XSD 'gYear' type.
 * Input is expected to be a string of characters returned
 * by a JSON parser. The string should have CCYY[-+hh:mm|Z] format.
 *
 * @param pctxt        Pointer to context block structure.
 * @param pvalue       OSXSDDateTime type pointer points to a OSXSDDateTime
 *                     value to receive decoded result.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecGYear (OSCTXT* pctxt, OSXSDDateTime* pvalue);

/**
 * This function decodes a variable of the XSD 'gYearMonth' type.
 * Input is expected to be a string of characters returned
 * by a JSON parser. The string should have CCYY-MM[-+hh:mm|Z] format.
 *
 * @param pctxt        Pointer to context block structure.
 * @param pvalue       OSXSDDateTime type pointer points to a OSXSDDateTime
 *                     value to receive decoded result.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecGYearMonth (OSCTXT* pctxt, OSXSDDateTime* pvalue);

/**
 * This function decodes a variable of the XSD 'gMonth' type.
 * Input is expected to be a string of characters returned
 * by a JSON parser. The string should have --MM[-+hh:mm|Z] format.
 *
 * @param pctxt        Pointer to context block structure.
 * @param pvalue       OSXSDDateTime type pointer points to a OSXSDDateTime
 *                     value to receive decoded result.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecGMonth (OSCTXT* pctxt, OSXSDDateTime* pvalue);

/**
 * This function decodes a variable of the XSD 'gMonthDay' type.
 * Input is expected to be a string of characters returned
 * by a JSON parser. The string should have --MM-DD[-+hh:mm|Z] format.
 *
 * @param pctxt        Pointer to context block structure.
 * @param pvalue       OSXSDDateTime type pointer points to a OSXSDDateTime
 *                     value to receive decoded result.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecGMonthDay (OSCTXT* pctxt, OSXSDDateTime* pvalue);

/**
 * This function decodes a variable of the XSD 'gDay' type.
 * Input is expected to be a string of characters returned
 * by a JSON parser. The string should have ---DD[-+hh:mm|Z] format.
 *
 * @param pctxt        Pointer to context block structure.
 * @param pvalue       OSXSDDateTime type pointer points to a OSXSDDateTime
 *                     value to receive decoded result.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecGDay (OSCTXT* pctxt, OSXSDDateTime* pvalue);

/**
 * This function decodes the contents of a decimal data type.
 * Input is expected to be a string of OSUTF8CHAR characters returned
 * by a JSON parser.
 *
 * @param pctxt        Pointer to context block structure.
 * @param pvalue       Pointer to 64-bit double value to receive
 *                       decoded result.
 * @param totalDigits  The total number of digits in the decimal value.
 * @param fractionDigits The number of fractional digits in the decimal value.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecDecimal (OSCTXT* pctxt, OSREAL* pvalue,
                        int totalDigits, int fractionDigits);

/**
 * This function decodes the contents of a float or double data type.
 * Input is expected to be a string of OSUTF8CHAR characters returned
 * by a JSON parser.
 *
 * @param pctxt        Pointer to context block structure.
 * @param pvalue       Pointer to 64-bit double value to receive
 *                       decoded result.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecDouble (OSCTXT* pctxt, OSREAL* pvalue);

/**
 * This function decodes a JSON string, interpreting the content as the
 * hexadecimal represention of the bytes for a character string, which it
 * returns.
 * This function is used to support the JSON encoding specified in X.697 for
 * the following ASN.1 types: TeletexString, T61String, VideotexString,
 * GraphicString, and GeneralString.
 *
 * @param pctxt        Pointer to context block structure.
 * @param ppvalue      Pointer to an string structure to receive the
 *                       decoded string.  Memory is allocated for the string
 *                       using the run-time memory manager.
 *                     If null, the JSON string is decoded but not retained.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecHexToCharStr (OSCTXT* pctxt, OSUTF8CHAR** ppvalue);


/**
 * This function decodes a JSON string consisting of hexadecimal characters
 * into a static memory structure.
 * Input is expected to be a string of OSUTF8CHAR characters returned
 * by a JSON parser.
 *
 * @param pctxt        A pointer to a context structure. This provides a
 *                       storage area for the function to store all working
 *                       variables that must be maintained between function
 *                       calls.
 * @param pvalue       A pointer to a variable to receive the decoded bit
 *                       string. This is assumed to be a static array large
 *                       enough to hold the number of octets specified in the
 *                       bufsize input parameter.
 * @param pnocts       A pointer to an integer value to receive the decoded
 *                       number of octets.
 * @param bufsize      The size (in octets) of
 *                       the sized octet string. An error will occur if
 *                       the number of octets in the decoded string is larger
 *                       than this value.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecHexStr (OSCTXT* pctxt, OSOCTET* pvalue,
                        OSUINT32* pnocts, size_t bufsize);

/**
 * This function is identical to rtJsonDecHexStr except that it supports
 * lengths up to 64-bits in size on 64-bit machines.
 *
 * @param pctxt        A pointer to a context structure. This provides a
 *                       storage area for the function to store all working
 *                       variables that must be maintained between function
 *                       calls.
 * @param pvalue       A pointer to a variable to receive the decoded bit
 *                       string. This is assumed to be a static array large
 *                       enough to hold the number of octets specified in the
 *                       bufsize input parameter.
 * @param pnocts       A pointer to an integer value to receive the decoded
 *                       number of octets.
 * @param bufsize      The size (in octets) of
 *                       the sized octet string. An error will occur if
 *                       the number of octets in the decoded string is larger
 *                       than this value.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 * @see rtJsonDecHexStr
 */
EXTERNJSON int rtJsonDecHexStr64(OSCTXT* pctxt, OSOCTET* pvalue,
                        OSSIZE* pnocts, size_t bufsize);

/**
 * This function deocdes a sequence of heaxadecimal characters until a
 * non-hexadecimal character (which is not consumed) is found OR the
 * preallocated array is filled.
 *
 * @param pctxt        A pointer to a context structure. This provides a
 *                       storage area for the function to store all working
 *                       variables that must be maintained between function
 *                       calls.
 * @param pvalue       A pointer to a variable to receive the decoded bit
 *                       string. This is assumed to be a preallocated array
 *                       large enough to hold the number of octets specified in
 *                       the bufsize input parameter.
 * @param pnocts       A pointer to an integer value to receive the decoded
 *                       number of octets.
 * @param bufsize      The size (in octets) of pvalue.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecHexData64(OSCTXT* pctxt, OSOCTET* pvalue,
                                    OSSIZE* pnocts, size_t bufsize);


/**
 * This function decodes a JSON string consisting of hexadecimal characters.
 * This function will allocate dynamic memory to store the decoded result.
 * Input is expected to be a string of OSUTF8CHAR characters returned
 * by a JSON parser.
 *
 * @param pctxt        A pointer to a context structure. This provides a
 *                       storage area for the function to store all working
 *                       variables that must be maintained between function
 *                       calls.
 * @param pvalue       A pointer to a dynamic octet string structure to receive
 *                       the decoded octet string. Dynamic memory is allocated
 *                       to hold the string using the ::rtxMemAlloc function.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecDynHexStr (OSCTXT* pctxt, OSDynOctStr* pvalue);


/**
 * This function is identical to rtJsonDecDynHexStr except that it supports
 * 64-bit integer lengths on 64-bit systems.
 *
 * @param pctxt        A pointer to a context structure. This provides a
 *                       storage area for the function to store all working
 *                       variables that must be maintained between function
 *                       calls.
 * @param pvalue       A pointer to a dynamic octet string structure to receive
 *                       the decoded octet string. Dynamic memory is allocated
 *                       to hold the string using the ::rtxMemAlloc function.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecDynHexStr64 (OSCTXT* pctxt, OSDynOctStr64* pvalue);


/**
 * This function decodes a sequence of hexadecimal characters until a
 * non-hexadecimal character (which is not consumed) is found.
 *
 * @param pctxt        A pointer to a context structure. This provides a
 *                       storage area for the function to store all working
 *                       variables that must be maintained between function
 *                       calls.
 * @param pvalue       A pointer to a dynamic octet string structure to receive
 *                       the decoded octet string. Dynamic memory is allocated
 *                       to hold the string using the ::rtxMemAlloc function.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecDynHexData64 (OSCTXT* pctxt, OSDynOctStr64* pvalue);


/**
 * This function decodes a variable of the ASN.1 Bit string type.
 * This provides ObjSys-specific behavior that predates ITU-T X.697.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nbits        A pointer to an unsigned integer to receive the number
 *                      of bits in the bit string.
 * @param data         A pointer to an OSOCTET array that will receive the
 *                      decoded bit string; the array will be allocated by
 *                      the decoding function.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecDynBitStrV72
   (OSCTXT* pctxt, OSUINT32 *nbits, OSOCTET **data);


/**
 * This function is identical to rtJsonDecDynBitStrV72 except that it supports
 * lengths up to 64-bits in size on 64-bit machines.
 * This provides ObjSys-specific behavior that predates ITU-T X.697.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nbits        A pointer to an unsigned integer to receive the number
 *                      of bits in the bit string.
 * @param data         A pointer to an OSOCTET array that will receive the
 *                      decoded bit string; the array will be allocated by
 *                      the decoding function.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 * @see rtJsonDecDynBitStrV72
 */
EXTERNJSON int rtJsonDecDynBitStr64V72
   (OSCTXT* pctxt, OSSIZE *nbits, OSOCTET **data);

/**
 * This function decodes a variable of the ASN.1 Bit string type.
 * This provides ObjSys-specific behavior that predates ITU-T X.697.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nbits        A pointer to an unsigned integer to receive the number
 *                      of bits in the bit string.
 * @param data         A pointer to an OSOCTET array that will receive the
 *                      decoded bit string.  The array must be preallocated.
 * @param bufsize      Size of the static buffer in bytes into which the
 *                      data is to be decoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecBitStrValueV72
(OSCTXT* pctxt, OSUINT32 *nbits, OSOCTET *data, OSSIZE bufsize);

/**
 * This function is identical to rtJsonDecBitStrValueV72 except that it supports
 * lengths up to 64-bits in size on 64-bit machines.
 * This provides ObjSys-specific behavior that predates ITU-T X.697.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nbits        A pointer to an unsigned integer to receive the number
 *                      of bits in the bit string.
 * @param data         A pointer to an OSOCTET array that will receive the
 *                      decoded bit string.  The array must be preallocated.
 * @param bufsize      Size of the static buffer in bytes into which the
 *                      data is to be decoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 * @see rtJsonDecBitStrValueV72
 */
EXTERNJSON int rtJsonDecBitStrValue64V72
(OSCTXT* pctxt, OSSIZE *nbits, OSOCTET *data, OSSIZE bufsize);

/**
 * This function decodes a variable of the ASN.1 Bit string type.
 * It handles bit strings with extdata member present.
 * This provides ObjSys-specific behavior that predates ITU-T X.697.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nbits        A pointer to an unsigned integer to receive the number
 *                      of bits in the bit string.
 * @param data         A pointer to an OSOCTET array that will receive the
 *                      decoded bit string.  The array must be preallocated.
 * @param bufsize      Size of the static buffer in bytes into which the
 *                      data is to be decoded.
 * @param extdata      A pointer to an OSOCTET array that will receive the
 *                      decoded extdata value.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecBitStrValueExtV72(OSCTXT* pctxt,
                                       OSUINT32 *nbits, OSOCTET *data,
                                       OSSIZE bufsize, OSOCTET **extdata);

/**
 * This function is identical to rtJsonDecBitStrValueExtV72 except that it
 * supports lengths up to 64-bits in size on 64-bit machines.
 * This provides ObjSys-specific behavior that predates ITU-T X.697.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nbits        A pointer to an unsigned integer to receive the number
 *                      of bits in the bit string.
 * @param data         A pointer to an OSOCTET array that will receive the
 *                      decoded bit string.  The array must be preallocated.
 * @param bufsize      Size of the static buffer in bytes into which the
 *                      data is to be decoded.
 * @param extdata      A pointer to an OSOCTET array that will receive the
 *                      decoded extdata value.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 * @see rtJsonDecBitStrValueExtV72
 */
EXTERNJSON int rtJsonDecBitStrValueExt64V72(OSCTXT* pctxt,
                                         OSSIZE *nbits, OSOCTET *data,
                                         OSSIZE bufsize, OSOCTET **extdata);

/**
 * This function decodes a value of an ASN.1 BIT STRING type, not constrained
 * to a fixed length, encoded according to X.697 as a JSON object.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nbits        A pointer to an unsigned integer to receive the number
 *                      of bits in the bit string.
 * @param data         A pointer to an OSOCTET array that will receive the
 *                      decoded bit string; the array will be allocated by
 *                      the decoding function.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecDynBitStr
   (OSCTXT* pctxt, OSUINT32 *nbits, OSOCTET **data);

/**
 * This function is identical to rtJsonDecDynBitStr except that it supports
 * lengths up to 64-bits in size on 64-bit machines.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nbits        A pointer to an unsigned integer to receive the number
 *                      of bits in the bit string.
 * @param data         A pointer to an OSOCTET array that will receive the
 *                      decoded bit string; the array will be allocated by
 *                      the decoding function.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 * @see rtJsonDecDynBitStr
 */
EXTERNJSON int rtJsonDecDynBitStr64
   (OSCTXT* pctxt, OSSIZE *nbits, OSOCTET **data);

/**
 * This function decodes a value of an ASN.1 BIT STRING type constrained to a
 * fixed length, encoded according to X.697 as a JSON string.
 *
 * This ensures the encoded data is the given number of bits and that unused
 * bits are zeros.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nbits        A pointer to an unsigned integer to receive the number
 *                      of bits in the bit string.
 * @param data         A pointer to an OSOCTET array that will receive the
 *                      decoded bit string; the array will be allocated by
 *                      the decoding function.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecFixedDynBitStr
   (OSCTXT* pctxt, OSSIZE nbits, OSOCTET **data);


/**
 * This function decodes a value of an ASN.1 BIT STRING type that is not
 * constrained to a fixed length, encoded according to X.697 as a JSON object.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nbits        A pointer to an unsigned integer to receive the number
 *                      of bits in the bit string.
 * @param data         A pointer to an OSOCTET array that will receive the
 *                      decoded bit string.  The array must be preallocated.
 * @param bufsize      Size of the static buffer in bytes into which the
 *                      data is to be decoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecBitStrValue
(OSCTXT* pctxt, OSUINT32 *nbits, OSOCTET *data, OSSIZE bufsize);

/**
 * This function is identical to rtJsonDecBitStrValue except that it supports
 * lengths up to 64-bits in size on 64-bit machines.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nbits        A pointer to an unsigned integer to receive the number
 *                      of bits in the bit string.
 * @param data         A pointer to an OSOCTET array that will receive the
 *                      decoded bit string.  The array must be preallocated.
 * @param bufsize      Size of the static buffer in bytes into which the
 *                      data is to be decoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 * @see rtJsonDecBitStrValue
 */
EXTERNJSON int rtJsonDecBitStrValue64
(OSCTXT* pctxt, OSSIZE *nbits, OSOCTET *data, OSSIZE bufsize);


/**
 * This function decodes a value of an ASN.1 BIT STRING type constrained to
 * have the given fixed length, encoded according to X.697 as a JSON string.
 *
 * This ensures the encoded data is the given number of bits and that unused
 * bits are zeros.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nbits        The number of bits the BIT STRING is fixed to.
 * @param data         A pointer to an OSOCTET array that will receive the
 *                      decoded bit string.  The array must be preallocated.
 * @param bufsize      Size of the static buffer in bytes into which the
 *                      data is to be decoded.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecFixedBitStrValue
(OSCTXT* pctxt, OSSIZE nbits, OSOCTET *data, OSSIZE bufsize);


/**
 * This function decodes a value of a ASN.1 BIT STRING type without a
 * fixed-length constraint, encoded according to X.697 as JSON object.
 *
 * It handles bit strings with extdata member present.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nbits        A pointer to an unsigned integer to receive the number
 *                      of bits in the bit string.
 * @param data         A pointer to an OSOCTET array that will receive the
 *                      decoded bit string.  The array must be preallocated.
 * @param bufsize      Size of the static buffer in bytes into which the
 *                      data is to be decoded.
 * @param extdata      A pointer to an OSOCTET array that will receive the
 *                      decoded extdata value.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecBitStrValueExt(OSCTXT* pctxt,
                                       OSUINT32 *nbits, OSOCTET *data,
                                       OSSIZE bufsize, OSOCTET **extdata);

/**
 * This function is identical to rtJsonDecBitStrValueExt except that it
 * supports lengths up to 64-bits in size on 64-bit machines.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nbits        A pointer to an unsigned integer to receive the number
 *                      of bits in the bit string.
 * @param data         A pointer to an OSOCTET array that will receive the
 *                      decoded bit string.  The array must be preallocated.
 * @param bufsize      Size of the static buffer in bytes into which the
 *                      data is to be decoded.
 * @param extdata      A pointer to an OSOCTET array that will receive the
 *                      decoded extdata value.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 * @see rtJsonDecBitStrValueExt
 */
EXTERNJSON int rtJsonDecBitStrValueExt64(OSCTXT* pctxt,
                                         OSSIZE *nbits, OSOCTET *data,
                                         OSSIZE bufsize, OSOCTET **extdata);

#define rtJsonDecInt8Value rtxTxtReadInt8

#define rtJsonDecInt16Value rtxTxtReadInt16

#define rtJsonDecInt32Value rtxTxtReadInt32

#define rtJsonDecIntValue rtxTxtReadInt32

#define rtJsonDecInt64Value rtxTxtReadInt64

#define rtJsonDecUInt8Value rtxTxtReadUInt8

#define rtJsonDecUInt16Value rtxTxtReadUInt16

#define rtJsonDecUInt32Value rtxTxtReadUInt32

#define rtJsonDecUIntValue rtxTxtReadUInt32

#if defined OSSIZE_IS_32BITS
#define rtJsonDecIntSizeValue(pctxt, pvalue) rtxTxtReadUInt32(pctxt,pvalue)
#elif defined OSSIZE_IS_64BITS
#define rtJsonDecIntSizeValue(pctxt, pvalue) rtxTxtReadUInt64(pctxt,pvalue)
#endif

#define rtJsonDecUInt64Value rtxTxtReadUInt64

/**
 * This function attempts to match the given character, skipping over any
 * whitesapce, if necessary.  If a different character is found, this function
 * returns RTERR_INVCHAR and does not consume the non-matching character.
 *
 * @param pctxt        Pointer to context block structure.
 * @param ch           The character to be matched.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - RTERR_INVCHAR = different character found
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecMatchChar (OSCTXT* pctxt, OSUTF8CHAR ch);

/**
 * This function decodes a JSON string and matches with a given token.
 * This is equivalent to rtJsonDecMatchToken.
 *
 * @param pctxt        A pointer to a context structure. This provides a
 *                       storage area for the function to store all working
 *                       variables that must be maintained between function
 *                       calls.
 * @param token        The token to be matched.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecMatchCharStr (OSCTXT* pctxt, const char* token);

/**
 * This function matches the start of a JSON object.
 * This will skip leading whitespace, then match the opening '{'.  It will
 * then match a key that matches any of the values in nameArray, and, if
 * successful, it then matches the subsequent ':' character after the key.
 *
 * There is no indication of which name was matched, making this function
 * not very useful.  See also rtJsonDecStringObject.
 *
 * It is an error if there is not an opening '{', if the key does not match
 * any of the given names, or if the ':' character is not found.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nameArray    Array of names to be matched.
 * @param numNames     Number of names in the name array
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecMatchObjectStart
(OSCTXT* pctxt, const OSUTF8NameAndLen* nameArray, size_t numNames);

/**
 * This function decodes a JSON string and matches with a given token.
 *
 * @param pctxt        A pointer to a context structure. This provides a
 *                       storage area for the function to store all working
 *                       variables that must be maintained between function
 *                       calls.
 * @param token        The token to be matched.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecMatchToken (OSCTXT* pctxt, const OSUTF8CHAR* token);

/**
 * This function decodes a JSON string and matches with a given token.
 *
 * @param pctxt        A pointer to a context structure. This provides a
 *                       storage area for the function to store all working
 *                       variables that must be maintained between function
 *                       calls.
 * @param token        The token to be matched.
 * @param tokenLen     The length of the token to be matched.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecMatchToken2
(OSCTXT* pctxt, const OSUTF8CHAR* token, size_t tokenLen);

/**
 * This function decodes a name/value pair.
 *
 * @param pctxt        Pointer to context block structure.
 * @param pvalue       Pointer to an structure to receive the
 *                       decoded name and value.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecNameValuePair (OSCTXT* pctxt, OSUTF8NVP* pvalue);


/**
 * This function decodes a JSON null.
 *
 * @param   pctxt    A pointer to a context data structure.
 *
 * @return  0 on success, less than zero otherwise.
 */
EXTERNJSON int rtJsonDecNull (OSCTXT *pctxt);

/**
 * This function will attempt to decode a null value at the current
 * buffer or stream position.  If the attempt fails, the decode cursor is
 * reset to the position it was at when the function was called and an
 * RTERR_IDNOTFOU status is returned.  The error is not logged in the context.
 *
 * @param pctxt        Pointer to context block structure.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - RTERR_IDNOTFOU = not boolean value (not logged)
 *                       - negative return value if other error (logged)
 */
EXTERNJSON int rtJsonTryDecNull (OSCTXT* pctxt);

/**
 * This function decodes a JSON number into a character string variable.
 *
 * @param pctxt        Pointer to context block structure.
 * @param ppCharStr    Pointer to character string pointer to receive
 *                       decoded value.  Dynamic memory is allocated for
 *                       the string using the rtxMemAlloc function.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecNumberString (OSCTXT* pctxt, char** ppCharStr);

/**
 * This function determines the next non-whitespace character in the input.
 * The non-whitespace character is not consumed.
 *
 * @param pctxt         Pointer to OSCTXT structure
 * @param pch           A pointer to a variable to receive the next character.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
#define rtJsonDecPeekChar(pctxt, pch) rtxTxtPeekChar(pctxt, pch, TRUE)

/**
 * This function determines the next non-whitespace character in the input.
 * The non-whitespace character is not consumed.
 *
 * @param pctxt         Pointer to OSCTXT structure
 * @return              The peeked character, or null if there is a failure.
 *                         The error will be logged in the context.
 */
#define rtJsonDecPeekChar2(pctxt) rtxTxtPeekChar2(pctxt, TRUE)

/**
 * This function decodes a JSON object containing a single entry with the given
 * key (name), and returns the key's associated value, which must be a JSON
 * string, via ppvalue.
 *
 * @param pctxt        Pointer to context block structure.
 * @param name         The name token.
 * @param ppvalue      Pointer to an string structure to receive the
 *                       decoded string.  Memory is allocated for the string
 *                       using the run-time memory manager.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecStringObject
(OSCTXT* pctxt, const OSUTF8CHAR* name, OSUTF8CHAR** ppvalue);

/**
 * This function decodes the contents of a string data type.
 * This type contains a pointer to a UTF-8 characer string.
 * Input is expected to be a string of UTF-8 characters returned by
 * a JSON parser.
 *
 * @param pctxt        Pointer to context block structure.
 * @param ppvalue      Pointer to an string structure to receive the
 *                       decoded string.  Memory is allocated for the string
 *                       using the run-time memory manager.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecStringValue (OSCTXT* pctxt, OSUTF8CHAR** ppvalue);

/**
* This function is the same as rtJsonDecStringValue except that it decodes
* into a character array.
*
* @param pctxt        Pointer to context block structure.
* @param pvalue       Pointer to character array to decode into.
* @param bufize       Size of the given array.
* @return             Completion status of operation:
*                       - 0 = success,
*                       - negative return value is error.
*/
EXTERNJSON int rtJsonDecStringValueArray(OSCTXT* pctxt, OSUTF8CHAR* pvalue,
                                          OSSIZE bufsize);

/**
 * This function decodes the contents of an XML string data type.
 * This type contains a pointer to a UTF-8 characer string plus flags
 * that can be set to alter the encoding of the string (for example, the
 * cdata flag allows the string to be encoded in a CDATA section).
 * Input is expected to be a string of UTF-8 characters returned by
 * a JSON parser.
 *
 * @param pctxt        Pointer to context block structure.
 * @param pvalue       Pointer to an XML string structure to receive the
 *                       decoded string.  Memory is allocated for the string
 *                       using the run-time memory manager.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - negative return value is error.
 */
EXTERNJSON int rtJsonDecXmlStringValue (OSCTXT* pctxt, OSXMLSTRING* pvalue);

/**
 * This function is used to decode input UTF-8 data into a UCS-2 / UTF-16
 * character string.
 *
 * @param   pctxt    A pointer to the context block structure.
 * @param   ppstr    A pointer to a UTF-16 string; memory will be allocated
 *                      to hold the string using the run-time memory manager.
 * @param   pnchars  A pointer to an integer to hold the number of characters
 *                      in the string. (The number of octets may be found
 *                      by multiplying by two.)
 *
 * @return  0 on success; less than zero on error.
 */
EXTERNJSON int rtJsonDecUCS2String (OSCTXT *pctxt, OSUNICHAR **ppstr,
      OSSIZE *pnchars);

/**
 * This function is used to decode input UTF-8 data into a UCS-4 / UTF-32
 * character string.
 *
 * @param   pctxt    A pointer to the context block structure.
 * @param   ppstr    A pointer to a UTF-32 string; memory will be allocated
 *                      to hold the string using the run-time memory manager.
 * @param   pnchars  A pointer to an integer to hold the number of characters
 *                      in the string. (The number of octets may be found
 *                      by multiplying by two.)
 *
 * @return  0 on success; less than zero on error.
 */
EXTERNJSON int rtJsonDecUCS4String (OSCTXT *pctxt, OS32BITCHAR **ppstr,
      OSSIZE *pnchars);

#define rtJsonDecSkipWhitespace rtxTxtSkipWhitespace

/**
 * This function determines which of several possible JSON strings appears
 * next in the input.
 *
 * This will skip any leading whitespace and then parses a JSON string. It is
 * an error if the input does not have a JSON string.  The value of the
 * JSON string is then matched against one of the values in nameArray and the
 * corresponding index is returned.
 *
 * @param pctxt        Pointer to context block structure.
 * @param nameArray    Elements descriptor table.
 * @param nrows        Number of descriptors in table.
 * @return             Completion status of operation:
 *                       - positive or zero value is element identifier,
 *                       - OSNULLINDEX return value is error.
 */
EXTERNJSON size_t rtJsonGetElemIdx
(OSCTXT* pctxt, const OSUTF8NameAndLen nameArray[], size_t nrows);

/**
 * @}
 */


#ifdef __cplusplus
}
#endif

#endif
