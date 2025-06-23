#
# EMLinux kernel recipe
#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#
FILESEXTRAPATHS:prepend := "${FILE_DIRNAME}/files/6.12:"

require recipes-kernel/linux/linux-cip-common.inc

LINUX_CIP_VERSION = "v6.12.32-cip2"
PV = "6.12.32-cip2"
BRANCH = "linux-6.12.y-cip"

SRC_URI:append:qemu-arm64 = " file://qemu-arm64_defconfig"
SRC_URI:append:raspberrypi4b-64 = " file://raspberrypi4-64_defconfig"

SRCREV = "0645c849aadd029e3382b5ab5dd785b2007cd9bf"
