FILESEXTRAPATHS_prepend := "${THISDIR}/qemu:"

SRC_URI += " \
	file://0001-Apply-patch-0001-linux-user-assume-__NR_gettid-alway.patch \
	file://0002-Apply-patch-0001-linux-user-rename-gettid-to-sys_get.patch \
	file://0003-Apply-patch-0011-linux-user-remove-host-stime-sysca.patch \
	file://0014-linux-user-fix-to-handle-variably-sized-SIOCGSTAMP-w-custom.patch \
"
