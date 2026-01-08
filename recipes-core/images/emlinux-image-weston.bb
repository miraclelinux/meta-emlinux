#
# EMLinux image to enable Weston
#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

require recipes-core/images/emlinux-image-base.bb

DESCRIPTION = "EMLinux target filesystem to enable Weston"

IMAGE_INSTALL:append = " weston-init"

IMAGE_PREINSTALL:append = " weston libgl1 libpam-systemd kbd"
IMAGE_PREINSTALL:append:trixie = " seatd"

GROUPS += "weston-launch"
GROUP_weston-launch[flags] = "system"
GROUPS += "wayland"
GROUP_wayland[flags] = "system"

USERS += "weston"
USER_weston[groups] = "video input render wayland"
USER_weston[home] = "/home/weston"
USER_weston[flags] = "create-home"

# Remove unnecessary account setting in the SDK generation
ROOTFS_POSTPROCESS_COMMAND:remove:class-sdk = "image_postprocess_accounts"
