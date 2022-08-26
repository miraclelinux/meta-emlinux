require linux-common.inc

PV = "4.19"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

CVE_VERSION = "${LINUX_CVE_VERSION}"

# CVE-2021-26934: It's Xen document problem. Not a kernel bug. http://xenbits.xen.org/xsa/advisory-363.html
# CVE-2021-43057: This issue was introduced in 5.13-rc1. 4.19.y is not affected.
# CVE-2022-29582: This is io_uring issue. linux 4.19 doesn't have this feature.
CVE_CHECK_WHITELIST = "CVE-2021-26934 CVE-2021-43057 CVE-2022-29582"
