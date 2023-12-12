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
 * @file rtxBuffer.h
 * Common runtime functions for reading from or writing to the message
 * buffer defined within the context structure.
 */
#ifndef _RTXBUFFER_H_
#define _RTXBUFFER_H_

#include "rtxsrc/rtxContext.h"
#include "rtxsrc/rtxSList.h"

/* reserve octets to enable short backoffs */
#define MIN_STREAM_BACKOFF 0


/**
* @defgroup bufreadwrite Context Message Buffer Read/Write Functions
* @{
*
* The context message buffer can be written to, or read from, using various
* functions.
*/

/**
 Buffer location descriptor
*/
typedef struct _OSRTBufLocDescr {
   OSSIZE numocts;
   OSSIZE offset;
} OSRTBufLocDescr;

#ifdef __cplusplus
extern "C" {
#endif


EXTERNRT int rtxCheckBuffer (OSCTXT* pctxt, size_t nbytes);

/**
 * This function checks to ensure that the output buffer has sufficient space
 * to hold an additional nbytes full bytes (if there is a partially filled byte,
 * it is treated as though full). Dynamic buffers are resized if the
 * check fails, while static buffers induce a buffer overflow error. This
 * function may return RTERR_NOMEM if reallocating the dynamic buffer fails.
 *
 * @param   pctxt    Pointer to a context structure.
 * @param   nbytes   The requested capacity for the buffer.
 *
 * @return  0 on success, or less than zero on failure.
 */
EXTERNRT int rtxCheckOutputBuffer (OSCTXT* pctxt, size_t nbytes);


/**
 * This function returns true if the context buffer can be flushed to
 * a stream by calling rtxFlushOutputBuffer.  This function is used to determine
 * whether it is safe to call rtxFlushOutputBuffer.
 *
 * @param   pctxt    Pointer to a context structure.
 *
 * @return  TRUE if the buffer can be flushed; FALSE is not.
 */
EXTERNRT OSBOOL rtxIsOutputBufferFlushable(OSCTXT* pctxt);


/**
 * This function flushes the buffer to a stream.
 * This function MUST only be called if rtxIsOutputBufferFlushable(pctxt)
 * returns TRUE; the behavior is otherwise undefined.
 * After a successful call, pctxt->buffer.byteIndex == 0.  Note that
 * pctxt->buffer.bitOffset is not changed - if there was a partial byte in the
 * buffer before this call, there will be a partial by afterward.
 *
 * @param   pctxt    Pointer to a context structure.
 *
 * @return  0 on success, or less than zero on failure.
 */
EXTERNRT int rtxFlushOutputBuffer(OSCTXT* pctxt);


/**
 * This function attempts to ensure the output buffer has at least the given
 * number of bytes available.  A partially full byte in the buffer counts
 * as being available.  Dynamic buffers are resized, if necessary,
 * while static buffers induce a buffer overflow error. This function may
 * return RTERR_NOMEM if reallocating a dynamic buffer fails.
 *
 * @param   pctxt    Pointer to a context structure.
 * @param   nbytes   The requested capacity for the buffer.
 *
 * @return  0 on success, or less than zero on failure.
 */
EXTERNRT int rtxExpandOutputBuffer (OSCTXT* pctxt, size_t nbytes);

/**
 * Ensures the given number of bytes are available in the context buffer.
 *
 * If a stream is attached to the context and is being buffered by the
 * context buffer, this may read from the stream to fill the buffer.  Thus this
 * function may alter the context buffer byteIndex and size.  Any bytes read
 * from the stream will be sent to the capture buffer, if there is one.
 *
 * @return 0 on success, or less than zero on failure.  RTERR_ENDOFBUF or
 * RTERR_ENDOFFILE (depending on whether the source is a stream or not)
 * is returned if the requested number of bytes are not available in the
 * input.
 */
EXTERNRT int rtxCheckInputBuffer (OSCTXT* pctxt, size_t nbytes);

EXTERNRT int rtxCopyAsciiText (OSCTXT* pctxt, const char* text);

EXTERNRT int rtxCopyUTF8Text (OSCTXT* pctxt, const OSUTF8CHAR* text);

EXTERNRT int rtxCopyUnicodeText (OSCTXT* pctxt, const OSUNICHAR* text);

/**
 * This is for meant for internal use by the runtime.
 *
 * Read at least as many bytes from the context's input stream into the
 * context buffer as necessary to make nbytes of data available in the context
 * buffer.
 *
 * Upon return, pctxt.buffer.byteIndex + nbytes <= pctxt.buffer.size OR
 * EOF has been reached OR an error has been logged and is being returned.
 *
 * If the context buffer has not been created, this will create it.  If the
 * context buffer needs to be made larger, this will enlarge it or else log,
 * and return, an error.
 *
 * @param pctxt   A context with an attached stream using the context's buffer
 *    as a buffer for the stream.
 * @return        0 or or negative error. EOF is not considered an error.
 */
EXTERNRT int rtxLoadInputBuffer(OSCTXT* pctxt, OSSIZE nbytes);

/**
 * This function peeks at the next byte of input, if there is one before EOF.
 * A return of 1 ensures the peeked byte can be skipped by incrementing
 * pctxt->buffer.byteIndex.
 * @param pbyte        Receives the value of the peeked byte.
 * @return        0 if there was no byte to peek at.
 *                1 if there was a byte to peek at.
 *                <0 if there was an error.
 */
EXTERNRT int rtxPeekByte(OSCTXT* pctxt, OSOCTET* pbyte);

/**
 * This function peeks at the next nocts bytes of input, peeking at fewer bytes
 * if EOF is encountered first.
 * A returned value (in *pactual) of n (>=0) ensures that n (or fewer) peeked
 * bytes can be skipped by adding n (or less) to pctxt->buffer.byteIndex.
 *
 * @param pdata        Receives the value of the peeked bytes.
 * @param bufsize      Size of pdata.  If less than nocts, nocts will be
 *                     adjusted accordingly.
 * @param nocts        The number of bytes to peek.
 * @param pactual      Receives the actual number of bytes peeked.
 * @return        0 for success
 *                <0 if there was an error.
 */
EXTERNRT int rtxPeekBytes(OSCTXT* pctxt, OSOCTET* pdata, OSSIZE bufsize,
                           OSSIZE nocts, OSSIZE* pactual);

/**
 * This function safely reads bytes from the currently open stream or
 * memory buffer into the given static buffer.  This function is preferred
 * over \c rtxReadBytes because it will detect buffer overflow.
 *
 * @param pctxt         Pointer to a context structure.
 * @param buffer        Static buffer into which bytes are to be read.
 * @param bufsize       Size of the static buffer.
 * @param nocts         Number of bytes (octets) to read.
 * @return              Status of the operation: 0 if success,
 *                        negative value if error.
 */
EXTERNRT int rtxReadBytesSafe
(OSCTXT* pctxt, OSOCTET* buffer, size_t bufsize, size_t nocts);

/**
 * This function reads bytes from the currently open stream or memory buffer.
 *
 * @param pctxt         Pointer to a context structure.
 * @param pdata         Pointer to byte array where bytes are to be copied.
 * @param nocts         Number of bytes (octets) to read.
 * @return              Status of the operation: 0 if success,
 *                        negative value if error.
 */
EXTERNRT int rtxReadBytes (OSCTXT* pctxt, OSOCTET* pdata, size_t nocts);

/**
 * This function reads bytes from the currently open stream or memory buffer.
 * In this case the function MAY allocate memory to hold the read bytes.  It
 * will only do this if the requested number of bytes will not fit in the
 * context buffer; othwerwise, a pointer to a location in the context buffer
 * is returned.  If memory was allocated, it should be freed using
 * rtxMemFreePtr.
 *
 * @param pctxt         Pointer to a context structure.
 * @param ppdata        Pointer to byte buffer pointer.
 * @param nocts         Number of bytes (octets) to read.
 * @param pMemAlloc     Pointer to boolean value which is set to true if
 *                        memory was allocated to hold requested bytes.
 * @return              Status of the operation: 0 if success,
 *                        negative value if error.
 */
EXTERNRT int rtxReadBytesDynamic
(OSCTXT* pctxt, OSOCTET** ppdata, size_t nocts, OSBOOL* pMemAlloc);

/**
 * This function writes bytes to the currently open stream or memory buffer.
 *
 * @param pctxt         Pointer to a context structure.
 * @param pdata         Pointer to location where bytes are to be copied.
 * @param nocts         Number of bytes to read.
 * @return              I/O byte count.
 */
EXTERNRT int rtxWriteBytes
(OSCTXT* pctxt, const OSOCTET* pdata, size_t nocts);


/**
* This function writes a newline followed by indentation whitespace to the
* buffer.  The amount of indentation to add is determined by the indent member
* variable in the context structure.
*
* If context flag OSNOWHITESPACE is set, this function will do nothing.
*
* @param pctxt        Pointer to context block structure.
* @return             Completion status of operation:
*                       - 0 = success,
*                       - negative return value is error.
*/
EXTERNRT int rtxWriteIndent(OSCTXT* pctxt);

/**
* This decreases the indentation level set in the given context by
* updating the indent member.
*
* @see rtxGetIndentLevels
*
* @param pctxt        Pointer to context block structure.
*/
EXTERNRT void rtxIndentDecr(OSCTXT* pctxt);

/**
* This increases the indentation level set in the given context by
* updating the indent member.
*
* @see rtxGetIndentLevels
*
* @param pctxt        Pointer to context block structure.
*/
EXTERNRT void rtxIndentIncr(OSCTXT* pctxt);

/**
* This resets the indentation level in the given context to zero.
*
* @see rtxGetIndentLevels
*
* @param pctxt        Pointer to context block structure.
*/
EXTERNRT void rtxIndentReset(OSCTXT* pctxt);


/**
* This returns the number of levels of indentation set in the given context.
* Currently, the indentation level in the context affects
* rtxPrintToStreamIndent (when used with a non-null OSCTXT), rtxWriteIndent,
* and rtJsonEncIndent, meaning it currently affects print-to-stream output,
* Abstract Syntax Notation output, and JSON (JER) output.
*
* @param pctxt        Pointer to context block structure.
*/
EXTERNRT size_t rtxGetIndentLevels(OSCTXT* pctxt);


/**
 * Sort a list of buffer locations, referring to component encodings, by
 * comparing the referenced encodings as octet strings.
 *
 * The sorting can be used with canonical-BER (CER), distinguished-BER (DER),
 * and canonical-XER (XER).
 *
 * Encoding into the buffer may be done as a normal encoding (start to end) or
 * as a reverse encoding (end to start).  This affects the parameters as
 * described below.
 *
 * @param refPoint      Reference point in the buffer for the buffer locations.
 *                      For normal encoding, refPoint is the start of the
 *                      buffer; for reverse encoding, refPoint is the end of the
 *                      buffer.
 * @param pList         List of OSRTBufLocDescr, each of which locates the
 *                      start of an encoded component.  The offsets for the
 *                      locations are relative to refPoint.
 *                      If normal is TRUE, this function orders the list from
 *                      least to greatest.  Otherwise, it is ordered from
 *                      greatest to least.
 * @param normal        TRUE for normal encoding; FALSE for reverse encoding.
 *                      This tells the function whether to add or substract
 *                      offsets from refPoint to locate the component encodings
 *                      and also how to order the list.
 * @returns             TRUE if any changes to pList were made; FALSE otherwise
 *                      (meaning the list was already in the desired order).
 */
EXTERNRT OSBOOL rtxCanonicalSort (OSOCTET* refPoint, OSRTSList* pList,
                                 OSBOOL normal);


#ifndef _NO_STREAM
/**
 * Encode the encodings held in pMemCtxt into pctxt, first sorting them as
 * required for canonical BER (and other encoding rules) by X.690 11.6.
 *
 * @param pctxt         Pointer to context structure into which the sorted
 *                      encodings should be encoded.
 * @param pMemCtxt      Pointer to context structure which holds the unsorted
 *                      encodings.
 * @param pList         List of Asn1BufLocDescr, each of which locates an
 *                      encoding in pMemCtxt's buffer, the whole being the
 *                      encodings that are to be sorted.
 */
EXTERNRT int rtxEncCanonicalSort (OSCTXT* pctxt,
                                   OSCTXT* pMemCtxt,
                                   OSRTSList* pList);

/**
 * Set the buffer location description's offset (pDescr->offset) to the current
 * position in pCtxt's buffer.
 */
EXTERNRT void rtxGetBufLocDescr (OSCTXT *pctxt, OSRTBufLocDescr* pDescr);

/**
 * Create a new Asn1BufLocDescr for an element just encoded and append it to
 * pElemList.
 *
 * @param pctxt      Pointer to context where data has been encoded.
 * @param pElemList  List of Asn1BufLocDescr to which a new entry will be added.
 * @param pDescr     Pointer to Asn1BufLocDescr whose offset indicates the start
 *                   of the element just encoded.  The new Asn1BufLocDescr that
 *                   is added will have the same offset and will have numocts
 *                   determined by this offset and pctxt's current buffer
 *                   position.
 */
EXTERNRT void rtxAddBufLocDescr (OSCTXT *pctxt, OSRTSList* pElemList,
                                  OSRTBufLocDescr* pDescr);
#endif /* _NO_STREAM */

/* Macros */

#define OSRTPUTCHAR(pctxt,ch) rtxWriteBytes (pctxt, (OSOCTET*)&ch, 1)

#define OSRTPUTCHARREV(pctxt,ch) \
(pctxt)->buffer.data[--(pctxt)->buffer.byteIndex]=(OSOCTET)ch;

#define OSRTZTERM(pctxt) \
(pctxt)->buffer.data[(pctxt)->buffer.byteIndex]=(OSOCTET)0;

#define OSRTSAFEZTERM(pctxt) \
do { \
if (rtxCheckOutputBuffer (pctxt, 1) == 0) \
(pctxt)->buffer.data[(pctxt)->buffer.byteIndex]=(OSOCTET)0; \
else return LOG_RTERRNEW (pctxt, RTERR_BUFOVFLW); \
} while (0)

#define OSRTSAFEPUTCHAR(pctxt,ch) \
do { \
if (rtxCheckOutputBuffer (pctxt, 1) == 0) \
(pctxt)->lastChar= \
(pctxt)->buffer.data[(pctxt)->buffer.byteIndex++]=(OSOCTET)ch; \
else return LOG_RTERRNEW (pctxt, RTERR_BUFOVFLW); \
} while (0)

/* Put character into buffer and terminate buffer with null character.
   Execute return LOG_RTERRNEW if there is not room in the buffer and
   the buffer cannot be expanded to make room.
*/
#define OSRTSAFEPUTCHAR_ZTERM(pctxt,ch) \
do { \
if (rtxCheckOutputBuffer (pctxt, 2) == 0) { \
(pctxt)->lastChar= \
(pctxt)->buffer.data[(pctxt)->buffer.byteIndex++]=(OSOCTET)ch; \
(pctxt)->buffer.data[(pctxt)->buffer.byteIndex]=(OSOCTET)0; } \
else return LOG_RTERRNEW (pctxt, RTERR_BUFOVFLW); \
} while (0)


#define OSRTSAFEPUTCHAR1(pctxt,ch,stat) \
do { \
OSOCTET b = (OSOCTET)ch; \
rtxWriteBytes (pctxt, &b, 1); \
} while (0)

#if 0
#define OSRTSAFEPUTCHAR2(pctxt,ch,prealloc) \
do { \
if (rtxCheckOutputBuffer (pctxt, ((prealloc > 1)?prealloc:1)) == 0) \
(pctxt)->lastChar= \
(pctxt)->buffer.data[(pctxt)->buffer.byteIndex++]=(OSOCTET)ch; \
else return LOG_RTERRNEW (pctxt, RTERR_BUFOVFLW); \
} while (0)
#endif

#define OSRTMEMCPY(pctxt,bdata,len) \
do { \
OSCRTLSAFEMEMCPY (&(pctxt)->buffer.data[(pctxt)->buffer.byteIndex], \
      (pctxt)->buffer.size-(pctxt)->buffer.byteIndex, bdata, len); \
(pctxt)->buffer.byteIndex += len; \
(pctxt)->lastChar = (pctxt)->buffer.data[(pctxt)->buffer.byteIndex-1]; \
} while (0)

#define OSRTMEMCPYREV(pctxt,bdata,len) \
do { \
(pctxt)->buffer.byteIndex -= len; \
OSCRTLSAFEMEMCPY (&(pctxt)->buffer.data[(pctxt)->buffer.byteIndex], \
      (pctxt)->buffer.size-(pctxt)->buffer.byteIndex, bdata, len); \
} while (0)

#define OSRTSAFEMEMCPY(pctxt,bdata,len) \
do { \
if (rtxCheckOutputBuffer (pctxt, len) == 0) { \
OSCRTLMEMCPY (&(pctxt)->buffer.data[(pctxt)->buffer.byteIndex], bdata, len); \
(pctxt)->buffer.byteIndex += len; \
(pctxt)->lastChar = (pctxt)->buffer.data[(pctxt)->buffer.byteIndex-1]; } \
else return LOG_RTERRNEW (pctxt, RTERR_BUFOVFLW); \
} while (0)

#define OSRTSAFEMEMCPY1(pctxt,bdata,len,stat) \
do { \
if (rtxCheckOutputBuffer (pctxt, len) == 0) { \
OSCRTLMEMCPY (&(pctxt)->buffer.data[(pctxt)->buffer.byteIndex], bdata, len); \
(pctxt)->buffer.byteIndex += len; \
(pctxt)->lastChar = (pctxt)->buffer.data[(pctxt)->buffer.byteIndex-1]; \
stat = 0; } \
else stat = RTERR_BUFOVFLW; \
} while (0)

#define OSRTGETBUFUTF8LEN(pctxt) \
rtxCalcUTF8Len (OSRTBUFPTR (pctxt), OSRTBUFSIZE (pctxt))

#define OSRTCHKBUFUTF8LEN(pctxt,lower,upper,stat) \
do { size_t nchars = OSRTGETBUFUTF8LEN (pctxt); \
stat = (nchars >= lower && nchars <= upper) ? 0 : RTERR_CONSVIO; } while(0)

#define OSRTENDOFBUF(pctxt) ((pctxt)->buffer.byteIndex >= (pctxt)->buffer.size)

#define OSRTByteAlign(pctxt)          \
if ((pctxt)->buffer.bitOffset != 8) { \
   (pctxt)->buffer.byteIndex++;       \
   (pctxt)->buffer.bitOffset = 8; }   \

   /**
* @} bufreadwrite
*/


#ifdef __cplusplus
}
#endif

#endif
