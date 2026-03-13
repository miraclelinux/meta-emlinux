#
# Startup script and systemd unit file for the Weston Wayland compositor
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

SUMMARY = "Startup script and systemd unit file for the Weston Wayland compositor"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${LAYERDIR_core}/licenses/COPYING.MIT;md5=838c366f69b72c5df05c96dff79b35f2"
MAINTAINER = "Kazunori Kobayashi <kazunori.kobayashi@miraclelinux.com>"

inherit dpkg-raw

SRC_URI = " \
    file://weston.env \
    file://weston.ini \
    file://weston.service \
    file://weston.socket \
    file://weston-socket.sh \
    file://weston-autologin \
    file://weston-start"

do_install () {
    # Install Weston systemd service
    install -D -p -m0644 ${WORKDIR}/weston.service ${D}/lib/systemd/system/weston.service
    install -D -p -m0644 ${WORKDIR}/weston.socket ${D}/lib/systemd/system/weston.socket
    install -D -p -m0644 ${WORKDIR}/weston-socket.sh ${D}/etc/profile.d/weston-socket.sh

    install -D -p -m0644 ${WORKDIR}/weston-autologin ${D}/etc/pam.d/weston-autologin

    install -D -p -m0644 ${WORKDIR}/weston.ini ${D}/etc/xdg/weston/weston.ini
    install -Dm644 ${WORKDIR}/weston.env ${D}/etc/default/weston

    if [ ${MACHINE} = "raspberrypi3bplus-64" -o ${MACHINE} = "raspberrypi4b-64" ]; then
        sed -i -e "/use-pixman/d" ${D}/etc/xdg/weston/weston.ini
    fi
}
