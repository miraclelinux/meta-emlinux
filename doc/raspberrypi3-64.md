# Raspberry Pi 3 Model Series

EMLinux for Raspberry Pi is __not__ officially supported. However Raspberry Pi is a popular device so it would be nice to test and evaluate EMLinux on it.
This document describes how to setup EMLinux for the Raspberry Pi 3 model series. The current description is about Raspberry Pi 3 model B+ only.

## Build EMLinux

1. Basic setup

Run the following command if you have an EMLinux commercial release.

```
$ tar zxf emlinux-3.0-2023xx.tar.gz
$ cd emlinux-3.0-2023xx/
$ source setup-emlinux build
```

Otherwise, run the following command instead.

```
$ mkdir emlinux
$ cd emlinux/
$ mkdir repos
$ git clone -b bookworm https://github.com/miraclelinux/meta-emlinux.git repos/meta-emlinux
$ source repos/meta-emlinux/scripts/setup-emlinux build
```

2. Build image

In the build directroy, you can build image. You need to set necessary variables in the relevant .conf files.

```
$ echo 'MACHINE = "raspberrypi3bplus-64"' >> conf/local.conf
$ echo 'BBLAYERS += "${TOPDIR}/../repos/isar/meta-isar"' >> conf/bblayers.conf
```

Start the image creation as below.

```
$ bitbake emlinux-image-base
```

## Write SD card image

Decompress the output SD card image.

```
$ xz -d tmp/deploy/images/raspberrypi3bplus-64/emlinux-image-base-emlinux-bookworm-raspberrypi3bplus-64.wic.xz
```

Then, a wic image will be output to the following location.

```
tmp/deploy/images/raspberrypi3bplus-64/emlinux-image-base-emlinux-bookworm-raspberrypi3bplus-64.wic
```

Write the wic image to a SD card with the dd command.

```
$ sudo dd if=emlinux-image-base-emlinux-bookworm-raspberrypi3bplus-64.wic of=/dev/sdX bs=4k conv=fsync
```

Output device name "of=*/dev/sdX*" depends on your PC environment. Please replace appropriate device name.

## Boot EMLinux

Unmount the SD card and insert it to your Raspberry Pi then start it. You can login to console via UART. Enter `root` in the both login account and password fields.

The following statement will be printed after you login.

```
EMLinux 3.0 EMLinux3 ttyS1
EMLinux3 login: root
Password:
Linux EMLinux3 6.1.24+ #1 SMP PREEMPT Thu, 01 Jan 1970 01:00:00 +0000 aarch64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Tue Feb 28 11:16:00 UTC 2023 on ttyS1
root@EMLinux3:~#
```
