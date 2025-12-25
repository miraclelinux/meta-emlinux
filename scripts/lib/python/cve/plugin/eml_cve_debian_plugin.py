from typing import Any
from lib.python.cve.cve_product import CveProductList
from lib.python.cve.plugin.eml_cve_plugin_base import EmlCvePlugin
from lib.python.cve.cve_info import CveStatus, CveCheckResult, CveCheckResultList
from lib.python.package_info import PackageList

import logging

logger = logging.getLogger("emlinux-cve-check")

import urllib.request
import urllib.parse
import gzip
import time
import json
import debian.debian_support
import os
import logging
import errno

SECURITY_TRACKER_JSON_UPDATE_INTERVAL = 86400

DEBIAN_CVE_TRACKER_JSON_URL = "https://security-tracker.debian.org/tracker/data/json"


class EmlDebianPlugin(EmlCvePlugin):
    def __init__(
        self,
        cve_data_dir: str,
        args: Any,
        bitbakeinfo: Any,
        installed_packages: PackageList,
        cve_products: CveProductList,
    ):
        super().__init__(
            "EmlDebianPlugin",
            2,
            cve_data_dir,
            args,
            bitbakeinfo,
            installed_packages,
            cve_products,
        )

        self.tracker = None
        self.debian_cve_json = f"{self.cve_data_dir}/debian_cves.json"

    def update_database(self) -> bool:
        self._fetch_cve_data()
        return True

    def run_check(self) -> CveCheckResultList:
        logger.debug(f"{self.plugin_name}: run-check start")
        if not os.path.exists(self.debian_cve_json):
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), self.debian_cve_json
            )

        self._collect_cves_from_installed_packages()

        return self.cve_check_result_list

    def _fetch_json_data(self):
        request = urllib.request.Request(DEBIAN_CVE_TRACKER_JSON_URL)
        for attempt in range(5):
            try:
                r = urllib.request.urlopen(request)

                if r.headers["content-encoding"] == "gzip":
                    buf = r.read()
                    raw_data = gzip.decompress(buf)
                else:
                    raw_data = r.read().decode("utf-8")

                r.close()
            except Exception as e:
                logger.debug(f"json file: received error ({e}), retrying")
                time.sleep(6)
            else:
                return json.loads(raw_data)
        else:
            # We failed at all attempts
            return None

    def _is_skip_fetch_json_file(self, json_file: str):
        if not json_file:
            return False

        if not os.path.exists(json_file):
            return False

        if (
            time.time() - os.path.getmtime(json_file)
            < SECURITY_TRACKER_JSON_UPDATE_INTERVAL
        ):
            logger.info(
                "Last database update is in 1day so skip Debian CVE database update"
            )
            return True

        return False

    def _fetch_cve_data(self):
        logger.info("Update debian CVE database")
        if self._is_skip_fetch_json_file(self.debian_cve_json):
            return

        data = self._fetch_json_data()
        if data is None:
            raise Exception("Failed to download Debian security tracker json file")

        with open(self.debian_cve_json, "w") as f:
            json.dump(data, f)

        return

    def _read_security_tracker_json(self):
        with open(self.debian_cve_json) as f:
            return json.load(f)

    def _collect_cves_from_installed_packages(self):
        tracker = self._read_security_tracker_json()

        for src_pkg_name in self.installed_packages:
            source_from = self.installed_packages.get_source_from(src_pkg_name)
            if source_from == "non-debian" or source_from == "unknown":
                # if package is build from a recipe and not based on debian package, skip cve check.
                continue

            # At fisrt, check default debian version which is used by emlinux
            target_codename = self.installed_packages.get_debian_codename(src_pkg_name)
            if not source_from == "debian":
                # Is package built from a recipe and it based on debian source package?
                if source_from in cvedata[cveid]["releases"]:
                    target_codename = source_from
            
            if src_pkg_name in tracker:
                cvedata = tracker[src_pkg_name]
                for cveid in cvedata:
                    if not target_codename in  cvedata[cveid]["releases"]:
                        # skip unknown debian codename
                        continue

                    data = cvedata[cveid]["releases"][target_codename]

                    # According to the json file, there are 3 types in the status filed.
                    # That are open, resolved, and undetermined
                    vuln_status = CveStatus.CVE_STATUS_UNPATCHED
                    if data["status"] == "resolved":
                        installed_version = debian.debian_support.Version(
                            self.installed_packages.get_version(src_pkg_name)
                        )
                        fixed_version = debian.debian_support.Version(
                            data["fixed_version"]
                        )
                        if installed_version >= fixed_version:
                            vuln_status = CveStatus.CVE_STATUS_PATCHED

                    ci = CveCheckResult(cveid, src_pkg_name, vuln_status)
                    self.cve_check_result_list.add_cve_info(src_pkg_name, ci)
