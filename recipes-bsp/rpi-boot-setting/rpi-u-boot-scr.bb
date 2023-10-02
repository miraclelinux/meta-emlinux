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

SRC_URI = "file://debian/"

TEMPLATE_FILES = "debian/control.tmpl debian/rules.tmpl"
TEMPLATE_VARS += "DEBIAN_BUILD_DEPENDS"

S = "${WORKDIR}/rpi-u-boot-${PV}"

MMC_DEV_NUM:raspberrypi3bplus-64 = "0"
MMC_DEV_NUM:raspberrypi4b-64 = "1"

do_prepare_build() {
    mkdir ${S}
    cp -r ${WORKDIR}/debian ${S}/

    cat << EOF > ${S}/boot.cmd
part uuid mmc ${MMC_DEV_NUM}:2 uuid
fatload mmc ${MMC_DEV_NUM} \${kernel_addr_r} Image
fatload mmc ${MMC_DEV_NUM} \${fdt_addr_r} ${DTB_FILES}
setenv bootargs dwc_otg.lpm_enable=0 earlyprintk root=PARTUUID=\${uuid} rootfstype=ext4 rootwait
booti \${kernel_addr_r} - \${fdt_addr_r}
EOF

    deb_add_changelog
}
