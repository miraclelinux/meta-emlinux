#
# EMLinux CVE checker
#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

from typing import Any, Tuple
from lib.python.cve.plugin.eml_cve_plugin_base import EmlCvePlugin
from lib.python.cve.cve_product import CveProduct, CveProductList
from lib.python.cve.cve_info import CveStatus, CveCheckResult, CveCheckResultList
from lib.python.package_info import PackageList
import lib.python.cve.common_libs as cl
import lib.python.cve.nvd_lib as nvd_lib

import logging

logger = logging.getLogger("emlinux-cve-check")

import sqlite3
import datetime
import urllib.request
import urllib.parse
import gzip
import time
import json
import os
import errno

CVE_DB_UPDATE_INTERVAL = 86400

NVDCVE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


class EmlNVDPlugin(EmlCvePlugin):
    def __init__(
        self,
        cve_data_dir: str,
        args: Any,
        bitbakeinfo: Any,
        installed_packages: PackageList,
        cve_products: CveProductList,
    ):
        super().__init__(
            "EmlNVDPlugin",
            1,
            cve_data_dir,
            args,
            bitbakeinfo,
            installed_packages,
            cve_products,
        )

        self.predownload_url = self.bitbakeinfo["cve_db_predownload"]
        self.predownload = self.args.cve_db_predownload

        self.db_file = f"{self.cve_data_dir}/{nvd_lib.CVE_DATABASE_NAME}"
        self.nvd_api_key = args.nvd_api_key

    def update_database(self) -> bool:
        return self._update_nvd_db()

    def run_check(self) -> CveCheckResultList:
        logger.debug(f"{self.plugin_name}: run-check start")
        if not os.path.exists(self.db_file):
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), self.db_file
            )
        self._collect_cves_from_installed_packages()
        logger.debug(f"{self.plugin_name}: run-check finish")
        return self.cve_check_result_list

    def _collect_cves_from_installed_packages(self):
        conn = sqlite3.connect(self.db_file)

        for src_pkg_name in self.installed_packages:
            # logger.debug(f"Check source package: {src_pkg_name}")
            cve_product = self.cve_products[src_pkg_name]
            version = self.installed_packages.get_version(src_pkg_name)
            self._check_cves(conn, src_pkg_name, version, cve_product)

        conn.close()

    def _check_cves(
        self,
        conn: sqlite3.Connection,
        src_pkg_name: str,
        version: str,
        cve_product: CveProduct,
    ) -> None:
        for cp in cve_product:
            vendor = cp.vendor
            product = cp.product

            if product is None:
                continue

            if vendor is None:
                vendor = "%"

            cve_cursor = conn.execute(
                "SELECT DISTINCT ID FROM PRODUCTS WHERE PRODUCT IS ? AND VENDOR LIKE ?",
                (product, vendor),
            )
            for cverow in cve_cursor:
                cveid = cverow[0]
                vulnerable = False
                product_cursor = conn.execute(
                    "SELECT VERSION_START, OPERATOR_START, VERSION_END, OPERATOR_END  FROM PRODUCTS WHERE ID IS ? AND PRODUCT IS ? AND VENDOR LIKE ?",
                    (cveid, product, vendor),
                )
                for row in product_cursor:
                    (version_start, operator_start, version_end, operator_end) = row
                    vuln_status = CveStatus.CVE_STATUS_PATCHED
                    vulnerable = cl.check_affected(
                        version,
                        version_start,
                        operator_start,
                        version_end,
                        operator_end,
                    )
                    if vulnerable:
                        # logger.debug(f"{src_pkg_name}:{cve}: vulnerable = {vulnerable}")
                        vuln_status = CveStatus.CVE_STATUS_UNPATCHED

                    ci = CveCheckResult(cveid, src_pkg_name, vuln_status)
                    self.cve_check_result_list.add_cve_info(src_pkg_name, ci)

    def _update_nvd_db(self) -> bool:
        result = False

        conn = sqlite3.connect(self.db_file)
        logger.debug(f"Initialize nvd cve database {self.db_file}")
        self._initialize_nvd_cve_db(conn)

        skip_db_update, last_modified = self._check_skip_db_update(conn)

        if not skip_db_update and self.predownload:
            # predownload database file is old, download latest file
            conn.close()
            logger.info("Predownload CVE database file.")
            if not self._predownload_db(self.predownload_url):
                return result

            conn = sqlite3.connect(self.db_file)
            # re-check last modified date
            skip_db_update, last_modified = self._check_skip_db_update(conn)

        if not skip_db_update:
            logger.info("Update NVD CVE database")
            if self._fetch_all_cves(conn, last_modified):
                logger.info("Update last modified date")
                self._update_last_modified_date(conn)
                conn.commit()
                result = True
        else:
            logger.info("Last database update is in 1 day skip NVD database update")
            result = True

        conn.close()
        return result

    def _initialize_nvd_cve_db(self, conn: sqlite3.Connection) -> None:
        with conn:
            c = conn.cursor()

            c.execute(
                "CREATE TABLE IF NOT EXISTS META (ID NUMBER UNIQUE, LASTMODIFIED TEXT)"
            )

            c.execute(
                "CREATE TABLE IF NOT EXISTS NVD (ID TEXT UNIQUE, VULNSTATUS TEXT, SUMMARY TEXT, SCOREV2 TEXT, \
                SCOREV3 TEXT, MODIFIED INTEGER, VECTOR TEXT, VECTORSTRING TEXT)"
            )

            c.execute(
                "CREATE TABLE IF NOT EXISTS PRODUCTS (ID TEXT, \
                VENDOR TEXT, PRODUCT TEXT, VERSION_START TEXT, OPERATOR_START TEXT, \
                VERSION_END TEXT, OPERATOR_END TEXT)"
            )

            c.execute("CREATE INDEX IF NOT EXISTS PRODUCT_ID_IDX on PRODUCTS(ID);")

            c.close()

    def _check_skip_db_update(self, conn: sqlite3.Connection) -> Tuple[bool, str]:
        skip_db_update = False
        last_modified = self._get_last_modified_date(conn)
        if last_modified:
            d1 = datetime.datetime.fromisoformat(datetime.datetime.now().isoformat())
            d2 = datetime.datetime.fromisoformat(last_modified)

            date_delta = d1 - d2
            if date_delta.total_seconds() < CVE_DB_UPDATE_INTERVAL:
                skip_db_update = True
            else:
                # Database is too old so that fetch all data
                if date_delta.days > 120:
                    last_modified = None

        return skip_db_update, last_modified

    def _get_last_modified_date(self, conn: sqlite3.Connection) -> str:
        with conn:
            c = conn.cursor()

            cursor = c.execute("SELECT LASTMODIFIED from META")

            last = cursor.fetchone()
            c.close()

            if last is None:
                return None

            return last[0]

    def _predownload_db(self, predownload_url: str) -> bool:
        logger.info(f"Download CVE database file from {predownload_url}.")

        request = urllib.request.Request(predownload_url)
        for attempt in range(5):
            try:
                r = urllib.request.urlopen(request)

                if r.headers["content-encoding"] == "gzip":
                    buf = r.read()
                    raw_data = gzip.decompress(buf)
                else:
                    raw_data = r.read()

                r.close()
            except Exception as e:
                logger.debug(f"CVE databese download: received error ({e}), retrying")
                time.sleep(6)
                pass
            else:
                with open(self.db_file, "wb") as f:
                    f.write(raw_data)
                    logger.info("Download CVE database file was succeeded.")

                return True
        else:
            # We failed at all attempts
            return False

    def _parse_node_and_insert(self, conn, node, cveId):
        def _cpe_generator():
            for cpe in node.get("cpeMatch", ()):
                if not cpe["vulnerable"]:
                    return
                cpe23 = cpe.get("criteria")
                if not cpe23:
                    return
                cpe23 = cpe23.split(":")
                if len(cpe23) < 6:
                    return
                vendor = cpe23[3]
                product = cpe23[4]
                version = cpe23[5]

                if cpe23[6] == "*" or cpe23[6] == "-":
                    version_suffix = ""
                else:
                    version_suffix = "_" + cpe23[6]

                if version != "*" and version != "-":
                    # Version is defined, this is a '=' match
                    yield [
                        cveId,
                        vendor,
                        product,
                        version + version_suffix,
                        "=",
                        "",
                        "",
                    ]
                elif version == "-":
                    # no version information is available
                    yield [cveId, vendor, product, version, "", "", ""]
                else:
                    # Parse start version, end version and operators
                    op_start = ""
                    op_end = ""
                    v_start = ""
                    v_end = ""

                    if "versionStartIncluding" in cpe:
                        op_start = ">="
                        v_start = cpe["versionStartIncluding"]

                    if "versionStartExcluding" in cpe:
                        op_start = ">"
                        v_start = cpe["versionStartExcluding"]

                    if "versionEndIncluding" in cpe:
                        op_end = "<="
                        v_end = cpe["versionEndIncluding"]

                    if "versionEndExcluding" in cpe:
                        op_end = "<"
                        v_end = cpe["versionEndExcluding"]

                    if op_start or op_end or v_start or v_end:
                        yield [cveId, vendor, product, v_start, op_start, v_end, op_end]
                    else:
                        # This is no version information, expressed differently.
                        # Save processing by representing as -.
                        yield [cveId, vendor, product, "-", "", "", ""]

        conn.executemany(
            "insert into PRODUCTS values (?, ?, ?, ?, ?, ?, ?)", _cpe_generator()
        ).close()

    def _update_db(self, conn, elt):
        """
        Update a single entry in the on-disk database
        """

        accessVector = None
        vectorString = None
        cveId = elt["cve"]["id"]
        logger.debug(f"Processing CVE {cveId}")

        if "vulnStatus" in elt["cve"]:
            vulnStatus = elt["cve"]["vulnStatus"]
        else:
            vulnStatus = ""

        cveDesc = ""
        for desc in elt["cve"]["descriptions"]:
            if desc["lang"] == "en":
                cveDesc = desc["value"]
        date = elt["cve"]["lastModified"]
        try:
            accessVector = elt["cve"]["metrics"]["cvssMetricV2"][0]["cvssData"][
                "accessVector"
            ]
            vectorString = elt["cve"]["metrics"]["cvssMetricV2"][0]["cvssData"][
                "vectorString"
            ]
            cvssv2 = elt["cve"]["metrics"]["cvssMetricV2"][0]["cvssData"]["baseScore"]
        except KeyError:
            cvssv2 = 0.0
        cvssv3 = None
        try:
            accessVector = (
                accessVector
                or elt["cve"]["metrics"]["cvssMetricV30"][0]["cvssData"]["attackVector"]
            )
            vectorString = (
                vectorString
                or elt["cve"]["metrics"]["cvssMetricV30"][0]["cvssData"]["vectorString"]
            )
            cvssv3 = elt["cve"]["metrics"]["cvssMetricV30"][0]["cvssData"]["baseScore"]
        except KeyError:
            pass
        try:
            accessVector = (
                accessVector
                or elt["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]["attackVector"]
            )
            vectorString = (
                vectorString
                or elt["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]["vectorString"]
            )
            cvssv3 = (
                cvssv3
                or elt["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]["baseScore"]
            )
        except KeyError:
            pass
        accessVector = accessVector or "UNKNOWN"
        vectorString = vectorString or "UNKNOWN"
        cvssv3 = cvssv3 or 0.0

        conn.execute(
            "insert or replace into NVD values (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                cveId.strip(),
                vulnStatus.strip(),
                cveDesc.strip(),
                cvssv2,
                cvssv3,
                date.strip(),
                accessVector.strip(),
                vectorString.strip(),
            ],
        ).close()

        try:
            # Remove any pre-existing CVE configuration. Even for partial database
            # update, those will be repopulated. This ensures that old
            # configuration is not kept for an updated CVE.
            conn.execute("delete from PRODUCTS where ID = ?", [cveId]).close()
            for config in elt["cve"]["configurations"]:
                # This is suboptimal as it doesn't handle AND/OR and negate, but is better than nothing
                for node in config["nodes"]:
                    self._parse_node_and_insert(conn, node, cveId)
        except KeyError:
            logger.debug("CVE %s has no configurations" % cveId)

    def _nvd_request_next(self, url: str, request_args: Any) -> str:
        """
        Request next part of the NVD dabase
        """

        request = urllib.request.Request(
            url + "?" + urllib.parse.urlencode(request_args)
        )
        if self.nvd_api_key:
            request.add_header("apiKey", self.nvd_api_key)
        logger.debug(f"Requesting {request.full_url}")

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
                logger.debug(f"CVE database: received error ({e}), retrying")
                time.sleep(6)
                pass
            else:
                return raw_data
        else:
            # We failed at all attempts
            return None

    def _fetch_all_cves(self, conn: sqlite3.Connection, last_modified: str) -> bool:
        index = 0
        url = NVDCVE_URL

        req_args = {}

        if last_modified is not None:
            req_args["lastModStartDate"] = last_modified
            req_args["lastModEndDate"] = datetime.datetime.now().isoformat()

        # Recommended by NVD
        sleep_time = 6
        if self.nvd_api_key:
            sleep_time = 2

        while True:
            logger.debug("Updating entries")

            req_args["startIndex"] = index

            raw_data = self._nvd_request_next(url, req_args)
            if raw_data is None:
                return False

            data = json.loads(raw_data)

            index = data["startIndex"]
            total = data["totalResults"]
            per_page = data["resultsPerPage"]
            logger.debug(f"Got {per_page} entries")
            for cve in data["vulnerabilities"]:
                self._update_db(conn, cve)

            index += per_page
            if index >= total:
                break

            time.sleep(sleep_time)

        return True

    def _update_last_modified_date(self, conn: sqlite3.Connection) -> None:
        d = datetime.datetime.now().isoformat()

        with conn:
            c = conn.cursor()

            cursor = c.execute("SELECT LASTMODIFIED from META where ID=1")
            last = cursor.fetchone()

            if last is None:
                sql = f"INSERT INTO META VALUES (1, '{d}')"
            else:
                sql = f"UPDATE META set LASTMODIFIED='{d}' where ID=1"

            c.execute(sql)

            c.close()
