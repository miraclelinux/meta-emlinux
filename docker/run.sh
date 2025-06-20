#!/bin/bash

script_dir=$(dirname $0)
docker_compose_cmd="docker compose"
docker compose version > /dev/null 2>&1
if [ $? != 0 ]; then
    docker-compose version > /dev/null 2>&1
    if [ $? != 0 ]; then
        echo "[*] docker compose or docker-compose command is not found."
        echo "    Please install newer version of docker engine (or docker-compose)."
        exit 1
    fi
    docker_compose_cmd="docker-compose"
fi

mode="run"
if [ $# = 1 ]; then
    mode="${1}"
fi

host_user_id=$(id -u)
host_user_name=$(id -un)
export host_user_id="${host_user_id}"
export host_user_name="${host_user_name}"

cd ${script_dir}
if [ "${mode}" = "build" ]; then
    ${docker_compose_cmd} build --no-cache emlinux3-build
elif [ "${mode}" = "run" ]; then
    ${docker_compose_cmd} run --rm emlinux3-build
elif [ "${mode}" = "clean" ]; then
    docker rmi -f "emlinux3-build-${host_user_name}"
fi
