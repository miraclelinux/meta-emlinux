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
INHERIT += "sdk-installer"

DISTRO_KERNELS ?= "linux-cip"
KERNEL_NAME ?= "cip"

WIC_IMAGER_INSTALL = "parted \
  gdisk \
  util-linux \
  dosfstools \
  mtools \
  e2fsprogs \
  python3-distutils \
  bmap-tools \
  tar \
  fdisk"

WKS_FILE ?= "${MACHINE}.wks"

