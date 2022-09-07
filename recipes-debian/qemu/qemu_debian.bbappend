SRC_URI_append_class-nativesdk += "\
  ${@oe.utils.conditional("DISTRO", "emlinux-k510", \
    "file://0014-linux-user-fix-to-handle-variably-sized-SIOCGSTAMP-w-custom.patch", "", d)} \
"
