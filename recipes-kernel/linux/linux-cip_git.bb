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

LINUX_CIP_VERSION = "v6.1.33"
PV = "6.1.33"
SRC_URI += " \
    git://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git;branch=linux-6.1.y;destsuffix=${P};protocol=https \
"

SRC_URI:append:qemu-arm64 = " file://qemu-arm64_defconfig"
SRC_URI:append:qemu-amd64 = " file://qemu-amd64_defconfig"
SRC_URI:append:generic-x86-64 = " file://generic-x86-64_defconfig"

SRC_URI[sha256sum] = "1caa1b8e24bcfdd55c3cffd8f147f3d33282312989d85c82fc1bc39b808f3d6b"
SRCREV = "2f3918bc53fb998fdeed8683ddc61194ceb84edf"

KBUILD_DEPENDS:append = ", zstd"
