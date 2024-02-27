#
# bitbake helper
#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

import re
import subprocess
import sys

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
    except FileNotFoundError as e:
        print("bitbake command is not found.")
        print("Please run [source setup-emlinux <your build directory>]")
        exit(1)

    if not process.returncode == 0:
        print(f"Please check image name {image}")
        exit(1)

    pattern_deploy_image_dir = r'\nDEPLOY_DIR_IMAGE="([^"]*)"'
    pattern_deploy_dir = r'\nDEPLOY_DIR="([^"]*)"'
    pattern_image_full_name = r'\nIMAGE_FULLNAME="([^"]*)"'
    pattern_dl_dir = r'\nDL_DIR="([^"]*)"'
    pattern_kernel_name = r'\nKERNEL_NAME="([^"]*)"'

    deploy_image_dir = re.findall(pattern_deploy_image_dir, output)[0]
    deploy_dir = re.findall(pattern_deploy_dir, output)[0]
    image_full_name = re.findall(pattern_image_full_name, output)[0]
    dl_dir = re.findall(pattern_dl_dir, output)[0]
    kernel_name = re.findall(pattern_kernel_name, output)[0]
    kernel_srcdir = get_linux_source_dir(kernel_name)

    dpkg_status = f"{deploy_image_dir}/{image_full_name}.dpkg_status"
    return {
        "deploy_dir": deploy_dir,
        "image_full_name": image_full_name,
        "dl_dir": dl_dir,
        "dpkg_status": dpkg_status,
        "kernel_srcdir": kernel_srcdir,
    }
