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
while [ $# -gt 0 ]; do
  case "$1" in
    run|build|clean)
	mode="$1"
	;;
    "-t")
	distro="-trixie"
	;;
    "-h")
	echo "Usage: $0 [-t] [run|build|clean]"
	echo "       -t:    Use trixie distribution (Default is bookworm)"
	echo "       run:   Run new docker container"
	echo "       build: Build docker image"
	echo "       clean: Remove docker image"
	exit
  esac
  shift
done

host_user_id=$(id -u)
host_user_name=$(id -un)
export host_user_id="${host_user_id}"
export host_user_name="${host_user_name}"

cd ${script_dir}
if [ "${mode}" = "build" ]; then
    ${docker_compose_cmd} build --no-cache emlinux3-build"${distro}"
elif [ "${mode}" = "run" ]; then
    ${docker_compose_cmd} run --rm emlinux3-build"${distro}"
elif [ "${mode}" = "clean" ]; then
    docker rmi -f "emlinux3-build${distro}-${host_user_name}"
fi
