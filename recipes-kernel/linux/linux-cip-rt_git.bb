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

LINUX_CIP_VERSION = "v6.1.38"
PV = "6.1.38"
SRC_URI += " \
    git://git.kernel.org/pub/scm/linux/kernel/git/rt/linux-stable-rt.git;branch=v6.1-rt;destsuffix=${P};protocol=https \
    file://preempt-rt.cfg \
"

SRC_URI:append:generic-x86-64 = " file://generic-x86-64_defconfig"

SRCREV = "7c574e2eb052aa39ba796334bf95c0baa9479411"

KBUILD_DEPENDS:append = ", zstd"
