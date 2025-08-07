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
# CVE-2007-2764: It's false positive due to a SunOS issue.
# CVE-2007-4998: It's false positive due to a coreutils issue.
# CVE-2008-2544: It's false positive because the replication way is not proper.
# CVE-2016-3699: It's false positive because it's not a mainline flaw.
# CVE-1999-0524: This issue is that ICMP exists, can be filewalled if required.
# CVE-2023-1076: It's false positive because 4.19.y is not affected.
# CVE-2015-7312: It's false positive because aufs is not merged into mainline.
# CVE-1999-0656: This issue is that specific to ugidd, part of the old user-mode NFS server.
# CVE-2006-2932: Specific to RHEL. 4.19.y is not affected.
# CVE-2023-1476: Specific to RHEL. 4.19.y is not affected.
# CVE-2023-6915: This is false positive because 4.19.y is not affected.
# CVE-2023-1611: This is false positive because 4.19.y is not affected.
# CVE-2024-26594: This is false positive because 4.19.y is not affected.
# CVE-2021-0399: This is false positive because it is Android kernel issue.
# CVE-2021-1076: This is false positive because it is NVIDIA driver issue.
# CVE-2021-29256: This is false positive because it is ARM Mali driver issue.
# CVE-2021-3492: This is false positive becuase it is Ubuntu specified kernel issue.
# CVE-2021-39802: This is false positive because it is Android kernel issue.
# CVE-2022-36397: This is false positive because it is Intel QAT driver issue.
# CVE-2021-39801: This is false positive because it is Android kernel issue.
# CVE-2023-20928: Vulnerable code not present.
# CVE-2020-0347: Due to the limited information, it is unclear whether this issue is specific to Android or also related to the mainline.
# CVE-2024-35948: This issue was introduced in 6.7-rc1. 4.19.y is not affected.
# CVE-2022-48789: This is false positive because 4.19.y is not affected.
# CVE-2024-21823: This is false positive because 4.19.y is not affected.
# CVE-2020-26140: This is false positive because Linux Kernel is not affected.
# CVE-2020-26142: This is false positive because Linux Kernel is not affected.
# CVE-2020-26143: This is false positive because Linux Kernel is not affected.
# CVE-2020-26144: This is false positive because it is Samsung Galaxy specific and Mainline Kernel is not affected.
# CVE-2020-26146: This is false positive because it is Samsung Galaxy specific and Mainline Kernel is not affected.
# CVE-2021-0961: This is false positive because it is Android Kernel specific.
# CVE-2021-33096: This is false positive because Linux Kernel is not affected.
# CVE-2021-39800: This is false positive because 4.19.y is not affected.
# CVE-2024-46705: Vulnerable code not present.
# CVE-2024-50242: Vulnerable code not present.
# CVE-2024-50246: Vulnerable code not present.
# CVE-2022-48950: Vulnerable code not present.
# CVE-2023-52511: Vulnerable code not present.
# CVE-2024-26648: Vulnerable code not present.
# CVE-2024-50003: Vulnerable code not present.
# CVE-2024-26768: Vulnerable code not present.
# CVE-2024-35866: Vulnerable code not present.
# CVE-2024-50108: Vulnerable code not present.
# CVE-2024-26647: Vulnerable code not present.
# CVE-2024-26944: Vulnerable code not present.
# CVE-2024-49939: Vulnerable code not present.
# CVE-2024-50090: Vulnerable code not present.
# CVE-2024-50091: Vulnerable code not present.
# CVE-2024-50111: Vulnerable code not present.
# CVE-2024-50244: Vulnerable code not present.
# CVE-2023-39176: This is false positive because vulnerable code not present.
# CVE-2023-39180: This is false positive because vulnerable code not present.
# CVE-2022-48766: Vulnerable code not present.
# CVE-2024-26865: Vulnerable code not present.
# CVE-2024-50177: Vulnerable code not present.
# CVE-2024-50285: Vulnerable code not present.
# CVE-2024-53084: Vulnerable code not present.
# CVE-2023-52506: Vulnerable code not present.
# CVE-2023-52640: Vulnerable code not present.
# CVE-2024-26699: Vulnerable code not present.
# CVE-2024-35784: Vulnerable code not present.
# CVE-2024-58087: Vulnerable code not present.
# CVE-2023-52589: Vulnerable code not present.
# CVE-2024-26691: Vulnerable code not present.
# CVE-2025-22040: Vulnerable code not present.
# CVE-2025-22041: Vulnerable code not present.
# CVE-2025-22038: Vulnerable code not present.
# CVE-2025-22037: Vulnerable code not present.
# CVE-2024-27297: Vulnerable code not present.
# CVE-2025-37805: Vulnerable code not present.
# CVE-2019-14899: This is not a kernel issue.
# CVE-2023-32256: Vulnerable code not present.
CVE_CHECK_WHITELIST = "\
    CVE-2021-26934 CVE-2021-43057 CVE-2022-29582 \
    CVE-2021-42327 CVE-2021-45402 CVE-2022-0168 \
    CVE-2022-1508 CVE-2022-1789 CVE-2023-1872 \
    CVE-2015-8955 CVE-2022-2327 CVE-2020-8834 \
    CVE-2017-6264 CVE-2017-1000377 CVE-2007-2764 \
    CVE-2007-4998 CVE-2008-2544 CVE-2016-3699 \
    CVE-1999-0524 CVE-2023-1076 CVE-2015-7312 \
    CVE-1999-0656 CVE-2006-2932 CVE-2023-1476 \
    CVE-2023-6915 CVE-2023-1611 CVE-2024-26594 \
    CVE-2021-0399 CVE-2021-1076 CVE-2021-29256 \
    CVE-2021-3492 CVE-2021-39802 CVE-2022-36397 \
    CVE-2021-39801 CVE-2023-20928 CVE-2020-0347 \
    CVE-2024-35948 CVE-2022-48789 CVE-2024-21823 \
    CVE-2020-26140 CVE-2020-26142 CVE-2020-26143 \
    CVE-2020-26144 CVE-2020-26146 CVE-2021-0961 \
    CVE-2021-33096 CVE-2021-39800 CVE-2024-46705 \
    CVE-2024-50242 CVE-2024-50246 CVE-2022-48950 \
    CVE-2023-52511 CVE-2024-26648 CVE-2024-50003 \
    CVE-2024-26768 CVE-2024-35866 CVE-2024-50108 \
    CVE-2024-26647 CVE-2024-26944 CVE-2024-49939 \
    CVE-2024-50090 CVE-2024-50091 CVE-2024-50111 \
    CVE-2024-50244 CVE-2023-39176 CVE-2023-39180 \
    CVE-2022-48766 CVE-2024-26865 CVE-2024-50177 \
    CVE-2024-50285 CVE-2024-53084 CVE-2023-52506 \
    CVE-2023-52640 CVE-2024-26699 CVE-2024-35784 \
    CVE-2024-58087 CVE-2023-52589 CVE-2024-26691 \
    CVE-2025-22040 CVE-2025-22041 CVE-2025-22038 \
    CVE-2025-22037 CVE-2024-27297 CVE-2025-37805 \
    CVE-2019-14899 CVE-2023-32256 \
"
