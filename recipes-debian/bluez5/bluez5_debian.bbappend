FILESEXTRAPATHS_prepend := "${THISDIR}/bluez5:"

SRC_URI += " \
	file://tools_Fix_build_after_y2038_changes_in_glibc.patch \	
"
