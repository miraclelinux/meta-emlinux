# Build environment setup by docker

## Install the docker engine and docker-compose command

If you want to build images with docker, you need to install Docker (to be precise: docker-ce, docker-ce-cli, containerd.io, docker-buildx-plugin, docker-compose-plugin) on your host machine. Please refer to the official web site (https://docs.docker.com/engine/install/) to install them.

## How to use run.sh
`run.sh` contained in the `docker/` directory is a utility to operate the docker container image for the build environment.

### Build a docker image

Go to the docker/ directory.

```sh
$ cd docker
```

Then, build docker image.

```sh
$ ./run.sh build
```

### Run a docker image

Execute the following command in the `docker/` directory to run a new container for the build environment. (If the docker image has not built yet, this command builds it implicitly.)

```sh
$ ./run.sh run
```

### Cleanup docker image

If you want to remove the docker image, execute the following command in the `docker/` directory.

```sh
$ ./run.sh clean
```

## How to check the behavior of GUI images booted with QEMU

Enter the docker container.

```
HOST-PC$ ./run.sh run
```

Note down IP address of docker container.

```
build@CONTAINER-ID:~/work$ ip address
```

Setup build directory and build core-image-weston with bitbake.

```
build@CONTAINER-ID:~/work$ . setup-emlinux
build@CONTAINER-ID:~/work/build$ core-image-weston
```

Start QEMU with "publicvnc" as an argument.

```
build@CONTAINER-ID:~/work/build$ runqemu qemuarm64 slirp publicvnc
```

Then, VNC server is started on docker container.

From VNC client on host PC, connect to VNC server on docker container.

```
HOST-PC$ vncviewer <CONTAINER-IP-ADDRESS>
```
