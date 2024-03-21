# 
# Raspberry Pi boot files
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# Authors:
#  Masami Ichikawa <masami.ichikawa@miraclelinux.com>
#
# SPDX-License-Identifier: MIT
#

DESCRIPTION = "Raspberry Pi boot files"
MAINTAINER = "Masami Ichikawa <masami.ichikawa@miraclelinux.com>"
COMPATIBLE_MACHINE="raspberrypi"

inherit dpkg-raw

RPI_FIRMWARE_VERSION = "1.20230405"
PV="${RPI_FIRMWARE_VERSION}"

# copyright file was imported from raspberrypi-bootloader_1%3a1.20230405-1_arm64.deb
SRC_URI = " \
  https://github.com/raspberrypi/firmware/archive/refs/tags/${RPI_FIRMWARE_VERSION}.zip \
  file://copyright \
"
SRC_URI[sha256sum] = "1e923f605b5be8c999dd4bdbe0b4e60d637a4d2dceff0c9a9fd3be314836d375"
 
UPSTREAM_FILE_UNPACK_DIR="${WORKDIR}/firmware-${RPI_FIRMWARE_VERSION}"

do_install() {
  cp -a ${UPSTREAM_FILE_UNPACK_DIR}/boot ${D}/
  install -d -m 0755 ${D}/usr/share/doc/${PN}/ 
  install -m 0644 ${WORKDIR}/copyright ${D}/usr/share/doc/${PN}/
}

# Keep a lower compatiblity level because file format recognition by dh_strip
# during the dpkg build task has been added since v11 then it fails when
# examining a particular bootloader file.
DEBIAN_COMPAT = "10"
