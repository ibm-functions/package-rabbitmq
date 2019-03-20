#!/bin/bash
#Author: Mark Purcell (markpurcell@ie.ibm.com)

source env.sh

cd invoker
ln -s ../messenger
python3 connect.py
rm messenger


