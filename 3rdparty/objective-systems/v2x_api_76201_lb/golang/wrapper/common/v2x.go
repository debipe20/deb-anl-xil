package common

import "strconv"

/* Error captures error information from the underlying V2X shared library. */
type Error struct {
   Errno int
   Message string
}

func (err Error) Error() string {
   return "(" + strconv.FormatInt(int64(err.Errno), 10) + ") " + err.Message
}


/* 
Converter specifies the interface for converting between text and binary
messages.

The functions which convert from text to binary accept the text encoding
in UTF-8 and return the binary data or an error.

The functions which convert from binary to text accept the binary data
and return the text encoding in UTF-8 or an error.   

When a conversion function is passed verbose=true, diagnostic information
is printed to standard output.
*/
type Converter interface {
   FromJson(text string, verbose bool) (data []byte, err error)
   FromXml(text string, verbose bool) (data []byte, err error)
   ToJson(data []byte, verbose bool) (text string, err error)
   ToXml(data []byte, verbose bool) (text string, err error)
}
