#
# Get kernel arch from DISTRO_ARCH
# This class based on isar/meta/recipes-kernel/linux/linux-custom.inc
#
# SPDX-License-Identifier: MIT

def get_kernel_arch(d):
    distro_arch = d.getVar("DISTRO_ARCH")
    if distro_arch in ["amd64", "i386"]:
        kernel_arch = "x86"
    elif distro_arch == "arm64":
        kernel_arch = "arm64"
    elif distro_arch == "armhf":
        kernel_arch = "arm"
    elif distro_arch == "mipsel":
        kernel_arch = "mips"
    elif distro_arch == "riscv64":
        kernel_arch = "riscv"
    else:
        kernel_arch = ""
    return kernel_arch

export KERNEL_ARCH ??= "${@get_kernel_arch(d)}"
