part uuid mmc 0:2 uuid
fatload mmc 0 ${kernel_addr_r} Image
fatload mmc 0 ${fdt_addr_r} bcm2837-rpi-3-b-plus.dtb
setenv bootargs dwc_otg.lpm_enable=0 earlyprintk root=PARTUUID=${uuid} rootfstype=ext4 rootwait
booti ${kernel_addr_r} - ${fdt_addr_r}
