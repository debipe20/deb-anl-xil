/*
 * Copyright (c) 1997-2022 Objective Systems, Inc.
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

// rtsrc/asn1CppEvtHndlr64.h - this .h file defines the object that is
// registered for the C++ version of the event handler feature.

/**
 * @file rtsrc/asn1CppEvtHndlr64.h
 * Declarations for C++ named event handlers.  These declarations use size-typed
 * arguments for all lengths and index variables which provides a full 64-bit
 * range for these variables.
 */
/**
 * @addtogroup Asn1EventHandler
 * @{
 */
#ifndef _ASN1CPPEVTHNDLR64_H_
#define _ASN1CPPEVTHNDLR64_H_

#include "rtsrc/asn1CppEvtHndlr.h"

#ifndef _WIN32
/* Set gcc to ignore the "virtual override intended?" warning for this header
   file.  It is not an error - the override is indeed intended (ASN-9912).
   However, a customer who has warnings set as errors (such as for ASN-11080)
   will get compilation failures if it is not marked as ignored...
*/
#pragma GCC diagnostic ignored "-Woverloaded-virtual"
#endif

// The following pure abstract class defines the event handler interface
// callback functions that are invoked as a message is parsed..
/**
 * Named event handler base class.  This is the base class from which
 * user-defined event handler classes are derived.  These classes can be
 * used to handle events during the parsing of an ASN.1 message.  The
 * event callback methods that can be implemented are startElement,
 * endElement, and contents methods.
 */
class EXTRTCLASS Asn1NamedEventHandler64 : public Asn1NullEventHandler {
 public:
   Asn1NamedEventHandler64() {}
   virtual ~Asn1NamedEventHandler64() {}

   // Start element callback function.  This is invoked upon entry into
   // an element in a constructed type (SEQUENCE, SET, SEQUENCE OF,
   // SET OF, or CHOICE).  A single char* argument (name) is passed.
   /**
    * This method is invoked from within a decode function when an element of a
    * SEQUENCE, SET, SEQUENCE OF, SET OF, or CHOICE construct is parsed.
    *
    * @param name         For SEQUENCE, SET, or CHOICE, this is the name of the
    *                       element as defined in the ASN.1 defination. For
    *                       SEQUENCE OF or SET OF, this is set to the name
    *                       "element".
    * @param index        For SEQUENCE, SET, or CHOICE, this is not used and is
    *                       set to the value OSNULLINDEX.
    *                       For SEQUENCE OF or SET OF, this contains the
    *                       zero-based index of the element in the conceptual
    *                       array associated with the construct.
    * @return             - none
    */
   virtual void startElement (const char* name, OSSIZE index) = 0;
#if __cplusplus >= 201103L
   using Asn1NullEventHandler::startElement;
#endif

   // End element callback function.  This is invoked upon exit from
   // a constructed type.  A single char* argument (name) is passed.
   /**
    * This method is invoked from within a decode function when parsing is
    * complete on an element of a SEQUENCE, SET, SEQUENCE OF, SET OF, or CHOICE
    * construct.
    *
    * @param name         For SEQUENCE, SET, or CHOICE, this is the name of the
    *                       element as defined in the ASN.1 defination. For
    *                       SEQUENCE OF or SET OF, this is set to the name
    *                       "element".
    * @param index        For SEQUENCE, SET, or CHOICE, this is not used and is
    *                       set to the value OSNULLINDEX.
    *                       For SEQUENCE OF or SET OF, this contains the
    *                       zero-based index of the element in the conceptual
    *                       array associated with the construct.
    * @return             - none
    */
   virtual void endElement (const char* name, OSSIZE index) = 0;
#if __cplusplus >= 201103L
   using Asn1NullEventHandler::endElement;
#endif

   // Data callback functions.  These are invoked when data contents
   // are parsed from a field.  A separate callback is invoked for
   // each of the ASN.1 primitive data types..

   /**
    * This method is invoked from within a decode function when a value of the
    * BIT STRING ASN.1 type is parsed.
    *
    * @param numbits      - Number of bits in the parsed value.
    * @param data         - Pointer to a byte array that contains the bit
    *                         string data.
    * @return             - none
    */
   virtual void bitStrValue (OSSIZE numbits, const OSOCTET* data) {
      OS_UNUSED_ARG(numbits);  OS_UNUSED_ARG(data);
   }
#if __cplusplus >= 201103L
   using Asn1NamedEventHandler::bitStrValue;
#endif

   /**
    * This method is invoked from within a decode function when a value of one
    * of the OCTET STRING ASN.1 type is parsed.
    *
    * @param numocts      Number of octets in the parsed value.
    * @param data         Pointer to byte array containing the octet string
    *                       data.
    * @return             - none
    */
   virtual void octStrValue (OSSIZE numocts, const OSOCTET* data) {
      OS_UNUSED_ARG(numocts);  OS_UNUSED_ARG(data);
   }
#if __cplusplus >= 201103L
   using Asn1NamedEventHandler::octStrValue;
#endif

   /**
    * This method is invoked from within a decode function when a value of a
    * UTF-8 character string type is parsed.
    *
    * @param nchars     Number of characters in the parsed value.
    * @param value      A UTF-8 character string.
    * @return           - none
    */
   virtual void charStrValue (OSSIZE nchars, const OSUTF8CHAR* value) {
      OS_UNUSED_ARG(nchars); OS_UNUSED_ARG(value);
   }
#if __cplusplus >= 201103L
   using Asn1NamedEventHandler::charStrValue;
#endif

   /**
    * This method is invoked from within a decode function when a value of one
    * of the 16-bit ASN.1 character string types is parsed.
    *
    * This is used for the ASN.1 BmpString type.
    *
    * @param nchars       Number of characters in the parsed value.
    * @param data         Pointer to an array containing 16-bit values.
    *                       These are represented using unsigned short integer
    *                       values.
    * @return             - none
    */
   virtual void charStrValue (OSSIZE nchars, OSUNICHAR* data) {
      OS_UNUSED_ARG(nchars); OS_UNUSED_ARG(data);
   }

   /**
    * This method is invoked from within a decode function when a value of one
    * of the 32-bit ASN.1 characer string types is parsed.
    *
    * This is used for the ASN.1 UniversalString type.
    *
    * @param nchars       Number of characters in the parsed value.
    * @param data         Pointer to an array containing 32-bit values.
    *                       Each 32-bit integer value is a universal character.
    * @return             - none
    */
   virtual void charStrValue (OSSIZE nchars, OS32BITCHAR* data) {
      OS_UNUSED_ARG(nchars); OS_UNUSED_ARG(data);
   }

   /**
    * This value is invoked from within a decode function when an ASN.1 open
    * type is parsed.
    *
    * @param numocts      Number of octets in the parsed value.
    * @param data         Pointer to byet array contain in tencoded ASN.1
    *                       value.
    * @return             - none
    */
   virtual void openTypeValue (OSSIZE numocts, const OSOCTET* data) {
      OS_UNUSED_ARG(numocts); OS_UNUSED_ARG(data);
   }
#if __cplusplus >= 201103L
   using Asn1NamedEventHandler::openTypeValue;
#endif

   // The following static methods are invoked from within the generated
   // code to call the various user-defined event handler methods ..

   /**
    * This method is called by generated code to invoke the event handlers'
    * start element methods.  It is static.
    *
    * @param   pCtxt       A pointer to an ::OSCTXT data structure.
    * @param   name        The name of the element.
    * @param   index       The index of the element, if it is in a SEQUENCE
    *                         or SET OF type.
    */
   EXTRTMETHOD static void invokeStartElement
      (OSCTXT* pCtxt, const char* name, OSSIZE index);

   /**
    * This method is called by generated code to invoke the event handlers'
    * end element methods.  It is static.
    *
    * @param   pCtxt       A pointer to an ::OSCTXT data structure.
    * @param   name        The name of the element.
    * @param   index       The index of the element, if it is in a SEQUENCE
    *                         or SET OF type.
    */
   EXTRTMETHOD static void invokeEndElement
      (OSCTXT* pCtxt, const char* name, OSSIZE index);

   /**
    * This method is called by generated code to invoke the event handlers'
    * bit string method.  It is static.
    *
    * @param   pCtxt       A pointer to an ::OSCTXT data structure.
    * @param   numbits     The number of bits in the decoded bit string.
    * @param   data        The decoded bit string data.
    */
   EXTRTMETHOD static void invokeBitStrValue
      (OSCTXT* pCtxt, OSSIZE numbits, const OSOCTET* data);

   /**
    * This method is called by generated code to invoke the event handlers'
    * octet string method.  It is static.
    *
    * @param   pCtxt       A pointer to an ::OSCTXT data structure.
    * @param   numocts     The number of octets in the decoded octet string.
    * @param   data        The decoded octet string data.
    */
   EXTRTMETHOD static void invokeOctStrValue
      (OSCTXT* pCtxt, OSSIZE numocts, const OSOCTET* data);

   /**
    * This method is called by generated code to invoke the event handlers'
    * 16-bit character string method.  It is static.
    *
    * @param   pCtxt       A pointer to an ::OSCTXT data structure.
    * @param   nchars      The number of characters in the string.
    * @param   value       The decoded 16-bit character string.
    */
   EXTRTMETHOD static void invokeCharStrValue
      (OSCTXT* pCtxt, OSSIZE nchars, OSUNICHAR* data);

   /**
    * This method is called by generated code to invoke the event handlers'
    * 32-bit character string method.  It is static.
    *
    * @param   pCtxt       A pointer to an ::OSCTXT data structure.
    * @param   nchars      The number of characters in the string.
    * @param   value       The decoded character string.
    */
   EXTRTMETHOD static void invokeCharStrValue
      (OSCTXT* pCtxt, OSSIZE nchars, OS32BITCHAR* data);

   /**
    * This method is called by generated code to invoke the event handlers'
    * UTF-8 character string method.  It is static.
    *
    * @param   pCtxt       A pointer to an ::OSCTXT data structure.
    * @param   nchars      The number of characters in the string.
    * @param   value       The decoded character string.
    */
   EXTRTMETHOD static void invokeCharStrValue
      (OSCTXT* pCtxt, OSSIZE nchars, const OSUTF8CHAR* data);

   /**
    * This method is called by generated code to invoke the event handlers'
    * open type method.  It is static.
    *
    * @param   pCtxt       A pointer to an ::OSCTXT data structure.
    * @param   numocts     The number of octets in the open type.
    * @param   data        The data octets that comprise the open type value.
    */
   EXTRTMETHOD static void invokeOpenTypeValue
      (OSCTXT* pCtxt, OSSIZE numocts, const OSOCTET* data);

} ;

// Null event handler class.  This class contains an empty implementation
// of all user methods..

/**
 * The Asn1NullEventHandler contains a completely empty implementation of all
 * user methods.
 */
class EXTRTCLASS Asn1NullEventHandler64 : public Asn1NamedEventHandler64 {
 public:
   /** This startElement method does nothing. */
   virtual void startElement (const char* , OSSIZE ) {}
   /** This endElement method does nothing. */
   virtual void endElement (const char* , OSSIZE ) {}
} ;

/**
 * @}
 */
#endif
