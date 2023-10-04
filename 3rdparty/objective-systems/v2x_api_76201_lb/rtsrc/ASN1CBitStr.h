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

#ifndef _ASN1CBITSTR_H_
#define _ASN1CBITSTR_H_

#include "rtsrc/asn1CppTypes.h"
/**
 * @file rtsrc/ASN1CBitStr.h
 * Bit string control class definitions.
 */
/**
 * @addtogroup asn1ctrl
 * @{
 */
//////////////////////////////////////////////////////////////////////
//
// ASN1CBitStr
//
// Bit string implementation. This class provides all functionalty
// necessary for bit strings.
//
#ifndef _NO_UTILS_CLASSES

/**
 * The ASN1CBitStrSizeHolder is a class used to hold sizes for the ASN1CBitStr
 * control class.  This base class is abstract and is implemented by the
 * 8-bit, 16-bit, and 32-bit varieties.
 */
class ASN1CBitStrSizeHolder {
 public:
   virtual ASN1CBitStrSizeHolder* clone () = 0;
   virtual OSSIZE getValue () const = 0;

   /**
    * Set the size to the given value.
    * Implementations of this method will return an error if the given
    * value is outside of the range of the field being used to hold the
    * size value.
    */
   virtual int setValue (OSSIZE value) = 0;

   virtual ~ASN1CBitStrSizeHolder() {}
} ;

/**
 * This is the 8-bit implementation of the ASN1CBitStrSizeHolder class.
 */
class ASN1CBitStrSizeHolder8 : public ASN1CBitStrSizeHolder {
 protected:
   OSUINT8& mSize;

 public:
   ASN1CBitStrSizeHolder8 (OSUINT8& value) : mSize(value) {}
   virtual ASN1CBitStrSizeHolder* clone () {
      return new ASN1CBitStrSizeHolder8 (mSize);
   }
   virtual OSSIZE getValue () const { return mSize; }
   virtual int setValue (OSSIZE value);

   virtual ~ASN1CBitStrSizeHolder8() {}

 private:
   ASN1CBitStrSizeHolder8& operator= (const ASN1CBitStrSizeHolder8&) {
      return *this;
   }
} ;

/**
 * This is the 16-bit implementation of the ASN1CBitStrSizeHolder class.
 */
class ASN1CBitStrSizeHolder16 : public ASN1CBitStrSizeHolder {
 protected:
   OSUINT16& mSize;

 public:
   ASN1CBitStrSizeHolder16 (OSUINT16& value) : mSize(value) {}
   virtual ASN1CBitStrSizeHolder* clone () {
      return new ASN1CBitStrSizeHolder16 (mSize);
   }
   virtual OSSIZE getValue () const { return mSize; }
   virtual int setValue (OSSIZE value);

   virtual ~ASN1CBitStrSizeHolder16() {}

 private:
   ASN1CBitStrSizeHolder16& operator= (const ASN1CBitStrSizeHolder16&) {
      return *this;
   }
} ;

/**
 * This is the 32-bit implementation of the ASN1CBitStrSizeHolder class.
 */
class ASN1CBitStrSizeHolder32 : public ASN1CBitStrSizeHolder {
 protected:
   OSUINT32& mSize;

 public:
   ASN1CBitStrSizeHolder32 (OSUINT32& value) : mSize(value) {}
   virtual ASN1CBitStrSizeHolder* clone () {
      return new ASN1CBitStrSizeHolder32 (mSize);
   }
   virtual OSSIZE getValue () const { return mSize; }
   virtual int setValue (OSSIZE value);

   virtual ~ASN1CBitStrSizeHolder32() {}

 private:
   ASN1CBitStrSizeHolder32& operator= (const ASN1CBitStrSizeHolder32&) {
      return *this;
   }
} ;

/**
 * This is the OSSIZE implementation of the ASN1CBitStrSizeHolder class.
 */
class ASN1CBitStrSizeHolder64 : public ASN1CBitStrSizeHolder {
 protected:
   OSSIZE& mSize;

 public:
   ASN1CBitStrSizeHolder64 (OSSIZE& value) : mSize(value) {}
   virtual ASN1CBitStrSizeHolder* clone () {
      return new ASN1CBitStrSizeHolder64 (mSize);
   }
   virtual OSSIZE getValue () const { return mSize; }
   virtual int setValue (OSSIZE value);

   virtual ~ASN1CBitStrSizeHolder64() {}

 private:
   ASN1CBitStrSizeHolder64& operator= (const ASN1CBitStrSizeHolder64&) {
      return *this;
   }
} ;


/**
 * ASN.1 bit string control class.
 * The ASN1CBitStr class is derived from the ASN1CType base class. It is used
 * as the base class for generated control classes for the ASN.1 BIT STRING
 * type. This class provides utility methods for operating on the bit string
 * referenced by the generated class. This class can also be used inline to
 * operate on bits within generated BIT STRING elements in a SEQUENCE, SET, or
 * CHOICE construct.
 */
class EXTRTCLASS ASN1CBitStr : public ASN1CType {
 private:
   OSSIZE      _numbits; /* used when constructor does not provide
                            a value by reference to give us something to
                            refer to */
   OSOCTET*    _units;   // placeholder

 protected:
   OSOCTET**   mpUnits;                /* pointer to pointer to data*/
   OSOCTET**   mppExtData;             // extended bit string data
   OSSIZE      mMaxNumBits;
   ASN1CBitStrSizeHolder* mpNumBits;
   OSSIZE      mUnitsUsed;             /* number of bytes used in *mpUnits */
   OSSIZE      mUnitsAllocated;
   OSBOOL      mDynAlloc;              /* true if *mpUnits is owned by me */

 private:
   OSOCTET* allocateMemory (OSSIZE sz);
   OSOCTET* reallocateMemory
      (OSOCTET* old, OSSIZE oldBufSz, OSSIZE newBufSz);
   void freeMemory (OSOCTET* mem);

   /*
    * Set the field mUnitsUsed with the logical size in units of the bit
    * set.  WARNING:This function assumes that the number of units actually
    * in use is less than or equal to the current value of mUnitsUsed!
    */
   void recalculateUnitsUsed();

   /*
    * Ensures that the bit string can hold enough units.
    * param	unitsRequired the minimum acceptable number of units.
    */
   int checkCapacity (OSSIZE unitsRequired);

   /*
    * Returns the unit of this bitset at index j as if this bit string had an
    * infinite amount of storage.
    */
   OSOCTET getBits (OSSIZE j);

   void privateInit (OSSIZE nbits);
   void privateInit (OSOCTET* bitStr, OSSIZE maxNumbits_, OSOCTET** ppExtData);
   void privateInit (ASN1TDynBitStr& bitStr);
   void privateInit (ASN1TDynBitStr64& bitStr);

 protected:
   /*
   * Creates an empty bit string. The string should be additionaly initialized
   * by call to 'init' method.
   */
   EXTRTMETHOD ASN1CBitStr (OSRTMessageBufferIF& msgBuf);

   /*
   * Default protected ctor. mpContext should be set and the string should be
   * additionaly initialized by call to 'init' method.
   */
   EXTRTMETHOD ASN1CBitStr();

   /*
    * This constructor creates an empty bit string.
    *
    * @param ctxt - Reference to reference-counted context object.
    */
   EXTRTMETHOD ASN1CBitStr (OSRTContext& ctxt);

#if SIZE_MAX > OSUINT32_MAX        //if size_t > 32 bits
   /*
    * This constructor initializes the internal bit string to the
    * given value.
    *
    * @param pBits - Pointer to binary bit string data.
    * @param numbits - Reference to counter to hold number of bits.
    * @param maxNumbits - Maximum size (in bits) of this bit string.
    */
   EXTRTMETHOD ASN1CBitStr
      (OSOCTET* pBits, OSSIZE& numbits, OSSIZE maxNumbits,
       OSOCTET** ppExtData = 0);
#endif

   /*
    * This constructor initializes the internal bit string to the
    * given value.
    *
    * @param pBits - Pointer to binary bit string data.
    * @param numbits - Reference to counter to hold number of bits.
    * @param maxNumbits - Maximum size (in bits) of this bit string.
    */
   EXTRTMETHOD ASN1CBitStr
      (OSOCTET* pBits, OSUINT32& numbits, OSSIZE maxNumbits,
       OSOCTET** ppExtData = 0);

   EXTRTMETHOD ASN1CBitStr
      (OSOCTET* pBits, OSUINT8& numbits, OSSIZE maxNumbits,
       OSOCTET** ppExtData = 0);

   EXTRTMETHOD ASN1CBitStr
      (OSOCTET* pBits, OSUINT16& numbits, OSSIZE maxNumbits,
       OSOCTET** ppExtData = 0);

   // Fixed-size bit string
   EXTRTMETHOD ASN1CBitStr (OSOCTET* pBits, OSSIZE maxNumbits);

   /*
    * This constructor initializes the internal bit string to the
    * given value.
    *
    * @param bitstr - Reference to a bit string variable.
    */
   EXTRTMETHOD ASN1CBitStr (ASN1TDynBitStr& bitStr);

   /*
    * Creates bits string from ASN1TDynBitStr64. Ctor does not copy bytes,
    * just assign array (data member of ASN1TDynBitStr64) to units.
    * This string will be extendable.
    */
   EXTRTMETHOD ASN1CBitStr (ASN1TDynBitStr64& bitStr);

   void initBase (OSOCTET* pBits, OSSIZE numbits, OSSIZE maxNumbits);

   EXTRTMETHOD void init
      (OSOCTET* pBits, OSUINT32& numbits, OSSIZE maxNumbits);

   EXTRTMETHOD void init
      (OSOCTET* pBits, OSUINT8& numbits, OSSIZE maxNumbits);

   EXTRTMETHOD void init
      (OSOCTET* pBits, OSUINT16& numbits, OSSIZE maxNumbits);

   EXTRTMETHOD void init (ASN1TDynBitStr& bitStr);

 public:
   /**
    * This constructor creates an empty bit string. If the \c nbits argument is
    * zero, the bit string is set to be dynamic; otherwise, the capacity is set
    * to \c nbits.
    *
    * @param msgbuf       - ASN.1 message buffer or stream object.
    * @param nbits        - Number of bits this bit string can contain (zero if
    *                       unbounded.
    */
   EXTRTMETHOD ASN1CBitStr (OSRTMessageBufferIF& msgbuf, OSSIZE nbits);

#if SIZE_MAX > OSUINT32_MAX        //if size_t > 32 bits
   /**
    * This constructor creates a bit string from an array of bits. The
    * constructor does not copy the bit string data, it just references the
    * given data variables. All operations on the bit string cause the
    * referenced items to be updated directly.
    *
    * @param msgbuf       - ASN.1 message buffer or stream object.
    * @param bitStr       - Pointer to static byte array
    * @param numbits      - Reference to length of bit string (in bits)
    * @param maxNumbits_  - sets maximum length in bits
    */
   EXTRTMETHOD ASN1CBitStr
      (OSRTMessageBufferIF& msgbuf, OSOCTET* bitStr,
       OSSIZE& numbits, OSSIZE maxNumbits_, OSOCTET** ppExtData = 0);
#endif

   /**
    * This constructor creates a bit string from an array of bits. The
    * constructor does not copy the bit string data, it just references the
    * given data variables. All operations on the bit string cause the
    * referenced items to be updated directly.
    *
    * @param msgbuf       - ASN.1 message buffer or stream object.
    * @param bitStr       - Pointer to static byte array
    * @param numbits      - Reference to length of bit string (in bits)
    * @param maxNumbits_  - sets maximum length in bits
    */
   EXTRTMETHOD ASN1CBitStr
      (OSRTMessageBufferIF& msgbuf, OSOCTET* bitStr,
       OSUINT32& numbits, OSSIZE maxNumbits_, OSOCTET** ppExtData = 0);

   EXTRTMETHOD ASN1CBitStr
      (OSRTMessageBufferIF& msgbuf, OSOCTET* bitStr,
       OSUINT8& numbits, OSSIZE maxNumbits_, OSOCTET** ppExtData = 0);

   EXTRTMETHOD ASN1CBitStr
      (OSRTMessageBufferIF& msgbuf, OSOCTET* bitStr,
       OSUINT16& numbits, OSSIZE maxNumbits_, OSOCTET** ppExtData = 0);

   EXTRTMETHOD ASN1CBitStr
      (OSRTMessageBufferIF& msgbuf, OSOCTET* bitStr, OSSIZE maxNumbits_);

   /*
    * Creates bits string from ASN1TDynBitStr. Ctor does not copy bytes,
    * just assign array (data member of ASN1TDynBitStr) to units.
    * This string will be extendable.
    */
   EXTRTMETHOD ASN1CBitStr
      (OSRTMessageBufferIF& msgBuf, ASN1TDynBitStr& bitStr);

   /*
    * Creates bits string from ASN1TDynBitStr64. Ctor does not copy bytes,
    * just assign array (data member of ASN1TDynBitStr64) to units.
    * This string will be extendable.
    */
   EXTRTMETHOD ASN1CBitStr
      (OSRTMessageBufferIF& msgBuf, ASN1TDynBitStr64& bitStr);

   /*
    * Creates empty bit string. If nbits == 0 then bit string is dynamic;
    * else capacity will be fixed to nbits.
    */
   EXTRTMETHOD ASN1CBitStr (OSRTContext& ctxt, OSSIZE nbits);

#if SIZE_MAX > OSUINT32_MAX        //if size_t > 32 bits
   /*
    * Creates bits string from array of bits. Ctor does not copy bytes,
    * just assign passed array to units.
    * Param bitStr - pointer to static byte array
    * Param numbits - reference to length of bit string (in bits);
    * Param maxNumbits_  - sets maximum length in bits
    */
   EXTRTMETHOD ASN1CBitStr
   (OSRTContext& ctxt, OSOCTET* bitStr,
      OSSIZE& octsNumbits, OSSIZE maxNumbits_, OSOCTET** ppExtData = 0);
#endif

   EXTRTMETHOD ASN1CBitStr
      (OSRTContext& ctxt, OSOCTET* bitStr,
       OSUINT32& octsNumbits, OSSIZE maxNumbits_, OSOCTET** ppExtData = 0);

   EXTRTMETHOD ASN1CBitStr
      (OSRTContext& ctxt, OSOCTET* bitStr,
       OSUINT8& octsNumbits, OSSIZE maxNumbits_, OSOCTET** ppExtData = 0);

   EXTRTMETHOD ASN1CBitStr
      (OSRTContext& ctxt, OSOCTET* bitStr,
       OSUINT16& octsNumbits, OSSIZE maxNumbits_, OSOCTET** ppExtData = 0);

   EXTRTMETHOD ASN1CBitStr
      (OSRTContext& ctxt, OSOCTET* bitStr, OSSIZE maxNumbits_);

   /*
   * Creates bits string from ASN1TDynBitStr. Ctor does not copy bytes,
   * just assign array (data member of ASN1TDynBitStr) to units.
   * This string will be extendable.
   */
   EXTRTMETHOD ASN1CBitStr (OSRTContext& ctxt, ASN1TDynBitStr& bitStr);

   /*
   * Creates bits string from ASN1TDynBitStr64. Ctor does not copy bytes,
   * just assign array (data member of ASN1TDynBitStr64) to units.
   * This string will be extendable.
   */
   EXTRTMETHOD ASN1CBitStr(OSRTContext& ctxt, ASN1TDynBitStr64& bitStr);

   /*
   * Copy constructor.
   */
   EXTRTMETHOD ASN1CBitStr (const ASN1CBitStr& bitStr);

   /*
   * Copy constructor, but allows to specify 'extendable' parameter
   */
   EXTRTMETHOD ASN1CBitStr (const ASN1CBitStr& bitStr, OSBOOL extendable);


   EXTRTMETHOD ~ASN1CBitStr();

  /**
   * This version of the set method sets the given bit in the target string.
   *
   * @param bitIndex     Relative index of the bit to set in the string. The
   *                       bit idex 0 refers to the MS bit (bit 8) in the first
   *                       octet. The index values then progress from the left
   *                       to right (MS to LS).
   * @return             Completion status of operation:
   *                       - 0 (0) = success,
   *                       - negative return value is error.
   */
   /*
   * Sets the bit at the specified index to 1.
   *
   * Returns: 0 - if succeed, or
   *          RTERR_OUTOFBND - if 'bitIndex' is out of bounds, or
   *          other error codes (see asn1type.h).
   */
   EXTRTMETHOD int set (OSSIZE bitIndex);

  /**
   * This version of teh set method sets the bits from the specified fromIndex
   * (inclusive) to the specified toIndex (exclusive) to one.
   *
   * @param fromIndex    Relative start index (inclusive) of bits in the
   *                       string. The bit index 0 refers to the MS bit (bit 8)
   *                       in the first octet. The index values then progress
   *                       from the left to right (MS to LS).
   * @param toIndex      Relative end index (exclusive) of bits in the string.
   *                       The bit index 0 refers to the MS bit (bit 8) in the
   *                       first octet. The index values then progress from the
   *                       left to right (MS to LS).
   * @return             Completion status of operation:
   *                       - 0 (0) = success,
   *                       - negative return value is error.
   */
   /*
   * Sets the bits from the specified fromIndex(inclusive) to the
   * specified toIndex(exclusive) to 1.
   *
   * Returns: 0 - if succeed, or
   *          RTERR_OUTOFBND - if one of indexes is out of bounds, or
   *          RTERR_RANGERR - if fromIndex > toIndex, or
   *          other error codes (see asn1type.h).
   */
   EXTRTMETHOD int set (OSSIZE fromIndex, OSSIZE toIndex);

   /**
    * Changes the bit at the specified index to the specified value.
    *
    * @param bitIndex     Relative index of bit to set in string. Bit index 0
    *                       refers to the MS bit (bit 8) in the first octet.
    *                       The index values then progress from left to right
    *                       (MS to LS bits).
    * @param value        Boolean value to which the bit is to be set.
    * @return             Completion status of operation: 0 - if succeed
    *                       - 0 (0) = success
    *                       - negative return value is error.
   */
   /*Returns (details): RTERR_OUTOFBND - if 'bitIndex' is out of bounds, or
   *          other error codes (see asn1type.h).
   */
   inline int change (OSSIZE bitIndex, OSBOOL value) {
      return (value) ? set (bitIndex) : clear (bitIndex);
   }

  /**
   * This version of the clear method sets the given bit in the target string
   * to zero.
   *
   * @param bitIndex     Relative index of bit in string. Bit index 0 refers to
   *                       the MS bit (bit 8) in the first octet. The index
   *                       values then progress from left to right (MS to LS
   *                       bits).
   * @return             Completion status of operation:
   *                       - 0 (0) = success,
   *                       - negative return value is error.
   */
   /*
   * Sets the bit specified by the index to 0.
   *
   * Returns: 0 - if succeed, or
   *          RTERR_OUTOFBND - if 'bitIndex' is out of bounds, or
   *          other error codes (see asn1type.h).
   */
   EXTRTMETHOD int clear (OSSIZE bitIndex);

  /**
   * This version of the clear method sets the bits from the specified
   * fromIndex (inclusive) to the specified toIndex (exclusive) to zero.
   *
   * @param fromIndex    Relative start index (inclusive) of bits in string.
   *                       Bit index 0 refers to the MS bit (bit 8) in the
   *                       first octet. The index values then progress from
   *                       left to right (MS to LS bits).
   * @param toIndex      Relative end index (exclusive) of bits in string. Bit
   *                       index 0 refers to the MS bit (bit 8) in the first
   *                       octet. The index values then progress from left to
   *                       right (MS to LS bits).
   * @return             Completion status of operation:
   *                       - 0 (0) = success,
   *                       - negative return value is error.
   */
   /*
   * Sets the bits from the specified fromIndex(inclusive) to the
   * specified toIndex(exclusive) to 0.
   *
   * Returns: 0 - if succeed, or
   *          RTERR_OUTOFBND - if one of indexes is out of bounds, or
   *          RTERR_RANGERR - if fromIndex > toIndex, or
   *          other error codes (see asn1type.h).
   */
   EXTRTMETHOD int clear (OSSIZE fromIndex, OSSIZE toIndex);

  /**
   * This version of the clear method sets all bits in the bit string to zero.
   *
   * @param             - none
   * @return             Completion status of operation:
   *                       - 0 (0) = success,
   *                       - negative return value is error.
   */
   /*
   * Sets all of the bits in this bit string to 0.
   */
   EXTRTMETHOD void clear();

  /**
   * This version of the invert method inverts the given bit in the target
   * string.
   *
   * If the bit in the bit string is a zero, it will be set to 1; if the bit is
   * a one, it will be set to 0.
   *
   * @param bitIndex     Relative index of bit in string. Bit index 0 refers to
   *                       the MS bit (bit 8) in the first octet. The index
   *                       values then progress from left to right (MS to LS
   *                       bits).
   * @return             Completion status of operation:
   *                       - 0 (0) = success,
   *                       - negative return value is error.
   */
   /*
   * Sets the bit at the specified index to to the complement of its
   * current value.
   *
   * Returns: 0 - if succeed, or
   *          RTERR_OUTOFBND - if 'bitIndex' is out of bounds, or
   *          other error codes (see asn1type.h).
   */
   EXTRTMETHOD int invert (OSSIZE bitIndex);

   /**
    * This version inverts the bits from the specified fromIndex (inclusive) to
    * the specified toIndex (exclusive).
    *
    * If the bit in the bit string is a zero, it will be set to 1; if the bit
    * is a one, it will be set to 0.
    *
    * @param fromIndex    Relative start index (inclusive) of bits in string.
    *                       Bit index 0 refers to the MS bit (bit 8) in the
    *                       first octet. The index values then progress from
    *                       left to right (MS to LS bits).
    * @param toIndex      Relative end index (exclusive) of bits in string. Bit
    *                       index 0 refers to the MS bit (bit 8) in the first
    *                       octet. The index values then progress from left to
    *                       right (MS to LS bits).
    * @return             Completion status of operation:
    *                       - 0 (0) = success,
    *                       - negative return value is error.
   */
   /*
   * Sets each bit from the specified fromIndex(inclusive) to the
   * specified toIndex(exclusive) to the complement of its current
   * value.
   *
   * Returns: 0 - if succeed, or
   *          RTERR_OUTOFBND - if one of indexes is out of bounds, or
   *          RTERR_RANGERR - if fromIndex > toIndex, or
   *          other error codes (see asn1type.h).
   */
   EXTRTMETHOD int invert(OSSIZE fromIndex, OSSIZE toIndex);

  /**
   * This method returns the value of the bit with the specified index.
   *
   * @param bitIndex     Relative index of bit in string. Bit index 0 refers to
   *                       the MS bit (bit 8) in the first octet. The index
   *                       values then progress from left to right (MS to LS
   *                       bits).
   * @return             Completion status of operation:
   *                       - 0 (0) = success,
   *                       - negative return value is error.
   */
   /*
   * Returns the value of the bit with the specified index.
   */
   EXTRTMETHOD OSBOOL get(OSSIZE bitIndex);

  /**
   * This method is the same as ASN1CBitStr::get.
   *
   * @see get           (OSSIZE bitIndex)
   */
   /*
   * Returns TRUE if the value of the bit with the specified index is set to 1.
   */
   inline OSBOOL isSet(OSSIZE bitIndex) { return get(bitIndex); }

  /**
   * This method returns TRUE if this bit string contains no bits that are set
   * to 1.
   *
   * @param             - none
   * @return             TRUE, if the bit string contains no bits that are set
   *                       to 1.
   */
   /*
   * Returns true if this bit string contains no bits that are set
   * to 1.
   */
   inline OSBOOL isEmpty() { return (mUnitsUsed == 0); }

  /**
   * This method returns the number of bytes of space actually in use by this
   * bit string to represent bit values.
   *
   * @param             - none
   * @return             Number of bytes of space actually in use by this bit
   *                       string to represent bit values.
   */
   /*
   * Returns the number of bytes of space actually in use by this
   * bit string to represent bit values.
   */
   EXTRTMETHOD OSSIZE size() const;

  /**
   * This method calculates the "logical size" of the bit string.
   *
   * The "logical size" is calculated by noting the index of the highest set
   * bit in the bit string, plus one. Zero will be returned if the bit string
   * contains no set bits. The highest bit in the bit string is the least
   * significant bit in the last octet set to 1.
   *
   * @param             - none
   * @return             Returns the "logical size" of this bit string.
   */
   EXTRTMETHOD OSSIZE length() const;

  /**
   * This method calculates the cardinality of the target bit string.
   *
   * Cardinality of the bit string is the number of bits set to 1.
   *
   * @param             - none
   * @return             The number of bytes of space actually in use by this
   *                       bit string to represent the bit values.
   */
   /*
   * Returns the number of bits set to 1 in this
   * bit string.
   */
   EXTRTMETHOD OSSIZE cardinality() const;

  /**
   * This method copies the bit string to the given buffer.
   *
   * @param pBuf         Pointer to the destination buffer where bytes will be
   *                       copied.
   * @param bufSz        Size of the destination buffer. If the size of
   *                       the buffer is not large enough to receive the
   *                       entire bit string, a negative status value
   *                       (RTERR_BUFOVFLOW) will be returned.
   * @return             Completion status of operation:
   *                       - 0 (0) = success,
   *                       - negative return value is error.
   */
   /*
   * Copies bit string to buffer (pBuf).
   */
   EXTRTMETHOD int getBytes (OSOCTET* pBuf, OSSIZE bufSz);

  /**
   * This version of the get method copies the bit string composed of bits from
   * this bit string from the specified fromIndex (inclusive) to the specified
   * toIndex (exclusive) into the given buffer.
   *
   * @param fromIndex    Relative start index (inclusive) of bits in string.
   *                       Bit index 0 refers to the MS bit (bit 8) in the
   *                       first octet. The index values then progress from
   *                       left to right (MS to LS bits).
   * @param toIndex      Relative end index (exclusive) of bits in string. Bit
   *                       index 0 refers to the MS bit (bit 8) in the first
   *                       octet. The index values then progress from left to
   *                       right (MS to LS bits).
   * @param pBuf         Pointer to destination buffer where bytes will be
   *                       copied.
   * @param bufSz        Size of the destination buffer. If the size of
   *                       the buffer is not large enough to receive the
   *                       entire bit string, a negative status value
   *                       (RTERR_BUFOVFLOW) will be returned.
   * @return             Completion status of operation:
   *                       - 0 (0) = success,
   *                       - RTERR_OUTOFBND index value is out of bounds
   *                       - RTERR_RANGERR fromIndex > toIndex
   *                       - other error codes (see asn1type.h).
   */
   EXTRTMETHOD int get
      (OSSIZE fromIndex, OSSIZE toIndex, OSOCTET* pBuf, OSSIZE bufSz);

  /**
   * Performs a logical AND of this target bit set with the
   * argument bit set.
   *
   * Returns: 0 - if succeed, or
   *          ASN_E_INVLEN - if 'octsNumbits' is negative, or
   *          RTERR_INVPARAM - if pOctstr is the same bit string as
   *          this or null, or
   *          other error codes (see asn1type.h).
   *
   * @param pOctstr      A pointer to octets of another bit string for
   *                       performing logical operation.
   * @param octsNumbits  A number of bits in arguent bit string.
   * @return             Completion status of operation:
   *                       - 0 (0) = success,
   *                       - negative return value is error.
   */
   EXTRTMETHOD int doAnd (const OSOCTET* pOctstr, OSSIZE octsNumbits);

  /**
   * This method performs a logical AND of the target bit string with the
   * argument bit string.
   *
   * @param bitStr       A reference t another bit string represented by
   *                       ASN1TDynBitStr type for performing logical
   *                       operation.
   * @return             Completion status of operation:
   *                       - 0 (0) = success,
   *                       - negative return value is error.
   */
   inline int doAnd (const ASN1TDynBitStr& bitStr) {
      return doAnd(bitStr.data, bitStr.numbits);
   }

  /**
   * This method performs a logical AND of the target bit string with the
   * argument bit string.
   *
   * @param bitStr       A reference to another bit string represented by
   *                       ASN1CBitStr type for performing logical operation.
   * @return             Completion status of operation:
   *                       - 0 (0) = success,
   *                       - negative return value is error.
   */
   inline int doAnd(const ASN1CBitStr& bitStr) {
      return doAnd(*bitStr.mpUnits, bitStr.length());
   }


  /**
   * Performs a logical OR of this target bit set with the
   * argument bit set.
   *
   * Returns: 0 - if succeed, or
   *          ASN_E_INVLEN - if 'octsNumbits' is negative, or
   *          RTERR_INVPARAM - if pOctstr is the same bit string as
   *          this or null, or other error codes (see asn1type.h).
   *
   * @param pOctstr      A pointer to octets of another bit string for
   *                       performing logical operation.
   * @param octsNumbits  A number of bits in arguent bit string.
   * @return             Completion status of operation:
   *                       - 0 (0) = success,
   *                       - negative return value is error.
   */
   EXTRTMETHOD int doOr(const OSOCTET* pOctstr, OSSIZE octsNumbits);

  /**
   * This method performs a logical OR of the target bit string with the
   * argument bit string.
   *
   * @param bitStr       A reference t another bit string represented by
   *                       ASN1TDynBitStr type for performing logical
   *                       operation.
   * @return             Completion status of operation:
   *                       - 0 (0) = success,
   *                       - negative return value is error.
   */
   inline int doOr(const ASN1TDynBitStr& bitStr) {
      return doOr(bitStr.data, bitStr.numbits);
   }

  /**
   * This method performs a logical OR of the target bit string with the
   * argument bit string.
   *
   * @param bitStr       A reference to another bit string represented by
   *                       ASN1CBitStr type for performing logical operation.
   * @return             Completion status of operation:
   *                       - 0 (0) = success,
   *                       - negative return value is error.
   */
   inline int doOr(const ASN1CBitStr& bitStr) {
      return doOr(*bitStr.mpUnits, bitStr.length());
   }

   /**
    * Performs a logical XOR of this target bit set with the
    * argument bit set.
    *
    * Returns: 0 - if succeed, or
    *          ASN_E_INVLEN - if 'octsNumbits' is negative, or
    *          RTERR_INVPARAM - if pOctstr is null, or
    *          other error codes (see asn1type.h).
    *
    * @param pOctstr      A pointer to octets of another bit string for
    *                       performing logical operation.
    * @param octsNumbits  A number of bits in arguent bit string.
    * @return             Completion status of operation:
    *                       - 0 (0) = success,
    *                       - negative return value is error.
   */
   EXTRTMETHOD int doXor(const OSOCTET* pOctstr, OSSIZE octsNumbits);

  /**
   * This method performs a logical XOR of the target bit string with the
   * argument bit string.
   *
   * @param bitStr       A reference t another bit string represented by
   *                       ASN1TDynBitStr type for performing logical
   *                       operation.
   * @return             Completion status of operation:
   *                       - 0 (0) = success,
   *                       - negative return value is error.
   */
   inline int doXor(const ASN1TDynBitStr& bitStr) {
      return doXor(bitStr.data, bitStr.numbits);
   }

  /**
   * This method performs a logical OR of the target bit string with the
   * argument bit string.
   *
   * @param bitStr       A reference to another bit string represented by
   *                       ASN1CBitStr type for performing logical operation.
   * @return             Completion status of operation:
   *                       - 0 (0) = success,
   *                       - negative return value is error.
   */
   inline int doXor(const ASN1CBitStr& bitStr) {
      return doXor(*bitStr.mpUnits, bitStr.length());
   }

  /**
   * This method performs a logical ANDNOT of the target bit string with the
   * argument bit string.
   *
   * Logical ANDNOT clars all of the bits in this bit string whose
   * corresponding bit is set in the specified bit string.
   *
   * @param pOctstr      A pointer to octets of another bit string for
   *                       performing logical operation.
   * @param octsNumbits  A number of bits in arguent bit string.
   * @return             Completion status of operation:
   *                       - 0 (0) = success,
   *                       - negative return value is error.
   */
   /*
   * Clears all of the bits in this bit string whose corresponding
   * bit is set in the specified bit string.
   *
   * Returns: 0 - if succeed, or
   *          ASN_E_INVLEN - if 'octsNumbits' is negative, or
   *          RTERR_INVPARAM - if pOctstr is null, or
   *          other error codes (see asn1type.h).
   */
   EXTRTMETHOD int doAndNot(const OSOCTET* pOctstr, OSSIZE octsNumbits);

  /**
   * This method performs a logical ANDNOT of the target bit string with the
   * argument bit string.
   *
   * Logical ANDNOT clears all of the bits in this bit string whose
   * corresponding bit is set in the specified bit string.
   *
   * @param bitStr       A reference t another bit string represented by
   *                       ASN1TDynBitStr type for performing logical
   *                       operation.
   * @return             Completion status of operation:
   *                       - 0 (0) = success,
   *                       - negative return value is error.
   */
   inline int doAndNot(const ASN1TDynBitStr& bitStr) {
      return doAndNot(bitStr.data, bitStr.numbits);
   }

  /**
   * This method performs a logical ANDNOT of the target bit string with the
   * argument bit string.
   *
   * Logical ANDNOT clears all of the bits in this bit string whose
   * corresponding bit is set in the specified bit string.
   *
   * @param bitStr       A reference to another bit string represented by
   *                       ASN1CBitStr type for performing logical operation.
   * @return             Completion status of operation:
   *                       - 0 (0) = success,
   *                       - negative return value is error.
   */
   inline int doAndNot(const ASN1CBitStr& bitStr) {
      return doAndNot(*bitStr.mpUnits, bitStr.length());
   }

  /**
   * This method shifts all bits to the left by the number of specified in the
   * shift operand.
   *
   * If the bit string can dynamically grow, then the length of the bit string
   * will be decreased by shift bits. Otherwise, bits that are shifted into the
   * bitstring are filled with zeros from the right. Most left bits are lost.
   *
   * @param shift        Number of bits to be shifted.
   * @return             Completion status of operation:
   *                       - 0 (0) = success,
   *                       - negative return value is error.
   */
   /*
   * Shifts all bits to the left by 'shift' bits.
   */
   EXTRTMETHOD int shiftLeft(OSSIZE shift);

  /**
   * This method shifts all bits to the right by the number of specified in the
   * shift operand.
   *
   * If the bit string can dynamically grow, then the length of the bit string
   * will be decreased by shift bits. Otherwise, bits that are shifted into the
   * bitstring are filled with zeros from the left. Most right bits are lost.
   *
   * @param shift        Number of bits to be shifted.
   * @return             Completion status of operation:
   *                       - 0 (0) = success,
   *                       - negative return value is error.
   */
   /*
   * Shifts all bits to the right by 'shift' bits.
   */
   EXTRTMETHOD int shiftRight(OSSIZE shift);

  /**
   * This method returns the number of unused bits in the last octet.
   *
   * @return             Number of bits in the last octet. It is equal to
   *                       length() % 8.
   */
   /*
   * Returns number of unused bits in last unit.
   */
   EXTRTMETHOD OSUINT32 unusedBitsInLastUnit();

  /**
   * This method returns a filled ANSDITDynBitStr variable.
   *
   * Memory is not allocated when calling this method; only a pointer is
   * assigned. Thus, the ASN1TDynBitStr variable is only valid while this
   * ASN1CBitStr is in scope, and could become invalid if this object is
   * modified. Upon return, retval.data will point to this bit string and
   * retval.numbits will equal length().
   *
   * Do not call this function if length() is outside the range of OSUINT32.
   *
   * @param             - none
   * @return             Filled ASN1TDynBitStr.
   */
   EXTRTMETHOD operator ASN1TDynBitStr();

  /**
   * This method returns a pointer to a newly allocated ASN1TDynBitStr object.
   * Upon return, retval->data will point to newly allocated copy of the data in
   * this bit string and retval->numbits will equal length().
   *
   * Do not call this function if length() is outside the range of OSUINT32.
   *
   * Memory for the ASN1DynBitStr variable is alloced using memory memAlloc and
   * bits are copied into it.
   *
   * @param             - none
   * @return             Pointer to a filled ASN1TDynBitStr.
   */
   EXTRTMETHOD operator ASN1TDynBitStr*();
} ;
#else
typedef class _ASN1CBitStr : public ASN1CType {
 public:
   _ASN1CBitStr (OSRTMessageBufferIF& msgBuf, OSUINT32 nbits) :
      ASN1CType (msgBuf) {}

   _ASN1CBitStr (OSRTMessageBufferIF& msgBuf, OSOCTET* bitStr,
      OSUINT32& octsNumbits, OSUINT32 maxNumbits_) :
      ASN1CType (msgBuf) {}

   _ASN1CBitStr (OSRTMessageBufferIF& msgBuf, ASN1TDynBitStr& bitStr) :
      ASN1CType (msgBuf) {}
} ASN1CBitStr;
#endif // _NO_UTILS_CLASSES
#endif // _ASN1CBITSTR_H_
/**
 * @}asn1cb
 */
