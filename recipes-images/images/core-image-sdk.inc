IMAGE_INSTALL_append = " kernel-devsrc "
TOOLCHAIN_HOST_TASK_append = " nativesdk-bc "

# Post process after installed sdk
sdk_post_process () {
        # Set up kernel for building kernel module now
        $SUDO_EXEC bash -c 'source "$0" && cd "${OECORE_TARGET_SYSROOT}/usr/src/kernel" && make scripts' $target_sdk_dir/environment-setup-@REAL_MULTIMACH_TARGET_SYS@

        # Set up kernel headers for building user application
        $SUDO_EXEC bash -c 'source "$0" && cd "${OECORE_TARGET_SYSROOT}/usr/src/kernel" && cp include/config/kernel.release _kernel.release; cp include/generated/utsrelease.h _utsrelease.h; make prepare; mv _kernel.release include/config/kernel.release; mv _utsrelease.h include/generated/utsrelease.h; make headers_check; make INSTALL_HDR_PATH=${OECORE_TARGET_SYSROOT}/usr headers_install' $target_sdk_dir/environment-setup-@REAL_MULTIMACH_TARGET_SYS@
}

SDK_POST_INSTALL_COMMAND_append = " ${sdk_post_process}"

