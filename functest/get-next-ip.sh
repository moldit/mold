#!/bin/bash

LOCKDIR=/tmp/ip.locks
BASE=${PRIVATE_IP_BASE=192.168}

mkdir -p $LOCKDIR

IP=
for i in {1..255}; do
    for j in {2..254}; do
        IP="${BASE}.$i.$j"
        lockfile -r0 "${LOCKDIR}/${IP}" 2>/dev/null
        X=$?
        if [ "$X" -eq "0" ]; then
            # succeeded in getting IP
            echo $IP
            exit 0
        fi
    done
done
echo "no IPs available :("
exit 1