#!/bin/sh
#
# This software is a part of ISAR.
# Copyright (c) Siemens AG, 2020-2023
#
# SPDX-License-Identifier: MIT

sdkroot=$(realpath $(dirname $0))
arch=$(uname -m)

new_sdkroot=$sdkroot
repatch_list=""

opt_short="hrl:"
opt_long="help,restore-chroot,repatch-list:"
OPTS=$(getopt -o "$opt_short" -l "$opt_long" -- "$@")
if [ $? -ne 0 ] ; then
	echo "Wrong input parameter!"; 1>&2
	exit 1;
fi
eval set -- "$OPTS"

while true; do
	case "$1" in
	--help|-h)
		echo "Usage: $0 [--restore-chroot|-r] [--repatch-list|-l <list>]"
		exit 0
		;;
	--restore-chroot|-r)
		new_sdkroot=/
		shift
		;;
	--repatch-list|-l)
		repatch_list=${2}
		shift 2
		;;
	--)
		shift; break
		;;
	esac
done

if [ -z $(which patchelf 2>/dev/null) ]; then
	echo "Please install 'patchelf' package first."
	exit 1
fi

echo -n "Adjusting path of SDK to '${new_sdkroot}'... "

for binary in $(find ${sdkroot}/usr/bin ${sdkroot}/usr/sbin ${sdkroot}/usr/lib/gcc* -executable -type f,l -exec file -L {} \; | grep ELF | awk -F ':' '{ print $1 }'); do
	interpreter=$(patchelf --print-interpreter ${binary} 2>/dev/null)
	oldpath=${interpreter%/lib*/ld-linux*}
	interpreter=${interpreter#${oldpath}}
	if [ -n "${interpreter}" ]; then
		patchelf --set-interpreter ${new_sdkroot}${interpreter} \
			--set-rpath ${new_sdkroot}/usr/lib:${new_sdkroot}/usr/lib/${arch}-linux-gnu \
			--force-rpath \
			$binary 2>/dev/null
	fi
done

for library in $(find ${sdkroot}/usr/lib -type f,l -name "lib*.so*" -exec file -L {} \; | grep ELF | awk -F ':' '{ print $1 }'); do
	rpath=$(patchelf --print-rpath ${library})
	if [ -n "${library}" ]; then
		patchelf --set-rpath ${new_sdkroot}/usr/lib:${new_sdkroot}/usr/lib/${arch}-linux-gnu \
		--force-rpath \
		$library 2>/dev/null
	fi
done

## HACK: Listed binaries require applying patchelf twice to avoid segfaults.
for binary in $(cat $repatch_list ${new_sdkroot}/repatch.list); do
	binary=${sdkroot}/${binary}
	if [ ! -f "${binary}" ]; then
		continue
	fi
	if file -L ${binary} |grep "executable" 2>&1 >/dev/null; then
		interpreter=$(patchelf --print-interpreter ${binary} 2>/dev/null)
		oldpath=${interpreter%/lib*/ld-linux*}
		interpreter=${interpreter#${oldpath}}
		if [ -n "${interpreter}" ]; then
			patchelf --set-interpreter ${new_sdkroot}${interpreter} \
				--set-rpath ${new_sdkroot}/usr/lib:${new_sdkroot}/usr/lib/${arch}-linux-gnu \
				--force-rpath \
				$binary 2>/dev/null
		fi
	else
		rpath=$(patchelf --print-rpath ${binary})
		if [ -n "${rpath}" ]; then
			patchelf --set-rpath ${new_sdkroot}/usr/lib:${new_sdkroot}/usr/lib/${arch}-linux-gnu \
			--force-rpath \
			$binary 2>/dev/null
		fi
	fi
done

sed -i 's|^GCC_SYSROOT=.*|GCC_SYSROOT="'"${new_sdkroot}"'"|' \
    ${sdkroot}/usr/bin/gcc-sysroot-wrapper.sh

echo "done"
