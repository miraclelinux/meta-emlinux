#
# This class enables getting source code of all packages which are included in rootfs.
#
# Copyright (C) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

#
# [How to use]
# Add following line into the local.conf.
# INHERIT += "dl-srcpkg"
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

rootfs_generate_manifest:append () {
    local not_exist_resolvconf=`file '${ROOTFSDIR}'/etc/resolv.conf 2>&1 | grep "cannot open" | wc -c`

    ### backup apt status
    sudo sh -c "(cd ${ROOTFSDIR} && tar zcpf apt_status.tar.gz var/cache/apt var/lib/apt)"

    ### prepare directory for output
    mkdir -p ${DEPLOY_DIR}/sources/${MACHINE}
    sudo -E mount --bind /tmp ${ROOTFSDIR}/tmp
    mkdir -p ${ROOTFSDIR}/tmp/source_dir
    sudo -E mount --bind ${DEPLOY_DIR}/sources/${MACHINE} ${ROOTFSDIR}/tmp/source_dir
    cp ${ROOTFS_MANIFEST_DEPLOY_DIR}/${ROOTFS_PACKAGE_SUFFIX}.manifest ${ROOTFSDIR}/tmp/source_dir/

    ### setup network & apt environment
    if [ ${not_exist_resolvconf} -ne 0 ]; then
        sudo cp /etc/resolv.conf ${ROOTFSDIR}/etc/resolv.conf
    else
        sudo mv ${ROOTFSDIR}/etc/resolv.conf ${ROOTFSDIR}/etc/resolv.conf.orig
        sudo cp /etc/resolv.conf ${ROOTFSDIR}/etc/resolv.conf
    fi
    prepare_local_isarapt
    sudo sh -c "echo 'deb [trusted=yes] copy:///${LOCAL_APT_DIR} ${EML_SELF_BUILD} main' > ${ROOTFSDIR}/etc/apt/sources.list.d/${EML_SELF_BUILD}.list"
    sudo sh -c "echo 'deb-src [trusted=yes] copy:///${LOCAL_APT_DIR} ${EML_SELF_BUILD} main' >> ${ROOTFSDIR}/etc/apt/sources.list.d/${EML_SELF_BUILD}.list"
    sudo sh -c "echo \"Package: *\nPin: release n=${EML_SELF_BUILD}\nPin-Priority: 2000\" > ${ROOTFSDIR}/etc/apt/preferences.d/${EML_SELF_BUILD}"
    sudo sh -c "echo \"APT::Get::allow-downgrades 1;\" > ${ROOTFSDIR}/etc/apt/apt.conf.d/30-${EML_SELF_BUILD}"
    sudo -E chroot ${ROOTFSDIR} sh -c "apt-get -y -q update"

    ### download source packages
    sudo -E chroot --userspec=$(id -u):$(id -g) ${ROOTFSDIR} sh -c \
	 "(cd /tmp/source_dir && cat ${ROOTFS_PACKAGE_SUFFIX}.manifest | awk -F '|' '{system(\"mkdir -p \"\$1\"; apt-get source --download-only \"\$1\"=\"\$2\"; mv \"\$1\"_* \"\$1\"\")}')"

    ### clean up and umount output directory
    sudo -E rm ${ROOTFSDIR}/etc/apt/apt.conf.d/30-${EML_SELF_BUILD} ${ROOTFSDIR}/etc/apt/preferences.d/${EML_SELF_BUILD} ${ROOTFSDIR}/etc/apt/sources.list.d/${EML_SELF_BUILD}.list
    rm ${ROOTFSDIR}/tmp/source_dir/${ROOTFS_PACKAGE_SUFFIX}.manifest
    sudo -E umount ${ROOTFSDIR}/tmp/source_dir
    sudo -E umount ${ROOTFSDIR}/tmp
    cleanup_local_isarapt
    if [ ${not_exist_resolvconf} -ne 0 ]; then
        sudo -E rm ${ROOTFSDIR}/etc/resolv.conf
    else
        sudo mv ${ROOTFSDIR}/etc/resolv.conf.orig ${ROOTFSDIR}/etc/resolv.conf
    fi

    ### restore apt status
    sudo sh -c "(cd ${ROOTFSDIR} && rm -fr var/cache/apt var/lib/apt; tar zxpf apt_status.tar.gz)"
    sudo rm ${ROOTFSDIR}/apt_status.tar.gz
}
