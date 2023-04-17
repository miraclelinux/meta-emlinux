#
# EMLinux base image
#
# Copyright (c) Cybertrust Japan Co., Ltd. 
#
# Authors:
#  Masami Ichikawa <masami.ichikawa@miraclelinux.com>
#
# SPDX-License-Identifier: MIT
#


DESCRIPTION = "EMLinux target filesystem"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${LAYERDIR_core}/licenses/COPYING.MIT;md5=838c366f69b72c5df05c96dff79b35f2"

PV = "1.0"

ISAR_RELEASE_CMD = "git -C ${LAYERDIR_emlinux} describe --tags --dirty --always --match 'v[0-9].[0-9]*'"

IMAGE_INSTALL:append = " emlinux-customization"
inherit image

