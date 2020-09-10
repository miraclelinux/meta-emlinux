FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI += "file://0001-tests-skip-ul-command-test.patch \
            file://0001-tests-check-kernel-btrfs-support.patch \
            file://0001-tests-check-kernel-raid-support.patch \
            file://0001-tests-fix-test-failed-on-busybox-environment.patch \
            file://run-ptest"
