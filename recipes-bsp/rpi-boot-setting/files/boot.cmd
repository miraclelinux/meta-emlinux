setenv setbootargs 'setenv bootargs dwc_otg.lpm_enable=0 earlyprintk root=PARTUUID=${uuid} rootfstype=ext4 rootwait'
setenv setuuid 'part uuid mmc ${devnum}:2 uuid'
setenv bootlinux 'run setuuid && run setbootargs && fatload mmc ${devnum} ${kernel_addr_r} Image && fatload mmc ${devnum} ${fdt_addr_r} ${fdt_name} && booti ${kernel_addr_r} - ${fdt_addr_r}'

setenv boot_rpi3 'setenv fdt_name bcm2837-rpi-3-b-plus.dtb && setenv devnum 0 && run bootlinux'
setenv boot_rpi4 'setenv fdt_name bcm2711-rpi-4-b.dtb && setenv devnum 1 && run bootlinux'

run boot_rpi3
run boot_rpi4
