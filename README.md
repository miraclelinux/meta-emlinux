# Quick Start

## Supported build host

EMLinux supported build host OS is Debian 11 or greater.

# Build environment setup 

## Build by docker

### Install the docker engine and docker-compose command

You can build and image by docker. If you want to build image, you need docker engine and docker-compose. Please refer to official web site to install the docker engine (https://docs.docker.com/engine/install/) and the docker-compose command (https://docs.docker.com/compose/install/other/).

### Install the qemu-user-static
You need to install the qemu-user-static package on the host PC to enable cross-building on docker.

```
$ sudo apt install qemu-user-static
```

### Build a docker image

The docker/ directory contains build script and docker-compose.yml file.

1. Goto docker/ directory

```
$ cd docker
```

Then, build docker image and logged into docker container.

```
$ ./run.sh
```

## Build directly on your host

### Setup host os development environment

If you want to set up directly on your build host, please refer to following steps.

Run following command to install required packages.

```
$ sudo apt install \
  binfmt-support \
  debootstrap \
  dosfstools \
  dpkg-dev \
  gettext-base \
  git \
  mtools \
  parted \
  python3 \
  quilt \
  qemu-user-static \
  reprepro \
  git-buildpackage \
  pristine-tar \
  sbuild \
  schroot \
  zstd \
  python3-distutils \
  mmdebstrap
```

### Setup user

1. Add user to the sbuild group

```
$ sudo gpasswd -a <username> sbuild
```

2. Setup sudo

Building EMLinux, user need to be able to run sudo command as root.

Please follow "Setup Sudo" section in ISAR user manual.

https://github.com/ilbers/isar/blob/master/doc/user_manual.md#setup-sudo

## Setup repositories

Download laysers to your build environment.

1. Create a directory

```
$ mkdir repos
```

2. Checkout meta-emlinux

```
$ git clone -b emlinux3 https://github.com/miraclelinux/meta-emlinux.git repos/meta-emlinux
```

3. Setup build directory

```
$ source repos/meta-emlinux/scripts/setup-emlinux build
```

## Build image

1.  Edit conf/local.conf

If you want to add package/change machine/etc edit conf/local.conf.
For example, if you want build qemu-arm64 image that includes iproute2 package, add folloinwg lines in conf/local.conf.

```
MACHINE = "qemu-arm64"
IMAGE_PREINSTALL = "iproute2"
```

EMLinux supports building Debian bookworm and trixie based images and you can choose distribution from them by specifying the DISTRO variable in conf/local.conf. This variable is set as emlinux-bookworm by default, so you do not have to add any changes to use bookworm. If you want to use trixie, add the following lines in conf/local.conf.

```
DISTRO = "emlinux-trixie"
```

### bootstrap class

EMLinux uses mmdebstrap as a default bootstrap class for both emlinux-bookworm and emlinux-trixie as the ISAR does. The debootstrap class doesn't support emlinux-trixie, so if you use emlinux-bookworm and wants to stay keep with debootstrap for some reason (e.g. you extend isar-bootstrap-[host|target].class), add following lines in your conf/local.conf.

```
PREFERRED_PROVIDER_bootstrap-host ?= "isar-bootstrap-host"
PREFERRED_PROVIDER_bootstrap-target ?= "isar-bootstrap-target"
```

2. Build image

Specify an image as either emlinux-image-base or emlinux-image-weston, then run bitbake.

```
$ bitbake <image>
```

## Run image by qemu

For running the image of a QEMU machine, run the runqemu script with arguments corresponding to the image as below.

```
usage: runqemu <machine> <distro> <image>

e.g.) runqemu qemu-amd64 emlinux-bookworm emlinux-image-base

Supported machines	qemu-amd64, qemu-arm64, qemu-arm

Any distro and image can be specified according to the image to run.
```

## Supported machines

EMLinux currently supports the following machines. The supported machines are different between distributions.

### Supported machines in bookworm

- qemu-amd64
- qemu-arm64
- qemu-arm
- generic-x86-64
- raspberrypi3bplus-64
- raspberrypi4b-64
- raspberrypi400-64

### Supported machines in trixie

- qemu-amd64
- qemu-arm64
- qemu-arm
- generic-x86-64
- raspberrypi4b-64

## Sample Recipe

There are some sample recipes under doc/samples/recipes-sample/ directory. Currently you can see following sample recipes.

- openssl-apt  
This recipe downloads openssl source package using _apt://_. This recipe shows how to change build option and how to add new patch for source code.
- openssl-http  
This recipe downloads openssl source package using _http://_. This recipe shows how to change build option and how to add new patch for source code.
- openssl-git  
This recipe downloads openssl source package using _git://_. This recipe shows how to change build option.

# License

All metadata is MIT licensed unless otherwise stated.
Source code included in tree for individual recipes is under the LICENSE stated in the associated recipe (.bb file) unless otherwise stated.

See [COPYING.MIT](COPYING.MIT) for more details about MIT license.

# Community Resources

#### Project home

* https://github.com/miraclelinux/meta-emlinux
