/*
Package main provides a sample program for running V2X conversions.
It demonstrates the use of the V2X Golang wrapper.
*/
package main

import "encoding/hex"
import "flag"
import "fmt"
import "io/ioutil"
import "os"

import "obj-sys.com/golang/v2x-wrapper/j2735"
import "obj-sys.com/golang/v2x-wrapper/etsi"
import "obj-sys.com/golang/v2x-wrapper/common"

/* Give a usage message */
func usage() {
   fmt.Println(
`Convert between text and binary formats using the following syntax.
   v2xconv (xml2bin | json2bin | bin2xml | bin2json) [-hex] [-verbose] (MessageName) in [out]

   The first argument indicates the kind of conversion to be performed. It is
   followed by any optional flags.
   
   The -hex flag indicates that hexadecimal should be used to represent the
   binary (UPER) message.
   
   The -verbose flag indicates diagnostic information should be written to
   standard output.

   MessageName is one of: "MessageFrame" (for J2735), or (for ETSI) "CAM",
   "DENM", "IVIM", "MAPEM", "SPATEM", "SREM", "SSEM".
   
   Output is sent to standard output unless a file name is given. If the
   conversion is to binary and no output is given, -hex is implied.` )   
}

func main() {
   /* Process the command line arguments. */
   
   if len(os.Args) < 2  { usage(); return }
   
   var cmd = os.Args[1]
   var useHex bool
   var verbose bool
   
   var flagset = flag.NewFlagSet("", flag.ExitOnError)
   flagset.BoolVar(&useHex, "hex", false, "Use hexadecimal representation for binary message.")
   flagset.BoolVar(&verbose, "verbose", false, "Send diagnostics to standard output.")
   flagset.Usage = usage
   flagset.Parse(os.Args[2:])
   
   var tail = os.Args[2 + flagset.NFlag():]  // Options after flags
   
   if len(tail) < 2 || len(tail) > 3 {
      if len(tail) < 2 { fmt.Println("Too few arguments.") 
      } else {
         fmt.Println("Too many arguments.")
      }
      usage()
      return
   }
   
   var msgName = tail[0]
   var in = tail[1]
   var out string
   
   if len(tail) > 2 { out = tail[2] }
   
   /* Choose the correct converter for the given message type. */
   var converter common.Converter

   switch msgName {
      case "MessageFrame":
         converter = j2735.MessageFrame
      case "CAM":
         converter = etsi.CAM
      case "DENM":
         converter = etsi.DENM
      case "IVIM":
         converter = etsi.IVIM
      case "MAPEM":
         converter = etsi.MAPEM
      case "SPATEM":
         converter = etsi.SPATEM
      case "SREM":
         converter = etsi.SREM
      case "SSEM":
         converter = etsi.SSEM
      default:
         fmt.Printf("Unknown message type: %s\n", msgName)
   }
      
   
   /* Read input from input file. */
   inFile, err := os.Open(in)
   if err != nil { panic(err) }
   defer inFile.Close()
   
   inpData, err := ioutil.ReadAll(inFile)
   if err != nil { panic(err) }   
   
   /* Open output file. */
   var outFile *os.File
   if len(out) == 0 {
      outFile = os.Stdout
   } else {
      /* Open file for writing */  
      outFile, err = os.Create(out)
      if err != nil { panic(err) }
      defer outFile.Close()
   }
   
   /* Run the appropriate conversion function. */
   if cmd == "xml2bin" || cmd == "json2bin" {
      var outData []byte
      var err error
      
      /* If writing to std out, use hex */
      if outFile == os.Stdout { useHex = true }
      
      if cmd == "xml2bin" {
         outData, err = converter.FromXml(string(inpData), verbose)
         if err != nil { panic(err) }   
      } else {
         outData, err = converter.FromJson(string(inpData), verbose)
         if err != nil { panic(err) }
      }

      if useHex {
         /* Convert outData from binary to hex */
         dst := make([]byte, hex.EncodedLen(len(outData)))
         hex.Encode(dst, outData)
         outData = dst
      }
      
      _, err = outFile.Write(outData)
      if err != nil { panic(err) }
   } else if cmd == "bin2xml" || cmd == "bin2json" {
      if useHex {
         /* Convert input from hex */
         dst := make([]byte, hex.DecodedLen(len(inpData)))
         written, err := hex.Decode(dst, inpData)
         if err != nil {
            fmt.Println("Failed to convert hex data after ",
                        written, " bytes.")
            panic(err)
         }

         inpData = dst
      }
      
      var outData string
      var err error
      
      if cmd == "bin2xml" {
         outData, err = converter.ToXml(inpData, verbose)
         if err != nil { panic(err) }   
      } else {
         outData, err = converter.ToJson(inpData, verbose)
         if err != nil { panic(err) }   
      }
      
      _, err = outFile.WriteString(outData)
      if err != nil { panic(err) }   
   } else {
      fmt.Println("Use one of the commands \"xml2bin\", \"json2bin\", " +
      "\"bin2xml\", \"bin2json\"")
      return
   }
}

