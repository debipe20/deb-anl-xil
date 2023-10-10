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
 * @file OSXMLMessageBuffer.h
 * XML encode/decode buffer and stream base class.
 */
#ifndef _OSXMLMESSAGEBUFFER_H_
#define _OSXMLMESSAGEBUFFER_H_

#include "rtxsrc/OSRTMsgBuf.h"
#include "rtxmlsrc/osrtxml.h"

/**
 * The XML message buffer class is derived from the OSMessageBuffer
 * base class. It is the base class for the OSXMLEncodeBuffer
 * and OSXMLDecodeBuffer classes. It contains variables and methods
 * specific to encoding or decoding XML messages.  It is used to manage
 * the buffer into which a message is to be encoded or decoded.
 *
 */
class EXTXMLCLASS OSXMLMessageBuffer : public OSRTMessageBuffer {
 protected:
   /**
    * The protected constructor creates a new context and sets the buffer class
    * type.
    *
    * @param bufferType   Type of message buffer that is being created (for
    *                       example, XMLEncode or XMLDecode).
    * @param pContext     Pointer to a context to use. If NULL, new context
    *                       will be allocated.
    */
   EXTXMLMETHOD OSXMLMessageBuffer (Type bufferType, OSRTContext* pContext = 0);

 public:
   /**
    * The getAppInfo method returns the pointer to application context
    * information.
    */
   EXTXMLMETHOD virtual void* getAppInfo ();

   /**
    * This method returns current XML output indent value.
    *
    * @return              Current indent value (>= 0) if OK, negative status
    *                      code if error.
    */
   EXTXMLMETHOD int getIndent ();

   /**
    * This method returns current XML output indent character value
    * (default is space).
    *
    * @return              Current indent character (> 0) if OK,
    *                      negative status code if error.
    */
   EXTXMLMETHOD int getIndentChar ();

   /**
    * This function returns whether writing the Unicode BOM is currently
    * enabled or disabled.
    *
    * @return              TRUE if writing BOM is enabled, FALSE otherwise.
    */
   EXTXMLMETHOD OSBOOL getWriteBOM ();

   /**
    * This method sets a namespace in the context namespace list.  If the
    * given namespace URI does not exist in the list, the namespace is added.
    * If the URI is found, the value of the namespace prefix will be changed
    * to the given prefix.
    *
    * @param prefix        Namespace prefix
    * @param uri           Namespace URI
    * @param pNSAttrs      Namespace list to which namespace is to be added
    */
   EXTXMLMETHOD virtual void setNamespace
      (const OSUTF8CHAR* prefix, const OSUTF8CHAR* uri,
       OSRTDList* pNSAttrs = 0);

   /**
    * This method sets application specific context information within
    * the common context structure.  For XML encoding/decoding, this is
    * a structure of type <i>OSXMLCtxtInfo</i>.
    *
    * @param pXMLInfo      Pointer to context information.
    */
   EXTXMLMETHOD virtual void setAppInfo (void* pXMLInfo);

   /**
    * This method sets XML output formatting to the given value.
    * If TRUE (the default), the XML document is formatted with indentation
    * and newlines.  If FALSE, all whitespace between elements is suppressed.
    * Turning formatting off can provide more compressed documents and also
    * a more canonical representation which is important for security
    * applications.
    *
    * @param doFormatting  Boolean value indicating if formatting is to be done
    * @return              Status of operation: 0 if OK, negative status
    *                      code if error.
    */
   EXTXMLMETHOD void setFormatting (OSBOOL doFormatting);

   /**
    * This method sets XML output indent to the given value.
    *
    * @param indent        Number of spaces per indent. Default is 3.
    */
   EXTXMLMETHOD void setIndent (OSUINT8 indent);

   /**
    * This method sets XML output indent character to the given value.
    *
    * @param indentChar    Indent character. Default is space.
    */
   EXTXMLMETHOD void setIndentChar (char indentChar);

   /**
    * This method sets whether to write the Unicode byte order mark
    * before the XML header.
    *
    * @param write          TRUE if BOM should be written, FALSE otherwise.
    */
   EXTXMLMETHOD void setWriteBOM (OSBOOL write);

} ;


/**
 * OSXMLEncodeBase is a base class for the XML encode buffer and
 * stream classes, OSXMLEncodeBuffer and OSXMLEncodeStream.
 */
class EXTXMLCLASS OSXMLEncodeBase : public OSXMLMessageBuffer {

 protected:
   /**
    * The protected constructor creates a new context and sets the buffer class
    * type.
    *
    * @param pContext     Pointer to a context to use. If NULL, new context
    *                       will be allocated.
    */
   EXTXMLMETHOD OSXMLEncodeBase (OSRTContext* pContext = 0);


 public:

   /**
    * This function encodes an attribute in which the name and value
    * are given as null-terminated UTF-8 strings.
    *
    * @param name         Attribute name.
    * @param value        UTF-8 string value to be encoded.
    * @return             Completion status of operation:
    *                       - 0 = success,
    *                       - negative return value is error.
    */
   EXTXMLMETHOD int encodeAttr
      (const OSUTF8CHAR* name, const OSUTF8CHAR* value);

   /**
    * This method encodes XML textual content.  XML metadata characters
    * such as '<' are escaped. The input value is specified in UTF-8
    * character format but may be transformed if a different character
    * encoding is enabled.
    *
    * @param value        UTF-8 string value to be encoded.
    * @return             Completion status of operation:
    *                       - 0 = success,
    *                       - negative return value is error.
    */
   EXTXMLMETHOD int encodeText (const OSUTF8CHAR* value);

   /**
    * This method ends an XML document by flushing any remaining data
    * to the stream.
    */
   EXTXMLMETHOD int endDocument ();

   /**
    * This method encodes an end element tag value (\</elemName\>).
    *
    * @param elemName     XML element name.
    * @param pNS          XML namespace information (prefix and URI).
    * @return             Completion status of operation:
    *                       - 0 = success,
    *                       - negative return value is error.
    */
   EXTXMLMETHOD int endElement
      (const OSUTF8CHAR* elemName, OSXMLNamespace* pNS = 0);

   /**
    * This method writes information to start an XML document to the
    * encode stream.  This includes the XML header declaration.
    */
   EXTXMLMETHOD int startDocument ();

   /**
    * This method writes information to start an XML element to the
    * encode stream.  It can leave the element open so that attributes
    * can be added.
    *
    * @param elemName     XML element name.
    * @param pNS          XML namespace information (prefix and URI).  If the
    *                     prefix is NULL, this method will search the context's
    *                     namespace stack for a prefix to use.
    * @param pNSAttrs     List of namespace attributes to be added to element.
    * @param terminate    Add closing '>' character.
    * @return             Completion status of operation:
    *                       - 0 = success,
    *                       - negative return value is error.
    */
   EXTXMLMETHOD int startElement
      (const OSUTF8CHAR* elemName, OSXMLNamespace* pNS = 0,
       OSRTDList* pNSAttrs = 0, OSBOOL terminate = FALSE);

   /**
    * This metod terminates a currently open XML start element by adding
    * either a '>' or '/>' (if empty) terminator.  It will also add XSI
    * attributes to the element.  Note that is important to use this
    * method to terminate the element rather than writng a closing angle
    * bracket text to the stream directly due to the way state is maintained
    * in the context.
    *
    * @return             Completion status of operation:
    *                       - 0 = success,
    *                       - negative return value is error.
    */
   EXTXMLMETHOD int termStartElement ();
};


#endif

