FILESEXTRAPATHS:prepend := "${FILE_DIRNAME}/files:"

SRC_URI:append = " \
   file://rules.hardening_no_branch \
   "

do_prepare_build:append() {
	if [ "${BASE_DISTRO_CODENAME}" = "trixie" ]; then
		if [ "${DISTRO_ARCH}" != "${HOST_ARCH}" -o "${DISTRO_ARCH}" = "arm64" ]; then
			cp "${WORKDIR}/rules.hardening_no_branch" "${S}/debian/rules"
		fi
	fi
}
