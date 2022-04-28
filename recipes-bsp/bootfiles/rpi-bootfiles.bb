# base recipe: meta-raspberrypi/recipes-bsp/bootfiles/rpi-bootfiles.bb
# base branch: master
# base commit: 68976061c5c130ce68430a59c23afb8044975d41

DESCRIPTION = "Closed source binary files to help boot the ARM on the BCM2835."
LICENSE = "Proprietary"

LIC_FILES_CHKSUM = "file://boot/LICENCE.broadcom;md5=4a4d169737c0786fb9482bb6d30401d1"

inherit deploy nopackages

include recipes-bsp/common/raspberrypi-firmware.inc

INHIBIT_DEFAULT_DEPS = "1"

COMPATIBLE_MACHINE = "^rpi$"

PR = "r1"

S = "${WORKDIR}/firmware-${SRCREV}"

do_deploy() {
    install -d ${DEPLOYDIR}/${PN}

    for i in ${S}/boot/start* ; do
        cp $i ${DEPLOYDIR}/${PN}
    done
    for i in ${S}/boot/fixup* ; do
        cp $i ${DEPLOYDIR}/${PN}
    done
    cp -r ${S}/boot/overlays ${DEPLOYDIR}/${PN}
    cp ${S}/boot/bootcode.bin ${DEPLOYDIR}/${PN}

    # Add stamp in deploy directory
    touch ${DEPLOYDIR}/${PN}/${PN}-${PV}.stamp
}

addtask deploy before do_build after do_install
do_deploy[dirs] += "${DEPLOYDIR}/${PN}"

PACKAGE_ARCH = "${MACHINE_ARCH}"
