#
# EMLinux CVE checker.
# Download cip-kernel-sec
#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

import os, os.path
import subprocess
import sys
import shutil
import time
import yaml
import logging
import tempfile

logger = logging.getLogger("emlinux-cve-check")

def update_remote(remotes_path):
    with open(remotes_path) as f:
        content = yaml.safe_load(f)

    with open(remotes_path, "w") as f:
        yaml.dump({"cip": content["cip"]}, f, default_flow_style=False)

def run_cip_kernel_sec(kernel_src_dir, kver, cip_kernel_sec_dir):
    cwd =os.getcwd()
    cves = {
        "patched": [],
        "unpatched": [],
    }

    os.chdir(cip_kernel_sec_dir)

    if not kver.startswith("v"):
        kver = f"v{kver}"

    with tempfile.NamedTemporaryFile(delete=False) as f:
        output_filename = f.name

    retcode = -1
    cmd = ["./scripts/report_affected.py", "--include-fixed", "--output-format=yaml",
            f"--output-filename={output_filename}", "--git-repo",
            kernel_src_dir, "--remote-name", "cip:origin", "--include-ignored", kver]
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        proc.wait()
        retcode = int(proc.returncode)

        if not retcode == 0:
            logger.warning('Failed to run cip-kernel-sec')
            for s in proc.stderr:
                logger.warning(s.decode())

    with open(output_filename) as f:
        yaml_data = yaml.safe_load(f.read())
        k = list(yaml_data)[0]

        cves["patched"] = yaml_data[k]["fixed"]
        cves["unpatched"] = yaml_data[k]["affected"]

    if retcode == 0:
        os.unlink(output_filename)

    os.chdir(cwd)

    return cves

def clone_cip_kernel_sec():
    logger.info("clone cip-kernel-sec")
    git_uri = "https://gitlab.com/cip-project/cip-kernel/cip-kernel-sec.git"

    cmd = [ 'git', 'clone', git_uri ]
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        proc.wait()
        retcode = int(proc.returncode)

        if not retcode == 0:
            logger.warning('Failed to clone cip-kernel-sec')
            return False

        remotes_path = "./cip-kernel-sec/conf/remotes.yml"
        update_remote(remotes_path)

    return True

def update_cip_kernel_sec():
    logger.info("Update cip-kernel-sec")

    cmd = [ 'git', 'pull' ]
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        proc.wait()
        retcode = int(proc.returncode)

        if not retcode == 0:
            logger.warning('Failed to pull cip-kernel-sec')
            return False

    return True


def fetch_cip_kernel_sec(dl_dir):
    cip_kernel_sec_dir = f"{dl_dir}/cip-kernel-sec"

    cwd = os.getcwd()

    need_clone = False
    if not os.path.exists(cip_kernel_sec_dir):
        need_clone = True

    if need_clone:
        os.chdir(dl_dir)
        ret = clone_cip_kernel_sec()
    else:
        os.chdir(cip_kernel_sec_dir)
        ret = update_cip_kernel_sec()

    os.chdir(cwd)

    if not ret:
        # Remove old cip-kernel-sec directory then clone all data next time.
        shutil.rmtree(clone_cip_kernel_sec)
        return None

    return cip_kernel_sec_dir
