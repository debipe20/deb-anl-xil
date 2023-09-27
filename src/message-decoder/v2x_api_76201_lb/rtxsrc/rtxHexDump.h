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
 * @file rtxHexDump.h
 */
#ifndef _RTXHEXDUMP_H_
#define _RTXHEXDUMP_H_

#include "rtxsrc/rtxContext.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @defgroup hexDumpFunc Hex Dump Functions
 * @{
 *
 * Function for printing binary data in hexadecimal text format and for doing
 * binary to hexadecimal text conversion.
 */
/**
 * This function converts a byte value into its hex string equivalent.
 *
 * @param byte          Byte to format.
 * @param buf           Output buffer.
 * @param bufsize       Output buffer size.
 */
EXTERNRT int rtxByteToHexChar (OSOCTET byte, char* buf, OSSIZE bufsize);

/**
 * This function converts a byte value into its hex string equivalent. The
 * hex string for this function is prefixed with the given parameter.
 *
 * @param byte          Byte to format.
 * @param buf           Output buffer.
 * @param bufsize       Output buffer size.
 * @param prefix        The string prefix.
 */
EXTERNRT int rtxByteToHexCharWithPrefix
   (OSOCTET byte, char* buf, OSSIZE bufsize, const char* prefix);

/**
 * This function outputs a hexadecimal dump of the current buffer contents to
 * the file with the given name.  The file is opened or created and then
 * closed after the writer operation is complete.
 *
 * @param filename     Full path to file to which data should be output.
 * @param data         The pointer to a buffer to be displayed.
 * @param numocts      The number of octets to be displayed
 * @return Status of operation: 0 for success or negative error code.
 */
EXTERNRT int rtxHexDumpToNamedFile
(const char* filename, const OSOCTET* data, OSSIZE numocts);

/**
 * This function outputs a hexadecimal dump of the current buffer contents to a
 * file.
 *
 * @param fp           A pointer to FILE structure. The file should be opened
 *                       for writing.
 * @param data         The pointer to a buffer to be displayed.
 * @param numocts      The number of octets to be displayed
 */
EXTERNRT void rtxHexDumpToFile
(FILE* fp, const OSOCTET* data, OSSIZE numocts);

/**
 * This function outputs a hexadecimal dump of the current buffer to a file,
 * but it may output the dump as an array of bytes, words, or double words.
 *
 * @param fp           A pointer to FILE structure. The file should be opened
 *                       for writing.
 * @param data         The pointer to a buffer to be displayed.
 * @param numocts      The number of octets to be displayed.
 * @param bytesPerUnit The number of bytes in one unit. May be 1 (byte), 2
 *                       (word), or 4 (double word).
 */
EXTERNRT void rtxHexDumpToFileEx
(FILE* fp, const OSOCTET* data, OSSIZE numocts, OSSIZE bytesPerUnit);

/**
 * This function outputs a hexadecimal dump of the current buffer to a file,
 * but it may output the dump as an array of bytes, words, or double words.
 * This function never contains an ASCII dump.
 *
 * @param fp           A pointer to FILE structure. The file should be opened
 *                       for writing.
 * @param data         The pointer to a buffer to be displayed.
 * @param numocts      The number of octets to be displayed.
 * @param bytesPerUnit The number of bytes in one unit. May be 1 (byte), 2
 *                       (word), or 4 (double word).
 */
EXTERNRT void rtxHexDumpToFileExNoAscii
(FILE* fp, const OSOCTET* data, OSSIZE numocts, OSSIZE bytesPerUnit);

/**
 * This function outputs a hexadecimal dump of the current buffer contents to
 * the file with the given name.  The file is opened or created and then
 * closed after the writer operation is complete.  The dump in this case
 * has no ASCII part which makes it easier to import into hex editor tools.
 *
 * @param filename     Full path to file to which data should be output.
 * @param data         The pointer to a buffer to be displayed.
 * @param numocts      The number of octets to be displayed.
 * @return Status of operation: 0 for success or negative error code.
 */
EXTERNRT int rtxHexDumpToNamedFileNoAscii
(const char* filename, const OSOCTET* data, OSSIZE numocts);

/**
 * This function outputs a hexadecimal dump of the current buffer contents to
 * stdout.
 *
 * @param data         The pointer to a buffer to be displayed.
 * @param numocts      The number of octets to be displayed.
 */
EXTERNRT void rtxHexDump (const OSOCTET* data, OSSIZE numocts);

/**
 * This function outputs a hexadecimal dump of the current buffer contents to
 * stdout, but it may display the dump as an array or bytes, words, or double
 * words.
 *
 * @param data         The pointer to a buffer to be displayed.
 * @param numocts      The number of octets to be displayed.
 * @param bytesPerUnit The number of bytes in one unit. May be 1 (byte), 2
 *                       (word), or 4 (double word).
 */
EXTERNRT void rtxHexDumpEx
(const OSOCTET* data, OSSIZE numocts, OSSIZE bytesPerUnit);

/**
 * This function formats a hexadecimal dump of the current buffer contents to a
 * string.
 *
 * @param data         The pointer to a buffer to be displayed.
 * @param numocts      The number of octets to be displayed.
 * @param buffer       The destination string buffer.
 * @param bufferIndex  The starting position in the destination buffer. The
 *                       formatting of the dump will begin at this position.
 * @param bufferSize   The total size of the destination buffer.
 * @return             The length of the final string.
 */
EXTERNRT int rtxHexDumpToString
(const OSOCTET* data, OSSIZE numocts, char* buffer, OSSIZE bufferIndex,
 OSSIZE bufferSize);

/**
 * This function formats a hexadecimal dump of the current buffer contents to a
 * string, but it may output the dump as an array of bytes, words, or double
 * words.
 *
 * @param data         The pointer to a buffer to be displayed.
 * @param numocts      The number of octets to be displayed.
 * @param buffer       The destination string buffer.
 * @param bufferIndex  The starting position in the destination buffer. The
 *                       formatting of the dump will begin at this position.
 * @param bufferSize   The total size of the destination buffer.
 * @param bytesPerUnit The number of bytes in one unit. May be 1 (byte), 2
 *                       (word), or 4 (double word).
 * @return             The length of the final string.
 */
EXTERNRT int rtxHexDumpToStringEx
(const OSOCTET* data, OSSIZE numocts, char* buffer,
 OSSIZE bufferIndex, OSSIZE bufferSize, OSSIZE bytesPerUnit);

/**
 * This function outputs a hexadecimal dump of the contents of the named
 * file to stdout.
 *
 * @param inFilePath   Name of file to be dumped.
 */
EXTERNRT int rtxHexDumpFileContents (const char* inFilePath);

/**
 * This function outputs a hexadecimal dump of the contents of the named
 * file to a text file.
 *
 * @param inFilePath   Name of file to be dumped.
 * @param outFilePath  Name of file to which dump contents will be written.
 */
EXTERNRT int rtxHexDumpFileContentsToFile
(const char* inFilePath, const char* outFilePath);

/**
 * This function generates a differences report between two binary data
 * buffers.  The buffers are assumed to each contain the same number of
 * bytes.  The result of the comparison operation is returned in a dynamic
 * allocated using the rtxMemAlloc function.  The buffer may be freed
 * using the rtxMemFreePtr function.
 *
 * @param pctxt    Pointer to context structure.
 * @param pdata1   Pointer to first binary buffer to compare.
 * @param pdata2   Pointer to second binary buffer to compare.
 * @param numocts  Number of bytes to compare.
 * @return Result of comparison in dynamically allocated string buffer.
 *   Null means buffers have no differences.  The format of the output
 *   is '[x]yy != zz, ...' where x is index and yy and zz are byte values.
 */
EXTERNRT char* rtxHexDiffToDynString
(OSCTXT* pctxt, const OSOCTET* pdata1, const OSOCTET* pdata2, OSSIZE numocts);

/**
 * @} hexDumpFunc
 */
#ifdef __cplusplus
}
#endif

#endif
