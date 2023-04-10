SRC_URI_append += "\
  ${@bb.utils.contains("DISTRO_FEATURES", "kernel-510", \
    "file://0014-linux-user-fix-to-handle-variably-sized-SIOCGSTAMP-w-custom.patch", "", d)} \
"
