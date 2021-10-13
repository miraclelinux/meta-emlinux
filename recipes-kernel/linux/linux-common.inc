SRC_URI += " \
        ${@oe.utils.conditional("VIRTUAL-RUNTIME_init_manager", "systemd",\
                                "file://systemd-dependencies.config", "", d)}"

SRC_URI_append_qemuall += "file://qemu-emlinux.config"
SRC_URI_append_qemuarm += "file://qemuarm.config"

SRC_URI_append_raspberrypi3-64 += "file://raspberrypi3-64.config"
LINUX_DEFCONFIG_raspberrypi3-64 = "defconfig"
KERNEL_IMAGETYPE_raspberrypi3-64 = "Image"
KERNEL_DEVICETREE_raspberrypi3-64 = "broadcom/bcm2837-rpi-3-b-plus.dtb \
                                     broadcom/bcm2837-rpi-3-b.dtb"

SRC_URI_append_beaglebone += "file://beaglebone.config"

LINUX_DEFCONFIG_genericx86-64 = "x86_64_defconfig"

SRC_URI_append = " \
    ${@oe.utils.conditional("EMLINUX_SECURITY_HARDENED", "1", " file://emlinux-security-hardened.config", "", d)} \
"
