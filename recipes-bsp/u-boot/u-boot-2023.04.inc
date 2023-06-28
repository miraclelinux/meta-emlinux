#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

require recipes-bsp/u-boot/u-boot-custom.inc

SRC_URI += " \
    https://ftp.denx.de/pub/u-boot/u-boot-${PV}.tar.bz2"

SRC_URI[sha256sum] = "e31cac91545ff41b71cec5d8c22afd695645cd6e2a442ccdacacd60534069341"

DEBIAN_BUILD_DEPENDS .= ",\
    libssl-dev, \
    libssl-dev:native"

S = "${WORKDIR}/u-boot-${PV}"
