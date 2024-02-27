#!/usr/bin/python3

#
# EMLinux CVE checker
#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

import argparse
import sys
import os, os.path
import sqlite3
import yaml
import logging
import debian.debian_support

logging.basicConfig(level = logging.INFO, format='%(asctime)s:%(levelname)s: %(message)s')
logger = logging.getLogger("emlinux-cve-check")

sys.path.append(os.path.join(os.path.dirname(__file__), 'lib/python'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib/python/cve'))

import nvd_cve
import debian_cve
import kernel_cve
import bitbake_runner
import json

def read_json(jsonfile):
    with open(jsonfile, "r") as f:
        return json.loads(f.read())

def get_cve_products(extra_cve_product):
    name = os.path.join(os.path.dirname(__file__), "../conf/cve/cve_products.yml")

    data = None
    with open(name, "r") as f:
        data = yaml.safe_load(f)

    if extra_cve_product:
        with open(extra_cve_product, "r") as f:
            tmp = yaml.safe_load(f)
            if tmp:
                data.update(tmp)

    return data

def get_cve_ignore(extra_cve_check_ignore):
    name = os.path.join(os.path.dirname(__file__), "../conf/cve/cve_check_ignore.yml")

    data = None
    with open(name, "r") as f:
        data = yaml.safe_load(f)

    if extra_cve_check_ignore:
        with open(extra_cve_check_ignore, "r") as f:
            tmp = yaml.safe_load(f)
            if tmp:
                if data is None:
                    data = {}
                for pkg in tmp:
                    if pkg in data:
                        data[pkg] = data[pkg] + tmp[pkg]
                    else:
                        data[pkg] = tmp[pkg]

    return data

def update_ignored_cves_status(cves, cve_ignore_list):
    if cve_ignore_list is None:
        return cves

    for pkg in cve_ignore_list:
        if pkg in cves:
            pkg_cves = cves[pkg]
            for cve in cve_ignore_list[pkg]:
                if cve in pkg_cves:
                    cves[pkg][cve]["CVE STATUS"] = "Ignored"

    return cves

def find_debian_pkg_cves(debian_cve_json, pkgs):
    cvedata = read_json(debian_cve_json)
    debian_pkg_cve_data = {}
    cve_not_found_pkgs = []

    # collect cves for each installed packages(based on source package name)
    for name in pkgs:
        if name in cvedata:
            debian_pkg_cve_data[name] = cvedata[name]
        else:
            cve_not_found_pkgs.append(name)

    return debian_pkg_cve_data, cve_not_found_pkgs

def create_unique_package(installed):
    ret = {}
    for pkg in installed:
        src = pkg['source']

        if src not in ret:
            ret[src] = pkg
            ret[src]["bin_pkgs"] = [pkg["package"]]
        else:
            ret[src]["bin_pkgs"].append(pkg["package"])

    return ret

def fill_cve_info(cves, cve_products, db_file):
    conn = sqlite3.connect(db_file)
    for pkgname in cves:
        for cveid in cves[pkgname]:
            c = conn.cursor()
            sql = f"SELECT VULNSTATUS, SUMMARY, SCOREV2, SCOREV3, VECTOR, VECTORSTRING FROM NVD WHERE ID=\"{cveid}\""
            cursor = c.execute(sql)
            data = cursor.fetchone()
            c.close()

            # CVE id such as TEMP-0290435-0B57B5 not in NVD database.
            if data:
                cves[pkgname][cveid]["PACKAGE NAME"] = cves[pkgname][cveid]["PACKAGE NAME"]
                cves[pkgname][cveid]["BINARY PACKAGE NAME"] = cves[pkgname][cveid]["BINARY PACKAGE NAME"]
                cves[pkgname][cveid]["VERSION"] = cves[pkgname][cveid]["VERSION"]
                if data[0] == "Rejected":
                    cves[pkgname][cveid]["CVE STATUS"] = "Rejected"

                cves[pkgname][cveid]["CVE SUMMARY"] = data[1]
                cves[pkgname][cveid]["CVSS v2 BASE SCORE"] = data[2]
                cves[pkgname][cveid]["CVSS v3 BASE SCORE"] = data[3]
                cves[pkgname][cveid]["VECTOR"] = data[4]
                cves[pkgname][cveid]["VECTOR STRING"] = data[5]
                cves[pkgname][cveid]["MORE INFORMATION"] = f"https://nvd.nist.gov/vuln/detail/{cveid}"
            else:
                cves[pkgname][cveid]["PACKAGE NAME"] = cves[pkgname][cveid]["PACKAGE NAME"]
                cves[pkgname][cveid]["BINARY PACKAGE NAME"] = cves[pkgname][cveid]["BINARY PACKAGE NAME"]
                cves[pkgname][cveid]["VERSION"] = cves[pkgname][cveid]["VERSION"]
                cves[pkgname][cveid]["CVE SUMMARY"] = ""
                cves[pkgname][cveid]["CVSS v2 BASE SCORE"] = "0.0"
                cves[pkgname][cveid]["CVSS v3 BASE SCORE"] = "0.0"
                cves[pkgname][cveid]["VECTOR"] = "UNKNOWN"
                cves[pkgname][cveid]["VECTOR STRING"] = "UNKNOWN"
                cves[pkgname][cveid]["MORE INFORMATION"] = f"https://security-tracker.debian.org/tracker/{cveid}"


    conn.close()

    return cves

def status_name(fixed):
    if fixed:
        return "Patched"
    return "Unpatched"

def create_debian_pkg_cve_info(pkgname, bin_pkgname, installed_version, debian_cveinfo, nvd_cveinfo, codename):
    ret = {}

    cve_ids = set(list(debian_cveinfo.keys()) + list(nvd_cveinfo.keys()))
    for cveid in cve_ids:
        fixed = False
        if cveid in debian_cveinfo:
            dc = debian_cveinfo[cveid]["releases"][codename]
            if dc["status"] == "resolved":
                for repo in dc["repositories"]:
                    fixed_ver = debian.debian_support.Version(dc["repositories"][repo])
                    if installed_version >= fixed_ver:
                        fixed = True
        else:
            nc = nvd_cveinfo[cveid]
            fixed = nc["FIXED"]

        ret[cveid] = {
            "CVE": cveid,
            "PACKAGE NAME": pkgname,
            "BINARY PACKAGE NAME": bin_pkgname,
            "VERSION": str(installed_version),
            "CVE STATUS": status_name(fixed),
        }

    return ret

def create_cve_info_by_nvd(pkgname, bin_pkgname, installed_version, nvd_cveinfo):
    cve_ids = set(list(nvd_cveinfo["CVE"].keys()))
    cves = nvd_cveinfo["CVE"]
    ret = {}

    for cveid in cve_ids:
        ret[cveid] = {
            "CVE": cveid,
            "PACKAGE NAME": pkgname,
            "BINARY PACKAGE NAME": bin_pkgname,
            "VERSION": str(installed_version),
            "CVE STATUS": status_name(cves[cveid]["FIXED"]),
        }

    return ret

def merge_cve_data(uniq_installed_pkgs, installed_pkgs_cves_by_debian_data, cve_not_in_debian, installed_pkgs_cves_by_nvd_data, codename):

    cveinfo = {}
    for pkgname in installed_pkgs_cves_by_debian_data:
        installed_version = uniq_installed_pkgs[pkgname]["version"]
        debian_cveinfo = installed_pkgs_cves_by_debian_data[pkgname]
        nvd_cveinfo = None
        if pkgname in installed_pkgs_cves_by_nvd_data:
            if "CVE" in installed_pkgs_cves_by_nvd_data:
                nvd_cveinfo = installed_pkgs_cves_by_nvd_data[pkgname]
            else:
                nvd_cveinfo = {}

        bin_pkgname = uniq_installed_pkgs[pkgname]["bin_pkgs"]
        cveinfo[pkgname] = create_debian_pkg_cve_info(pkgname, bin_pkgname, installed_version, debian_cveinfo, nvd_cveinfo, codename)

    for pkgname in cve_not_in_debian:
        installed_version = uniq_installed_pkgs[pkgname]["version"]
        nvd_cveinfo = None
        if pkgname in installed_pkgs_cves_by_nvd_data:
            if installed_pkgs_cves_by_nvd_data[pkgname] is None:
                installed_pkgs_cves_by_nvd_data[pkgname] = {}

            if "CVE" in installed_pkgs_cves_by_nvd_data[pkgname]:
                nvd_cveinfo = installed_pkgs_cves_by_nvd_data[pkgname]
            else:
                nvd_cveinfo = {"CVE": {}}

        bin_pkgname = uniq_installed_pkgs[pkgname]["bin_pkgs"]
        cveinfo[pkgname] = create_cve_info_by_nvd(pkgname, bin_pkgname, installed_version, nvd_cveinfo)

    return cveinfo

def get_cves_by_package_from_nvd(conn, vendor, product):
    c = conn.cursor()

    """
    NVD's CVE data has several data for a CVE.
    e.g.
    sqlite> select count(*) from products where id="CVE-2016-6321";
    42
    sqlite> select * from products where id="CVE-2016-6321";
    ...
    CVE-2016-6321|gnu|tar|1.25|=||
    CVE-2016-6321|gnu|tar|1.26|=||
    CVE-2016-6321|gnu|tar|1.27|=||
    CVE-2016-6321|gnu|tar|1.27.1|=||
    CVE-2016-6321|gnu|tar|1.28|=||
    CVE-2016-6321|gnu|tar|1.29|=||
    ...

    So, get unique CVE IDs then get CVE data by each ID.
    """

    if vendor:
        sql = f"SELECT DISTINCT(ID) FROM PRODUCTS WHERE VENDOR=\"{vendor}\" AND PRODUCT=\"{product}\""
    else:
        sql = f"SELECT DISTINCT(ID) FROM PRODUCTS WHERE PRODUCT=\"{product}\""

    cursor = c.execute(sql)

    # Get unique CVE ID
    cves = []
    if cursor:
        for cve in cursor:
            cves.append(cve[0])

    c.close()

    return cves

def is_fixed_in_upstream_version(upstream_version, debian_upstream_version, operator):

    if upstream_version == "":
        # Can't determine affected or not. So return True to it may be affected
        return False

    uver = debian_cve.parse_version(upstream_version)
    dver = debian_upstream_version

    if operator == "=":
        return uver == dver
    elif operator == "<":
        return uver < dver
    elif operator == "<=":
        return uver <= dver
    elif operator == ">":
        return dver > uver
    elif operator == ">=":
        return dver >= uver
    return False # unknown operator


def is_affected_upstream_version(upstream_version, debian_upstream_version, operator):

    if upstream_version == "":
        # Can't determine affected or not. So return True to it may be affected
        return True

    uver = debian_cve.parse_version(upstream_version)
    dver = debian_upstream_version

    if operator == "=":
        return uver == dver
    elif operator == "<":
        return dver < uver
    elif operator == "<=":
        return dver <= uver
    elif operator == ">":
        return dver > uver
    elif operator == ">=":
        return dver >= uver

    return True # unknown operator

def check_affected_upstream_version(conn, cveid, pkg, vendor, product):
    """
    Check debian package's upstream version and start/end version in NVD database.
    if debian's upstream version is less than start version or greator than or equal
    debian's package version, this CVE may not be affected.
    However, debian package may backport vulnerable feature from upstream so we can't
    completely determine this CVE is affected or not.
    """

    cves = []
    c = conn.cursor()

    if vendor:
        sql = f"SELECT * FROM PRODUCTS WHERE ID=\"{cveid}\" AND VENDOR=\"{vendor}\" AND PRODUCT=\"{product}\""
    else:
        sql = f"SELECT * FROM PRODUCTS WHERE ID=\"{cveid}\" AND PRODUCT=\"{product}\""

    cursor = c.execute(sql)
    if cursor:
        for cve in cursor:
            d = {
                "CVE": cve[0],
                "VERSION_START": cve[3],
                "VERSION_START_OPERAND": cve[4],
                "VERSION_END": cve[5],
                "VERSION_END_OPERAND": cve[6],
            }
            cves.append(d)
    c.close()

    affected = False
    fixed = False

    for cve in cves:
        start_version = cve["VERSION_START"]
        end_version = cve["VERSION_END"]

        if not start_version == "":
            if not affected:
                op = cve["VERSION_START_OPERAND"]
                affected = is_affected_upstream_version(start_version, pkg["upstream_version"], op)

        if not end_version == "":
            if not fixed:
                op = cve["VERSION_END_OPERAND"]
                fixed = is_fixed_in_upstream_version(end_version, pkg["upstream_version"], op)

    # if start version's operator uses "=" and end vesion is not set in nvd database,
    # it may be able to set not affected(e.g. CVE-2002-0059. This CVE is not in debian security tracker)
    if not affected and not fixed:
        fixed = True

    return affected, fixed

def pkg_cve_fixed_check_by_nvd_data(uniq_installed_pkgs, installed_debian_pkgs_cves, db_file, cve_products):
    conn = sqlite3.connect(db_file)

    cve_analyzed = {}

    for name in uniq_installed_pkgs:
        cve_analyzed[name] = None

        pkg = uniq_installed_pkgs[name]
        vendor = None
        product = name
        if name in cve_products:
            vendor = cve_products[name]["vendor"]
            product = cve_products[name]["product"]

        cve_ids = get_cves_by_package_from_nvd(conn, vendor, product)

        for cveid in cve_ids:
            affected, fixed = check_affected_upstream_version(conn, cveid, pkg, vendor, product)
            tmp = {
                "DEBIAN_SRC_PKG_NAME": name,
                "VENDOR": vendor,
                "PRODICT": product,
                "CVE": cveid,
                "AFFECTED": affected,
                "FIXED": fixed,
            }

            if cve_analyzed[name] is None:
                cve_analyzed[name] = { "CVE": {}, }

            cve_analyzed[name]["CVE"][cveid] = tmp

    conn.close()

    return cve_analyzed

def recheck_kernel_cve(db_file, kernel_pkg_name, kernel_src_name, version, cveid):
    conn = sqlite3.connect(db_file)
    cve = {}
    sql = f"SELECT VULNSTATUS, SUMMARY, SCOREV2, SCOREV3, VECTOR, VECTORSTRING FROM NVD WHERE ID=\"{cveid}\""

    c = conn.cursor()
    cursor = c.execute(sql)
    data = cursor.fetchone()
    c.close()
    conn.close()

    cve["BINARY PACKAGE NAME"] = kernel_pkg_name,
    cve["PACKAGE NAME"] = kernel_src_name
    cve["VERSION"] = version
    cve["CVE"] = cveid

    if data is None:
        # No CVE data but it may be reserved.
        cve["CVE STATUS"] = status_name(False)
        cve["CVE SUMMARY"] = ""
        cve["CVSS v2 BASE SCORE"] = "0.0"
        cve["CVSS v3 BASE SCORE"] = "0.0"
        cve["VECTOR"] = "UNKNOWN"
        cve["VECTOR STRING"] = "UNKNOWN"
    else:
        fixed = False
        if data[0] == "Rejected":
            cve["CVE STATUS"] = "Rejected"
        else:
            cve["CVE STATUS"] = status_name(fixed)
        cve["CVE SUMMARY"] = data[1]
        cve["CVSS v2 BASE SCORE"] = data[2]
        cve["CVSS v3 BASE SCORE"] = data[3]
        cve["VECTOR"] = data[4]
        cve["VECTOR STRING"] = data[5]

    cve["MORE INFORMATION"] = f"https://nvd.nist.gov/vuln/detail/{cveid}"

    return cve

def check_kernel_cves_by_cip_kernel_sec(uniq_installed_pkgs, cves, kernel_src_dir, cip_kernel_sec_dir, db_file):
    if "linux-cip" in uniq_installed_pkgs:
        kernel_name = "linux-cip"
    elif "linux-cip-rt" in uniq_installed_pkgs:
        kernel_name = "linux-cip-rt"
    else:
        logger.debug("kernel name is not linux-cip or linux-cip-rt")
        logger.debug("Skip kernel CVE check by cip-kernel-sec")
        return cves

    kernel_cves = cves[kernel_name]
    pkgname = uniq_installed_pkgs[kernel_name]["package"]
    kver = str(uniq_installed_pkgs[kernel_name]["version"]).split("+")[0]

    cip_kernel_sec_result = kernel_cve.run_cip_kernel_sec(kernel_src_dir, kver, cip_kernel_sec_dir)

    for cve in cip_kernel_sec_result:
        if cve in kernel_cves:
            status = kernel_cves[cve]["CVE STATUS"]
            if status == "Patched":
                # Replace cve status by cip-kernel-sec result.
                kernel_cves[cve]["CVE STATUS"] = "Unpatched"
        else:
            cveinfo = recheck_kernel_cve(db_file, pkgname, kernel_name, kver, cve)
            kernel_cves[cve] = cveinfo

    return cves

def create_cves_info(db_file, debian_cve_list, uniq_installed_pkgs, installed_pkgs, codename, cve_products, kernel_src_dir, cip_kernel_sec_dir):
    logger.info("Checking CVEs ...")

    installed_pkgs_cves_by_debian_data, cve_not_in_debian = find_debian_pkg_cves(debian_cve_list, uniq_installed_pkgs)
    installed_pkgs_cves_by_nvd_data = pkg_cve_fixed_check_by_nvd_data(uniq_installed_pkgs, installed_pkgs_cves_by_debian_data, db_file, cve_products)

    cves = merge_cve_data(uniq_installed_pkgs, installed_pkgs_cves_by_debian_data, cve_not_in_debian, installed_pkgs_cves_by_nvd_data, codename)

    cves = fill_cve_info(cves, cve_products, db_file)

    cves = check_kernel_cves_by_cip_kernel_sec(uniq_installed_pkgs, cves, kernel_src_dir, cip_kernel_sec_dir, db_file)
    return cves

def write_text(cves, output_dir, uniq_installed_pkgs):
    filenames = []

    for pkgname in cves:
        if len(cves[pkgname]) == 0:
            continue

        filename = f"{output_dir}/{pkgname}"
        filenames.append(filename)

        with open(filename, "w") as f:
            for cve in sorted(cves[pkgname]):
                info = cves[pkgname][cve]
                f.write(f"PACKAGE NAME: {info['PACKAGE NAME']}\n")
                f.write(f"BINARY PACKAGE NAME: {' '.join(info['BINARY PACKAGE NAME'])}\n")
                f.write(f"VERSION: {info['VERSION']}\n")
                f.write(f"CVE: {info['CVE']}\n")
                f.write(f"CVE STATUS: {info['CVE STATUS']}\n")
                f.write(f"CVE SUMMARY: {info['CVE SUMMARY']}\n")
                f.write(f"CVSS v2 BASE SCORE: {info['CVSS v2 BASE SCORE']}\n")
                f.write(f"CVSS v3 BASE SCORE: {info['CVSS v3 BASE SCORE']}\n")
                f.write(f"VECTOR: {info['VECTOR']}\n")
                f.write(f"VECTOR STRING: {info['VECTOR STRING']}\n")
                f.write(f"MORE INFORMATION: {info['MORE INFORMATION']}\n")
                f.write("\n")

    return filenames

def write_json(cves, output_dir, uniq_installed_pkgs, cve_products):
    filenames = []

    for pkgname in cves:
        filename = f"{output_dir}/{pkgname}_cve.json"
        filenames.append(filename)

        info = cves[pkgname]
        pkginfo = uniq_installed_pkgs[pkgname]

        product = pkgname
        if pkgname in cve_products:
            product = cve_products[pkgname]["product"]

        cvesInRecord = "Yes"
        if len(info) == 0:
            cvesInRecord = "No"
            issues = []
        else:
            issues = []
            for cve in sorted(cves[pkgname]):
                issues.append(cves[pkgname][cve])

        data = {
            "version": "1",
            "package": [
                {
                    "name": pkginfo["source"],
                    "binary package name": pkginfo["bin_pkgs"],
                    "version": str(pkginfo["version"]),
                    "products": [
                        {
                            "product": product,
                            "cvesInRecord": cvesInRecord,
                        },
                    ],
                    "issue": issues,
                },
            ],
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=4, sort_keys=False)

    return sorted(filenames)

def write_all_in_one_text(output_dir, image_name, text_filenames):
    output_file = f"{output_dir}/{image_name}_cve"
    with open(output_file, "w") as out:
        for filename in text_filenames:
            with open(filename, "r") as f:
                out.write(f.read())
        out.write("")

def write_all_in_one_json(output_dir, image_name, json_filenames):
    all_in_one_data = {
        "version": "1",
        "package": [],
    }
    
    for filename in json_filenames:
        with open(filename, "r") as f:
            data = json.load(f)
            all_in_one_data["package"].extend(data["package"])

    output_file = f"{output_dir}/{image_name}_cve.json"
    with open(output_file, "w") as f:
        json.dump(all_in_one_data, f, indent=4, sort_keys=False)

def create_directory(target):
    if not os.path.exists(target):
        os.makedirs(target)

def main(args):
    if args.verbose_output:
       logger.setLevel(logging.DEBUG)

    bitbakeinfo = bitbake_runner.get_bitbake_information(args.image_name)
    
    cve_data_dl_dir = f"{bitbakeinfo['dl_dir']}/CVE"
    create_directory(cve_data_dl_dir)

    db_file = nvd_cve.update_nvd_db(cve_data_dl_dir, args.nvd_api_key)
    if db_file is None:
        logger.critical("Faied to fetch CVE database from NVD")
        exit(1)

    debian_cve_list = debian_cve.fetch_cve_data(cve_data_dl_dir)
    if debian_cve_list is None:
        logger.critical("Failed to fetch CVE data from Debian")
        exit(1)

    cip_kernel_sec_dir = kernel_cve.fetch_cip_kernel_sec(cve_data_dl_dir)
    if cip_kernel_sec_dir is None:
        logger.critical("Failed to fetch kernel-cip-sec")
        exit(1)

    installed_pkgs = debian_cve.parse_dpkg_status(bitbakeinfo["dpkg_status"])
    cve_products = get_cve_products(args.extra_cve_product)
    cve_ignore_list = get_cve_ignore(args.extra_cve_check_ignore)

    uniq_installed_pkgs = create_unique_package(installed_pkgs)
    linux_kernel_src_dir = os.path.abspath(bitbakeinfo["kernel_srcdir"])
    cves = create_cves_info(db_file, debian_cve_list, uniq_installed_pkgs, installed_pkgs, args.debian_codename, cve_products, linux_kernel_src_dir, cip_kernel_sec_dir)

    cves = update_ignored_cves_status(cves, cve_ignore_list)

    output_base_dir = f"{bitbakeinfo['deploy_dir']}/cve/{bitbakeinfo['image_full_name']}"

    create_directory(output_base_dir)

    formats = args.output_format.split(",")
    for fmt in formats:
        if fmt == "text":
            text_output_dir = f"{output_base_dir}/text"
            create_directory(text_output_dir)
            text_filenames = write_text(cves, text_output_dir, uniq_installed_pkgs)
            write_all_in_one_text(output_base_dir, bitbakeinfo["image_full_name"], text_filenames)
        elif fmt == "json":
            json_output_dir = f"{output_base_dir}/json"
            create_directory(json_output_dir)
            json_filenames = write_json(cves, json_output_dir, uniq_installed_pkgs, cve_products)
            write_all_in_one_json(output_base_dir, bitbakeinfo["image_full_name"], json_filenames)

    logger.info(f"CVE check finished. CVE check results are stored in {output_base_dir}")

def parse_options():
    parser = argparse.ArgumentParser()

    parser.add_argument("--nvd-api-key", dest="nvd_api_key", help="API key for NVD API",
            metavar="NVDAPIKEY")
    parser.add_argument("--debian-codename", dest="debian_codename", help="debian codename(Debian 12 is bookworm)",
            default="bookworm", metavar="DEBIANCODENAME")
    parser.add_argument("--output-format", dest="output_format", help="output format. available formats are text, json. formats can be comma separated string(e.g. text,json)",
            default="text", metavar="OUTPUTFORMAT")
    parser.add_argument("--cve-product", dest="extra_cve_product", help="User defined cve-product file",
            metavar="CVEPRODUCT")
    parser.add_argument("--cve-ignore", dest="extra_cve_check_ignore", help="User defined cve-check-ignore file",
            metavar="CVEPRODUCT")
    parser.add_argument("--image-name", dest="image_name", help="EMLinux image name",
            metavar="IMAGENAME", required=True)
    parser.add_argument("--verbose", dest="verbose_output", help="Enable verbose output",
            default=False, action="store_true")

    return parser.parse_args()

if __name__ == "__main__":
    main(parse_options())
