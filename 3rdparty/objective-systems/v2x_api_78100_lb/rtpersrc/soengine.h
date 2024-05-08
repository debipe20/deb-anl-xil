/*
 * Copyright (c) 2022-2024 Objective Systems, Inc.
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

#ifndef SOENGINE_H
#define SOENGINE_H

#ifdef __cplusplus
extern "C" {
#endif

#if defined(_MSC_VER) && _MSC_VER == 1500
   // VS 2008.  No stdint.h to include.  We'll use _WIN64 macro.
#else
   #include <stdint.h>
#endif

#include "rtxsrc/rtxContext.h"

/*
The PSZPICK macro picks out the first or second argument, depending on the
pointer size for the build.
val32 and val64 are the values to use for 32-bit and 64-bit pointer sizes,
respectively.
This macro is for use in internal and generated code and subject to change
(for example, to cover more pointer sizes).
*/
#if defined(_MSC_VER) && _MSC_VER == 1500
   //Visual Studio 2008
   #ifdef _WIN64
      //64-bit pointers
      #define PSZPICK(val32,val64) val64
   #else
      //32-bit pointers
      #define PSZPICK(val32,val64) val32
   #endif
#elif defined(PTRDIFF_MAX)
   #if PTRDIFF_MAX == INT64_MAX
      //64-bit pointers
      #define PSZPICK(val32,val64) val64
   #elif PTRDIFF_MAX == INT32_MAX
      //32-bit pointers
      #define PSZPICK(val32,val64) val32
   #else
      #define PSZPICK(val32,val64) ? /* unsupported pointer size */
   #endif
#else
   #define PSZPICK(val32,val64) ? /* PTRDDIFF_MAX not defined */
#endif

/*
Macro DEBUGFIELD is used to add values for fields that are present in
a _DEBUG build but are not present otherwise.  It is for use by generated code
and the runtime only.
*/
#ifdef _DEBUG
#define DEBUGFIELD(a) , a
#else
#define DEBUGFIELD(a)
#endif

/*
The engine code will use both SODEBUG* and SOREL* macros.  It is expected that
at most one of them will correspond to non-empty statements.

The SODEBUG push and pop macros are for use when _DEBUG is defined and the
schema data includes element names, which will be used with those macros.

The SOREL push and pop macros are for use when _DEBUG is NOT defined and the
schema data does NOT include element names.  Then (if _COMPACT is not
defined) we'll at least have something in the element stack for use with
bit trace.

These macros are for use in the runtime only.  Having both SODEBUG* and SOREL*
macros allows us to use them in appropriate (and different) places without
having to guard them in #if blocks.

SOPUSHARRAYELEMNAME and SOPOPARRAYELEMNAME are for use regardless of whether
_DEBUG is defined or not - the same calls would be made regardless of whether
the schema data includes element names.
*/
#ifdef _SODEBUG
   /* If _SODEBUG is defined, exactly what gets pushed/popped depends on whether _DEBUG is defined or not,
      since that controls whether the schema tables contain the element names or not.
   */
   #ifdef _DEBUG
      #define SODEBUGPUSHELEMNAME(pctxt, name) RTXCTXTPUSHELEMNAME(pctxt, name)
      #define SODEBUGPOPELEMNAME(pctxt) RTXCTXTPOPELEMNAME(pctxt)
      #define SORELPUSHELEMNAME(pctxt, name)
      #define SORELPOPELEMNAME(pctxt)
   #else
      #define SODEBUGPUSHELEMNAME(pctxt, name)
      #define SODEBUGPOPELEMNAME(pctxt)
      #define SORELPUSHELEMNAME(pctxt, name) RTXCTXTPUSHELEMNAME(pctxt, name)
      #define SORELPOPELEMNAME(pctxt) RTXCTXTPOPELEMNAME(pctxt)
   #endif

   #define SOPUSHARRAYELEMNAME(pctxt, name, idx) RTXCTXTPUSHARRAYELEMNAME(pctxt, name, idx)
   #define SOPOPARRAYELEMNAME(pctxt) RTXCTXTPOPARRAYELEMNAME(pctxt)

#else
   /* If _SODEBUG is not defined, there is no pushing or popping of any names.*/
   #define SODEBUGPUSHELEMNAME(pctxt, name)
   #define SODEBUGPOPELEMNAME(pctxt)
   #define SORELPUSHELEMNAME(pctxt, name)
   #define SORELPOPELEMNAME(pctxt)
   #define SOPUSHARRAYELEMNAME(pctxt, name, idx)
   #define SOPOPARRAYELEMNAME(pctxt)
#endif

/*
SO_NEWFIELD and SO_SETBITCOUNT are for use in producing a PER bit trace.
They are for use in the runtime code only.
To produce bit trace information, both _SOTRACE and _TRACE must be defined.

In non-SO code, PU_NEWFIELD and PU_SETBITCOUNT are mainly used in generated code,
but not exclusively so.  The standard debug runtime (lib) is built with _TRACE, but
a sample program may be built without _TRACE, so that some trace statements have
effect but most don't.  Having _SOTRACE as a separate define from _TRACE allows us to
keep _TRACE defined when building the library but by having _SOTRACE not defined
we can omit most of the trace statements, making it more comparable to the non-SO case.*/
#ifdef _SOTRACE
   #define SO_NEWFIELD(pctxt,suffix) PU_NEWFIELD(pctxt,suffix)
    #define SO_SETBITCOUNT(pctxt) PU_SETBITCOUNT(pctxt)
#else
   #define SO_NEWFIELD(pctxt,suffix)
   #define SO_SETBITCOUNT(pctxt)
#endif

typedef enum {
   Type_NotSupported,
   Type_Boolean,
   Type_NullType,
   Type_EmptySequence,
   Type_EmptyExtSequence,
   Type_CompactEnumerated,
   Type_CompactExtEnumerated,
   Type_Enumerated,
   Type_Integer,
   Type_ConstrIntegerSRange,
   Type_ConstrIntegerURange,
   Type_BitString,
   Type_BitStringFixedDyn,
   Type_BitStringRangeDyn,
   Type_BitStringRangeNamedDyn,
   Type_BitStringContains,
   Type_OctetString,
   Type_OctetStringFixedDyn,
   Type_OctetStringRangeDyn,
   Type_OctetStringContains,
   Type_Sequence,
   Type_Sequence1,
   Type_Sequence2,
   Type_Sequence3,
   Type_SequenceExtNoAddn,
   Type_SequenceExt,
   Type_Choice,
   Type_Choice1,
   Type_Choice2,
   Type_Choice3,
   Type_ChoiceExt,
   Type_SeqOfFixed,
   Type_SeqOfRange,
   Type_KnownMult8,
   Type_ObjIdDyn,
   Type_OpenType
} TypeId;


typedef struct Component {
   OSUINT16 isPointerToType : 1; /* Is T* or T, where T represents component's type. */
   OSUINT16 presence : 2; /* ComponentPresence value. */
   OSUINT16 idx : 13; /* If presence == default, then an index into the ComponentWithDefault table. Otherwise, an index into the types table.*/
#ifdef _DEBUG
   const char* elemName;      /* ASN.1 name of element */
#endif
} Component;

/* Type table entry. */
typedef struct Type {
   OSUINT8 id; /* The TypeId value. */
   OSUINT8 hasDynMem : 4;        /* 1 if type owns memory, directly or indirectly; 0 otherwise */
   OSUINT8 alignment : 4;        /* 1, 2, 4, 8 */
   OSUINT16 sizeof_type; /* in bytes */

   union {
      /* tabidx is an index into another table that provides additional
      information for the type.  The different tables are arrays of
      different C types.  The following table interprets tabidx for various
      ids.
        id                            meaning
        -------------------           ------------------------------------
        Type_Choice                   ChoHeader table
        Type_ChoiceExt                ChoHeader table
        Type_Choice1                  Type table (single alt)
        Type_ChoiceN                  (N>1) Alternatives table (first alt)
        Type_Sequence                 SeqHeader table
        Type_SequenceN                (N>1) Component table (first comp)
        Type_SequenceExtNoAddn        SeqHeader table
        Type_SequenceExtn             SeqExtnHeader table
        Type_SeqOfFixed               SeqOfFixed table
        Type_SeqOfRange               SeqOfRange table
        Type_SeqOf                    Type table
        Type_ConstrIntegerSRange      ConstrIntegerRange table
        Type_ConstrIntegerURange      ConstrIntegerRange table
        Type_BitStringRange           SizeRange table
        Type_BitStringRangeNamed      SizeRange table
        Type_BitStringContains        Type table(for the contained type)
        Type_OctetStringContains      Type table(for the contained type)
        Type_KnownMult8               CharString table
        Type_Enumerated               EnumHeader table
      */
      OSUINT16   tabidx;
      /* fixedMinus1 is the fixed size - 1 for a BIT STRING or OCTET STRING.
      It is used for:
         Type_BitStringFixed
         Type_OctetStringFixed
      */
      OSUINT16 fixedMinus1;

      /* enumRangeMinus1 is the PER range for an enum, minus 1.
      Used for Type_CompactExtEnumerated and Type_CompactExtEnumerated*/
      OSUINT8 enumRangeMinus1; /* number of root values minus 1 */

      /* component is used for Type_Sequence1. */
      Component component;
   } u;

#ifdef _DEBUG
   const char* typeName;      /* ASN.1 type name, for defined types.
                              Note that (anonymous) nested types will have
                              a manufactured name.
                              Note that if types A and B are equivalent, then
                              the name for A may appear in place of the name for
                              B. */
#endif
} Type;

typedef struct SeqHeader{
   OSUINT8 sizeof_m; /* sizeof(m); 0 if no m struct */
   OSUINT8 numOptBits;  /* Number of bits in the encoding's optional bit field.*/
   OSUINT8 numRoots;    /* Number of root components.*/
   OSUINT16 componentIndex;  /* index to 1st root component in Component table. N/A if numRoots == 0. */
} SeqHeader;

typedef struct SeqExtnHeader {
   SeqHeader stdHeader; /* Non-extension information. */
   OSUINT8 numExtnAddns; /* Number of extension additions, whether single or group addition. */
   OSUINT16 addnIndex;  /* index to first extension addition, in SeqExtnAddn table */
} SeqExtnHeader;

typedef enum {
   ComponentPresence_present_,
   ComponentPresence_optional_,
   ComponentPresence_default_
} ComponentPresence;

typedef struct ComponentWithDefault {
   OSUINT16 typeIndex;  /* index to component type in Type table. */
   union {
      OSUINT64 value;      /* The default value.  This will work for
                              BOOLEAN, non-negative INTEGER, non-negative ENUM.
                           */
      struct {
         OSSIZE numbits;
         const OSOCTET* data;
      } bitstr;
   } u;
} ComponentWithDefault;

typedef struct SeqExtnAddn {
   OSUINT8 numComps; /* 0 for single extension addition; otherwise the number of components in the extension group. */
   OSUINT8 numOptBits; /* Number of optional bits for extension group */
   union {
      Component component;  /* for single addition, the component */
      OSUINT16 index;  /* for group addition, index to first component in Component table */
   } u;
} SeqExtnAddn;

typedef struct ChoiceHeader {
   OSUINT8 numRootsMinus1; /* number of root alternatives, minus 1. */
   OSUINT8 numExtn; /* number of extension alternatives, whether in a group or not */
   OSUINT16 altIndex; /* index to first alternative in Alternatives table, an array of type indices. */
} ChoiceHeader;


typedef struct Alternative {
   OSUINT16 typeIndex;
#ifdef _DEBUG
   const char* elemName;      /* ASN.1 name of element */
#endif
} Alternative;


typedef struct SizeRange {
   OSUINT8 lb;
   OSUINT16 ubMinus1; /* upper bound - 1 */
} SizeRange;

typedef struct SeqOfFixed {
   OSUINT16 compIndex;  /* index into type table for component type */
   OSUINT8 fixedMinus1; /* the lower/upper bound minus 1 */
} SeqOfFixed;

typedef struct SeqOfRange {
   OSUINT16 compIndex; /* index into type table for component type */
   OSUINT8 sizeRangeIdx; /* index into SizeRange table */
   OSUINT8 sizeof_n;     /* sizeof(n field) */
} SeqOfRange;

typedef struct ConstrIntegerRange {
   OSUINT8 numbits;
   union {
      OSUINT64 unsigned_;
      OSINT64 signed_;
   } lb; /* the type will signify signed vs. unsigned */
} ConstrIntegerRange;

typedef struct CharString {
   OSUINT8 bitsPerChar; /* # of bits per char in encoding */
   OSBOOL translate;    /* true if chars are encoded by translation w.r.t
                           the effective permitted alphabet. */
   OSBOOL sizeConstr; /* is there a size constraint? */
   OSUINT8 sizeRangeIdx; /* index into SizeRange table */
   const char** alphabet; /* pointer to alphabet, in canonical order, or null */
} CharString;

typedef struct EnumHeader {
   OSUINT16 numRoots;         /* number of roots; > 0 */
   OSUINT16 extensible : 1;   /* 1/0 for ENUMERATED extensible or not */
   OSUINT16 numExtn : 15;     /* number of extensions */
   const OSINT64* values;     /* pointer to values, with roots first and sorted,
                        followed by extensions */
} EnumHeader;

/* All of the tables for a schema. */
typedef struct SchemaData {
   const Type* types;
   const size_t numTypes;
   const SeqHeader* seqHeaders;
   const SeqExtnHeader* seqExtnHeaders;
   const Component* components;
   const ComponentWithDefault* componentsWithDefault;
   const SeqExtnAddn* seqExtnAddns;
   const ChoiceHeader* choiceHeaders;
   const Alternative* alternatives; /* Alternatives table.  Each value is the alternative's index into the type table. */
   const SeqOfFixed* seqOfFixed;
   const SeqOfRange* seqOfRange;
   const ConstrIntegerRange* constrIntegerRange;
   const SizeRange* sizeRange;
   const CharString* charString;
   const EnumHeader* enums;
} SchemaData;

/**
 * Encode the value pointed at by pTargetVar.
 *
 * @param pctxt Context to encode with.
 * @param pschema Pointer to schema data.
 * @param pType Pointer to Type to encode. It must correspond to the ASN.1
 *    type for pTargetVar.
*/
int soEncode(OSCTXT* pctxt, const SchemaData* pschema, const Type* pType, void* pTargetVar);

/**
 * Decode into the value pointed at by pTargetVar.
 *
 * @param pctxt Context to decode with.
 * @param pschema Pointer to schema data.
 * @param pType Pointer to Type to decode. It must correspond to the ASN.1
 *    type for pTargetVar.
 */
int soDecode(OSCTXT* pctxt, const SchemaData* pschema, const Type* pType, void* pTargetVar);

/**
 * Free memory owned by the value pointed at by pTargetVar, if any.
 * This does not free the memory that pTargetVar points at.
 *
 * @param pctxt Context to decode with.
 * @param pschema Pointer to schema data.
 * @param pType Pointer to Type. It must correspond to the ASN.1
 *    type for pTargetVar.
 */
int soFree(OSCTXT* pctxt, const SchemaData* pschema, const Type* pType, void* pTargetVar);

/* Return true/false according to whether the given type uses pointer-to-type in a CHOICE alternative.
*/
int soIsAltPointer(const SchemaData* pschema, const Type* pType);

/**
 * Given a sequence header with numRoots and componentIndex set, fill in
 * sizeof_m and numOptBits (both initialized to 0) by looking at the components.
 * This assumes the SEQUENCE involved is not extensible (if it were, that would
 * affect the sizeof_m computation).
 */
void soCompleteSeqHeader(const SchemaData* pschema, SeqHeader* pheader);

/**
 * This function sets the specified 1-bit bit field in a structure with the
 * given number of 1-bit bit fields.
 *
 * @param pstruct        Pointer to structure.
 * @param numfields      Number of 1-bit bit fields in the structure.
 * @param index          Index of field to be set, 0 for the first.
 * @param value          Boolean value to which field is to be set.
 * @return               If successful, returns the previous state of the bit
 *                       field.  If the field was previously set, the return
 *                       value is positive.  If the field was not previously
 *                       set, the return value is zero. Otherwise, return value
 *                       is RTERR_OUTOFBND.
 */
int soSetBitField
(OSOCTET* pstruct, OSSIZE numfields, OSSIZE bitIndex, OSBOOL value);


/**
 * This function tests the specified 1-bit bit field in a structure with the
 * given number of 1-bit bit fields.
 *
 * @param pstruct        Pointer to structure.
 * @param numfields      Number of 1-bit bit fields in the structure.
 * @param index          Index of field to be set, 0 for the first.
 * @return              True if field set or false if not set or array index is
 *                       beyond range of number of fields.
 */
OSBOOL soTestBitField (OSOCTET* pstruct, OSSIZE numfields, OSSIZE bitIndex);

/**
 * Compare value to a default value.
 *
 * @param pCompDef Provides the default value and the type.
 * @param pTargetVar Points to the value to be compared.
 * @param pmatch Content of *pmatch is set to TRUE/FALSE according to whether
 *       the value matches the default value or not.
 * @return 0 if success, or < 0 for an error.
 */
int soCompareDefault(const SchemaData* pschema,
   const ComponentWithDefault* pCompDef,
   void* pTargetVar,
   OSBOOL* pmatch);

/**
 * Set default value in target variable.
 *
 * @param pctxt Pointer to context variable.
 * @param pschema Pointer to schema data.
 * @param pCompDef Provides the default value and the type.
 * @param pTargetVar Points to the value to be compared.
 * @return 0 if success, or < 0 for an error.
 */
int soSetDefaultValue(OSCTXT* pctxt, const SchemaData* pschema,
   const ComponentWithDefault* pCompDef, void* pTargetVar);

#ifdef __cplusplus
}
#endif

#endif
