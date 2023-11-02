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

LINUX_CIP_VERSION = "v6.1.59-cip8"
PV = "6.1.59-cip8"
SRC_URI += " \
    git://git.kernel.org/pub/scm/linux/kernel/git/cip/linux-cip.git;branch=linux-6.1.y-cip;destsuffix=${P};protocol=https \
"

SRC_URI:append:qemu-arm64 = " file://qemu-arm64_defconfig"
SRC_URI:append:qemu-amd64 = " file://qemu-amd64_defconfig"
SRC_URI:append:generic-x86-64 = " file://generic-x86-64_defconfig"
SRC_URI:append:raspberrypi3bplus-64 = " \
    file://raspberrypi3-64_defconfig \
    file://0001-ARM-dts-bcm2837-rpi-3-b-plus-Add-an-__overrides__-no.patch \
    file://0002-arm64-dts-broadcom-Add-a-compilation-flag-to-include.patch \
"

SRC_URI[sha256sum] = "1caa1b8e24bcfdd55c3cffd8f147f3d33282312989d85c82fc1bc39b808f3d6b"
SRCREV = "5ac26de5cee674d669fd90d11fb844eaf356ec9c"

KBUILD_DEPENDS:append = ", zstd"
