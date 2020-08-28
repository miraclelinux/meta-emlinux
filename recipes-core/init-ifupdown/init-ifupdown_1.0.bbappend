# interfaces file is based on commit 733ae41f20983a7e6f1c147188aa6b4db951d05b.
FILESEXTRAPATHS_append := "${THISDIR}/${PN}-${PV}"

SRC_URI += "file://wait-iface.sh"

do_install_append_raspberrypi3-64() {
    install -m 0755 ${WORKDIR}/wait-iface.sh ${D}${sysconfdir}/network/if-up.d/wait-iface.sh
}
