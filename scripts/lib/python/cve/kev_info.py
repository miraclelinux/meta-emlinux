#
# EMLinux CVE checker
#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

import logging

logger = logging.getLogger("emlinux-cve-check")


class KevInfoList:
    def __init__(self, kev_json_data) -> None:
        self.kev_list = {}
        self.kev_json_data = kev_json_data

        self._create_kev_list()

    def __contains__(self, value: str) -> bool:
        return value in self.kev_list

    def __iter__(self) -> str:
        return iter(self.kev_list)

    def __repr__(self) -> str:
        return f"{self.kev_list}"

    def _create_kev_list(self):
        for vul in self.kev_json_data["vulnerabilities"]:
            self._add_kev_data(vul)

    def _add_kev_data(self, kev_data: dict) -> None:
        cveid = kev_data["cveID"]
        if not cveid in self.kev_list:
            self.kev_list[cveid] = kev_data
        else:
            logger.info(f"CVE ID {cveid} is duplicated in the KEV data")

    def get_known_ransomware_campaign_use(self, cveid: str):
        return self.kev_list[cveid]["knownRansomwareCampaignUse"]
