#
# EMLinux kernel recipe
#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#
FILESEXTRAPATHS:prepend := "${FILE_DIRNAME}/files/6.12:"

require recipes-kernel/linux/linux-cip-common.inc

LINUX_CIP_VERSION = "v6.12.41-cip6"
PV = "6.12.41-cip6"
BRANCH = "linux-6.12.y-cip"

SRC_URI:append:qemu-arm64 = " file://qemu-arm64_defconfig"
SRC_URI:append:qemu-arm = " file://qemu-arm_defconfig"
SRC_URI:append:qemu-amd64 = " file://qemu-amd64_defconfig"
SRC_URI:append:generic-x86-64 = " file://generic-x86-64_defconfig"
SRC_URI:append:raspberrypi4b-64 = " file://raspberrypi4-64_defconfig"

SRCREV = "90d753ffff95206265b517c1e36880510c03c2cb"
