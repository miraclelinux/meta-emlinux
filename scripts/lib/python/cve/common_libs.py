#
# EMLinux CVE checker
#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

import os
import json
from looseversion import LooseVersion


def read_json(jsonfile: str) -> dict:
    with open(jsonfile, "r") as f:
        return json.loads(f.read())


def create_directory(target):
    if not os.path.exists(target):
        os.makedirs(target)


def check_affected(
    target_version: str,
    version_start: str,
    operator_start: str,
    version_end: str,
    operator_end: str,
) -> bool:
    lv_target_version = LooseVersion(target_version)

    if not (version_start is None or version_start == "-" or len(version_start) == 0):
        lv_version_start = LooseVersion(version_start)

    if not (version_end is None or version_end == "-" or len(version_end) == 0):
        lv_version_end = LooseVersion(version_end)

    vulnerable = True
    if (
        operator_start == "=" and target_version == version_start
    ) or version_start == "-":
        vulnerable = True
    else:
        if operator_start:
            try:
                vulnerable_start = (
                    operator_start == ">=" and lv_target_version >= lv_version_start
                )
                vulnerable_start |= (
                    operator_start == ">" and lv_target_version > lv_version_start
                )
            except:
                vulnerable_start = False
        else:
            vulnerable_start = False

        if operator_end:
            try:
                vulnerable_end = (
                    operator_end == "<=" and lv_target_version <= lv_version_end
                )
                vulnerable_end |= (
                    operator_end == "<" and lv_target_version < lv_version_end
                )
            except:
                vulnerable_end = False
        else:
            vulnerable_end = False

        if operator_start and operator_end:
            vulnerable = vulnerable_start and vulnerable_end
        else:
            vulnerable = vulnerable_start or vulnerable_end

    return vulnerable
