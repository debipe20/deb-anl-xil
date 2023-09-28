/* 
Package etsi provides functions for converting ETSI V2X messages between
binary (UPER) and text formats.

The following ETSI messages are supported:
   CAM, DENM, IVIM, MAPEM, SPATEM, SREM, SSEM
   
For each message, there is a variable of a type that implements the 
common.Converter interface.
*/
package etsi

/* I created the ETSI and J2735 packages separately with the thought that if
a user program depended on only one of them, it would depend on only one of the
shared libraries.
*/


/*
#include <stdbool.h>
#include "utilsrc/etsi.h"
#include "../c/v2x.h"
*/
// #cgo CPPFLAGS: -I ../../..
// #cgo LDFLAGS: -L ../../../debug/lib -lv2xasn1_etsi
import "C"
import "unsafe"
import "obj-sys.com/golang/v2x-wrapper/common"

/* CAM et. al are Converters for the various ETSI messages. */
var ( CAM common.Converter = cAM{}
      DENM common.Converter = dENM{}
      IVIM common.Converter = iVIM{}
      MAPEM common.Converter = mAPEM{}
      SPATEM common.Converter = sPATEM{}
      SREM common.Converter = sREM{}
      SSEM common.Converter = sSEM{}
   )

type cAM struct {}
type dENM struct {}
type iVIM struct {}
type mAPEM struct {}
type sPATEM struct {}
type sREM struct {}
type sSEM struct {}

func (cAM) FromJson(text string, verbose bool) (data []byte, err error) {
   var fn C.FROM_TEXT_FN = C.FROM_TEXT_FN(C.etsi_CAM_from_json)
   return fromText(fn, text, verbose)
}

func (cAM) FromXml(text string, verbose bool) (data []byte, err error) {
   var fn C.FROM_TEXT_FN = C.FROM_TEXT_FN(C.etsi_CAM_from_xml)
   return fromText(fn, text, verbose)
}

func (cAM) ToJson(data []byte, verbose bool) (text string, err error) {
   var fn C.TO_TEXT_FN = C.TO_TEXT_FN(C.etsi_CAM_to_json)
   return toText(fn, data, verbose)
}

func (cAM) ToXml(data []byte, verbose bool) (text string, err error) {
   var fn C.TO_TEXT_FN = C.TO_TEXT_FN(C.etsi_CAM_to_xml)
   return toText(fn, data, verbose)
}

func (dENM) FromJson(text string, verbose bool) (data []byte, err error) {
   var fn C.FROM_TEXT_FN = C.FROM_TEXT_FN(C.etsi_DENM_from_json)
   return fromText(fn, text, verbose)
}

func (dENM) FromXml(text string, verbose bool) (data []byte, err error) {
   var fn C.FROM_TEXT_FN = C.FROM_TEXT_FN(C.etsi_DENM_from_xml)
   return fromText(fn, text, verbose)
}

func (dENM) ToJson(data []byte, verbose bool) (text string, err error) {
   var fn C.TO_TEXT_FN = C.TO_TEXT_FN(C.etsi_DENM_to_json)
   return toText(fn, data, verbose)
}

func (dENM) ToXml(data []byte, verbose bool) (text string, err error) {
   var fn C.TO_TEXT_FN = C.TO_TEXT_FN(C.etsi_DENM_to_xml)
   return toText(fn, data, verbose)
}

func (iVIM) FromJson(text string, verbose bool) (data []byte, err error) {
   var fn C.FROM_TEXT_FN = C.FROM_TEXT_FN(C.etsi_IVIM_from_json)
   return fromText(fn, text, verbose)
}

func (iVIM) FromXml(text string, verbose bool) (data []byte, err error) {
   var fn C.FROM_TEXT_FN = C.FROM_TEXT_FN(C.etsi_IVIM_from_xml)
   return fromText(fn, text, verbose)
}

func (iVIM) ToJson(data []byte, verbose bool) (text string, err error) {
   var fn C.TO_TEXT_FN = C.TO_TEXT_FN(C.etsi_IVIM_to_json)
   return toText(fn, data, verbose)
}

func (iVIM) ToXml(data []byte, verbose bool) (text string, err error) {
   var fn C.TO_TEXT_FN = C.TO_TEXT_FN(C.etsi_IVIM_to_xml)
   return toText(fn, data, verbose)
}

func (mAPEM) FromJson(text string, verbose bool) (data []byte, err error) {
   var fn C.FROM_TEXT_FN = C.FROM_TEXT_FN(C.etsi_MAPEM_from_json)
   return fromText(fn, text, verbose)
}

func (mAPEM) FromXml(text string, verbose bool) (data []byte, err error) {
   var fn C.FROM_TEXT_FN = C.FROM_TEXT_FN(C.etsi_MAPEM_from_xml)
   return fromText(fn, text, verbose)
}

func (mAPEM) ToJson(data []byte, verbose bool) (text string, err error) {
   var fn C.TO_TEXT_FN = C.TO_TEXT_FN(C.etsi_MAPEM_to_json)
   return toText(fn, data, verbose)
}

func (mAPEM) ToXml(data []byte, verbose bool) (text string, err error) {
   var fn C.TO_TEXT_FN = C.TO_TEXT_FN(C.etsi_MAPEM_to_xml)
   return toText(fn, data, verbose)
}

func (sPATEM) FromJson(text string, verbose bool) (data []byte, err error) {
   var fn C.FROM_TEXT_FN = C.FROM_TEXT_FN(C.etsi_SPATEM_from_json)
   return fromText(fn, text, verbose)
}

func (sPATEM) FromXml(text string, verbose bool) (data []byte, err error) {
   var fn C.FROM_TEXT_FN = C.FROM_TEXT_FN(C.etsi_SPATEM_from_xml)
   return fromText(fn, text, verbose)
}

func (sPATEM) ToJson(data []byte, verbose bool) (text string, err error) {
   var fn C.TO_TEXT_FN = C.TO_TEXT_FN(C.etsi_SPATEM_to_json)
   return toText(fn, data, verbose)
}

func (sPATEM) ToXml(data []byte, verbose bool) (text string, err error) {
   var fn C.TO_TEXT_FN = C.TO_TEXT_FN(C.etsi_SPATEM_to_xml)
   return toText(fn, data, verbose)
}

func (sREM) FromJson(text string, verbose bool) (data []byte, err error) {
   var fn C.FROM_TEXT_FN = C.FROM_TEXT_FN(C.etsi_SREM_from_json)
   return fromText(fn, text, verbose)
}

func (sREM) FromXml(text string, verbose bool) (data []byte, err error) {
   var fn C.FROM_TEXT_FN = C.FROM_TEXT_FN(C.etsi_SREM_from_xml)
   return fromText(fn, text, verbose)
}

func (sREM) ToJson(data []byte, verbose bool) (text string, err error) {
   var fn C.TO_TEXT_FN = C.TO_TEXT_FN(C.etsi_SREM_to_json)
   return toText(fn, data, verbose)
}

func (sREM) ToXml(data []byte, verbose bool) (text string, err error) {
   var fn C.TO_TEXT_FN = C.TO_TEXT_FN(C.etsi_SREM_to_xml)
   return toText(fn, data, verbose)
}

func (sSEM) FromJson(text string, verbose bool) (data []byte, err error) {
   var fn C.FROM_TEXT_FN = C.FROM_TEXT_FN(C.etsi_SSEM_from_json)
   return fromText(fn, text, verbose)
}

func (sSEM) FromXml(text string, verbose bool) (data []byte, err error) {
   var fn C.FROM_TEXT_FN = C.FROM_TEXT_FN(C.etsi_SSEM_from_xml)
   return fromText(fn, text, verbose)
}

func (sSEM) ToJson(data []byte, verbose bool) (text string, err error) {
   var fn C.TO_TEXT_FN = C.TO_TEXT_FN(C.etsi_SSEM_to_json)
   return toText(fn, data, verbose)
}

func (sSEM) ToXml(data []byte, verbose bool) (text string, err error) {
   var fn C.TO_TEXT_FN = C.TO_TEXT_FN(C.etsi_SSEM_to_xml)
   return toText(fn, data, verbose)
}

/*
The fromText and toText functions are not put into a common package because the
cgo documentation says that packages must not export C types from one package
to another.
*/


/*
fromText invokes the given function to convert from text to binary.
*/
func fromText(fn C.FROM_TEXT_FN, text string, verbose bool) (data []byte, err error) {

   ctext := C.CString(text)
   defer C.free(unsafe.Pointer(ctext))
   
   var cverbose C.uchar
   if verbose { cverbose = 1 } else { cverbose = 0 }
   
   var cdata *C.char
   var len C.size_t
   var cerrmsg *C.char
   errno := int( C.from_text(fn, ctext, &cdata, &len, &cerrmsg, cverbose))
   if errno == 0 {
      data = C.GoBytes(unsafe.Pointer(cdata), C.int(len))
      C.etsi_delete_array(unsafe.Pointer(cdata))
      return
   } else {
      errmsg := C.GoString(cerrmsg)
      C.etsi_delete_array(unsafe.Pointer(cerrmsg))
      err = &common.Error{errno, errmsg}
      return
   }
}


/*
toText invokes the given function to convert from binary to text.
*/
func toText(fn C.TO_TEXT_FN, data []byte, verbose bool) (text string, err error) {
         
   pdata := unsafe.Pointer(&data[0])
   
   var ptxt *C.char
   var perrmsg *C.char
   var cverbose C.uchar

   if verbose {
      cverbose = 1
   } else { 
      cverbose = 0
   }
   
   errno := int( C.to_text(fn, (*C.char)(pdata), C.size_t(len(data)),
                                 &ptxt, &perrmsg, cverbose))

   if (errno == 0) {
      text = C.GoString(ptxt)
      C.etsi_delete_array(unsafe.Pointer(ptxt))   
   } else {
      errmsg := C.GoString(perrmsg)   
      C.etsi_delete_array(unsafe.Pointer(perrmsg))
      err = common.Error{errno, errmsg}
   }
   return
}