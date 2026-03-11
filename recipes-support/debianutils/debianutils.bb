#
# Copyright (c) Cybertrust Japan Co., Ltd. 
#
# SPDX-License-Identifier: MIT
#

inherit dpkg

MAINTAINER = "Masami Ichikawa <masami.ichikawa@miraclelinux.com>"

FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI = "\
  apt://${PN} \
  file://debian/patches/savelog_do_not_use_reference_option.patch \
  file://debian/patches/do_not_use_reference_option_when_update_shell.patch \
  file://debian/patches/do_no_use_Z_option.patch \
"

DEB_BUILD_PROFILES += "nocheck"

do_dpkg_source:prepend() {
    cp -r ${WORKDIR}/debian ${S}
    echo "savelog_do_not_use_reference_option.patch" >> ${S}/debian/patches/series
    echo "do_not_use_reference_option_when_update_shell.patch" >> ${S}/debian/patches/series
    echo "do_no_use_Z_option.patch" >> ${S}/debian/patches/series
   
    # patch file was installed into the ${S}/patches which directory is not needed.
    rm -fr ${S}/patches
}
