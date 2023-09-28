# Raspberry Pi profile
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

include conf/machine/raspberrypi-64.inc

WKS_FILE ?= "rpi4-sdimg"

KERNEL_DEFCONFIG = "raspberrypi4-64_defconfig"

IMAGE_BOOT_FILES ?= "${KERNEL_IMAGE} ${DTB_FILES} \
                     ${IMAGE_ROOTFS}/boot/overlays/*;overlays/ \
                     ${IMAGE_ROOTFS}/usr/lib/u-boot/${MACHINE}/u-boot.bin;./ \
                     ${IMAGE_ROOTFS}/boot/boot.scr;./ \
                     ${IMAGE_ROOTFS}/boot/COPYING.linux;./ \
                     ${IMAGE_ROOTFS}/boot/LICENCE.broadcom;./ \
                     ${IMAGE_ROOTFS}/boot/bootcode.bin;./ \
                     ${IMAGE_ROOTFS}/boot/config.txt;./ \
                     ${IMAGE_ROOTFS}/boot/start.elf;./ \
                     ${IMAGE_ROOTFS}/boot/start_cd.elf;./ \
                     ${IMAGE_ROOTFS}/boot/start_db.elf;./ \
                     ${IMAGE_ROOTFS}/boot/start_x.elf;./ \
                     ${IMAGE_ROOTFS}/boot/fixup.dat;./ \
                     ${IMAGE_ROOTFS}/boot/fixup_cd.dat;./ \
                     ${IMAGE_ROOTFS}/boot/fixup_db.dat;./ \
                     ${IMAGE_ROOTFS}/boot/fixup_x.dat;./"

