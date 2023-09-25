#
# EMLinux kernel recipe
#
# Copyright (c) Cybertrust Japan Co., Ltd. 
#
# Authors:
#  Masami Ichikawa <masami.ichikawa@miraclelinux.com>
#
# SPDX-License-Identifier: MIT
#
FILESEXTRAPATHS:prepend := "${FILE_DIRNAME}/files:"

require recipes-kernel/linux/linux-custom.inc

LINUX_CIP_VERSION = "v6.1.46-cip4"
PV = "6.1.46-cip4"
SRC_URI += " \
    git://git.kernel.org/pub/scm/linux/kernel/git/cip/linux-cip.git;branch=linux-6.1.y-cip;destsuffix=${P};protocol=https \
"

SRC_URI:append:qemu-arm64 = " file://qemu-arm64_defconfig"
SRC_URI:append:qemu-amd64 = " file://qemu-amd64_defconfig"
SRC_URI:append:generic-x86-64 = " file://generic-x86-64_defconfig"
SRC_URI:append:raspberrypi3bplus-64 = " file://raspberrypi3-64_defconfig"
SRC_URI:append:raspberrypi4-64 = " file://raspberrypi4-64_defconfig"

SRC_URI[sha256sum] = "1caa1b8e24bcfdd55c3cffd8f147f3d33282312989d85c82fc1bc39b808f3d6b"
SRCREV = "58f7d1bf36cb697e7cab922b71d04f7d925e3b1f"

KBUILD_DEPENDS:append = ", zstd"
