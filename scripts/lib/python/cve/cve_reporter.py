#
# EMLinux CVE checker
#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

from lib.python.cve.nvd_lib import NvdCveNvdInfoList, NvdCveNvdInfo
from lib.python.package_info import PackageList

import logging

logger = logging.getLogger("emlinux-cve-check")
import json
import os

CVE_REPORT_JSON_VERSION = "1"


class CveReporter:
    def __init__(self, output_base_dir: str, image_name: str) -> None:
        self.output_base_dir = output_base_dir
        self.image_name = image_name

    def write_report(
        self,
        formats: str,
        cve_info_list: NvdCveNvdInfoList,
        installed_packages: PackageList,
    ) -> None:
        fmts = formats.split(",")
        for fmt in fmts:
            filenames = None
            if fmt == "text":
                filenames = self._write_text_report(cve_info_list)
                self._create_all_in_one_text_report(filenames)
            if fmt == "json":
                filenames = self._write_json_report(cve_info_list, installed_packages)
                self._create_all_in_one_json_report(filenames)

    def _create_dir(self, path: str) -> None:
        if not os.path.exists(path):
            os.makedirs(path)

    def _write_text_report(self, cve_info_list: NvdCveNvdInfoList) -> list[str]:
        text_dir = f"{self.output_base_dir}/text"
        self._create_dir(text_dir)

        filenames = []

        for src_pkg_name in cve_info_list:
            cve_list = cve_info_list[src_pkg_name]
            filename = f"{text_dir}/{src_pkg_name}"
            filenames.append(filename)

            with open(filename, "w") as f:
                for ci in cve_list:
                    f.write(f"PACKAGE NAME: {ci.src_pkg_name}\n")

                    bin_names = " ".join(ci.bin_pkg_names)

                    f.write(f"BINARY PACKAGE NAME: {bin_names}\n")
                    f.write(f"VERSION: {ci.version}\n")
                    f.write(f"CVE: {ci.cveid}\n")
                    f.write(f"CVE STATUS: {ci.status}\n")
                    f.write(f"CVE SUMMARY: {ci.summary}\n")
                    f.write(f"CVSS v2 BASE SCORE: {ci.scorev2}\n")
                    f.write(f"CVSS v3 BASE SCORE: {ci.scorev3}\n")
                    f.write(f"VECTOR: {ci.vector}\n")
                    f.write(f"VECTORSTRING: {ci.vector_string}\n")

                    if ci.kev == "Found":
                        f.write(f"KEV: Found\n")
                        f.write(f"KNOWN RANSOMWARE CAMPAIGN USE: {ci.kev_use}\n")
                    else:
                        f.write("KEV: Not Found\n")

                    f.write(f"MORE INFORMATION: {ci.moreinfo}\n")

                    f.write("\n")

        logger.info(f"Text report were written to {text_dir}")
        return filenames

    def _write_json_report(
        self, cve_info_list: NvdCveNvdInfoList, installed_packages: PackageList
    ) -> list[str]:
        json_dir = f"{self.output_base_dir}/json"
        self._create_dir(json_dir)
        filenames = []

        for src_pkg_name in installed_packages:
            has_cve = src_pkg_name in cve_info_list
            cve_list = cve_info_list[src_pkg_name]
            data = self._create_json_data_for_package(
                src_pkg_name, cve_list, installed_packages, has_cve
            )

            filename = f"{json_dir}/{src_pkg_name}_cve.json"
            filenames.append(filename)

            with open(filename, "w") as f:
                json.dump(data, f, indent=4, sort_keys=False)

        logger.info(f"Json report were written to {json_dir}")
        return filenames

    def _create_json_data_for_package(
        self,
        src_pkg_name: str,
        cve_info: NvdCveNvdInfo,
        installed_packages,
        has_cve: bool,
    ):
        if has_cve:
            cvesInRecord = "Yes"
            issue = self._create_issue_data(cve_info)
            version = cve_info[0].version
            bin_pkg_names = cve_info[0].bin_pkg_names
        else:
            cvesInRecord = "No"
            issue = []
            version = installed_packages.get_version(src_pkg_name)
            bin_pkg_names = (
                installed_packages.get_binary_package_names_by_src_package_name(
                    src_pkg_name
                )
            )

        data = {
            "version": CVE_REPORT_JSON_VERSION,
            "package": [
                {
                    "name": src_pkg_name,
                    "binary package name": bin_pkg_names,
                    "version": version,
                    "products": [
                        {
                            "product": src_pkg_name,
                            "cvesInRecord": cvesInRecord,
                        },
                    ],
                    "issue": issue,
                }
            ],
        }

        return data

    def _create_issue_data(self, cve_info: NvdCveNvdInfo) -> list[dict]:
        issue = []

        for ci in cve_info:
            data = {}

            data["CVE"] = ci.cveid
            data["PACKAGE NAME"] = ci.src_pkg_name
            data["BINARY PACKAGE NAME"] = ci.bin_pkg_names
            data["VERSION"] = ci.version
            data["CVE STATUS"] = ci.status
            data["CVE SUMMARY"] = ci.summary
            data["CVSS v2 BASE SCORE"] = ci.scorev2
            data["CVSS v3 BASE SCORE"] = ci.scorev3
            data["VECTOR"] = ci.vector
            data["VECTORSTRING"] = ci.vector_string

            if ci.kev == "Found":
                data["KEV"] = "Found"
                data["KNOWN RANSOMWARE CAMPAIGN USE"] = ci.kev_use
            else:
                data["KEV"] = "Not Found"

            data["MORE INFORMATION"] = ci.moreinfo
            issue.append(data)

        return issue

    def _create_all_in_one_text_report(self, filenames: list[str]) -> None:
        if filenames is None:
            return

        output_file = f"{self.output_base_dir}/{self.image_name}_cve"
        with open(output_file, "w") as out:
            for filename in filenames:
                with open(filename, "r") as f:
                    out.write(f.read())
            out.write("")
        logger.info(f"All in one text report was written to {output_file}")

    def _create_all_in_one_json_report(self, filenames: list[str]) -> None:
        if filenames is None:
            return

        all_in_one_data = {
            "version": "1",
            "package": [],
        }

        for filename in filenames:
            with open(filename, "r") as f:
                data = json.load(f)
                all_in_one_data["package"].extend(data["package"])

        output_file = f"{self.output_base_dir}/{self.image_name}_cve.json"
        with open(output_file, "w") as f:
            json.dump(all_in_one_data, f, indent=4, sort_keys=False)

        logger.info(f"All in one json report was written to {output_file}")
