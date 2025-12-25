#
# EMLinux CVE checker
#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

from typing import Any
import debian.debian_support

import re

SOURCE_VERSION_PATTERN = re.compile(
    r"\s*(?P<pkg>[^\s(]+)(?:\s*\(\s*(?P<ver>[^)]+?)\s*\))?\s*$"
)


class PackageInfo:
    def __init__(self, binary_pkg_name, src_pkg_name, version, debian_codename):
        self.binary_pkg_name = binary_pkg_name
        self.source_from = "debian"  # default is debian package
        self.debian_codename = debian_codename

        self.version = debian.debian_support.Version(version)
        self.upstream_version = self.version.upstream_version

        if src_pkg_name is None:
            # If Source line is not in dpkg_status file,
            # source package name and version is same as binary package name and version.
            self.src_pkg_name = self.binary_pkg_name
            self.src_pkg_version = self.version
        else:
            # If binary package was uploaded by binNMU, source version and binary package
            # version is different. Source package version is in Source line.
            # So, we need track both versions
            """
            Source: bash (5.2.15-2)
            Version: 5.2.15-2+b8

            Source: bzip2 (1.0.8-5)
            Version: 1.0.8-5+b1
            """
            m = SOURCE_VERSION_PATTERN.match(src_pkg_name)
            tmp_src_pkg_name = m.group("pkg")
            tmp_src_pkg_ver = m.group("ver")

            self.src_pkg_name = tmp_src_pkg_name

            if not tmp_src_pkg_ver:
                self.src_pkg_version = self.version
            else:
                self.src_pkg_version = debian.debian_support.Version(tmp_src_pkg_ver)

    def __repr__(self) -> str:
        return f"{self.__dict__}"


class PackageList:
    def __init__(self) -> None:
        self.packages = {}

    def __repr__(self) -> str:
        return f"{self.__dict__}"

    def __iter__(self) -> str:
        return iter(self.packages)

    def __getitem__(self, key: str) -> PackageInfo:
        return self.packages[key]

    def add_package(self, pkginfo: PackageInfo) -> None:
        name = pkginfo.src_pkg_name
        if not name in self.packages:
            self.packages[name] = [pkginfo]
        else:
            self.packages[name].append(pkginfo)

    def merge_recipe_source_info(self, recipe_source_info: Any) -> None:
        for src_name in recipe_source_info:
            recipe = recipe_source_info[src_name]
            if src_name in self.packages:
                # print(f"merge source info {src_name}")
                for pkg in self.packages[src_name]:
                    pkg.source_from = recipe["source_from"]
                    pkg.src_pkg_name = recipe["source_package_name"]

    def get_binary_package_names_by_src_package_name(
        self, src_pkg_name: str
    ) -> list[str]:
        ret = []
        for pkg in self.packages.get(src_pkg_name):
            ret.append(pkg.binary_pkg_name)
        return ret

    def get_upstream_version(self, src_pkg_name: str) -> str:
        if not src_pkg_name in self.packages:
            return None

        return str(self.packages[src_pkg_name][0].upstream_version)

    def get_version(self, src_pkg_name: str) -> str:
        if not src_pkg_name in self.packages:
            return None

        return str(self.packages[src_pkg_name][0].version)

    def get_source_from(self, src_pkg_name: str) -> str:
        if not src_pkg_name in self.packages:
            return None

        return str(self.packages[src_pkg_name][0].source_from)

    def get_debian_codename(self, src_pkg_name: str) ->str:
        if not src_pkg_name in self.packages:
            return None

        return self.packages[src_pkg_name][0].debian_codename

class PackageInfoHelper:
    @staticmethod
    def parse_dpkg_status_file(
        filepath: str, debian_codename: str,
        target_source_package: str = None
    ) -> PackageList:
        results = PackageList()

        with open(filepath) as f:
            # split by package data
            blocks = f.read().split("\n\n")

            for block in blocks:
                binary_pkg_name = None
                src_pkg_name = None
                actual_src_pkg_name = None
                version = None

                lines = block.split("\n")
                if len(lines) < 2:
                    continue

                for line in lines:
                    if line.startswith("Package:"):
                        binary_pkg_name = line.split(":")[1].strip()
                    elif line.startswith("Source:"):
                        # If binary package is rebuilt by binNMU, source package line
                        # contains source package version.
                        # bash (5.2.15-2)
                        # This text will be normalized in PackageInfo's constroctor.
                        src_pkg_name = line.split(":")[1].strip()
                        actual_src_pkg_name = src_pkg_name.split(" ")[0].strip()
                    elif line.startswith("Version"):
                        # Version contains ":" in it(e.g. 5.36.0-7+deb12u3")
                        version = ":".join(line.split(":")[1:]).strip()

                pkginfo = None
                if (
                    target_source_package is None
                    or target_source_package == actual_src_pkg_name
                ):
                    pkginfo = PackageInfo(binary_pkg_name, actual_src_pkg_name, version, debian_codename)

                if pkginfo:
                    results.add_package(pkginfo)

        return results
