#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

FILESEXTRAPATHS:prepend := "${FILE_DIRNAME}/files:"

DESCRIPTION = "U-boot boot script for Raspberry Pi"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${LAYERDIR_core}/licenses/COPYING.MIT;md5=838c366f69b72c5df05c96dff79b35f2"

inherit dpkg

DEBIAN_BUILD_DEPENDS = "u-boot-tools"

SRC_URI = "file://debian/ file://boot.cmd"

TEMPLATE_FILES = "debian/control.tmpl debian/rules.tmpl"
TEMPLATE_VARS += "DEBIAN_BUILD_DEPENDS"

S = "${WORKDIR}/rpi-u-boot-${PV}"

do_prepare_build() {
    mkdir ${S}
    cp -r ${WORKDIR}/debian ${S}/
    cp ${WORKDIR}/boot.cmd ${S}/

    deb_add_changelog
}
