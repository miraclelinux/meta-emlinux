#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

IMAGE_INSTALL:append = "${@bb.utils.contains('IMAGE_PREINSTALL', 'openssh-server', ' sshd-regen-keys', '', d)}"
