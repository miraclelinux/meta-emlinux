#
# EMLinux kernel recipe
#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

inherit linux-kernel

MAINTAINER = "EMLinux development team <emlinux-dev@emlinux-host>"

SRC_URI += " \
    git://git.kernel.org/pub/scm/linux/kernel/git/cip/linux-cip.git;branch=${BRANCH};destsuffix=${P};protocol=https \
"

SRC_URI[sha256sum] = "1caa1b8e24bcfdd55c3cffd8f147f3d33282312989d85c82fc1bc39b808f3d6b"

KBUILD_DEPENDS:append = ", zstd"

LIBSSL_DEP:armhf:trixie = "libssl3t64"

EMLINUX_SOURCE_FROM="non-debian"
