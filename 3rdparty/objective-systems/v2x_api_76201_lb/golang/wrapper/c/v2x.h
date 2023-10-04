// Header for Go-V2X

#ifndef V2X_HELPER_H
#define V2X_HELPER_H

#include "rtsrc/asn1type.h"

// Function pointer type for methods doing conversion to text
typedef int (*TO_TEXT_FN) (const char* dat, size_t len, char** txt, char** errmsg, OSBOOL verbose);

// Function pointer type for methods doing conversion from text
typedef int (*FROM_TEXT_FN) (const char* str, char** dat, size_t* len, char** errmsg, OSBOOL verbose);

// Helper to call "to text" function using pointer
static inline int to_text(TO_TEXT_FN fn, const char* dat, size_t len, char** txt, char** errmsg, OSBOOL verbose)
{
   return fn(dat, len, txt, errmsg, verbose);
}

// Helper to call "from text" function using pointer
static inline int from_text(FROM_TEXT_FN fn, const char* str, char** dat, size_t* len, char** errmsg, OSBOOL verbose)
{
   return fn(str, dat, len, errmsg, verbose);
}

#endif