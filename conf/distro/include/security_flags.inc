# 
# Copyright (C) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#
# Following settings are based on 
#    https://git.yoctoproject.org/poky/tree/meta/conf/distro/include/security_flags.inc?h=langdale
#    https://git.yoctoproject.org/poky/tree/meta/conf/bitbake.conf?h=langdale

SELECTED_OPTIMIZATION ?= "-O2"

# _FORTIFY_SOURCE requires -O1 or higher, so disable in debug builds as they use
# -O0 which then results in a compiler warning.
OPTLEVEL = "${@bb.utils.filter('SELECTED_OPTIMIZATION', '-O0 -O1 -O2 -O3 -Ofast -Og -Os -Oz -O', d)}"

lcl_maybe_fortify ?= "${@oe.utils.conditional('OPTLEVEL','-O0','','${OPTLEVEL} -D_FORTIFY_SOURCE=2',d)}"

# Error on use of format strings that represent possible security problems
SECURITY_STRINGFORMAT ?= "-Wformat -Wformat-security -Werror=format-security"

SECURITY_STACK_PROTECTOR ?= "-fstack-protector-strong"
SECURITY_CFLAGS ?= "${SECURITY_STACK_PROTECTOR} ${lcl_maybe_fortify} ${SECURITY_STRINGFORMAT}"

DEBUG_BUILD ?= "1"

CFLAGS ?= "-pipe"
CXXFLAGS ?= "-pipe"

CFLAGS += "${@oe.utils.conditional('DEBUG_BUILD','1',' -g -feliminate-unused-debug-types','',d)}"
CXXFLAGS += "${@oe.utils.conditional('DEBUG_BUILD','1',' -g -feliminate-unused-debug-types','',d)}"

TARGET_CFLAGS = "${SELECTED_OPTIMIZATION} ${CFLAGS}"
TARGET_CXXFLAGS = "${SELECTED_OPTIMIZATION} ${CFLAGS}"

TUNE_CCARGS ?= ""
TARGET_CC_ARCH = "${TUNE_CCARGS} ${SECURITY_CFLAGS}"

TARGET_LINK_HASH_STYLE ?= "${@['-Wl,--hash-style=gnu',''][d.getVar('LINKER_HASH_STYLE') != 'gnu']}"
ASNEEDED ?= "-Wl,--as-needed"
SECURITY_LDFLAGS ?= "-Wl,-z,relro,-z,now"
TARGET_LDFLAGS = "-Wl,-O1 ${TARGET_LINK_HASH_STYLE} ${ASNEEDED} ${SECURITY_LDFLAGS}"

TARGET_AS_ARCH ?= ""
TARGET_LD_ARCH ?= ""

