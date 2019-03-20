#!/bin/bash
#Author: Mark Purcell (markpurcell@ie.ibm.com)

source env.sh

#Launch the client application to drive some messages to the listener
cd invoker
ln -s ../messenger
python3 round_trip.py
rm messenger


