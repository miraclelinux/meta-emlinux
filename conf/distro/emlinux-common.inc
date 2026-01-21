#
# EMLinux distro common file
#
# Copyright (c) Cybertrust Japan Co., Ltd. 
#
# Authors:
#  Masami Ichikawa <masami.ichikawa@miraclelinux.com>
#
# SPDX-License-Identifier: MIT
#

require include/security_flags.inc

INHERIT += "sdk-installer source-info"

DISTRO_KERNELS ?= "linux-cip"
KERNEL_NAME ?= "cip"

PREFERRED_VERSION_linux-cip-native ?= "${PREFERRED_VERSION_linux-cip}"
PREFERRED_VERSION_linux-cip-kbuildtarget ?= "${PREFERRED_VERSION_linux-cip}"

IMAGER_INSTALL:wic = "parted \
  gdisk \
  util-linux \
  dosfstools \
  mtools \
  e2fsprogs \
  python3-setuptools \
  bmap-tools \
  tar \
  fdisk"

IMAGE_PREINSTALL:append = " netbase"

WKS_FILE ?= "${MACHINE}.wks"

SDK_PREINSTALL += " \
  bc \
  libncurses-dev \
  flex \
  bison \
  pkg-config \
  libssl-dev \
  libelf-dev"

SDK_INSTALL += "${@ "linux-headers-"+d.getVar('KERNEL_NAME') if d.getVar('KERNEL_NAME') else '' }"

