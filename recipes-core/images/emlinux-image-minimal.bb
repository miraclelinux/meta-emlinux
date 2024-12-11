#
# EMLinux minimal rootfs image
#
# Copyright (c) Cybertrust Japan Co., Ltd. 
#
# SPDX-License-Identifier: MIT
#

FILESEXTRAPATHS:prepend := "${FILE_DIRNAME}/files/minimal:"

SRC_URI = "\
    file://minimal-image-replace-basic-list.yml \
"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${LAYERDIR_core}/licenses/COPYING.MIT;md5=838c366f69b72c5df05c96dff79b35f2"

PV = "1.0"

ISAR_RELEASE_CMD = "git -C ${LAYERDIR_emlinux} describe --tags --dirty --always --match 'v[0-9].[0-9]*'"

IMAGE_INSTALL:append = " emlinux-customization"

# Remove kernel, initramfs, and etc in /boot
EMLINUX_IMAGE_MINIMAL_REMOVE_BOOT_DIR ??= "0"

# Remove man pages
EMLINUX_IMAGE_MINIMAL_REMOVE_MAN ??= "0"

# Remove perl packages
EMLINUX_IMAGE_MINIMAL_REMOVE_PERL ??= "0"

# Remove dtb files in /usr/lib/linux-image-<linux version>
EMLINUX_IMAGE_MINIMAL_REMOVE_DTB ??= "0"

# It is needed to build and install essential packages
ROOTFS_APT_ARGS:append = " --allow-downgrades"

EMLINUX_SYSVINIT_INSTALL_PACKAGE = "\
  sysvinit-core \
  sysv-rc \
  sysvinit-utils \
  bootlogd \
  busybox-syslogd \
"

IMAGE_INSTALL:append = "\
  ${EMLINUX_SYSVINIT_INSTALL_PACKAGE} \
"

IMAGE_INSTALL:append = "\
  busybox \
  debianutils \
"

inherit image emlinux-minimal

DEPENDS:class-sdk:append = " ${IMAGE_INSTALL}"

EMLINUX_MINIMAL_IMAGE_REMOVE_LIBSTDCPLUSPLUS ?= " libstdc++6"
EMLINUX_MINIMAL_IMAGE_REMOVE_COREUTILS ?= " \
coreutils \
initramfs-tools-core \
initramfs-tools \
klibc-utils \
libklibc \
"

EMLINUX_MINIMAL_IMAGE_REMOVE_PERL ?= " \
perl-modules-5.36 \
libperl5.36 perl \
perl-base \
libnumber-compare-perl \
libtext-glob-perl \
"

EMLINUX_MINIMAL_IMAGE_REMOVE_SHELLS ?= " bash"
EMLINUX_MINIMAL_IMAGE_REMOVE_UTILS ?= " \
pinentry-curses \
mawk \
cpio \
diffutils \
grep \
gzip \
findutils \
hostname \
sed \
tar \
usr-is-merged \
"

EMLINUX_MINIMAL_IMAGE_REMOVE_APT ?= " \
apt \
libapt-pkg6.0 \
debian-archive-keyring \
"

EMLINUX_MINIMAL_IMAGE_REMOVE_LOCALE ?= " locales"

EMLINUX_MINIMAL_IMAGE_REMOVE_UTIL_LINUX ?= " \
util-linux \
util-linux-extra \
libsmartcols1 \
libuuid1 \
"

EMLINUX_MINIMAL_IMAGE_REMOVE_MOUNT ?= " mount libmount1"

EMLINUX_MINIMAL_IMAGE_REMOVE_BSDUTILS ?= " bsdutils"

EMLINUX_MINIMAL_IMAGE_REMOVE_SELINUX ?= " \
libsemanage2 \
libsemanage-common \
libsepol2 \
"

EMLINUX_MINIMAL_IMAGE_REMOVE_GNUPG ?= " \
gpgv \
dirmngr \
gnupg-l10n \
gnupg-utils \
gpg-wks-server \
gpgconf \
gpgsm \
gnupg \
gpg \
gpg-agent \
gpg-wks-client \
libassuan0 \
"

EMLINUX_MINIMAL_IMAGE_REMOVE_AUTH_UTILS ?= " \
login \
passwd \
adduser \
"

EMLINUX_MINIMAL_IMAGE_REMOVE_FILE_SYSTEM_UTILS ?= " \
e2fsprogs \
"

EMLINUX_MINIMAL_IMAGE_REMOVE_PROCESS_UTILS ?= " \
procps \
"

EMLINUX_MINIMAL_IMAGE_REMOVE_LIBGPG_ERROR ?= " \
libgpg-error0 \
"

EMLINUX_MINIMAL_IMAGE_REMOVE_GNUTLS ?= " \
libgnutls30 \
libidn2-0 \
libunistring2 \
"

EMLINUX_MINIMAL_IMAGE_REMOVE_SQLITE3 ?= " libsqlite3-0"
EMLINUX_MINIMAL_IMAGE_REMOVE_LIBLDAP ?= " \
libldap-2.5-0 \
libsasl2-2 \
libsasl2-modules-db \
"

EMLINUX_MINIMAL_IMAGE_REMOVE_LIBXXHASH ?= " libxxhash0"

EMLINUX_MINIMAL_IMAGE_REMOVE_PAM ?= " \
libpam-modules \
libpam-modules-bin \
libpam-runtime \
libpam0g \
"

EMLINUX_MINIMAL_IMAGE_REMOVE_LIBNTPH ?= " libnpth0"

EMLINUX_MINIMAL_IMAGE_REMOVE_NCURSES ?= " \
ncurses-base \
ncurses-bin \
libncursesw6 \
"

EMLINUX_MINIMAL_IMAGE_REMOVE_READLINE ?= " \
readline-common \
libreadline8 \
"

EMLINUX_MINIMAL_IMAGE_REMOVE_SENSIBLE_UTIL ?= " sensible-utils"

EMLINUX_MINIMAL_IMAGE_REMOVE_LSB ?= " lsb-base"

EMLINUX_MINIMAL_IMAGE_REMOVE_PAKCAGES ?= " \
${EMLINUX_MINIMAL_IMAGE_REMOVE_COREUTILS} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_SHELLS} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_UTILS} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_APT} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_AUTH_UTILS} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_GNUPG} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_FILE_SYSTEM_UTILS} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_PROCESS_UTILS} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_LIBGPG_ERROR} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_UTIL_LINUX} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_BSDUTILS} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_MOUNT} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_GNUTLS} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_SELINUX} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_SQLITE3} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_LIBLDAP} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_LIBSTDCPLUSPLUS} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_LIBXXHASH} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_PAM} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_LIBNTPH} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_LOCALE} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_NCURSES} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_READLINE} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_SENSIBLE_UTIL} \
${EMLINUX_MINIMAL_IMAGE_REMOVE_LSB} \
"
