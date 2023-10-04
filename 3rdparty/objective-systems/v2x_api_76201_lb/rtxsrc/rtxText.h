/*
* Copyright (c) 2003-2022 Objective Systems, Inc.
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
* @file rtxText.h
*/

#ifndef _RTXTEXT_H_
#define _RTXTEXT_H_

#include "rtxContext.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Run-time functions for reading/writing values to/from the context buffer
   in text form.
*/

/**
* @defgroup textReadWrite Text Reading and Writing Functions
* @{
*
* These functions support working with a textual representation of values.
* Values of various C/C++ types can be written to, or read from, the 
* context buffer, with the buffer holding a text representation.
*/

/**
 * This function matches the given character or logs and returns an error.
 *
 * You may optionally choose to skip any leading whitespace.
 *
 * @param pctxt        Pointer to context block structure.
 * @param ch           The character to be matched.
 * @param skipWs       If TRUE, skip any leading whitespace.
 * @return             Completion status of operation:
 *                       - 0 = success,
 *                       - RTERR_INVCHAR = different character found
 *                       - negative return value is error.
 */
EXTERNRT int rtxTxtMatchChar(OSCTXT* pctxt, OSUTF8CHAR ch, OSBOOL skipWs);


/**
* This function matches the given characters or logs and returns an error.
*
* You may optionally choose to skip any leading whitespace.
*
* @param pctxt        Pointer to context block structure.
* @param chars        The characters to be matched.
* @param skipWs       If TRUE, skip any leading whitespace.
* @return             Completion status of operation:
*                       - 0 = success,
*                       - RTERR_INVCHAR = different character found
*                       - negative return value is error.
*/
EXTERNRT int rtxTxtMatchChars(OSCTXT* pctxt, const OSUTF8CHAR* chars, 
                                 OSBOOL skipWs);

/**
* This function determines the next character in the input.
* 
* You may optionally skip any whitespace and peek at the first non-whitespace
* character.  Skipping whitespace consumes it.
* 
* It is an error if EOF prevents a character from being returned.
*
* @param pctxt         Pointer to OSCTXT structure
* @param pch           A pointer to a variable to receive the next character.
* @return             Completion status of operation:
*                       - 0 = success,
*                       - negative return value is error.
*/
EXTERNRT int rtxTxtPeekChar(OSCTXT* pctxt, OSUTF8CHAR* pch, OSBOOL skipWs);

/**
* This function determines the next character in the input.
*
* You may optionally skip any whitespace and peek at the first non-whitespace
* character.  Skipping whitespace consumes it.
*
* It is an error if EOF prevents a character from being returned.
*
* @param pctxt         Pointer to OSCTXT structure
* @return              The peeked character, or null if there is a failure.
*                         The error will be logged in the context.
*/
EXTERNRT char rtxTxtPeekChar2(OSCTXT* pctxt, OSBOOL skipWs);


/**
* This function skips any whitespace in the input.
*
* @param pctxt         Pointer to OSCTXT structure
* @return             Completion status of operation:
*                       - 0 = success,
*                       - negative return value is error.
*/
EXTERNRT int rtxTxtSkipWhitespace(OSCTXT* pctxt);


/**
* This function reads an integer, using standard decimal notation, into
* a character string.  Leading whitespace is consumed.
*
* This recognizes an optional minus sign, followed by 1 or more digits,
* with no superfluous leading zeros.
*
* @param pctxt        Pointer to context block structure.
* @param ppvalue       Pointer to string to receive newly allocated string with
*                     decoded result.
* @return             Completion status of operation:
*                       - 0 = success,
*                       - negative return value is error.
*/
EXTERNRT int rtxTxtReadBigInt(OSCTXT* pctxt, char** ppvalue);

/**
* This function reads an integer, using standard decimal notation, into
* an 8-bit signed integer.  Leading whitespace is consumed.
*
* This recognizes an optional minus sign, followed by 1 or more digits,
* with no superfluous leading zeros.
*
* @param pctxt        Pointer to context block structure.
* @param pvalue       Pointer to 8-bit integer value to receive
*                       decoded result.
* @return             Completion status of operation:
*                       - 0 = success,
*                       - negative return value is error.
*/
EXTERNRT int rtxTxtReadInt8(OSCTXT* pctxt, OSINT8* pvalue);

/**
* This function reads an integer, using standard decimal notation, into
* an 16-bit signed integer.  Leading whitespace is consumed.
*
* This recognizes an optional minus sign, followed by 1 or more digits,
* with no superfluous leading zeros.
*
* @param pctxt        Pointer to context block structure.
* @param pvalue       Pointer to 16-bit integer value to receive
*                       decoded result.
* @return             Completion status of operation:
*                       - 0 = success,
*                       - negative return value is error.
*/
EXTERNRT int rtxTxtReadInt16(OSCTXT* pctxt, OSINT16* pvalue);

/**
* This function reads an integer, using standard decimal notation, into
* an 32-bit signed integer.  Leading whitespace is consumed.
*
* This recognizes an optional minus sign, followed by 1 or more digits,
* with no superfluous leading zeros.
*
* @param pctxt        Pointer to context block structure.
* @param pvalue       Pointer to 32-bit integer value to receive
*                       decoded result.
* @return             Completion status of operation:
*                       - 0 = success,
*                       - negative return value is error.
*/
EXTERNRT int rtxTxtReadInt32(OSCTXT* pctxt, OSINT32* pvalue);

/**
* This function reads an integer, using standard decimal notation, into
* an 64-bit signed integer.  Leading whitespace is consumed.
*
* This recognizes an optional minus sign, followed by 1 or more digits,
* with no superfluous leading zeros.
*
* @param pctxt        Pointer to context block structure.
* @param pvalue       Pointer to 64-bit integer value to receive
*                       decoded result.
* @return             Completion status of operation:
*                       - 0 = success,
*                       - negative return value is error.
*/
EXTERNRT int rtxTxtReadInt64(OSCTXT* pctxt, OSINT64* pvalue);

/**
* This function reads an integer, using standard decimal notation, into
* an 8-bit unsigned integer.  Leading whitespace is consumed.
*
* This recognizes 1 or more digits, with no superfluous leading zeros.
*
* @param pctxt        Pointer to context block structure.
* @param pvalue       Pointer to 8-bit unsigned integer value to receive
*                       decoded result.
* @return             Completion status of operation:
*                       - 0 = success,
*                       - negative return value is error.
*/
EXTERNRT int rtxTxtReadUInt8(OSCTXT* pctxt, OSUINT8* pvalue);

/**
* This function reads an integer, using standard decimal notation, into
* an 16-bit unsigned integer.  Leading whitespace is consumed.
*
* This recognizes 1 or more digits, with no superfluous leading zeros.
*
* @param pctxt        Pointer to context block structure.
* @param pvalue       Pointer to 16-bit unsigned integer value to receive
*                       decoded result.
* @return             Completion status of operation:
*                       - 0 = success,
*                       - negative return value is error.
*/
EXTERNRT int rtxTxtReadUInt16(OSCTXT* pctxt, OSUINT16* pvalue);

/**
* This function reads an integer, using standard decimal notation, into
* an 32-bit unsigned integer.  Leading whitespace is consumed.
*
* This recognizes 1 or more digits, with no superfluous leading zeros.
*
* @param pctxt        Pointer to context block structure.
* @param pvalue       Pointer to 32-bit unsigned integer value to receive
*                       decoded result.
* @return             Completion status of operation:
*                       - 0 = success,
*                       - negative return value is error.
*/
EXTERNRT int rtxTxtReadUInt32(OSCTXT* pctxt, OSUINT32* pvalue);

/**
* This function reads an integer, using standard decimal notation, into
* an 64-bit unsigned integer.  Leading whitespace is consumed.
*
* This recognizes 1 or more digits, with no superfluous leading zeros.
*
* @param pctxt        Pointer to context block structure.
* @param pvalue       Pointer to 64-bit unsigned integer value to receive
*                       decoded result.
* @return             Completion status of operation:
*                       - 0 = success,
*                       - negative return value is error.
*/
EXTERNRT int rtxTxtReadUInt64(OSCTXT* pctxt, OSUINT64* pvalue);

/**
* This writes a 32-bit signed integer to the buffer using standard decimal
* (base 10) notation.  A sign is used only for negative values.
*
* @param pctxt        Pointer to context block structure.
* @param value        Value to be encoded.
* @return             Completion status of operation:
*                       - 0 = success,
*                       - negative return value is error.
*/
EXTERNRT int rtxTxtWriteInt(OSCTXT* pctxt, OSINT32 value);

/**
* This writes a 64-bit signed integer to the buffer using standard decimal
* (base 10) notation.  A sign is used only for negative values.
*
* @param pctxt        Pointer to context block structure.
* @param value        Value to be encoded.
* @return             Completion status of operation:
*                       - 0 = success,
*                       - negative return value is error.
*/
EXTERNRT int rtxTxtWriteInt64(OSCTXT* pctxt, OSINT64 value);


/**
* This writes a 32-bit unsigned integer to the buffer using standard decimal
* (base 10) notation.  No sign is used.
*
* @param pctxt        Pointer to context block structure.
* @param value        Value to be encoded.
* @return             Completion status of operation:
*                       - 0 = success,
*                       - negative return value is error.
*/
EXTERNRT int rtxTxtWriteUInt(OSCTXT* pctxt, OSUINT32 value);

/**
* This writes a 64-bit unsigned integer to the buffer using standard decimal
* (base 10) notation.  No sign is used.
*
* @param pctxt        Pointer to context block structure.
* @param value        Value to be encoded.
* @return             Completion status of operation:
*                       - 0 = success,
*                       - negative return value is error.
*/
EXTERNRT int rtxTxtWriteUInt64(OSCTXT* pctxt, OSUINT64 value);

/**
* @}
*/

#ifdef __cplusplus
}
#endif

#endif
