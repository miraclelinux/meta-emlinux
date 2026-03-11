#
# Copyright (c) Cybertrust Japan Co., Ltd. 
#
# SPDX-License-Identifier: MIT
#

# This recipe replaces bootclean.sh with one that works with busybox commands.
# It replaced find command option in the clean_tmp() to use -user option instead of -uid option.

inherit dpkg

FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

MAINTAINER = "Masami Ichikawa <masami.ichikawa@miraclelinux.com>"

SRC_URI = " \
apt://${PN} \
file://custom-debian \
"

DEB_BUILD_PROFILES += "nocheck"

PROVIDES += " \
  sysvinit-core \
  sysv-rc \
  sysvinit-utils \
  bootlogd \
  busybox-syslogd \
"

do_move_debian_files() {
    cp -r ${WORKDIR}/custom-debian/* ${S}/debian/
}
addtask move_debian_files after do_prepare_build before do_dpkg_build
