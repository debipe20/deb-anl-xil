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

/**
 * @file asn1CRawEvtHndlr.h
 * C raw event handler declarations.
 */
/**
 * @addtogroup Asn1CEventHandler
 * @{
 */
#ifndef _ASN1CRAWEVTHNDLR_H_
#define _ASN1CRAWEVTHNDLR_H_

#include <stdio.h>
#include "rtsrc/asn1type.h"
#include "rtsrc/rtContext.h"

#ifdef __cplusplus
extern "C" {
#endif


/**
 * Define values that can be returned from certain events.
 * <UL>
 * <LI>ASN1RER_CONSUMED: indicates the event handler consumed the data.
 * </LI>
 * <LI>ASN1RER_PARSE: indicates the parser should proceed to parse the
 * component, sending events from nested values.
 * </LI>
 * <LI>ASN1RER_QUIET_PARSE: indicates the parser should proceed to parse the
 * component, without sending events for nested values.
 * </LI>
 * </UL>
 */
typedef enum ASN1RawEventResp 
   { ASN1RER_CONSUMED, ASN1RER_PARSE, ASN1RER_QUIET_PARSE }
   ASN1RawEventResp;
 

/**
 * This is a function pointer for a callback function which is invoked
 * from within a parser function when an element of a SEQUENCE, SET,
 * SEQUENCE OF, SET OF, or CHOICE construct is parsed.
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
typedef ASN1RawEventResp(*rtxComponent) (OSCTXT* pctxt, OSSIZE componentID,
         OSBOOL nestedValues);

/**
 * This is a function pointer for a callback function which is invoked to
 * indicate the end of a component with nested values has been reached.
 * If either the rtxComponent event handler or the rtxActualType event handler
 * do not respond with ASN1RER_PARSE, this function will not be called.
 *
 * @param pctxt          The OSCTXT object.
 * @param componentID    Identifies the component for which the function is
 *                       being called. The code generator will generate a
 *                       globally unique identifier for each component.
 */
typedef void(*rtxEndComponent) (OSCTXT* pctxt, OSSIZE componentID);

/**
 * This is a function pointer for a callback function which is invoked to
 * signal the actual type for an open type component.
 *
 * @param pctxt          The OSCTXT object.  Provides access to the data buffer.
 *                       The pUserData field can be used to hold user data
 *                       between events.
 * @param actualTypeID   Identifies the actual type. The code generator will
 *                       generate a globally unique identifier for each type.
 * @param len            The length of the open type content.
 * @return               Response from the handler.
 */
typedef ASN1RawEventResp(*rtxActualType) (OSCTXT* pctxt, OSSIZE actualTypeID,
                                          OSSIZE len);

/**
 * Structure for a raw event handler.
 */
typedef struct Asn1CRawEventHandler {
   rtxComponent component;
   rtxEndComponent endComponent; /** may be null */
   rtxActualType actualType; /** may be null */
} Asn1CRawEventHandler;

/** 
 * Add the given raw event handler to the given context, replacing any previous
 * event.  The context does not take ownership of the handler.
 */
EXTERNRT void rtAddRawEventHandler(OSCTXT* pctxt, Asn1CRawEventHandler* pHandler);

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
EXTERNRT ASN1RawEventResp rtInvokeComponent (OSCTXT* pctxt, OSSIZE componentID,
   OSBOOL nestedValues);

/**
 * Invoke the component-end event on the raw event handler.
 *
 * @param pctxt          The OSCTXT object.
 * @param componentID    Identifies the component for which the function is
 *                       being called. The code generator will generate a
 *                       globally unique identifier for each component.
 */
EXTERNRT void rtInvokeEndComponent (OSCTXT* pctxt, OSSIZE componentID);

/**
 * Invoke the actual-type event on the raw event handler.
 *
 * @param pctxt          The OSCTXT object.  Provides access to the data buffer.
 *                       The pUserData field can be used to hold user data
 *                       between events.
 * @param actualTypeID   Identifies the actual type. The code generator will
 *                       generate a globally unique identifier for each type.
 * @param len            Length of open type content.
 * @return               Response from the handler.
 */
EXTERNRT ASN1RawEventResp rtInvokeActualType (OSCTXT* pctxt, 
                                              OSSIZE actualTypeID,
                                              OSSIZE len);


/** Remove the raw event handler from given context. */
EXTERNRT void rtRemoveRawEventHandler(OSCTXT* pctxt);

#ifdef __cplusplus
}
#endif

#endif

/**
 * @}
 */
