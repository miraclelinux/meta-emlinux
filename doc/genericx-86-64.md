# Generic x86-64 machines

This document describes how to build and run a EMLinux image on generic 64-bit Intel architecture platforms(genericx86-64).
Please note that the EMLinux image built with following procedure is not necessarily guaranteed to work on all x86-64 hardware.

## Setup the build environment

If you have an EMLinux commercial release (emlinux-3.x-yyyymm.tar.gz), run following commands to setup the build environment.

```
$ tar zxf emlinux-3.0-202304.tar.gz
$ cd emlinux-3.0-202304/
$ source setup-emlinux build
```

Otherwise, run following commands instead.

```
$ mkdir emlinux
$ cd emlinux/
$ mkdir repos
$ git clone -b bookworm https://github.com/miraclelinux/meta-emlinux.git repos/meta-emlinux
$ source repos/meta-emlinux/scripts/setup-emlinux build
```

## Build the bootable image

In the build directory, you need to set "generic-x86-64" to MACHINE variable.

```
$ echo 'MACHINE = "genericx-86-64"' >> conf/local.conf
$ bitbake emlinux-image-base
```

After the build completes, you can find bootable disk image(emlinux-image-base-emlinux-bookworm-generic-x86-64.wic) under `tmp/deploy/images/generic-x86-64/`.


## Boot EMLinux

If you use a USB flash drive or other disk drives for your target machine, write the wic disk image to your drive with the following commands.
Please select an appropriate sdX device file for your drive.

```
$ dd if=emlinux-image-base-emlinux-bookworm-generic-x86-64.wic of=/dev/sdX bs=1G
```

After connecting the drive to your target machine, power on the machine.
