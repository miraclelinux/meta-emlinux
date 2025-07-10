#
# EMLinux kernel recipe
#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# Authors:
#  Hirotaka Motai <hirotaka.motai@miraclelinux.com>
#
# SPDX-License-Identifier: MIT
#
FILESEXTRAPATHS:prepend := "${FILE_DIRNAME}/files/6.1:"

require recipes-kernel/linux/linux-cip-common.inc

LINUX_CIP_VERSION = "v6.1.141-cip43-rt23"
PV = "6.1.141-cip43-rt23"
BRANCH = "linux-6.1.y-cip-rt"
SRC_URI += " file://preempt-rt.cfg"

SRC_URI:append:generic-x86-64 = " file://generic-x86-64_defconfig"
SRC_URI:append:raspberrypi3bplus-64 = " file://raspberrypi3-64_defconfig"
SRC_URI:append:raspberrypi4b-64 = " file://raspberrypi4-64_defconfig"

SRCREV = "449a79932bbacaf5cd660398fa3bfbfa0b3626ee"
