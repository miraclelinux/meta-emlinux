fatload mmc 0 ${kernel_addr_r} Image
fatload mmc 0 ${fdt_addr_r} bcm2837-rpi-3-b-plus.dtb
setenv bootargs dwc_otg.lpm_enable=0 earlyprintk root=/dev/mmcblk0p2 rootfstype=ext4 rootwait
booti ${kernel_addr_r} - ${fdt_addr_r}
