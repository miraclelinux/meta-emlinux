#
# EMLinux kernel recipe
#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#
FILESEXTRAPATHS:prepend := "${FILE_DIRNAME}/files/6.12:"

require recipes-kernel/linux/linux-cip-common.inc

LINUX_CIP_VERSION = "v6.12.36-cip4"
PV = "6.12.36-cip4"
BRANCH = "linux-6.12.y-cip"

SRC_URI:append:qemu-arm64 = " file://qemu-arm64_defconfig"

SRCREV = "24cd8155efab47b262747fcae9db7404333c9312"
