# Raspberry Pi profile
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

DISTRO_ARCH ?= "arm64"

# Raspberry Pi needs non-free-firmware repository.
DISTRO_APT_SOURCES:remove = " conf/distro/emlinux-bookworm.list"
DISTRO_APT_SOURCES:prepend = " conf/distro/emlinux-bookworm-full.list "

# wic file settings
IMAGE_FSTYPES ?= "wic wic.xz tar.gz"
WKS_FILE ?= "emlinux-rpi-sdimg.wks.in"

IMAGE_PREINSTALL += "\
  firmware-brcm80211 \
"
IMAGE_INSTALL += "\
  rpi-u-boot-scr \
  rpi-boot-config \
  raspberrypi-bootfiles \
"

IMAGER_INSTALL:wic = "\
  parted \
  dosfstools \
  mtools \
  e2fsprogs \
  bmap-tools \
"

U_BOOT_BIN = "u-boot.bin"

KERNEL_IMAGE = "Image"
