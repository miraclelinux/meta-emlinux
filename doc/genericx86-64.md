# Generic x86-64 machines

This document describes how to build and run a EMLinux image on generic 64-bit Intel architecture platforms(genericx86-64).
Please note that the EMLinux image built with following procedure is not necessarily guaranteed to work on all x86-64 hardware.

## Setup the build environment

If you have an EMLinux commercial release (emlinux-2.x-yyyymm.tar.gz), run following commands to setup the build environment.

```
$ tar zxf emlinux-2.5-202204.tar.gz
$ cd emlinux-2.5-202204/
$ source setup-emlinux build
```

Otherwise, run following commands instead.

```
$ mkdir emlinux
$ cd emlinux/
$ mkdir repos
$ git clone -b warrior https://github.com/miraclelinux/meta-emlinux.git repos/meta-emlinux
$ source repos/meta-emlinux/scripts/setup-emlinux build
```

## Build the bootable image

In the build directory, you need to set "genericx86-64" to MACHINE variable.
In addition, you need to set "emlinux-k510" to DISTRO variable to use Linux 5.10.
Then, build a EMLinux image (core-image-minimal, core-image-weston).
The example below shows the commands to build core-image-minimal.

```
$ echo 'MACHINE = "genericx86-64"' >> conf/local.conf
$ echo 'DISTRO = "emlinux-k510"' >> conf/local.conf
$ bitbake core-image-minimal
```

After the build completes, you can find bootable disk image(core-image-minimal-genericx86-64.wic) under `tmp-glibc/deploy/images/genericx86-64`.


## Boot EMLinux

If you use a USB flash drive or other disk drives for your target machine, write the wic disk image to your drive with the following commands.
Please select an appropriate sdX device file for your drive.

```
$ dd if=core-image-minimal-genericx86-64.wic of=/dev/sdX bs=1G
```

After connecting the drive to your target machine, power on the machine.
