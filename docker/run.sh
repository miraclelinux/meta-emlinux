#!/bin/bash

docker_compose_cmd="docker compose"
docker compose version >/dev/null
if [ $? != 0 ]; then
    docker-compose version >/dev/null
    if [ $? != 0 ]; then
	echo "[*] docker compose or docker-compose command is not found. Please install newer version of docker engine (or docker-compose)."
	exit 1
    fi
    docker_compose_cmd="docker-compose"
fi

mode="run"
if [ $# = 1 ]; then
  mode="${1}"
fi

host_user_id=$(id -u)
export host_user_id="${host_user_id}"

if [ "${mode}" = "build" ]; then
  $docker_compose_cmd build --no-cache
elif [ "${mode}" = "run" ]; then
  $docker_compose_cmd run --rm emlinux3-build
fi
