#!/usr/bin/env python
#-*- coding: utf-8 -*-
##
# A sample program for using the V2X DLL, compatible with Python 2.7.12.  See
# the usage statement or help(main) for details on how to call the main
# function of this module.
##

from __future__ import print_function

import sys
import binascii

# set up the environment
import os

##
# To import the osys module, please see the V2X ASN.1 Python User's Manual for
# instructions.  The PATH, PYTHONPATH, and LD_LIBRARY_PATH environment
# variables may need to be set for this application to run.
##
from osys import v2x

space_fmt = lambda s: ' '.join(['{}{}'.format(a,b) for a,b in \
        zip(s[::2],s[1::2])])


def usage(name):
    print("""Usage:

    {name} <-j | -x | -b> [-o <output file>] [--type=<type>] [--verbose=<bool>]
        <input file>

    Where:

        -j      Converts the <input file> to JSON, assuming it is binary.
                This is the default behavior.
        -x      Converts the <input file> to XML, assuming it is binary.
        -b      Converts the <input file> to binary; specify -j or -x to 
                    convert from JSON or XML.  (JSON is default.)  If the
                    output file is not specified, an ASCII representation is
                    printed to standard output.
        -o      Outputs the content to <output file>.  Standard output is the
                    default output.
        -h      This help.

        --hex   Treats the input file as a hexadecimal text file, converting
                    it first to binary and then to the specified output
                    format.

        --type=<type> Treats the input message as one of the three listed PDUtoto
                    data types in the V2X specifications:
					MessageFrame, CAM, DENM, SPATEM, MAPEM, IVIM, SREM, SSEM
                    By default, the MessageFrame PDU is assumed.
        --verbose=<bool> Turn verbosity on/off.  Default is on. This does little
                    to nothing when a release build of the V2X shared library
                    is being used.

    For example:

        {name} -jb -o message.dat message.json

    or

        {name} -b -o message.dat message.json

    converts the input file message.json to a binary file message.dat,
    assuming it is a MessageFrame data type.  An equivalent set of options is

        {name} -j message.dat

    converts the input file message.dat to JSON, outputting it to standard
    output.

        {name} -x -o message.xml --type=CAM message.dat

    converts the input file message.dat to XML, outputting it to message.xml.
    The input PDU type is assumed to be a CAM message.
""".format(name=name))


def main(inf, outf=sys.stdout, cls=v2x.MessageFrame, outfmt='json',
        inpfmt='bin', verbose=False):
    """buf = main(inf, outf=sys.stdout, cls=v2x.MessageFrame,
    outfmt='json', inpfmt='bin', verbose=True)

    Converts the input file inf to the output format specified by outfmt.
    outfmt may take one of three values: 'bin', 'json', and 'xml'.  If outfmt
    is 'bin', the input format inpfmt must be set to either 'json' or 'xml'.

    If the inpfmt is 'hex', the input format is assumed to be hexadecimal text
    and is packed into a binary encoding prior to conversion.

    If outfmt is one of 'json' or 'xml', inpfmt is ignored: transcoding
    between JSON and XML is not currently supported, and the assumption is
    that the input format is binary.

    The input file will be decoded according to the given cls, which defaults
    to the v2x.MessageFrame class.  The class may be given as MessageFrame,
    CAM, DENM, SPATEM, MAPEM, IVIM, SREM, or SSEM.

    On success, a message buffer is returned that contains the encoded
    content.  On failure, None is returned."""
    
    if type(inf) == str:
        inp_data = open(inf, 'rb').read()
    else:
        inp_data = inf.read()
        inf.close() 

    if inpfmt == 'hex':
        # Get rid of whitespace
        inp_data = b"".join(inp_data.split())
        
        # Pad with a zero nibble if length is odd
        if len(inp_data) % 2 == 1:
            inp_data = inp_data + '0'
            
        inp_data = binascii.unhexlify(inp_data)

    if type(outf) == str:
        if outfmt == "bin":
            out_data = open(outf, 'wb')
        else:
            out_data = open(outf, 'wt')
    else:
        out_data = outf

    if cls not in [v2x.MessageFrame, v2x.CAM, v2x.DENM, v2x.SPATEM, v2x.MAPEM,
				   v2x.IVIM, v2x.SREM, v2x.SSEM]:
        raise ValueError("The class for decoding must be one of "
						 "v2x.MessageFrame, v2x.CAM, v2x.DENM, v2x.SPATEM, "
						 "v2x.MAPEM, v2x.IVIM, v2x.SREM, v2x.SSEM")


    # The rest of the example code is just infrastructure; at the end of the
    # day, conversions between binary and XML/JSON are as easy as seen in the
    # following 15 lines of code.
    if outfmt == 'bin':
        if inpfmt == 'json':
            buf = cls.from_json(inp_data, verbose=verbose)
        elif inpfmt == 'xml':
            buf = cls.from_xml(inp_data, verbose=verbose)
        else:
            raise ValueError("The input format for a binary message must be JSON or XML, not {}.".format(inpfmt))
    elif outfmt == 'json':
        buf = cls.to_json(inp_data, len(inp_data), verbose=verbose)
    elif outfmt == 'xml':
        buf = cls.to_xml(inp_data, len(inp_data), verbose=verbose)
    else:
        raise ValueError("The output format must be one of 'bin', 'json', or 'xml', not {}".format(outfmt))

    if type(buf) == tuple:
        errcode, errtext = buf
        print(errtext)        
    else:
       if out_data is sys.stdout and outfmt == 'bin':
           print(binascii.hexlify(buf))
       else:
           if outfmt == 'bin':
               out_data.write(buf)
           else:
               print(buf, file=out_data)
           
           out_data.close()

    return buf


if __name__ == "__main__":
    import getopt

    opts, args = getopt.getopt(sys.argv[1:], 't:jxbo:h', ['type=', 'hex', 'verbose='])

    kwargs = {
            'outf':     sys.stdout,
            'cls':      v2x.MessageFrame,
            'outfmt':   'json',
            'inpfmt':   'bin',
            'inf':      None
    }

    binary_selected = False
    json_selected = True
    xml_selected = False
    num = 1
  
    for opt in opts:
        if opt[0] == '-h':
            usage(os.path.basename(sys.argv[0]))
            sys.exit()

        if opt[0] == '-o':
            kwargs['outf'] = opt[1]

        if opt[0] == '-j':
            json_selected = True

        if opt[0] == '-x':
            xml_selected = True

        if opt[0] == '-b':
            binary_selected = True

        if opt[0] == '--type':
            map = {
                "cam" : v2x.CAM, "denm" : v2x.DENM, "spatem" : v2x.SPATEM,
                "mapem" : v2x.MAPEM, "ivim" : v2x.IVIM, "ssrem" : v2x.SREM,
                "ssem" : v2x.SSEM }
            if opt[1].lower() in map:
                kwargs['cls'] = map[opt[1].lower()]
            else:
                kwargs['cls'] = v2x.MessageFrame

        if opt[0] == '--hex':
            kwargs['inpfmt'] = 'hex'

        if opt[0] == '-t':
            num = int(opt[1])
            
        if opt[0] == '--verbose':
            kwargs['verbose'] = opt[1].lower() == "true"

    if binary_selected:
        kwargs['outfmt'] = 'bin'
        kwargs['inpfmt'] = 'xml' if xml_selected else 'json'
    elif xml_selected:
        kwargs['outfmt'] = 'xml'
    else:
        kwargs['outfmt'] = 'json'

    if len(args) == 0:
        raise RuntimeError("Missing input file name.")
    elif len(args) > 1:
        raise RuntimeError("Too many input file names.")
        
    kwargs['inf'] = args[0]

    for i in range(num):
        buf = main(**kwargs)
        del(buf)
