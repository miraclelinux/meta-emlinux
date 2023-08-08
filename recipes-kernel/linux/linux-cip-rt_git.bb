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

LINUX_CIP_VERSION = "v6.1.38-cip1-rt1"
PV = "6.1.38-cip1-rt1"
SRC_URI += " \
    git://git.kernel.org/pub/scm/linux/kernel/git/cip/linux-cip.git;branch=linux-6.1.y-cip-rt;destsuffix=${P};protocol=https \
    file://preempt-rt.cfg \
"

SRC_URI:append:generic-x86-64 = " file://generic-x86-64_defconfig"

SRCREV = "b24e2a62dde025ade5db3ed51d07425f14a67e49"

KBUILD_DEPENDS:append = ", zstd"
