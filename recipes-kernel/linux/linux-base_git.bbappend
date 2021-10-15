require linux-common.inc

PV = "4.19"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI_append = " \
	file://base.config \
"

CVE_VERSION = "${LINUX_CVE_VERSION}"
