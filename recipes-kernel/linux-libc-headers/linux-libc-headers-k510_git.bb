require recipes-kernel/linux-libc-headers/linux-libc-headers-base_git.bb

# Use linux kernel major and minor version instead of git revision.
PV = "5.10"

LIC_FILES_CHKSUM = "file://COPYING;md5=6bc538ed5bd9a7fc9398086aedcd7e46"

DEPENDS += " rsync-native"
