FILESEXTRAPATHS:prepend := "${FILE_DIRNAME}/files:"

SRC_URI:append = "\
  file://environment-setup-template \
"

do_install:append() {
    install -m 644 ${WORKDIR}/environment-setup-template ${D}
}
