LINUX_DEFCONFIG = "defconfig"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI = "${LINUX_GIT_URI}/${LINUX_GIT_PREFIX}${LINUX_GIT_REPO};branch=${LINUX_GIT_BRANCH};protocol=${LINUX_GIT_PROTOCOL} \
           file://rpi3b.config \
          "

KERNEL_IMAGETYPE = "Image"

KERNEL_DEVICETREE = "broadcom/bcm2837-rpi-3-b-plus.dtb \
                     broadcom/bcm2837-rpi-3-b.dtb"
		      
