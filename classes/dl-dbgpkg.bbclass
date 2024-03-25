#
# This class gets debug symbol packages for SDK.
#
# Copyright (C) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

#
# [How to use]
# Add following line into the local.conf.
# INHERIT += "dl-dbgpkg"
#
# If you want to get debian patched source tree, add following line too.
# PREPARE_PATCHED_SRC = "1"
#

inherit dl-srcpkg

python sdk_virtclass_handler_for_dbgpkg() {
    pn = e.data.getVar('PN')
    if pn.endswith('-sdk'):
        e.data.setVar('BPN', pn[:-len('-sdk')])
        e.data.appendVar('OVERRIDES', ':class-sdk')
        # install_debug_symbol deploy only for sdk image
        bb.build.addtask('install_debug_symbol', 'do_image_tar', 'do_rootfs', d)
}
addhandler sdk_virtclass_handler_for_dbgpkg
sdk_virtclass_handler_for_dbgpkg[eventmask] = "bb.event.RecipePreFinalise"

#
# for self build packages
#
EML_SELF_BUILD="eml-apt"
LOCAL_APT_DIR="tmp/${EML_SELF_BUILD}/${DISTRO}-${DISTRO_ARCH}/apt/${DISTRO}"

prepare_local_isarapt() {
    # Make a local copy of isar-apt repo
    rm -rf "${ROOTFSDIR}/tmp/${EML_SELF_BUILD}/${DISTRO}-${DISTRO_ARCH}/*"
    mkdir -p "${ROOTFSDIR}/${LOCAL_APT_DIR}"
    cp -Rf "${REPO_ISAR_DIR}/${DISTRO}/dists" "${ROOTFSDIR}/${LOCAL_APT_DIR}/"
    if [ -d "${REPO_ISAR_DIR}/${DISTRO}/pool" ]; then
        cp -Rf "${REPO_ISAR_DIR}/${DISTRO}/pool" "${ROOTFSDIR}/${LOCAL_APT_DIR}/"
    fi
    # change repository name
    mv ${ROOTFSDIR}/${LOCAL_APT_DIR}/dists/${DEBDISTRONAME} ${ROOTFSDIR}/${LOCAL_APT_DIR}/dists/${EML_SELF_BUILD}
    sed -i -e "s/Codename\:\ isar/Codename\:\ ${EML_SELF_BUILD}/g" ${ROOTFSDIR}/${LOCAL_APT_DIR}/dists/${EML_SELF_BUILD}/Release
}

cleanup_local_isarapt() {
    rm -fr /tmp/${EML_SELF_BUILD}
}

DBG_SYMBOL="dbgsym-apt"

SDKTARGETROOTFSDEPS = ""
SDKTARGETROOTFSDEPS:class-sdk = "${BPN}:do_install_source_package"
do_install_debug_symbol[depends] += "${SDKTARGETROOTFSDEPS}"
do_install_debug_symbol[network] = "${TASK_USE_SUDO}"

TARGET_ROOTFS_MANIFEST="${BPN}-${DISTRO}-${MACHINE}"

DEBIAN_DBG_REPO = "http://deb.debian.org/debian-debug"

do_install_debug_symbol() {
    local not_exist_resolvconf=`file '${ROOTFSDIR}'/etc/resolv.conf 2>&1 | grep "cannot open" | wc -c`

    ### prepare directory for chroot environment
    sudo -E mount --bind /tmp ${ROOTFSDIR}/tmp
    sudo -E mount --bind /dev ${ROOTFSDIR}/dev
    sudo -E mount --bind /dev/pts ${ROOTFSDIR}/dev/pts
    sudo -E mount -t proc none ${ROOTFSDIR}/proc

    cp "${DEPLOY_DIR}/images/${MACHINE}/${TARGET_ROOTFS_MANIFEST}".manifest /tmp

    ### setup network & apt environment
    if [ ${not_exist_resolvconf} -ne 0 ]; then
        sudo cp /etc/resolv.conf ${ROOTFSDIR}/etc/resolv.conf
    else
        sudo mv ${ROOTFSDIR}/etc/resolv.conf ${ROOTFSDIR}/etc/resolv.conf.orig
        sudo cp /etc/resolv.conf ${ROOTFSDIR}/etc/resolv.conf
    fi

    ### for self-build packages
    prepare_local_isarapt
    sudo sh -c "echo 'deb [trusted=yes] copy:///${LOCAL_APT_DIR} ${EML_SELF_BUILD} main' > ${ROOTFSDIR}/etc/apt/sources.list.d/${EML_SELF_BUILD}.list"
    sudo sh -c "echo 'deb-src [trusted=yes] copy:///${LOCAL_APT_DIR} ${EML_SELF_BUILD} main' >> ${ROOTFSDIR}/etc/apt/sources.list.d/${EML_SELF_BUILD}.list"
    sudo sh -c "echo \"Package: *\nPin: release n=${EML_SELF_BUILD}\nPin-Priority: 2000\" > ${ROOTFSDIR}/etc/apt/preferences.d/${EML_SELF_BUILD}"
    sudo sh -c "echo \"APT::Get::allow-downgrades 1;\" > ${ROOTFSDIR}/etc/apt/apt.conf.d/30-${EML_SELF_BUILD}"

    ### for pre-build packages
    sudo sh -c "echo 'deb [arch=${DISTRO_ARCH}] ${DEBIAN_DBG_REPO} ${BASE_DISTRO_CODENAME}-debug main' > ${ROOTFSDIR}/etc/apt/sources.list.d/${DBG_SYMBOL}.list"
    sudo sh -c "echo 'deb [arch=${DISTRO_ARCH}] ${DEBIAN_DBG_REPO} ${BASE_DISTRO_CODENAME}-proposed-updates-debug main' >> ${ROOTFSDIR}/etc/apt/sources.list.d/${DBG_SYMBOL}.list"
    sudo sh -c "echo \"Package: *\nPin: release n=${DBG_SYMBOL}\nPin-Priority: 1000\" > ${ROOTFSDIR}/etc/apt/preferences.d/${DBG_SYMBOL}"
    sudo sh -c "echo \"APT::Get::allow-downgrades 1;\" > ${ROOTFSDIR}/etc/apt/apt.conf.d/40-${DBG_SYMBOL}"

    sudo -E chroot ${ROOTFSDIR} sh -c "rm /var/lib/dpkg/status; touch /var/lib/dpkg/status; apt-get -y -q update"

    ### download debug symbol packages
    cat << 'EOS' > /tmp/dl_dbgsym.sh
while read line
do
    tmpName=`echo ${line} | cut -d'|' -f3`
    pkgName=${tmpName%%\:${DISTRO_ARCH}}
    # echo "PKG: ${pkgName}" >> /etc/pkg-list.txt
    pkgVer=`echo ${line} | cut -d'|' -f4`
    dbgsym_pkg=`apt-cache search "^${pkgName}-dbgsym" | cut -d' ' -f1`
    if [ -z "${dbgsym_pkg}" ]; then
        dbgsym_pkg=`apt-cache search "^${pkgName}-dbg" | cut -d' ' -f1`
    fi
    if [ -n "${dbgsym_pkg}" ]; then
        _chk_ver=`apt-cache show ${dbgsym_pkg} | grep "^Version"`
	chk_ver=${_chk_ver##Version\:\ }
	if [ "${chk_ver}" = "${pkgVer}" ]; then
            apt-get install ${pkgName}=${pkgVer} -y
            apt-get install ${dbgsym_pkg}=${pkgVer} -y
	else
	    echo "[INFO]: Found debug symbol package but package version is not match. pkg: ${dbgsym_pkg} , pkgVer: ${pkgVer} , getVer:${chk_ver}"
	fi
    else
        echo "[INFO]: Can't find debug symbol package for ${pkgName}"
    fi
done < ${TARGET_ROOTFS_MANIFEST}.manifest
EOS
    sudo -E chroot ${ROOTFSDIR} sh -c "(cd /tmp && bash ./dl_dbgsym.sh)"

    ### prepare patched source
    if [ "${PREPARE_PATCHED_SRC}" = "1" ]; then
	sudo mkdir -p ${ROOTFSDIR}/usr/src/pkg_src
        cd ${DEPLOY_DIR}/sources/${MACHINE}
        for dir in *
        do
            if [ -d ${dir} ]; then
                (cd ${dir} && sudo dpkg-source --no-copy -x *.dsc ${ROOTFSDIR}/usr/src/pkg_src/${dir})
            fi
        done
    fi

    ### clean up and umount output directory
    sudo -E rm ${ROOTFSDIR}/etc/apt/apt.conf.d/30-${EML_SELF_BUILD} ${ROOTFSDIR}/etc/apt/preferences.d/${EML_SELF_BUILD} ${ROOTFSDIR}/etc/apt/sources.list.d/${EML_SELF_BUILD}.list
    rm ${ROOTFSDIR}/tmp/${TARGET_ROOTFS_MANIFEST}.manifest
    sudo -E umount ${ROOTFSDIR}/proc
    sudo -E umount ${ROOTFSDIR}/dev/pts
    sudo -E umount ${ROOTFSDIR}/dev
    sudo -E umount ${ROOTFSDIR}/tmp
    cleanup_local_isarapt
    if [ ${not_exist_resolvconf} -ne 0 ]; then
        sudo -E rm ${ROOTFSDIR}/etc/resolv.conf
    else
        sudo mv ${ROOTFSDIR}/etc/resolv.conf.orig ${ROOTFSDIR}/etc/resolv.conf
    fi
}
