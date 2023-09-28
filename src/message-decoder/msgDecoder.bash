#!/bin/bash

# export PYROOT=${PWD}/v2x_api_76201_lb
export PYROOT=/home/carma/Desktop/deb-anl-xil/3rdparty/objective-systems/v2x_api_76201_lb
export BUILD=debug

export LIBROOT=${PYROOT}/${BUILD}/lib
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${LIBROOT}
export PYTHONPATH=${PYTHONPATH}:${PYROOT}/python/src

PYEXE=$(which python3)

${PYEXE} msg-decoder.py
