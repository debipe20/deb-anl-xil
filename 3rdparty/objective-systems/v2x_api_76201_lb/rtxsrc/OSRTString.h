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
 * @file OSRTString.h
 * C++ string class definition.  This can be used to hold standard ASCII
 * or UTF-8 strings.  The standard C++ 'new' and 'delete' operators are
 * used to allocate/free memory for the strings.  All strings are
 * deep-copied.
 */
#ifndef _OSRTSTRING_H_
#define _OSRTSTRING_H_

/* Disable MS VC++ Level 4 warning about unreferenced inline functions */
#ifdef _MSC_VER
#pragma warning(disable: 4514)
#endif /* _MSC_VER */

#include "rtxsrc/rtxCommon.h"
#include "rtxsrc/rtxPrint.h"
#include "rtxsrc/OSRTStringIF.h"

/**
 * C++ string class definition.  This can be used to hold standard ASCII
 * or UTF-8 strings.  The standard C++ 'new' and 'delete' operators are
 * used to allocate/free memory for the strings.  All strings are
 * deep-copied.
 */
class EXTRTCLASS OSRTString : public OSRTStringIF {
 protected:
   char* mpValue;

 public:
   /**
    * The default constructor creates an empty string.
    */
   OSRTString();

   /**
    * This constructor initializes the string to contain the given
    * standard ASCII string value.
    *
    * @param strval       - Null-terminated C string value
    */
   OSRTString (const char* strval);

   /**
    * This constructor initializes the string to contain the given
    * UTF-8 string value.
    *
    * @param strval       - Null-terminated C string value
    */
   OSRTString (const OSUTF8CHAR* strval);

   /**
    * Copy constructor.
    *
    * @param str          - C++ string object to be copied.
    */
   OSRTString (const OSRTString& str);

   /**
    * The destructor frees string memory using the standard 'delete'
    * operator.
    */
   virtual ~OSRTString();

   /**
    * This method creates a copy of the given string object.
    */
   virtual OSRTStringIF* clone() { return new OSRTString (*this); }

   /**
    * This method is a synonym for getValue().
    */
   inline const char* data() const { return getValue(); }

   /**
    * This method returns the pointer to UTF-8 null terminated string
    * as a standard ASCII string.
    */
   virtual const char* getValue() const {
      return mpValue;
   }

   /**
    * This method returns the pointer to UTF-8 null terminated string
    * as a UTF-8 string.
    */
   virtual const OSUTF8CHAR* getUTF8Value() const {
      return (const OSUTF8CHAR*)mpValue;
   }

   /**
    * This method returns the index of the first occurence of the given
    * characetr within the string or -1 if the character is not found.
    */
   int indexOf (char ch) const;

   /**
    * This method returns the length of the string.
    */
   inline size_t length() const { return OSCRTLSTRLEN(mpValue); }

   /**
    * This method prints the string value to standard output.
    *
    * @param name - Name of generated string variable.
    */
   virtual void print (const char* name) {
      rtxPrintCharStr (name, mpValue);
   }

   /**
    * This method sets the string value to the given string.
    *
    * @param str - C null-terminated string.
    */
   virtual EXTRTMETHOD void setValue (const char* strval);

   /**
    * This method sets the string value to the given UTF-8 string value.
    *
    * @param str - C null-terminated UTF-8 string.
    */
   virtual EXTRTMETHOD void setValue (const OSUTF8CHAR* strval);

   /**
    * This method sets the string value to the given string value pointer.
    * This is assumed to be a mutable string allocated with the new
    * operator.  This class will assume ownership of the string memory.
    *
    * @param str - Mutable null-terminated string allocated with new.
    */
   virtual EXTRTMETHOD void setValuePtr (char* strval);

   // Integer conversion methods - return value is TRUE if conversion
   // successful or FALSE otherwise..
   /**
    * This method converts the string to a signed 32-bit integer value.
    *
    * @param value Reference to variable to receive converted integer value.
    * @return Boolean result, true if successful or false if failed.
    */
   bool toInt (OSINT32& value) const;

   /**
    * This method converts the string to a size typed (site_t) value.
    *
    * @param value Reference to variable to receive converted integer value.
    * @return Boolean result, true if successful or false if failed.
    */
   bool toSize (OSSIZE& value) const;

   /**
    * This method converts the string to an unsigned 32-bit integer value.
    *
    * @param value Reference to variable to receive converted integer value.
    * @return Boolean result, true if successful or false if failed.
    */
   bool toUInt (OSUINT32& value) const;

#if !defined(_NO_INT64_SUPPORT)
   /**
    * This method converts the string to an unsigned 64-bit integer value.
    *
    * @param value Reference to variable to receive converted integer value.
    * @return Boolean result, true if successful or false if failed.
    */
   bool toUInt64 (OSUINT64& value) const;
#endif

   /**
    * Assignment operator.
    */
   EXTRTMETHOD OSRTString& operator= (const OSRTString& original);

   inline operator const char* (void) const {
      return getValue();
   }
} ;

#endif
