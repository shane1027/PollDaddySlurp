#!/usr/bin/sh

# script to automate the work done by two python scripts since they depend on
# different versions of python (thus can't be merged) and i'm too lazy to bring
# compatibility to one or the other using 2to3

python find_proxies.py
regex="//([0-9]*.[0-9]*.[0-9]*.[0-9]*:[0-9]*)"

cat proxies.txt | grep -oE $regex | sed "s/s//g" | sed "s|/||g" >> proxy_formatted.txt

echo 'built formatted live proxy list!'

sudo python2 poll_slurp.py
