#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

DESCRIPTION = "Configuration file for Raspberry Pi Bootloader"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${LAYERDIR_core}/licenses/COPYING.MIT;md5=838c366f69b72c5df05c96dff79b35f2"

inherit dpkg-raw

SRC_URI = "file://config.txt"

do_install() {
    install -d -m 0755 ${D}/boot
    install -m 0644 ${WORKDIR}/config.txt ${D}/boot/
}
