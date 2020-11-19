FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
# Fix build issue on ubuntu 18.04
SRC_URI += "file://override-uservariables.patch"

