#!/bin/bash

which docker-compose >/dev/null
if [ $? != 0 ]; then
  echo "[*] docker-compose command is not found. Please install it."
  exit 1
fi  

mode="run"
if [ $# = 1 ]; then
  mode="${1}"
fi

host_user_id=$(id -u)
export host_user_id="${host_user_id}"

if [ "${mode}" = "build" ]; then
  docker-compose build --no-cache
elif [ "${mode}" = "run" ]; then
  docker-compose run --rm emlinux3-build
fi
