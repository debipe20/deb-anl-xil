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

// rtsrc/asn1CppEvtHndlr.h - this .h file defines the object that is registered
// for the C++ version of the event handler feature.

/**
 * @file rtsrc/asn1CppRawEvtHndlr.h
 * Contains declarations for raw event handlers.
 */
/**
 * @addtogroup Asn1EventHandler
 * @{
 */
#ifndef _ASN1CPPRAWEVTHNDLR_H_
#define _ASN1CPPRAWEVTHNDLR_H_

#include "asn1CRawEvtHndlr.h"

class OSRTMessageBuffer;

/**
 * Asn1RawEventHandler is the base class for user-defined raw event handlers.
 */
class EXTRTCLASS Asn1RawEventHandler {
 public:
   Asn1RawEventHandler() {}
   virtual ~Asn1RawEventHandler() {}

   /**
    * This callback function is invoked from within a parser function when an
    * element of a SEQUENCE, SET, SEQUENCE OF, SET OF, or CHOICE construct is
    * parsed.
    *
    * @param pctxt          The OSCTXT object.  Provides access to the data
    *                       buffer.
    * @param componentID    Identifies the component for which the function is
    *                       being called. The code generator will generate a
    *                       globally unique identifier for each component.
    * @param nestedValues   TRUE if the component may contain nested values.
    * @return               Response from the handler.
    */
   virtual ASN1RawEventResp component(OSCTXT* pctxt, OSSIZE componentID,
      OSBOOL nestedValues) = 0;

   /**
   * This callback function is invoked to indicate the end of a component with
   * nested values has been reached.
   * If either the component event handler or the actualType event handler
   * do not respond with ASN1RER_PARSE, this function will not be called.
   *
   * The implementation provided here does nothing.
   *
   * @param pctxt          The OSCTXT object.
   * @param componentID    Identifies the component for which the function is
   *                       being called. The code generator will generate a
   *                       globally unique identifier for each component.
   */
   virtual void endComponent(OSCTXT* pctxt, OSSIZE componentID) 
   { OS_UNUSED_ARG(pctxt); OS_UNUSED_ARG(componentID); }

   /**
    * This callback function invoked to signal the actual type for an open type
    * component.
    *
    * The implementation provided returns ASN1RER_PARSE.
    *
    * @param pctxt          The OSCTXT object.  Provides access to the data
    *                       buffer.
    * @param actualTypeID   Identifies the actual type. The code generator will
    *                       generate a globally unique identifier for each type.
    * @param len            The length of the open type content.
    * @return               Response from the handler.
    */
   virtual ASN1RawEventResp actualType(OSCTXT* pctxt, OSSIZE actualTypeID,
                                       OSSIZE len)
   {
      OS_UNUSED_ARG(pctxt);
      OS_UNUSED_ARG(actualTypeID);
      OS_UNUSED_ARG(len);

      return ASN1RER_PARSE;
   }


   /** Add this event handler to the given context, replacing any previous event
   handler. The context does not take ownership of the handler.*/
   void addEventHandler(OSCTXT* pctxt);

   /** Add this event handler to the context belonging to the given buffer,
   replacing any previous event handler. Neither the buffer nor its context
   take ownership of the handler. */
   void addEventHandler(OSRTMessageBuffer& buffer);


   /**
    * Invoke the component event on the raw event handler.
    *
    * @param pctxt          The OSCTXT object.  Provides access to the data buffer.
    *                       The pUserData field can be used to hold user data
    *                       between events.
    * @param componentID    Identifies the component for which the function is
    *                       being called. The code generator will generate a
    *                       globally unique identifier for each component.
    * @param nestedValues   TRUE if the component may contain nested values.
    * @return               Response from the handler.
    */
   static ASN1RawEventResp invokeComponent(OSCTXT* pctxt, OSSIZE componentID,
      OSBOOL nestedValues);

   /**
    * Invoke the component-end event on the raw event handler.
    *
    * @param pctxt          The OSCTXT object.
    * @param componentID    Identifies the component for which the function is
    *                       being called. The code generator will generate a
    *                       globally unique identifier for each component.
    */
   static void invokeEndComponent(OSCTXT* pctxt, OSSIZE componentID);

   /**
    * Invoke the actual-type event on the raw event handler.
    *
    * @param pctxt          The OSCTXT object.  Provides access to the data buffer.
    *                       The pUserData field can be used to hold user data
    *                       between events.
    * @param actualTypeID   Identifies the actual type. The code generator will
    *                       generate a globally unique identifier for each type.
    * @param len            The length of the open type content.
    * @return               Response from the handler.
    */
   static ASN1RawEventResp invokeActualType(OSCTXT* pctxt, OSSIZE actualTypeID,
                                            OSSIZE len);

   /** Remove the event handler from given context. */
   static void removeEventHandler(OSCTXT* pctxt);
} ;



/**
 * @}Asn1EventHandler
 */
#endif
