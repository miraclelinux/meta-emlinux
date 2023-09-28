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

U_BOOT_BIN = "u-boot.bin"

KERNEL_IMAGE = "Image"
