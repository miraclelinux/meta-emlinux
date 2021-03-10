# base recipe: meta-raspberrypi/recipes-kernel/linux-firmware-rpidistro/linux-firmware-rpidistro_git.bb
# base branch: master 
# base commit: 68976061c5c130ce68430a59c23afb8044975d41

SUMMARY = "Linux kernel firmware files from Raspbian distribution"
DESCRIPTION = "Updated firmware files for RaspberryPi hardware. \
RPi-Distro obtains these directly from Cypress; they are not submitted \
to linux-firmware for general use."
HOMEPAGE = "https://github.com/RPi-Distro/firmware-nonfree"
SECTION = "kernel"

# In maintained upstream linux-firmware:
# * brcmfmac43430-sdio falls under LICENCE.cypress
# * brcmfmac43455-sdio falls under LICENCE.broadcom_bcm43xx
# * brcmfmac43456-sdio falls under LICENCE.broadcom_bcm43xx
#
# It is likely[^1] that both of these should be under LICENCE.cypress.
# Further, at this time the text of LICENCE.broadcom_bcm43xx is the same
# in linux-firmware and RPi-Distro/firmware-nonfree, but this may
# change.
#
# Rather than make assumptions about what's supposed to be what, we'll
# use the license implied by the source of these files, named to avoid
# conflicts with linux-firmware.
#
# [^1]: https://github.com/RPi-Distro/bluez-firmware/issues/1
LICENSE = "\
    Firmware-broadcom_bcm43xx-rpidistro \
    & WHENCE \
"
LIC_FILES_CHKSUM = "\
    file://LICENCE.broadcom_bcm43xx;md5=3160c14df7228891b868060e1951dfbc \
    file://WHENCE;md5=7b12b2224438186e4c97c4c7f3a5cc28 \
"

# These are not common licenses, set NO_GENERIC_LICENSE for them
# so that the license files will be copied from fetched source
NO_GENERIC_LICENSE[Firmware-broadcom_bcm43xx-rpidistro] = "LICENCE.broadcom_bcm43xx"
NO_GENERIC_LICENSE[WHENCE] = "WHENCE"

SRC_URI = "git://github.com/RPi-Distro/firmware-nonfree"

SRCREV = "b66ab26cebff689d0d3257f56912b9bb03c20567"
PV = "20190114-1+rpt10"

S = "${WORKDIR}/git"

inherit allarch

CLEANBROKEN = "1"

do_compile() {
    :
}

do_install() {
    install -d ${D}${nonarch_base_libdir}/firmware

    cp ./LICENCE.broadcom_bcm43xx ${D}${nonarch_base_libdir}/firmware/LICENCE.broadcom_bcm43xx-rpidistro
}


LICENSE_${PN}-bcm43430 = "Firmware-broadcom_bcm43xx-rpidistro"
LICENSE_${PN}-bcm43455 = "Firmware-broadcom_bcm43xx-rpidistro"
LICENSE_${PN}-bcm43456 = "Firmware-broadcom_bcm43xx-rpidistro"
LICENSE_${PN}-broadcom-license = "Firmware-broadcom_bcm43xx-rpidistro"
FILES_${PN}-broadcom-license = "${nonarch_base_libdir}/firmware/LICENCE.broadcom_bcm43xx-rpidistro"

# Firmware files are generally not run on the CPU, so they can be
# allarch despite being architecture specific
INSANE_SKIP = "arch"
