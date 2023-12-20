#
# EMLinux CVE checker.
# Download and store Debian's CVE data
#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

import urllib.request
import gzip
import json
import os.path
import time
import debian.debian_support
import logging

logger = logging.getLogger("emlinux-cve-check")
DEBIAN_CVE_TRACKER_JSON_URL = "https://security-tracker.debian.org/tracker/data/json"

def remove_extra_suffix_in_version_string(version_str):
    vs = version_str

    # Some version string in NVD database contains additional suffix
    # such as _ubuntu1, _exp, and so of
    if "\\" in vs:
        vs = vs.split("\\")[0]
    if "_" in vs:
        vs = vs.split("_")[0]
    if "+" in vs:
        vs = vs.split("+")[0]

    return vs

def parse_version(version_str):
    vs = remove_extra_suffix_in_version_string(version_str)

    v = debian.debian_support.Version(vs)

    # Some debian packages added extra version info to upstream version.
    if "+" in v.upstream_version:
        v.upstream_version = v.upstream_version.split("+")[0]
    if ".dfsg" in v.upstream_version:
        v.upstream_version = v.upstream_version.split(".dfsg")[0]

    return v

def parse_dpkg_status(dpkgstatus):
    ret = []

    with open(dpkgstatus, "r") as f:
        lines = f.readlines()
        d = {}
        for line in lines:
            line = line.strip()
            if line.startswith("Package:"):
                d["package"] = line.split(":")[1].strip()
            elif line.startswith("Source"):
                # some package contain version number so remove it.
                # util-linux (2.38.1-5)
                d["source"] = line.split(":")[1].strip().split(" ")[0].strip()
            elif line.startswith("Version"):
                tmp = line.split(" ")[1].strip()
                d["version"] = debian.debian_support.Version(tmp)
                v = parse_version(tmp)
                d["upstream_version"] = parse_version(v.upstream_version)
            elif len(line) == 0:
                if not "source" in d:
                    # If source is not found in data, source package name should
                    # be same as binary package name
                    d["source"] = d["package"]

                ret.append(d)
                d = {}

    return ret

def fetch_json_data():
    request = urllib.request.Request(DEBIAN_CVE_TRACKER_JSON_URL)
    for attempt in range(5):
        try:
            r = urllib.request.urlopen(request)

            if (r.headers['content-encoding'] == 'gzip'):
                buf = r.read()
                raw_data = gzip.decompress(buf)
            else:
                raw_data = r.read().decode("utf-8")

            r.close()
        except Exception as e:
            logger.debug(f"json file: received error ({e}), retrying")
            time.sleep(6)
            pass
        else:
            return json.loads(raw_data)
    else:
        # We failed at all attempts
        return None

def is_skip_fetch_json_file(json_file):
    if json_file:
        if os.path.exists(json_file):
            if time.time() - os.path.getmtime(json_file) < 86400:
                logger.info(f"Last database update is in 1day so skip Debian CVE database update")
                return True

    return False

def fetch_cve_data(dl_dir):
    logger.info("Update debian CVE database")
    debian_cve_json = f"{dl_dir}/debian_cves.json"
    if is_skip_fetch_json_file(debian_cve_json):
        return debian_cve_json

    data = fetch_json_data()
    if data is None:
        return None

    with open(debian_cve_json, "w") as f:
        json.dump(data, f)

    return debian_cve_json

