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
FILESEXTRAPATHS_prepend := "${FILE_DIRNAME}/files:"

require recipes-kernel/linux/linux-custom.inc

LINUX_CIP_VERSION = "v6.1.10"
PV = "6.1.10"
SRC_URI += " \
    git://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git;branch=linux-6.1.y;destsuffix=${P};protocol=https \
    file://${MACHINE}_defconfig \
"

KERNEL_DEFCONFIG = "${MACHINE}_defconfig"
SRC_URI[sha256sum] = "1caa1b8e24bcfdd55c3cffd8f147f3d33282312989d85c82fc1bc39b808f3d6b"
SRCREV = "17d99ea98b6238e7e483fba27e8f7a7842d0f345"

KBUILD_DEPENDS_append = ", zstd"
