require linux-common.inc

PV = "4.19"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

CVE_VERSION = "${LINUX_CVE_VERSION}"

# CVE-2021-26934: It's Xen document problem. Not a kernel bug. http://xenbits.xen.org/xsa/advisory-363.html
# CVE-2021-43057: This issue was introduced in 5.13-rc1. 4.19.y is not affected.
# CVE-2022-29582: This is io_uring issue. linux 4.19 doesn't have this feature.
# CVE-2021-42327: This issue was introduced in 5.10-rc1. 4.19.y is not affected.
# CVE-2021-45402: This issue was introduced in 5.7. 4.19.y is not affected.
# CVE-2022-0168: This issue was introduced in 4.20-rc1. 4.19.y is not affected.
# CVE-2022-1508: This is io_uring issue. linux 4.19 doesn't have this feature.
# CVE-2022-1789: This issue was introduced in 5.8-rc1. 4.19.y is not affected.
# CVE-2023-1872: This is io_uring issue. linux 4.19 doesn't have this feature.
# CVE-2015-8955: It's false positive because it was fixed in v4.1-rc1.
# CVE-2022-2327: It's false positive because 4.19.y is not affected.
# CVE-2020-8834: It's false positive because 4.19.y is not affected.
# CVE-2017-6264: It's false positive because it's not a mainline flaw.
# CVE-2017-1000377: It's false positive because it's not a mainline flaw.
CVE_CHECK_WHITELIST = "\
    CVE-2021-26934 CVE-2021-43057 CVE-2022-29582 \
    CVE-2021-42327 CVE-2021-45402 CVE-2022-0168 \
    CVE-2022-1508 CVE-2022-1789 CVE-2023-1872 \
    CVE-2015-8955 CVE-2022-2327 CVE-2020-8834 \
    CVE-2017-6264 CVE-2017-1000377 \
"
