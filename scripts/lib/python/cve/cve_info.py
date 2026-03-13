#
# EMLinux CVE checker
#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

import logging

logger = logging.getLogger("emlinux-cve-check")


class CveStatus:
    CVE_STATUS_PATCHED = "Patched"
    CVE_STATUS_UNPATCHED = "Unpatched"
    CVE_STATUS_REJECTED = "Rejected"
    CVE_STATUS_IGNORED = "Ignored"


class CveCheckResult:
    def __init__(self, cveid: str, src_pkg_name: str, status: str) -> None:
        self.cveid = cveid
        self.src_pkg_name = src_pkg_name
        self.status = status

    def __repr__(self) -> str:
        return f"{self.__dict__}"


class CveCheckResultList:
    def __init__(self, plugin_name, priority) -> None:
        self.plugin_name = plugin_name
        self.priority = priority
        self.cves = {}

    def __repr__(self):
        return f"{self.__dict__}"

    def __iter__(self) -> str:
        return iter(self.cves)

    def __getitem__(self, key: str) -> CveCheckResult:
        if key in self.cves:
            return self.cves[key]
        return None

    def add_cve_info(self, src_pkg_name: str, check_result: CveCheckResult) -> None:
        if not src_pkg_name in self.cves:
            self.cves[src_pkg_name] = {check_result.cveid: check_result}
        else:
            if not check_result.cveid in self.cves[src_pkg_name]:
                self.cves[src_pkg_name][check_result.cveid] = check_result
            else:
                # We already have this CVE information
                pass
                # logger.debug(f"Source:{src_pkg_name}: CVE:{check_result.cveid} is duplicated")

    def src_pkg_names(self) -> list[str]:
        return sorted(self.cves.keys())

    def cve_ids_by_src_pkg(self, src_pkg_name: str) -> list[str]:
        if not src_pkg_name in self.cves:
            return None

        return sorted(self.cves[src_pkg_name].keys())


class CveInfo:
    def __init__(self, cveid: str, src_pkg_name: str, status: str) -> None:
        self.cveid = cveid
        self.src_pkg_name = src_pkg_name
        self.status = status
        self.summary = None
        self.cvssv2 = None
        self.cvessv3 = None
        self.vector = None
        self.vector_string = None
        self.more_information = None

    def __repr__(self) -> str:
        return f"{self.__dict__}"


class CveInfoList:
    def __init__(self) -> None:
        self.cves = {}

    def __repr__(self):
        return f"{self.__dict__}"

    def add_cve_info(self, src_pkg_name: str, cveinfo: CveInfo) -> None:
        if not src_pkg_name in self.cves:
            self.cves[src_pkg_name] = [cveinfo]
        else:
            self.cves[src_pkg_name].append(cveinfo)
