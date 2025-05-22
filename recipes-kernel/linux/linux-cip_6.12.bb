#
# EMLinux kernel recipe
#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#
FILESEXTRAPATHS:prepend := "${FILE_DIRNAME}/files/6.12:"

require recipes-kernel/linux/linux-cip-common.inc

LINUX_CIP_VERSION = "v6.12.29-cip1"
PV = "6.12.29-cip1"
BRANCH = "linux-6.12.y-cip"

SRC_URI:append:qemu-arm64 = " file://qemu-arm64_defconfig"

SRCREV = "af4062852978b4a204076202d0ff1293987354b9"
