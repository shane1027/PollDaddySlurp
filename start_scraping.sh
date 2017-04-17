#!/usr/bin/sh

# script to automate the work done by two python scripts since they depend on
# different versions of python (thus can't be merged) and i'm too lazy to bring
# compatibility to one or the other using 2to3
echo 'clearing out old proxies..'
rm proxies.txt

echo 'building list, please wait a min... some garbage may come up periodically'
python find_proxies.py 2&> /dev/null
regex="//([0-9]*.[0-9]*.[0-9]*.[0-9]*:[0-9]*)"

cat proxies.txt | grep -oE $regex | sed "s/s//g" | sed "s|/||g" > proxy_formatted.txt

echo 'built formatted live proxy list!'
read lines words chars filename <<< $(wc proxy_formatted.txt)

echo 'starting voting process using ' $lines ' live proxies...'

python2 poll_slurp.py
