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
 * @file OSXMLEncodeStream.h
 * XML encode stream class definition.
 */
#ifndef _OSXMLENCODESTREAM_H_
#define _OSXMLENCODESTREAM_H_

#include "rtxsrc/OSRTOutputStream.h"
#include "rtxmlsrc/OSXMLMessageBuffer.h"

/**
 * The OSXMLEncodeStream class is derived from the OSXMLEncodeBase class.
 * It contains variables and methods specific to streaming encoding
 * XML messages.  It is used to manage the stream into which a message is
 * to be encoded.
 */
class EXTXMLCLASS OSXMLEncodeStream : public OSXMLEncodeBase {
 protected:
   /** A pointer to an OSRTOutputStream object. */
   OSRTOutputStream* mpStream;

   /** TRUE if the OSXMLEncodeStream object will close and free the stream
    * in the destructor. */
   OSBOOL mbOwnStream;

 public:
   /**
    * This version of the OSXMLEncodeStream constructor takes a reference
    * to the OSOutputStream object. The stream is assumed to have been
    * previously initialized.
    *
    * @param outputStream  reference to the OSOutputStream object
    */
   EXTXMLMETHOD OSXMLEncodeStream (OSRTOutputStream& outputStream);

   /**
    * This version of the OSXMLEncodeStream constructor takes a pointer
    * to the OSRTOutputStream object. The stream is assumed to have been
    * previously initialized. If ownStream is set to TRUE, then stream
    * will be closed and freed in the destructor.
    *
    * @param pOutputStream  reference to the OSOutputStream object
    * @param ownStream      set ownership for the passed stream object.
    */
   OSXMLEncodeStream (OSRTOutputStream* pOutputStream,
                      OSBOOL ownStream = TRUE);

   ~OSXMLEncodeStream ();

   /**
    * This method reinitializes the encode stream to allow a new message
    * to be encoded.  This makes it possible to reuse one stream
    * object in a loop to encode multiple messages.
    */
   virtual EXTXMLMETHOD int init ();

   /**
    * This is a virtual method that must be overridden by derived classes to
    * allow identification of the class. The base class variant is abstract.
    * This method matches an enumerated identifier defined in the base class.
    * One identifier is declared for each of the derived classes.
    *
    * @param bufferType   Enumerated identifier specifying a derived class.
    *                       This type is defined as a public access type in the
    *                       OSRTMessageBufferIF base interface. Possible values
    *                       include BEREncode, BERDecode, PEREncode, PERDecode,
    *                       XMLEncode, and XMLDecode.
    * @return             Boolean result of the match operation. True if the
    *                       \c bufferType argument is \c XMLEncode or
    *                       \c Stream.
    */
   virtual OSBOOL isA (Type bufferType) {
      return bufferType == XMLEncode || bufferType == Stream;
   }

   /**
    * This is a virtual method that must be overridden by derived classes
    * to allow access to the stored message.  The base class
    * implementation returns a null value.
    *
    * @return              A pointer to the stored message.
    */
   virtual const OSOCTET* getMsgPtr () { return 0; }

   /**
    * This method returns the output stream associated with the object.
    *
    * @return              A pointer to the output stream.
    */
   inline OSRTOutputStream* getStream () const { return mpStream; }

} ;

#endif

