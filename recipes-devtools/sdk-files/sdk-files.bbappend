FILESEXTRAPATHS:prepend := "${FILE_DIRNAME}/files:"

inherit kernel-arch

SRC_URI:append = "\
  file://environment-setup-template.tmpl \
"

TEMPLATE_FILES = "environment-setup-template.tmpl"
TEMPLATE_VARS = "TARGET_CC_ARCH TARGET_AS_ARCH TARGET_LD_ARCH TARGET_CFLAGS TARGET_CXXFLAGS TARGET_LDFLAGS KERNEL_ARCH"

do_install:append() {
    install -m 644 ${WORKDIR}/environment-setup-template ${D}
}
