/**
 * Define Utility Functions for J2735 Release 202007 MessageFrame.
 * These functions make basic conversions between binary and text accessible
 * through a C interface.
 *
 * Each of the conversion functions has a parameter that receives a newly
 * allocated array.  The memory for this array must be subsequently freed using
 * the j2735_delete_array function.  The same is true for the errmsg argument.
 * 
 */

#include "rtsrc/asn1type.h"

#ifdef __cplusplus
extern "C" {
#endif   
   
/**
 * Delete memory for an array that was previously allocated by the functions
 * in this library.
 */
EXTERN void j2735_delete_array(void* memptr);


EXTERN int j2735_MessageFrame_to_json(const char* dat, size_t len, char** txt, char** errmsg, bool verbose);

EXTERN int j2735_MessageFrame_from_json(const char* str, char** dat, size_t* len, char** errmsg, bool verbose);

EXTERN int j2735_MessageFrame_to_xml(const char* dat, size_t len, char** txt, char** errmsg, bool verbose);

EXTERN int j2735_MessageFrame_from_xml(const char* str, char** dat, size_t* len, char** errmsg, bool verbose);

#ifdef __cplusplus
}
#endif