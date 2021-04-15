FILESEXTRAPATHS_prepend := "${THISDIR}/qemu:"

SRC_URI += " \
	file://0014-linux-user-fix-to-handle-variably-sized-SIOCGSTAMP-w-custom.patch \
"
