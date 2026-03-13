#
# Copyright (c) Cybertrust Japan Co., Ltd. 
#
# SPDX-License-Identifier: MIT
#

inherit dpkg

MAINTAINER = "Masami Ichikawa <masami.ichikawa@miraclelinux.com>"

SRC_URI = "apt://${PN}"

DEB_BUILD_PROFILES += "nocheck"

PACKAGES += "${PN}-syslogd"

do_prepare_build() {
    # Enable -delete option for find command.
    sed -i 's/# CONFIG_FEATURE_FIND_DELETE is not set/CONFIG_FEATURE_FIND_DELETE=y/' "${S}/debian/config/pkg/deb"

    # Enable passwd command
    sed -i 's/# CONFIG_PASSWD is not set/CONFIG_PASSWD=y/' "${S}/debian/config/pkg/deb"
    sed -i 's/# CONFIG_USE_BB_CRYPT is not set/CONFIG_USE_BB_CRYPT=y/' "${S}/debian/config/pkg/deb"
    sed -i 's/# CONFIG_USE_BB_CRYPT_SHA is not set/CONFIG_USE_BB_CRYPT_SHA=y/' "${S}/debian/config/pkg/deb"

    # Enable user management commands
    sed -i 's/# CONFIG_ADDUSER is not set/CONFIG_ADDUSER=y/' "${S}/debian/config/pkg/deb"
    sed -i 's/# CONFIG_ADDGROUP is not set/CONFIG_ADDGROUP=y/' "${S}/debian/config/pkg/deb"
    sed -i 's/# CONFIG_CHPASSWD is not set/CONFIG_CHPASSWD=y/' "${S}/debian/config/pkg/deb"
    sed -i 's/# CONFIG_DELUSER is not set/CONFIG_DELUSER=y/' "${S}/debian/config/pkg/deb"
    sed -i 's/# CONFIG_DELGROUP is not set/CONFIG_DELGROUP=y/' "${S}/debian/config/pkg/deb"

    # Enable util-linux commands
    sed -i 's/# CONFIG_MOUNTPOINT is not set/CONFIG_MOUNTPOINT=y/' "${S}/debian/config/pkg/deb"
    
}
