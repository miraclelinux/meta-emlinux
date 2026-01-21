#
# EMLinux CVE checker
#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

from typing import Any
from lib.python.cve.cve_product import CveProductList
from lib.python.cve.cve_info import CveCheckResultList
from lib.python.package_info import PackageList


class EmlCvePlugin:
    def __init__(
        self,
        plugin_name: str,
        priority: int,
        cve_data_dir: str,
        args: Any,
        bitbakeinfo: Any,
        installed_packages: PackageList,
        cve_products: CveProductList,
    ):
        self.plugin_name = plugin_name
        self.plugin_priority = priority
        self.cve_data_dir = cve_data_dir
        self.args = args
        self.bitbakeinfo = bitbakeinfo
        self.installed_packages = installed_packages
        self.cve_check_result_list = CveCheckResultList(
            self.plugin_name, self.plugin_priority
        )
        self.cve_products = cve_products

    def update_database(self) -> bool:
        raise NotImplementedError("It must be implemented in your plugin module")

    def run_check(self) -> CveCheckResultList:
        raise NotImplementedError("It must be implemented in your plugin module")
