#
# EMLinux initramfs base image
#
# Copyright Cybertrust Japan Co., Ltd.
#
# Authors:
#  Hirotaka Motai <hirotaka.motai@miraclelinux.com>
#
# SPDX-License-Identifier: MIT
#
# The image will be deployed to:
#   build/tmp/deploy/images/${MACHINE}/emlinux-initramfs-base-${DISTRO}-${MACHINE}-initrd.img
#

inherit initramfs

# Debian packages that should be install into the system for building the
# initramfs.
INITRAMFS_PREINSTALL += " \
	dmsetup \
	systemd \
"

# Recipes that should be install into the initramfs build rootfs.
INITRAMFS_INSTALL += " \
"
