#!/bin/bash

for var in "$@"
do
  python3 ./ips_extend_mon.py "$var" &
  sleep 4
done
