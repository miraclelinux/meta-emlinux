do_install_prepend() {
    cd ${S}
    if [ "${@bb.utils.vercmp_string_op(d.getVar("KERNEL_VERSION"), '5.10', '>=')}" = "True" ]; then
        touch arch/arm64/kernel/vdso/gettimeofday.S
        touch arch/arm64/kernel/module.lds
    fi
}

do_install_append() {
    if [ "${@bb.utils.vercmp_string_op(d.getVar("KERNEL_VERSION"), '5.10', '>=')}" = "True" ]; then
        cd ${S}
        if [ "${ARCH}" = "arm64" ]; then
            install -D arch/arm64/kernel/vdso/*gettimeofday.* \
                $kerneldir/build/arch/arm64/kernel/vdso/
        fi
        install -D lib/vdso/gettimeofday.* $kerneldir/build/lib/vdso/
        install -D Kbuild $kerneldir/build/
        install -D Kconfig $kerneldir/build/
        install -D kernel/bounds.c $kerneldir/build/kernel/
        install -D kernel/time/timeconst.bc $kerneldir/build/kernel/time/
        install -D arch/arm64/kernel/asm-offsets.c $kerneldir/build/arch/arm64/kernel/

        cd ${B}
        install -D scripts/module.lds $kerneldir/build/scripts/
    else
        cd ${S}
        install -D kernel/bounds.c $kerneldir/build/kernel/
        install -D kernel/time/timeconst.bc $kerneldir/build/kernel/time/
        install -D arch/arm64/kernel/asm-offsets.c $kerneldir/build/arch/arm64/kernel/
    fi
}

