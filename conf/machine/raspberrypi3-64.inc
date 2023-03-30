# Raspberry Pi profile
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

DISTRO_ARCH ?= "arm64"

# Raspberry Pi needs non-free-firmware repository.
DISTRO_APT_SOURCES += "conf/distro/emlinux-bookworm-full.list"

# wic file settings
IMAGE_FSTYPES ?= "wic wic.xz"
WKS_FILE ?= "rpi-sdimg"

IMAGE_PREINSTALL += "\
  firmware-brcm80211 \
"
IMAGE_INSTALL += "\
  rpi-u-boot-scr \
  rpi-boot-config \
  raspberrypi-bootfiles \
"

WIC_IMAGER_INSTALL = "\
  parted \
  dosfstools \
  mtools \
  e2fsprogs \
  python3-distutils \
  bmap-tools \
"

KERNEL_DEFCONFIG = "raspberrypi3-64_defconfig"

U_BOOT_BIN = "u-boot.bin"

KERNEL_IMAGE = "Image"

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

