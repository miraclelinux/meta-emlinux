#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

python() {
    if bb.utils.contains('IMAGE_INSTALL', 'sshd-regen-keys', True, False, d):
        return
    if bb.utils.contains('IMAGE_PREINSTALL', 'openssh-server', True, False, d) or \
       bb.utils.contains('IMAGE_INSTALL', 'openssh-server', True, False, d):
        d.appendVar('IMAGE_INSTALL', ' sshd-regen-keys')
}
