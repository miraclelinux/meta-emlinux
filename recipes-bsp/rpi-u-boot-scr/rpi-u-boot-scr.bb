# base recipe: meta-raspberrypi/recipes-bsp/rpi-u-boot-scr/rpi-u-boot-scr.bb            
# base branch: master 
# base commit: 68976061c5c130ce68430a59c23afb8044975d41

SUMMARY = "U-boot boot scripts for Raspberry Pi"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"
COMPATIBLE_MACHINE = "^rpi$"

DEPENDS = "u-boot-mkimage-native"

INHIBIT_DEFAULT_DEPS = "1"

PR = "r1"

SRC_URI = "file://boot.cmd \ 
           file://config.txt \
"

do_compile() {
    mkimage -A arm64 -T script -C none -n "Boot script" -d "${WORKDIR}/boot.cmd" boot.scr
}

inherit deploy nopackages

do_deploy() {
    cp ${WORKDIR}/config.txt ${DEPLOYDIR}
    install -d ${DEPLOYDIR}
    install -m 0644 boot.scr ${DEPLOYDIR}
}

addtask do_deploy after do_compile before do_build
