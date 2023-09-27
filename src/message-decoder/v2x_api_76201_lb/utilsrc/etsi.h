/**
 * Define Utility Functions for ETSI V2X messages.
 * These functions make basic conversions between binary and text accessible
 * through a C interface.
 *
 * Each of the conversion functions has a parameter that receives a newly
 * allocated array.  The memory for this array must be subsequently freed using
 * the etsi_delete_array function.  The same is true for the errmsg argument.
 */

#include "rtsrc/asn1type.h"

#ifdef __cplusplus
extern "C" {
#endif
   
/**
 * Delete memory for an array that was previously allocated by the functions
 * in this library.
 */
EXTERN void etsi_delete_array(void* memptr);


EXTERN int etsi_CAM_to_json(const char* dat, size_t len, char** txt, char** errmsg, bool verbose);

EXTERN int etsi_CAM_from_json(const char* str, char** dat, size_t* len, char** errmsg, bool verbose);

EXTERN int etsi_CAM_to_xml(const char* dat, size_t len, char** txt, char** errmsg, bool verbose);

EXTERN int etsi_CAM_from_xml(const char* str, char** dat, size_t* len, char** errmsg, bool verbose);


EXTERN int etsi_DENM_to_json(const char* dat, size_t len, char** txt, char** errmsg, bool verbose);

EXTERN int etsi_DENM_from_json(const char* str, char** dat, size_t* len, char** errmsg, bool verbose);

EXTERN int etsi_DENM_to_xml(const char* dat, size_t len, char** txt, char** errmsg, bool verbose);

EXTERN int etsi_DENM_from_xml(const char* str, char** dat, size_t* len, char** errmsg, bool verbose);


EXTERN int etsi_SPATEM_to_json(const char* dat, size_t len, char** txt, char** errmsg, bool verbose);

EXTERN int etsi_SPATEM_from_json(const char* str, char** dat, size_t* len, char** errmsg, bool verbose);

EXTERN int etsi_SPATEM_to_xml(const char* dat, size_t len, char** txt, char** errmsg, bool verbose);

EXTERN int etsi_SPATEM_from_xml(const char* str, char** dat, size_t* len, char** errmsg, bool verbose);


EXTERN int etsi_MAPEM_to_json(const char* dat, size_t len, char** txt, char** errmsg, bool verbose);

EXTERN int etsi_MAPEM_from_json(const char* str, char** dat, size_t* len, char** errmsg, bool verbose);

EXTERN int etsi_MAPEM_to_xml(const char* dat, size_t len, char** txt, char** errmsg, bool verbose);

EXTERN int etsi_MAPEM_from_xml(const char* str, char** dat, size_t* len, char** errmsg, bool verbose);


EXTERN int etsi_IVIM_to_json(const char* dat, size_t len, char** txt, char** errmsg, bool verbose);

EXTERN int etsi_IVIM_from_json(const char* str, char** dat, size_t* len, char** errmsg, bool verbose);

EXTERN int etsi_IVIM_to_xml(const char* dat, size_t len, char** txt, char** errmsg, bool verbose);

EXTERN int etsi_IVIM_from_xml(const char* str, char** dat, size_t* len, char** errmsg, bool verbose);


EXTERN int etsi_SREM_to_json(const char* dat, size_t len, char** txt, char** errmsg, bool verbose);

EXTERN int etsi_SREM_from_json(const char* str, char** dat, size_t* len, char** errmsg, bool verbose);

EXTERN int etsi_SREM_to_xml(const char* dat, size_t len, char** txt, char** errmsg, bool verbose);

EXTERN int etsi_SREM_from_xml(const char* str, char** dat, size_t* len, char** errmsg, bool verbose);


EXTERN int etsi_SSEM_to_json(const char* dat, size_t len, char** txt, char** errmsg, bool verbose);

EXTERN int etsi_SSEM_from_json(const char* str, char** dat, size_t* len, char** errmsg, bool verbose);

EXTERN int etsi_SSEM_to_xml(const char* dat, size_t len, char** txt, char** errmsg, bool verbose);

EXTERN int etsi_SSEM_from_xml(const char* str, char** dat, size_t* len, char** errmsg, bool verbose);

#ifdef __cplusplus
}
#endif
