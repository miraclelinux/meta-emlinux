#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

FILESPATH:append := ":${FILE_DIRNAME}/files"

inherit u-boot

MAINTAINER = "Kazunori Kobayashi <kazunori.kobayashi@miraclelinux.com>"

SRC_URI += " \
    https://ftp.denx.de/pub/u-boot/u-boot-${PV}.tar.bz2"

SRC_URI[sha256sum] = "e31cac91545ff41b71cec5d8c22afd695645cd6e2a442ccdacacd60534069341"

DEBIAN_BUILD_DEPENDS .= ",\
    libssl-dev, \
    libssl-dev:native"

S = "${WORKDIR}/u-boot-${PV}"

do_prepare_build() {
    cp -r ${WORKDIR}/debian ${S}/

    deb_add_changelog

    rm -f ${S}/debian/u-boot.install
    for bin in ${U_BOOT_BIN_INSTALL}; do
        echo "$bin /usr/lib/u-boot/${MACHINE}" >> \
            ${S}/debian/u-boot.install
    done

    echo "tools/env/libubootenv.a usr/lib" > \
        ${S}/debian/u-boot-dev.install

    if [ "${U_BOOT_TOOLS_PACKAGE}" = "1" ]; then
        cat <<EOF >>${S}/debian/control

Package: u-boot-tools
Architecture: linux-any
Depends: \${shlibs:Depends}, \${misc:Depends}
Description: ${DESCRIPTION}, companion tools
EOF
    fi
}
