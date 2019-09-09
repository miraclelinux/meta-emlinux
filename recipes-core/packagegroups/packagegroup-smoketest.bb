SUMMARY = "Package group for smoke test"
PR = "r1"

inherit packagegroup

# following packages are installed by default
# - sysvinit
# - systemd-udev

# they are required packages to run test script
RDEPENDS_${PN} = "\
    bash \
    coreutils \
"

# test target packages
# sort by package name
RDEPENDS_${PN} += "\
    acl \
    attr \
    adduser \
    openssl \
"
