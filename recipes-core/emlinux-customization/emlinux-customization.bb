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

EMLINUX_SOURCE_FROM="non-debian"
DESCRIPTION = "EMLinux 3.x specific customization"
LICENSE = "MIT"
DEBIAN_DEPENDS = "netbase"
MAINTAINER = "Masami Ichikawa <masami.ichikawa@miraclelinux.com>"

inherit dpkg-raw

SRC_URI = " \
    file://postinst \
"

do_install[cleandirs] += "${D}/etc/profile.d"
do_install:append() {
    if [ -n "${EMLINUX_ENVIRONMENT_VARIABLE_PS1}" ]; then
        echo "PS1=\"${EMLINUX_ENVIRONMENT_VARIABLE_PS1}\"" > "${D}/etc/profile.d/ps1.sh"
    fi
}
