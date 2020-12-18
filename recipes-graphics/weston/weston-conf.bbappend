DEFAULTBACKEND ??= ""
DEFAULTBACKEND_qemuall ?= "fbdev"
DEFAULTBACKEND_raspberrypi3-64 ?= "fbdev"
DEFAULTBACKEND_beaglebone ?= "fbdev"

do_install() {
        if [ -n "${DEFAULTBACKEND}" ]; then
                mkdir -p ${D}/${sysconfdir}/xdg/weston
                cat << EOF > ${D}/${sysconfdir}/xdg/weston/weston.ini
[core]
backend=${DEFAULTBACKEND}-backend.so
EOF
        fi
}
