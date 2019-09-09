# This target use default emlinux setting
# e.g. sysvinit as default init program, systemd-udev as udev component.

SUMMARY = "Smoke test target for default emlinux setting"

IMAGE_INSTALL = "packagegroup-core-boot packagegroup-smoketest ${CORE_IMAGE_EXTRA_INSTALL}"

IMAGE_FEATURES += "ssh-server-dropbear"

IMAGE_LINGUAS = " "

LICENSE = "MIT"

inherit core-image

IMAGE_ROOTFS_SIZE ?= "8192"

