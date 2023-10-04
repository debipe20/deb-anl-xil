/* 
Package j2735 provides functions for converting J2735 V2X messages between
binary (UPER) and text formats.
*/
package j2735

/*
Comments immediately before the import "C" are processed by cgo.
I don't know why, but using a C multi-line comment for the include of
c/v2x.h is important to avoid a duplicate definition error for the to_text
and from_text functions.
*/

/*
#include <stdbool.h>
#include "utilsrc/j2735_202007.h"
#include "../c/v2x.h"
*/
// #cgo CPPFLAGS: -I ../../..
// #cgo LDFLAGS: -L ../../../debug/lib -lv2xasn1_j2735_202007
import "C"
import "unsafe"
import "obj-sys.com/golang/v2x-wrapper/common"

type messageFrame struct {}

/*
MessageFrame is the Converter for J2735 MessageFrame messages.
*/
var MessageFrame common.Converter = messageFrame{}

func (messageFrame) FromJson(text string, verbose bool) (data []byte, err error) {
   var fn C.FROM_TEXT_FN = C.FROM_TEXT_FN(C.j2735_MessageFrame_from_json)
   return fromText(fn, text, verbose)
}

func (messageFrame) FromXml(text string, verbose bool) (data []byte, err error) {
   var fn C.FROM_TEXT_FN = C.FROM_TEXT_FN(C.j2735_MessageFrame_from_xml)
   return fromText(fn, text, verbose)
}

func (messageFrame) ToJson(data []byte, verbose bool) (text string, err error) {
   var fn C.TO_TEXT_FN = C.TO_TEXT_FN(C.j2735_MessageFrame_to_json)
   return toText(fn, data, verbose)
}

func (messageFrame) ToXml(data []byte, verbose bool) (text string, err error) {
   var fn C.TO_TEXT_FN = C.TO_TEXT_FN(C.j2735_MessageFrame_to_xml)
   return toText(fn, data, verbose)
}


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
      C.j2735_delete_array(unsafe.Pointer(cdata))
      return
   } else {
      errmsg := C.GoString(cerrmsg)
      C.j2735_delete_array(unsafe.Pointer(cerrmsg))
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
      C.j2735_delete_array(unsafe.Pointer(ptxt))   
   } else {
      errmsg := C.GoString(perrmsg)   
      C.j2735_delete_array(unsafe.Pointer(perrmsg))
      err = common.Error{errno, errmsg}
   }
   return
}

