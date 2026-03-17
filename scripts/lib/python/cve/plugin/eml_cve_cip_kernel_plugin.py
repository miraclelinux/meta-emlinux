from typing import Any
from lib.python.cve.cve_product import CveProductList
from lib.python.cve.plugin.eml_cve_plugin_base import EmlCvePlugin
from lib.python.cve.cve_info import CveStatus, CveCheckResult, CveCheckResultList
from lib.python.package_info import PackageList

import yaml
import subprocess
from datetime import datetime, timezone
import os
import errno
import re
import tempfile
import shutil

import logging
logger = logging.getLogger("emlinux-cve-check")

CIP_KERNEK_SEC_UPDATE_INTERVAL = 86400
CIP_KERNEL_SEC_GIT_REPO_URL = (
    "https://gitlab.com/cip-project/cip-kernel/cip-kernel-sec.git"
)


class EmlCIPKernelPlugin(EmlCvePlugin):
    def __init__(
        self,
        cve_data_dir: str,
        args: Any,
        bitbakeinfo: Any,
        installed_packages: PackageList,
        cve_products: CveProductList,
    ):
        super().__init__(
            "EmlCIPKernelPlugin",
            2,
            cve_data_dir,
            args,
            bitbakeinfo,
            installed_packages,
            cve_products,
        )

        self.cip_kernel_sec_dir = f"{self.cve_data_dir}/cip-kernel-sec"
        self.kernel_src_pkg_name = None

    def update_database(self) -> bool:
        return self._fetch_cve_data()

    def run_check(self) -> CveCheckResultList:
        logger.debug(f"{self.plugin_name}: run-check start")
        if not os.path.exists(self.cip_kernel_sec_dir):
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), self.cip_kernel_sec_dir
            )

        if "linux-cip" in self.installed_packages:
            self.kernel_src_pkg_name = "linux-cip"
        elif "linux-cip-rt" in self.installed_packages:
            self.kernel_src_pkg_name = "linux-cip"
        else:
            logger.info("No linux kernel package in the image")
            return self.cve_check_result_list

        logger.debug(f"Linux kernel package is {self.kernel_src_pkg_name}")

        pkg_ver = self.installed_packages.get_version(self.kernel_src_pkg_name)
        pattern = r"^([^+]+)"
        m = re.search(pattern, pkg_ver)
        kver = m.group(1)

        cves = self._run_report_affected(kver)

        self._create_cve_check_result(cves)
        return self.cve_check_result_list

    def _is_update_need(self) -> bool:
        if not os.path.exists(self.cip_kernel_sec_dir):
            return True

        logger.info("check update")
        cmd = ["git", "reflog", "--date=iso"]

        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.cip_kernel_sec_dir,
            text=True,
        ) as proc:
            proc.wait()
            retcode = int(proc.returncode)
            if not retcode == 0:
                logger.warning("Failed to get last updated date in cip-kernel-sec")
                return False

            stdout, stderr = proc.communicate()
            last_log = stdout.split("\n")[0]
            m = re.search(r"HEAD@\{(.*?)\}", last_log)
            if not m:
                return True

            timestamp = m.group(1)
            last_date = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S %z")
            now = datetime.now(timezone.utc)
            diff = now - last_date

            logger.debug(f"time diff: {diff}")
            if diff.total_seconds() <= CIP_KERNEK_SEC_UPDATE_INTERVAL:
                logger.info(
                    f"cip-kernel-sec has been updated in {CIP_KERNEK_SEC_UPDATE_INTERVAL} second. skip update."
                )
                return False

        return True

    def _fetch_cve_data(self) -> bool:
        if not self._is_update_need():
            return True

        logger.info("Update cip-kernel-sec CVE database")

        is_cloned = os.path.exists(self.cip_kernel_sec_dir)

        ret = self._clone_or_updatecip_kernel_sec(is_cloned)

        if not ret:
            # Remove old cip-kernel-sec directory then clone all data next time.
            shutil.rmtree(self.cip_kernel_sec_dir)
            return False

        return True

    def _clone_or_updatecip_kernel_sec(self, is_cloned: bool) -> bool:
        logger.info("clone/update cip-kernel-sec")

        if is_cloned:
            cmd = ["git", "pull"]
            workdir = self.cip_kernel_sec_dir
        else:
            cmd = ["git", "clone", CIP_KERNEL_SEC_GIT_REPO_URL]
            workdir = self.cve_data_dir

        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=workdir
        ) as proc:
            proc.wait()
            retcode = int(proc.returncode)

            if not retcode == 0:
                logger.warning("Failed to clone/update cip-kernel-sec")
                return False

        if not is_cloned:
            remotes_path = f"{self.cip_kernel_sec_dir}/conf/remotes.yml"
            self._update_remote(remotes_path)

        return True

    def _update_remote(self, remotes_path: str):
        with open(remotes_path) as f:
            content = yaml.safe_load(f)

        with open(remotes_path, "w") as f:
            yaml.dump({"cip": content["cip"]}, f, default_flow_style=False)
            return True

        return False

    def _run_report_affected(self, kver: str) -> list:
        cves = {
            "Patched": [],
            "Unpatched": [],
        }

        if not kver.startswith("v"):
            kver = f"v{kver}"

        with tempfile.NamedTemporaryFile(delete=False) as f:
            output_filename = f.name

        kernel_dir = os.path.abspath(self.bitbakeinfo["kernel_srcdir"])

        retcode = -1
        cmd = [
            "./scripts/report_affected.py",
            "--include-fixed",
            "--output-format=yaml",
            f"--output-filename={output_filename}",
            "--git-repo",
            kernel_dir,
            "--remote-name",
            "cip:origin",
            "--include-ignored",
            kver,
        ]

        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.cip_kernel_sec_dir,
        ) as proc:
            proc.wait()
            retcode = int(proc.returncode)

            if not retcode == 0:
                logger.warning("Failed to run cip-kernel-sec")
                for s in proc.stderr:
                    logger.warning(s.decode())

        with open(output_filename) as f:
            yaml_data = yaml.safe_load(f.read())
            k = list(yaml_data)[0]

            if len(yaml_data[k]["fixed"]) > 0:
                cves["Patched"] = yaml_data[k]["fixed"]
            if len(yaml_data[k]["affected"]) > 0:
                cves["Unpatched"] = yaml_data[k]["affected"]

        if os.path.exists(output_filename):
            os.unlink(output_filename)

        return cves

    def _create_cve_check_result(self, cves: dict):
        for cveid in cves["Patched"]:
            ci = CveCheckResult(
                cveid, self.kernel_src_pkg_name, CveStatus.CVE_STATUS_PATCHED
            )
            self.cve_check_result_list.add_cve_info(self.kernel_src_pkg_name, ci)

        for cveid in cves["Unpatched"]:
            ci = CveCheckResult(
                cveid, self.kernel_src_pkg_name, CveStatus.CVE_STATUS_UNPATCHED
            )
            self.cve_check_result_list.add_cve_info(self.kernel_src_pkg_name, ci)

