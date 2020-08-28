#!/bin/sh

if [ $# -ne 1 ]; then
  echo "usage $0 [interface]"
  exit 1
fi

IFACE=$1
echo "checking ${IFACE}"

for i in $(seq 10);
do
  if [ -d /sys/class/net/${IFACE} ]; then
    exit 0
  fi
  sleep 1
done

exit 1
