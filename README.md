Quick Start
===========

The meta-emlinux layer has been tested primarily on Ubuntu 18.04 LTS and 20.04 LTS.
This layer probably works on Debian 10.

> [!NOTE]
> The standard support period for Ubuntu 20.04 LTS ends in April 2025.
> If you are setting up a build environment using Docker container, see doc/build-env-docker.md.

Install essential packages for poky:

```sh
$ sudo apt-get install -y gawk wget git-core diffstat unzip texinfo gcc-multilib \
build-essential chrpath socat cpio python python3 python3-pip python3-pexpect \
python3-debian xz-utils debianutils iputils-ping libsdl1.2-dev xterm rsync
```

Clone meta-emlinux:

```sh
$ mkdir repos
$ git clone -b warrior https://github.com/miraclelinux/meta-emlinux.git repos/meta-emlinux
```

Setup build directory:

```sh
$ source repos/meta-emlinux/scripts/setup-emlinux build
```

Set your target machine to `conf/local.conf`:

```sh
$ echo "MACHINE = \"qemuarm64\"" >> conf/local.conf
```

You can use following variables for MACHINE.

- qemuarm64
- qemuarm
- raspberrypi3-64 (Raspberry Pi3 64bit mode)

Build:

```sh
$ bitbake core-image-minimal
```

License
=======

License of meta-emlinux is same as meta in poky i.e.
All metadata is MIT licensed unless otherwise stated.
Source code included in tree for individual recipes is under the LICENSE stated in the associated recipe (.bb file) unless otherwise stated.

See COPYING.MIT for more details about MIT license.

Community Resources
===================

#### Project home
* https://github.com/miraclelinux/meta-emlinux
