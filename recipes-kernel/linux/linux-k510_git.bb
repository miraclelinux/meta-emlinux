require linux-common.inc
require recipes-kernel/linux/linux-base_git.bb

PV = "5.10"

PROVIDES += " linux-k510"
LIC_FILES_CHKSUM = "file://COPYING;md5=6bc538ed5bd9a7fc9398086aedcd7e46"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

FILESEXTRAPATHS_append := ":${LAYERDIR_DEBIAN_debian}/recipes-kernel/linux/files/"

KERNEL_CONFIG_COMMAND = "oe_runmake_call O=${B} -C ${S} olddefconfig"

CVE_VERSION = "${LINUX_CVE_VERSION}"

addtask shared_workdir_modules after do_compile_kernelmodules before do_sizecheck

do_shared_workdir_modules () {
        cd ${B}
        kerneldir=${STAGING_KERNEL_BUILDDIR}

        install -d $kerneldir/scripts 
        [ -e scripts/module.lds ] && cp scripts/module.lds $kerneldir/scripts
}

do_shared_workdir_prepend () {
        cd ${B}
        touch Module.symvers
}

# CVE-2021-43057: This issue was introduced in 5.13-rc1. 5.10.y is not affected.
# CVE-2015-8955: It's false positive because it was fixed in v4.1-rc1.
# CVE-2020-8834: It's false positive because 5.10.y is not affected.
# CVE-2017-6264: It's false positive because it's not a mainline flaw.
# CVE-2017-1000377: It's false positive because it's not a mainline flaw.
CVE_CHECK_WHITELIST = "\
    CVE-2021-43057 CVE-2015-8955 CVE-2020-8834 \
    CVE-2017-6264 CVE-2017-1000377 \
"
