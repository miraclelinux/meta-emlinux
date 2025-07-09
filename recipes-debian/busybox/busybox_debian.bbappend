# In busybox, ADD_PR was set to 2 because of the following two modifications:
#- busybox: Add patch to fix CVE-2022-48174 (meta-debian-extended#470)
#- busybox: remove patch to fix CVE-2022-48174 (meta-debian-extended#498)
# As a result, the busybox_%.bbappend file in meta-debian-extended was deleted,
# so set it on meta-emlinux.
ADD_PR += "2"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI += "file://runtest-setup-resolve-conf.patch \
            file://0001-du-l-works-fix-to-use-145-instead-of-144.patch"

