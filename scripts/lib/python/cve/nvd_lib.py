#
# EMLinux CVE checker
#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

from lib.python.cve.cve_info import CveStatus
from lib.python.package_info import PackageList
from lib.python.cve.kev_info import KevInfoList
import logging

logger = logging.getLogger("emlinux-cve-check")

import sqlite3

CVE_DATABASE_NAME = "nvd_cve_db.db"


class NvdCveNvdInfo:
    def __init__(
        self,
        cveid: str,
        src_pkg_name: str,
        bin_pkg_names: list[str],
        version: str,
        summary: str,
        scorev2: str,
        scorev3: str,
        vector: str,
        vector_string: str,
        status: str,
    ) -> None:
        self.cveid = cveid
        self.src_pkg_name = src_pkg_name
        self.bin_pkg_names = bin_pkg_names
        self.version = version
        if summary is None or len(summary) == 0:
            self.summary = ""
        else:
            self.summary = summary.strip()
        self.scorev2 = scorev2
        self.scorev3 = scorev3
        self.vector = vector
        self.vector_string = vector_string
        self.status = status
        self.kev = "Not Found"
        self.kev_use = None
        self.moreinfo = f"https://nvd.nist.gov/vuln/detail/{cveid}"

    def set_kev(self, kev_use: str) -> None:
        self.kev = "Found"
        self.kev_use = kev_use

    def __repr__(self) -> str:
        return f"{self.__dict__}"


class NvdCveNvdInfoList:
    def __init__(self) -> None:
        self.nvd_cve_nvd_info_list = {}

    def __repr__(self) -> str:
        return f"{self.nvd_cve_nvd_info_list}"

    def __iter__(self) -> str:
        return iter(self.nvd_cve_nvd_info_list)

    def __getitem__(self, key: str) -> NvdCveNvdInfo:
        if key in self.nvd_cve_nvd_info_list:
            return self.nvd_cve_nvd_info_list[key]
        return None

    def add_nvd_cve_nvd_info(self, data: NvdCveNvdInfo) -> None:
        if not data.src_pkg_name in self.nvd_cve_nvd_info_list:
            self.nvd_cve_nvd_info_list[data.src_pkg_name] = [data]
        else:
            self.nvd_cve_nvd_info_list[data.src_pkg_name].append(data)


class NvdCveProductInfo:
    def __init__(
        self,
        cveid: str,
        src_pkg_name: str,
        vendor: str,
        product: str,
        version_start: str,
        operator_start: str,
        version_end: str,
        operator_end: str,
    ) -> None:
        self.cveid = cveid
        self.src_pkg_name = src_pkg_name
        self.vendor = vendor
        self.product = product
        self.version_start = version_start
        self.operator_start = operator_start
        self.version_end = version_end
        self.operator_end = operator_end

    def __repr__(self) -> str:
        return f"{self.__dict__}"


class CveCheckMergedList:
    def __init__(self):
        self.merged = {}

    def __repr__(self):
        return f"{self.merged}"

    def __iter__(self) -> dict:
        return iter(self.merged)

    def __getitem__(self, key: str) -> NvdCveProductInfo:
        if key in self.merged:
            return self.merged[key]
        return None

    def add_data(
        self, src_pkg_name: str, cveid: str, cve_data: dict, priority: int
    ) -> None:
        # print(f"found cve {cveid} in {cr.plugin_name}")
        if not src_pkg_name in self.merged:
            self.merged[src_pkg_name] = {
                cveid: {
                    "cve_info": cve_data,
                    "priority": priority,
                }
            }
        elif src_pkg_name in self.merged and not cveid in self.merged[src_pkg_name]:
            # print(f"Append {cveid} to {src_pkg_name}")
            self.merged[src_pkg_name][cveid] = {
                "cve_info": cve_data,
                "priority": priority,
            }
        else:
            # print(f"CVE:{cveid} is already found")
            if priority > self.merged[src_pkg_name][cveid]["priority"]:
                # print(f"{cveid}:{src_pkg_name}: cr.priority > cve_check_merged_list[cveid].priority = {cr.priority > cve_check_merged_list[cveid]['priority']}: replace data")
                self.merged[src_pkg_name][cveid]["cve_info"] = cve_data
                self.merged[src_pkg_name][cveid]["priority"] = priority

    def apply_ignore_list_info(self, ignore_list: dict) -> None:
        for src_pkg_name in ignore_list:
            if src_pkg_name in self.merged:
                for cveid in ignore_list[src_pkg_name]:
                    if cveid in self.merged[src_pkg_name]:
                        self.merged[src_pkg_name][cveid][
                            "cve_info"
                        ].status = CveStatus.CVE_STATUS_IGNORED

    def get_cve_status(self, src_pkg_name: str, cveid: str) -> str:
        return self.merged[src_pkg_name][cveid]["cve_info"].status


class NvdCveInfoListCreator:
    def __init__(
        self,
        cve_data_dir: str,
        package_info_list: PackageList,
        kev_info_list: KevInfoList,
    ) -> None:
        self.db_file = f"{cve_data_dir}/{CVE_DATABASE_NAME}"
        self.nvd_info_list = NvdCveNvdInfoList()
        self.package_info_list = package_info_list
        self.kev_info_list = kev_info_list
        self.conn = None

    def get_nvd_info_list(self) -> NvdCveNvdInfoList:
        return self.nvd_info_list

    def create_cve_info_list(
        self, cve_check_merged_list: CveCheckMergedList
    ) -> NvdCveNvdInfoList:
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_file)

        for src_pkg_name in cve_check_merged_list:
            for cveid in cve_check_merged_list[src_pkg_name]:
                # status = cve_check_merged_list[src_pkg_name][cveid].status
                status = cve_check_merged_list.get_cve_status(src_pkg_name, cveid)
                binary_package_names = (
                    self.package_info_list.get_binary_package_names_by_src_package_name(
                        src_pkg_name
                    )
                )
                debian_pkg_version = self.package_info_list.get_version(src_pkg_name)

                ni = self._get_cve_information(
                    cveid,
                    src_pkg_name,
                    binary_package_names,
                    debian_pkg_version,
                    status,
                )
                if cveid in self.kev_info_list:
                    ni.set_kev(
                        self.kev_info_list.get_known_ransomware_campaign_use(cveid)
                    )

                self.nvd_info_list.add_nvd_cve_nvd_info(ni)
        self.conn.close()
        self.conn = None

    def _get_cve_information(
        self,
        cveid: str,
        src_pkg_name: str,
        bin_pkg_names: list[str],
        debian_pkg_version: str,
        status: str,
    ) -> NvdCveNvdInfo:
        c = self.conn.cursor()
        sql = f'SELECT VULNSTATUS, SUMMARY, SCOREV2, SCOREV3, VECTOR, VECTORSTRING FROM NVD WHERE ID="{cveid}"'
        cursor = c.execute(sql)
        data = cursor.fetchone()
        c.close()

        vuln_status = status
        summary = ""
        scorev2 = "0.0"
        scorev3 = "0.0"
        vector = "UNKNOWN"
        vector_string = "UNKNOWN"

        if data:
            if data[0] == "Rejected":
                vuln_status = CveStatus.CVE_STATUS_REJECTED

            summary = data[1]
            scorev2 = data[2]
            scorev3 = data[3]
            vector = data[4]
            vector_string = data[5]

        return NvdCveNvdInfo(
            cveid,
            src_pkg_name,
            bin_pkg_names,
            debian_pkg_version,
            summary,
            scorev2,
            scorev3,
            vector,
            vector_string,
            vuln_status,
        )
