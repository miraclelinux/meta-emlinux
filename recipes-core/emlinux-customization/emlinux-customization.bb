#
# EMLinux customization
#
# Copyright (c) Cybertrust Japan Co., Ltd. 
#
# Authors:
#  Masami Ichikawa <masami.ichikawa@miraclelinux.com>
#
# SPDX-License-Identifier: MIT
#
FILESEXTRAPATHS:prepend := "${FILE_DIRNAME}/files:"

DESCRIPTION = "EMLinux 3.x specific customization"

inherit dpkg-raw

SRC_URI = " \
    file://postinst \
"

