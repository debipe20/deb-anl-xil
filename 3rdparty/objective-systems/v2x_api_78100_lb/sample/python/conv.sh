#!/bin/bash
##
# This script sets the environment for running the v2x_conv.py script.
# Primarily we are concerned with setting the LD_LIBRARY_PATH and PYTHONPATH
# environment variables, since they control finding the appropriate shared
# libraries for running the sample.
##


export PYROOT=${PWD}/../..
export BUILD=debug

export LIBROOT=${PYROOT}/${BUILD}/lib
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${LIBROOT}
export PYTHONPATH=${PYTHONPATH}:${PYROOT}/python/src

#PYEXE=$(which python2.7)
PYEXE=$(which python3)

if [[ "${PYEXE}x" == "x" ]] ; then
   PYEXE=$(which python)
fi

echo Encoding message.dat to JSON:

${PYEXE} v2x_conv.py -j message.dat

echo Encoding message.hex to JSON:
${PYEXE} v2x_conv.py -j --hex message.hex

echo Encoding message.json to binary:
${PYEXE} v2x_conv.py -jb message.json

