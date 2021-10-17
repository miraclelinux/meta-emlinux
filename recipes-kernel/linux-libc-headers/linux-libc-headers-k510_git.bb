require recipes-kernel/linux-libc-headers/linux-libc-headers-base_git.bb

# Use linux kernel major and minor version instead of git revision.
PV = "5.10"

LIC_FILES_CHKSUM = "file://COPYING;md5=6bc538ed5bd9a7fc9398086aedcd7e46"

DEPENDS += " rsync-native"

#
# For 5.10/arm, "asm/kvm.h" has been removed in the following kernel commit:
#     541ad0150ca4 [arm: Remove 32bit KVM host support]
#
# NOTE:
# It's the dirty hack that "_remove" a string for the function (it simply
# removes the matching string in the function), but it works and is simpler
# than rewriting do_install_armmultilib(). So we only adopt this method here.
# The oe-core upstream resolved this issue in other method:
#     4c3750bbc9da [libc-headers: update to v5.8]
#
do_install_armmultilib_remove_arm = "asm/kvm.h"
