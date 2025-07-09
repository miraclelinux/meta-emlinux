# In openssh, ADD_PR was set to 1 because of the following one modification:
# - openssh: Add CVE-2025-32728.patch (meta-emlinux#493)
ADD_PR += "1"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI += " \
           file://CVE-2025-32728.patch \
           "
