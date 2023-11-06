# Raspberry Pi profile
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

include conf/machine/raspberrypi-64.inc

KERNEL_DEFCONFIG = "raspberrypi4-64_defconfig"

IMAGE_BOOT_FILES ?= "${KERNEL_IMAGE} ${DTB_FILES} \
                     ${IMAGE_ROOTFS}/boot/overlays/*;overlays/ \
                     ${IMAGE_ROOTFS}/usr/lib/u-boot/${MACHINE}/u-boot.bin;./ \
                     ${IMAGE_ROOTFS}/boot/boot.scr;./ \
                     ${IMAGE_ROOTFS}/boot/COPYING.linux;./ \
                     ${IMAGE_ROOTFS}/boot/LICENCE.broadcom;./ \
                     ${IMAGE_ROOTFS}/boot/config.txt;./ \
                     ${IMAGE_ROOTFS}/boot/start4.elf;./ \
                     ${IMAGE_ROOTFS}/boot/start4cd.elf;./ \
                     ${IMAGE_ROOTFS}/boot/start4db.elf;./ \
                     ${IMAGE_ROOTFS}/boot/start4x.elf;./ \
                     ${IMAGE_ROOTFS}/boot/fixup4.dat;./ \
                     ${IMAGE_ROOTFS}/boot/fixup4cd.dat;./ \
                     ${IMAGE_ROOTFS}/boot/fixup4db.dat;./ \
                     ${IMAGE_ROOTFS}/boot/fixup4x.dat;./"

