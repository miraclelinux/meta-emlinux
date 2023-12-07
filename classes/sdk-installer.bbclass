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

create_sdk_installer_script() {
    toolchain_prefix=""
    if [ "${DISTRO_ARCH}" = "amd64" ]; then
        toolchain_prefix="x86_64-linux-gnu"
    elif [ "${DISTRO_ARCH}" = "arm64" ]; then
        toolchain_prefix="aarch64-linux-gnu"
    elif [ "${DISTRO_ARCH}" = "armhf" ]; then
        toolchain_prefix="arm-linux-gnueabihf"
    fi

    cat << "EOF" > ${EMLINUX_SDK_INSTALLER_FILE_PATH}
#!/bin/bash

which patchelf 2>&1>/dev/null 
if [ $? != 0 ]; then
  echo "Please install patchelf package in your system"
  exit 1
fi

answer=""
target_sdk_dir="/opt"

while getopts ":yd:" OPT; do
    case $OPT in
    y)
        answer="Y"
        ;;
    d)
        target_sdk_dir=$OPTARG
        ;;
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

sudo "${sdk_installed_dir}/relocate-sdk.sh" || (echo "Setup SDK environment failed." ; exit 1)

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

ROOTFS_POSTPROCESS_COMMAND:append:class-sdk = " rename_installer_script"
rename_installer_script() {
    setupfile="${ROOTFSDIR}/environment-setup-${MACHINE}-${DISTRO}"
    sudo mv "${ROOTFSDIR}/environment-setup-template" "${ROOTFSDIR}/environment-setup-${MACHINE}-${DISTRO}"
}

