require linux-common.inc
require recipes-kernel/linux/linux-base_git.bb

PV = "5.10"

PROVIDES += " linux-k510"
LIC_FILES_CHKSUM = "file://COPYING;md5=6bc538ed5bd9a7fc9398086aedcd7e46"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI_append = " \
	file://base.config \
"

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
