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
FILESEXTRAPATHS:prepend := "${FILE_DIRNAME}/files:"

require recipes-kernel/linux/linux-custom.inc

LINUX_CIP_VERSION = "v6.1.132-cip40-rt21"
PV = "6.1.132-cip40-rt21"
SRC_URI += " \
    git://git.kernel.org/pub/scm/linux/kernel/git/cip/linux-cip.git;branch=linux-6.1.y-cip-rt;destsuffix=${P};protocol=https \
    file://preempt-rt.cfg \
"

SRC_URI:append:generic-x86-64 = " file://generic-x86-64_defconfig"
SRC_URI:append:raspberrypi3bplus-64 = " file://raspberrypi3-64_defconfig"
SRC_URI:append:raspberrypi4b-64 = " file://raspberrypi4-64_defconfig"

SRCREV = "6d3b527e6ebaf563d6e6c441c8c0c9c11de39180"

KBUILD_DEPENDS:append = ", zstd"
