# 
# SDK Installer
#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# Authors:
#  Masami Ichikawa <masami.ichikawa@miraclelinux.com>
#
# SPDX-License-Identifier: MIT
#
EMLINUX_SDK_BASE_NAME="${PN}-${DISTRO}-${MACHINE}"
EMLINUX_SDK_FILE_NAME="${EMLINUX_SDK_BASE_NAME}.${SDK_FORMATS}"
EMLINUX_SDK_FILE_PATH="${DEPLOY_DIR_IMAGE}/${EMLINUX_SDK_FILE_NAME}"
EMLINUX_SDK_INSTALLER_NAME="${PN}-${DISTRO}-${MACHINE}-sdk-installer.sh"
EMLINUX_SDK_INSTALLER_FILE_PATH="${DEPLOY_DIR_IMAGE}/${EMLINUX_SDK_INSTALLER_NAME}"

get_toolchain_prefix() {
    toolchain_prefix=""
    if [ "${DISTRO_ARCH}" = "amd64" ]; then
        toolchain_prefix="x86_64-linux-gnu"
    elif [ "${DISTRO_ARCH}" = "arm64" ]; then
        toolchain_prefix="aarch64-linux-gnu"
    elif [ "${DISTRO_ARCH}" = "armhf" ]; then
        toolchain_prefix="arm-linux-gnueabihf"
    fi
    echo "${toolchain_prefix}"
}

create_sdk_installer_script() {
    toolchain_prefix=$(get_toolchain_prefix)
    cat << "EOF" > ${EMLINUX_SDK_INSTALLER_FILE_PATH}
#!/bin/bash

which patchelf 2>&1>/dev/null 
if [ $? != 0 ]; then
  echo "Please install patchelf package in your system"
  exit 1
fi

answer=""
target_sdk_dir="/opt"
repatch_list=""

while getopts ":yd:l:" OPT; do
    case $OPT in
    y)
        answer="Y"
        ;;
    d)
        target_sdk_dir=$OPTARG
        ;;
    l)
        repatch_list=$OPTARG
    esac
done

SDK_START_LINE=$(awk '/^__SDK_BEGINS__/ { print NR + 1; exit 0; }' $0)

echo "Will you continue to install EMLinux SDK? [y/N]"
if [ "$answer" = "" ]; then
    read answer
fi

if [ "$answer" != "y" ] && [ "$answer" != "Y" ]; then
    echo "Abort installation."
    exit 0
fi

if [ ! -d "${target_sdk_dir}" ]; then
    mkdir -p "${target_sdk_dir}"
fi

sdk_install_target_dir=$(realpath ${target_sdk_dir})
sdk_installed_dir="${sdk_install_target_dir}/${EMLINUX_SDK_BASE_NAME}"

echo "Installing EMLinux SDK to ${sdk_install_target_dir} ."
tail -n +${SDK_START_LINE} $0 | sudo tar xpJ -C ${sdk_install_target_dir}

if [ -f "${repatch_list}" ]; then
    arg="-l ${repatch_list}"
else
    arg=""
fi
sudo "${sdk_installed_dir}/relocate-sdk.sh" $arg || (echo "Setup SDK environment failed." ; exit 1)

sudo sed -i "s:@EMLINUX_SDK_INSTALL_DIR@:${sdk_installed_dir}:g" "${sdk_installed_dir}/environment-setup-${MACHINE}-${DISTRO}"
sudo sed -i "s/@EMLINUX_SDK_TOOLCHAIN_PREFIX@/${EMLINUX_SDK_TARGET_TOOLCHAIN_PREFIX}/g" "${sdk_installed_dir}/environment-setup-${MACHINE}-${DISTRO}"

echo "When you use the SDK in a new shell session, you need to run following command."
echo "  $ source ${sdk_installed_dir}/environment-setup-${MACHINE}-${DISTRO}"

exit 0
__SDK_BEGINS__
EOF

    sed -i -e "2a EMLINUX_SDK_TARGET_TOOLCHAIN_PREFIX=\"${toolchain_prefix}\"" ${EMLINUX_SDK_INSTALLER_FILE_PATH}
    cat ${EMLINUX_SDK_FILE_PATH} >> ${EMLINUX_SDK_INSTALLER_FILE_PATH}

    chmod 755 ${EMLINUX_SDK_INSTALLER_FILE_PATH}
}

python do_create_sdk_installer() {
    pn = d.getVar("PN")
    if pn.endswith("-sdk"):
        bb.build.exec_func('create_sdk_installer_script', d)
}

do_image_tar[postfuncs] += "do_create_sdk_installer"

setup_toolchains_for_container() {
    tmpl_file="$1"
    toolchain_prefix=$(get_toolchain_prefix)
    sudo sed -i '1d' "${tmpl_file}"
    sudo sed -i 's:@EMLINUX_SDK_INSTALL_DIR@::g' "${tmpl_file}"
    sudo sed -i -e "s/@EMLINUX_SDK_TOOLCHAIN_PREFIX@/${toolchain_prefix}/g" "${tmpl_file}"
    sudo mkdir -p "${ROOTFSDIR}/etc/profile.d/"
    bname=$(basename ${tmpl_file})
    sudo mv "${tmpl_file}" "${ROOTFSDIR}/etc/profile.d/${bname}.sh"
    sudo chmod 755 "${ROOTFSDIR}/etc/profile.d/${bname}.sh"
}

setup_docker_files() {
    container_sdk_dir="${DEPLOY_DIR_IMAGE}/${PN}-${SDK_FORMATS}"
    # Remove old directory
    if [ -d "${container_sdk_dir}" ]; then
        rm -fr "${container_sdk_dir}"
    fi
    mkdir "${container_sdk_dir}"
    templates_dir="${TOPDIR}/../repos/meta-emlinux/templates/containerized-sdk"
    cp "${templates_dir}/Dockerfile" "${container_sdk_dir}/"
    cp "${templates_dir}/docker-compose.yml" "${container_sdk_dir}/"
    sed -i "s/@CONTAINER_IMAGE_NAME@/${CONTAINER_IMAGE_NAME}/g" "${container_sdk_dir}/Dockerfile"
    sed -i "s/@CONTAINER_IMAGE_TAG@/${CONTAINER_IMAGE_TAG}/g" "${container_sdk_dir}/Dockerfile"
}

ROOTFS_POSTPROCESS_COMMAND:append:class-sdk = " rename_installer_script setup_kernel_source_dir"
rename_installer_script() {
    setupfile="${ROOTFSDIR}/environment-setup-${MACHINE}-${DISTRO}"
    sudo mv "${ROOTFSDIR}/environment-setup-template" "${ROOTFSDIR}/environment-setup-${MACHINE}-${DISTRO}"

    if [ "${SDK_FORMATS}" = "docker-archive" ]; then
        setup_toolchains_for_container "${ROOTFSDIR}/environment-setup-${MACHINE}-${DISTRO}"
        setup_docker_files
    fi
}

setup_kernel_source_dir() {
    (cd ${ROOTFSDIR}/usr/src && sudo ln -s linux-headers-* kernel)
}

do_move_docker_archive() {
    mv "${DEPLOY_DIR_IMAGE}/${PN}-${DISTRO}-${DISTRO_ARCH}.${SDK_FORMATS}" "${DEPLOY_DIR_IMAGE}/${PN}-${SDK_FORMATS}"
}

do_image_docker_archive[postfuncs] += "do_move_docker_archive"
