require linux-common.inc

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI_append = " \
	file://base.config \
"

CVE_VERSION = "${LINUX_CVE_VERSION}"
