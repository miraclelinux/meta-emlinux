#
# EMLinux kernel recipe
#
# Copyright (c) Cybertrust Japan Co., Ltd. 
#
# Authors:
#  Masami Ichikawa <masami.ichikawa@miraclelinux.com>
#
# SPDX-License-Identifier: MIT
#
FILESEXTRAPATHS_prepend := "${FILE_DIRNAME}/files:"

require recipes-kernel/linux/linux-custom.inc

SRC_URI += " \
    https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-${PV}.tar.gz \
    file://${MACHINE}_defconfig \
"

KERNEL_DEFCONFIG = "${MACHINE}_defconfig"
SRC_URI[sha256sum] = "003176045aaddb245e5b64cd88c34846b8265f1197ca14baa43c91c9ec7d5e23"

S = "${WORKDIR}/linux-${PV}"
