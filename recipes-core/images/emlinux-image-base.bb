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

LICENSE = "gpl-2.0"
LIC_FILES_CHKSUM = "file://${LAYERDIR_core}/licenses/COPYING.GPLv2;md5=751419260aa954499f7abaabaa882bbe"

PV = "1.0"

ISAR_RELEASE_CMD = "git -C ${LAYERDIR_emlinux} describe --tags --dirty --always --match 'v[0-9].[0-9]*'"

inherit image

