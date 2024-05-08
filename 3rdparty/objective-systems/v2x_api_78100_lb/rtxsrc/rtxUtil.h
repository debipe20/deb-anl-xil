/*
 * Copyright (c) 2003-2024 Objective Systems, Inc.
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

#ifndef _RTXUTIL_H_
#define _RTXUTIL_H_

#include "rtxsrc/osSysTypes.h"
#include "rtxsrc/rtxExternDefs.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Utility functions */

/**
 * Compare to byte strings, a and b, and return:
 *    <0 if a < b,
 *    0 if a == b,
 *    >0 if a > b
 * This has the same behavior as memcmp, except that if one of the strings
 * is longer, the function returns a value as if the strings had been of equal
 * length, with the shorter string having had trailing zero bytes appended to
 * match the length of the longer string.
 *
 * @param pa Pointer to first string to compare
 * @param palen Length of first string
 * @param pb Pointer to second string to compare
 * @param pblen Length of second string
 */
EXTERNRT int rtxByteStrCmp(OSOCTET* pa, OSSIZE palen,
                           OSOCTET* pb, OSSIZE pblen);

EXTERNRT OSUINT32 rtxGetIdentByteCount (OSUINT32 ident);

/**
 * Returns the smallest octet length needed to
 * hold the given long int value.
 */
EXTERNRT OSUINT32 rtxIntByteCount (OSINT32 val);

EXTERNRT OSUINT32 rtxOctetBitLen (OSOCTET w);

/**
 * Return the smallest number of bytes that can represent val in unsigned
 * integer format.
 */
EXTERNRT OSSIZE rtxSizeByteCount( OSSIZE val );

EXTERNRT OSUINT32 rtxUInt32BitLen (OSUINT32 w);

/**
 * This function retrieves the binary logarithm of the given value
 * (by excess).
 *
 * @param w     Word value for which to get binary logarithm.
 * @return      The smallest x such as w <= 2^x
 */
EXTERNRT OSUINT32 rtxLog2Ceil (OSSIZE w);

/**
 * This function retrieves the binary logarithm of the given value
 * (by default).
 *
 * @param w     Word value for which to get binary logarithm.
 * @return      The smallest x such as 2^x <= w < 2^(x+1)
 */
EXTERNRT OSUINT32 rtxLog2Floor (OSSIZE w);

/**
 * This function retrieves the base 10 logarithm of the given value, rounded
 * down.
 *
 * @param w     Word value for which to get base 10 logarithm.  w > 0.
 * @return      The smallest x such as 10^x <= w < 10^(x+1)
 */
EXTERNRT OSUINT32 rtxLog10Floor (OSUINT32 w);

/**
 * This function converts an IPv4 address string into binary form.
 *
 * @param ipv4str  IPv4 address string (xxx.xxx.xxx.xxx)
 * @param outbuf   Fixed-size output buffer to receive converted bytes. Must
 *                   be 4 bytes or more in size.
 * @param bufsize  Size of the output buffer.
 * @return         Status of the conversion operation.  Zero for success
 *                   or negative code.
 */
EXTERNRT int rtxIpv4AddrToBin
(const char* ipv4str, OSOCTET* outbuf, OSSIZE bufsize);

#if !defined(_NO_INT64_SUPPORT)
EXTERNRT int rtxEncIdent64(OSUINT64 ident, OSOCTET* buffer, OSSIZE bufsize);
EXTERNRT OSUINT32 rtxGetIdent64ByteCount (OSUINT64 ident);
EXTERNRT OSUINT32 rtxUInt64BitLen (OSUINT64 w);
#endif

typedef int (*OSCompareFn) (void* v1, void* v2);

/**
 * Function to do a binary search on a sorted array.
 * @param key Value passed as first argument to compare function.
 * @param pArray Pointer to first element in array.  The elements must be
 *       sorted consistent with the compare function.
 * @param arraySize Size of the array (number of elements)
 * @param elemSize Size of individual element in array
 * @param compare Function used to compare key to an element in the array.
 *          The first argument will be the key.  The second argument will be
 *          an element.  Thus, the key and the elements may be of different
 *          types.  It shall return:
 *          <0 if elements matching key are less than the given element
 *           0 if the key matches the element
 *          >0 if elements matching key are greater than the given element
 * @return Matching index or (OSSIZE)-1 if there is no match.  If multiple
 *    elements match the key, the index of the smallest such element is
 *    returned.
 */
EXTERNRT OSSIZE rtxArrayBinSearch(void* key, void* pArray, OSSIZE arraySize,
                  OSSIZE elemSize, OSCompareFn compare);


#ifdef __cplusplus
}
#endif

#endif
