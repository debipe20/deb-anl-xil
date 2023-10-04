V2X API

This distribution contains an API for encoding and decoding ASN.1 
messages defined in Vehicle-to-everything (V2X) standards.  This
includes  the SAE Dedicated Short-Range Communications (DSRC) Protocol 
Specification as well as the equivalent ETSI standards (CAM and DENM).

INSTALLATION

The package may be unzipped in any directory on the target 
system.  The following directory tree will be created: 

v2x_api_<version>
  +- debug
     +- lib
     +- src
  +- doc
  +- golang
  +- python
  +- release
     +- lib
     +- src
  +- rtjsonsrc
  +- rtpersrc
  +- rtsrc
  +- rtxmlsrc
  +- rtxsrc
  +- sample
     +- BasicSafetyMessage
     +- CAMMessage
     +- DENMMessage
     +- python
  +- utilsrc

The doc directory contains the User's Guide documents.

The debug and release directories contain the debug and release version 
of the API and associated header files respectively.

The golang directory contains the Go wrapper and a Go sample.  See the
V2XGolangUsersGuide document in the doc directory.

The python directory contains the Python wrapper.  See the V2XPythonUsersGuide
document in the doc directory.

The rt*src directories contain common run-time header files.

The sample directory contains various sample programs that use the API.

The sample/pthon directory contains a sample Python script.  See the
V2XPythonUsersGuide document in the doc directory.

The utilsrc directory contains definitions of C++ mechanisms used by the
Go and Python wrappers.

BUILD PROCEDURE

To build and run the sample programs, go to the sample subdirectory. 
You can then go to each of the sample subdirectories within and invoke 
make to compile and link the writer and reader programs.  The writer 
and reader programs can then be invoked from a command-line prompt 
to demonstrate the encoding and decoding of PER messages.

Note that to use the DLL on Windows, it must be present within 
the system's PATH environment variable.  One way to achieve this 
is to modify the PATH within the sample directory in which the 
executable file exists using the following command:

SET PATH=%PATH%;..\..\debug\lib

On Linux, the LD_LIBRARY_PATH environment variable must be defined
to point at the location in which the shared object file is 
located: 

export LD_LIBRARY_PATH=../../debug/lib

In both of these cases, the path to the release library directory 
could be used in places of the debug library directory.

It is also possible to copy the DLL to any directory within the 
PATH to avoid having to set the environment variable each time. 
The variable as set will also only work for sample programs at 
that directory since relative paths were used.

It may also be necessary to set an environment variable to allow 
the DLL to find the a license file needed to run.  This environment 
variable is the ACLICFILE variable and must be set to point to the 
full path to an osyslic.txt file that should have been provided when
the product was downloaded.  Normally, this file would be placed in 
the same directory as the DLL or .so file.  This may be sufficient to 
allow it to be found.  If not create an environment variable as follows:

export ACLICFILE=../../debug/lib/osyslic.txt


GETTING STARTED

The best way to begin using the software is by executing the sample 
program.  Go to the sample/BasicSafetyMessage directory and execute 
the makefile.  On Windows, this would be done using nmake from a 
Visual Studio command prompt or other command shell:

  nmake

On Linux, make would be used: 

  make

This will build the writer and reader programs.  

Before running the programs, be sure the O/S can locate the V2X
DLL by setting the PATH or LD_LIBRARY_PATH environment variable
as described above.

You can then execute the writer as follows:

  writer

It will encode a Basic Safety Message and write it to the message.dat 
file.  A trace dump of the message will be done do that you can observe a 
human-readable representation of what was encoded.

You can then invoke the reader program to read the message:

  reader

This will read and decode the message.  The contents of the decoded 
structure will be displayed.  You can verify these contents with the 
code in the writer program to ensure you got back what originally was 
encoded.

This can then be used as a template for further development.  The most 
time consuming task in developing an API is poulating data structures for 
encoding.  ASN1C provides some assistance in this area through the test 
code generation command-line option (-genTest).  This will populate a test 
instance of a generated type with random test data.  This can then be used
as a model for populating structures with real data.

USING THE GO AND PYTHON WRAPPERS

Consult the V2XGolangUsersGuide and the V2XPythonUsersGuide documents in the
doc directory.

REPORTING PROBLEMS

Report problems you encounter by sending E-mail to support@obj-sys.com.  
The preferred format of example programs is the same as the sample 
programs.  Please provide a writer and reader and indicate where in 
the code the problem occurs.

If you have any further questions or comments on what you would like to 
see in the product or what is difficult to use or understand, please 
communicate them to us.  Your feedback is important to us.  Please let 
us know how it works out for you.
