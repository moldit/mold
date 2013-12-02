#!/bin/bash

LOCKDIR=/tmp/ip.locks

mkdir -p $LOCKDIR
while read ip; do
    echo "returning $ip to the pool"
    rm -f "${LOCKDIR}/${ip}"
done