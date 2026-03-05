#
# bitbake helper
#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

import re
import subprocess
import pathlib

def find_layers():
    cmd = ["bitbake-layers", "show-layers"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
    output, errors = process.communicate()

    layers = []

    lines = output.split("\n")
    for line in lines:
        tmp = [col for col in line.split(" ") if not col == ""]
        if len(tmp) >= 2:
            if pathlib.Path(tmp[1]).exists():
                layers.append(tmp[1])

    return layers

def get_linux_source_dir(kernel_name):
    cmd = ["bitbake", f"linux-{kernel_name}", "-e"]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
    output, errors = process.communicate()

    pattern_kernel_srcdir=r'\nS="([^"]*)"'
    kernel_srcdir = re.findall(pattern_kernel_srcdir, output)

    return kernel_srcdir[0]

def get_bitbake_information(image):
    cmd = ["bitbake", image, "-e"]

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, errors = process.communicate()
    except FileNotFoundError:
        print("bitbake command is not found.")
        print("Please run [source setup-emlinux <your build directory>]")
        exit(1)

    if not process.returncode == 0:
        print(f"Cannot find image name {image} in build artifacts.")
        exit(1)

    pattern_deploy_image_dir = r'\nDEPLOY_DIR_IMAGE="([^"]*)"'
    pattern_deploy_dir = r'\nDEPLOY_DIR="([^"]*)"'
    pattern_image_full_name = r'\nIMAGE_FULLNAME="([^"]*)"'
    pattern_dl_dir = r'\nDL_DIR="([^"]*)"'
    pattern_kernel_name = r'\nKERNEL_NAME="([^"]*)"'
    pattern_rootfsdir = r'\nROOTFSDIR="([^"]*)"'
    pattern_distro_arch = r'\nDISTRO_ARCH="([^"]*)"'
    pattern_repo_isar_dir = r'\nREPO_ISAR_DIR="([^"]*)"'
    pattern_image_distro = r'\nDISTRO="([^"]*)"'
    pattern_cve_db_predownload = r'\nCVE_DB_PREDOWNLOAD_URL="([^"]*)"'
    pattern_layer_emlinux = r'\nLAYERDIR_emlinux="([^"]*)"'

    deploy_image_dir = re.findall(pattern_deploy_image_dir, output)[0]
    deploy_dir = re.findall(pattern_deploy_dir, output)[0]
    image_full_name = re.findall(pattern_image_full_name, output)[0]
    dl_dir = re.findall(pattern_dl_dir, output)[0]
    kernel_name = re.findall(pattern_kernel_name, output)[0]
    kernel_srcdir = get_linux_source_dir(kernel_name)
    rootfs_dir = re.findall(pattern_rootfsdir, output)[0]
    distro_arch = re.findall(pattern_distro_arch, output)[0]
    repo_isar_dir = re.findall(pattern_repo_isar_dir, output)[0]
    image_distro = re.findall(pattern_image_distro, output)[0]
    emlinux_layer_dir = re.findall(pattern_layer_emlinux, output)[0]

    cve_db_url = re.findall(pattern_cve_db_predownload, output)
    if not len(cve_db_url) == 0:
        cve_db_predownload = cve_db_url[0]
    else:
        cve_db_predownload = None

    dpkg_status = f"{deploy_image_dir}/{image_full_name}.dpkg_status"
    return {
        "deploy_dir": deploy_dir,
        "deploy_image_dir": deploy_image_dir,
        "image_full_name": image_full_name,
        "dl_dir": dl_dir,
        "dpkg_status": dpkg_status,
        "kernel_srcdir": kernel_srcdir,
        "rootfs_dir": rootfs_dir,
        "distro_arch": distro_arch,
        "repo_isar_dir": repo_isar_dir,
        "image_distro": image_distro,
        "cve_db_predownload": cve_db_predownload,
        "emlinux_layer_dir": emlinux_layer_dir,
    }
