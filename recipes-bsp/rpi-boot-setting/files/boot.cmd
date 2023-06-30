fatload mmc 0 ${kernel_addr_r} Image
setenv fdt_addr_r 0x02600000
fdt addr ${fdt_addr_r}
setenv bootargs dwc_otg.lpm_enable=0 earlyprintk root=/dev/mmcblk0p2 rootfstype=ext4 rootwait
booti ${kernel_addr_r} - ${fdt_addr_r}
