#!/usr/bin/python3

import argparse
import sys
import os, os.path
import io
from debian import copyright
import debian.debfile
import json
import yaml
import glob
import hashlib

sys.path.append(os.path.join(os.path.dirname(__file__), 'lib/python'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib/python/sbom'))

import logging
logging.basicConfig(level = logging.INFO, format='%(asctime)s:%(levelname)s: %(message)s')
logger = logging.getLogger("emlinux-sbom-creator")

import bitbake_runner
import sbom_cyclonedx
import sbom_spdx

# Only show critical error from debian copyright library
copyright.logger.setLevel(logging.CRITICAL)

def merge_package_data(installed_pkgs, packages_info):
    for pkg in installed_pkgs:
        if pkg in packages_info:
            installed_pkgs[pkg]["sha256sum"] = packages_info[pkg]["sha256sum"]
            installed_pkgs[pkg]["description"] = packages_info[pkg]["description"]

    return installed_pkgs

def find_deb_packages(dl_dir, repo_isar_dir, distro, image_distro):
    targets  = [
        f"{dl_dir}/deb/debian-{distro}/*.deb",
        f"{repo_isar_dir}/{image_distro}/pool/**/*.deb",
    ]

    ret = []

    for target in targets:
        ret += glob.glob(target, recursive=True)

    return ret

def get_package_info_from_control(dl_dir, repo_isar_dir, distro, image_distro, distro_arch):
    ret = {}

    debs = find_deb_packages(dl_dir, repo_isar_dir, distro, image_distro)
    for debfile in debs:
        pkgname = None
        with debian.debfile.DebFile(debfile) as deb:
            control = deb.debcontrol()
            pkgname = control.get("Package", "Unkown")
            arch = control.get('Architecture', 'Unknown')
            desc = control.get("Description", "")

            if arch == distro_arch or arch == "all":
                sha256sum = None
                sha256hash = hashlib.sha256()
                with open(debfile, "rb") as f:
                    for block in iter(lambda: f.read(4096), b""):
                        sha256hash.update(block)
                        sha256sum = sha256hash.hexdigest()
                ret[pkgname] = {
                        "sha256sum": sha256sum,
                        "description": desc,
                }

    return ret

def parse_copyright_file(copyright_file):
    licenses = []

    with io.open(copyright_file, "rt", encoding='utf-8') as f:
        try:
            c = copyright.Copyright(f, strict=False)
        except Exception as e:
            logger.debug(f"Read copyright file error for {copyright_file}")
            licenses.append("unknown")
        else:
            for p in c.all_files_paragraphs():
                files = " ".join(p.files)
                if p.license:
                    licenses.append(p.license.synopsis)
                else:
                    if not "unkown" in licenses:
                        licenses.append("unkown")

    return sorted(licenses)

def parse_dpkg_status(dpkgstatus):
    ret = {}

    with open(dpkgstatus, "r") as f:
        lines = f.readlines()
        d = {}
        for line in lines:
            line = line.strip()
            if line.startswith("Package:"):
                d["package"] = line.split(":")[1].strip()
            elif line.startswith("Source:"):
                # some package contain version number so remove it.
                # util-linux (2.38.1-5)
                d["source"] = line.split(":")[1].strip().split(" ")[0].strip()
            elif line.startswith("Version:"):
                d["version"] = line.split(" ")[1].strip()
            elif line.startswith("Maintainer:"):
                d["maintainer"] = " ".join(line.split(" ")[1:]).strip()
            elif line.startswith("Section:"):
                d["section"] = line.split(":")[1].strip()
            elif line.startswith("Homepage:"):
                d["homepage"] = "".join(line.split(":")[1:]).strip()
            elif line.startswith("Architecture:"):
                d["arch"] = line.split(":")[1].strip()
            elif len(line) == 0:
                if not "source" in d:
                    # If source is not found in data, source package name should
                    # be same as binary package name
                    d["source"] = d["package"]

                ret[d["package"]] = d
                d = {}

    return ret

def find_copyright_files(rootfs, installed_pkgs, user_defined_licenses):
    
    for pkg in installed_pkgs:
        if pkg in user_defined_licenses:
            installed_pkgs[pkg]["licenses"] = user_defined_licenses[pkg]["licenses"]
        else:
            path = f"{rootfs}/usr/share/doc/{installed_pkgs[pkg]['package']}/copyright"

            if os.path.exists(path):
                installed_pkgs[pkg]["licenses"] = parse_copyright_file(path)
            else:
                installed_pkgs[pkg]["licenses"] = ["unkown"]

def read_user_defined_license_file(user_defined_licenses):
    name = os.path.join(os.path.dirname(__file__), "../conf/licenses/licenses.yml")

    data = None
    with open(name, "r") as f:
        data = yaml.safe_load(f)

    if user_defined_licenses:
        with open(user_defined_licenses, "r") as f:
            tmp = yaml.safe_load(f)
            if tmp:
                data.update(tmp)

    return data

def read_license_mapping_file(user_defined_license_mapping):
    name = os.path.join(os.path.dirname(__file__), "../conf/licenses/license-mapping.yml")
    data = None
    with open(name, "r") as f:
        data = yaml.safe_load(f)

    if user_defined_license_mapping:
        with open(user_defined_license_mapping, "r") as f:
            tmp = yaml.safe_load(f)
            if tmp:
                data.update(tmp)
    return data

def write_sbom_json(output_filepath, sbom_data):

    with open(output_filepath, "w") as f:
        json.dump(sbom_data, f, indent=4, sort_keys=True)

def main(args):
    if args.verbose_output:
        logging.basicConfig(level = logging.DEBUG)

    bitbakeinfo = bitbake_runner.get_bitbake_information(args.image)
    rootfs = bitbakeinfo["rootfs_dir"]
    dpkg_status = bitbakeinfo["dpkg_status"]

    installed_pkgs = parse_dpkg_status(dpkg_status)
    
    user_defined_licenses = read_user_defined_license_file(args.user_defined_licenses)
    license_mapping = read_license_mapping_file(args.user_defined_license_mapping)

    packages_info = get_package_info_from_control(bitbakeinfo["dl_dir"], bitbakeinfo["repo_isar_dir"],
            args.distro, bitbakeinfo["image_distro"], bitbakeinfo["distro_arch"])

    installed_pkgs = merge_package_data(installed_pkgs, packages_info)

    find_copyright_files(rootfs, installed_pkgs, user_defined_licenses)

    output_dir = f"{bitbakeinfo['deploy_dir']}/sbom/{bitbakeinfo['image_full_name']}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_filepath = f"{output_dir}/{args.image}-{args.sbom_format}.json"

    sbom_data = None

    logger.info(f"Create {args.sbom_format} format sbom for {args.image}")

    if args.sbom_format == "cyclonedx":
        sbom_data = sbom_cyclonedx.create_cyclonedx_sbom(args.product, args.image, args.distro, installed_pkgs, args.supplier, license_mapping)
    else:
        sbom_data = sbom_spdx.create_spdx_sbom(args.product, args.image, args.distro, installed_pkgs, args.supplier, license_mapping)

    if sbom_data:
        write_sbom_json(output_filepath, sbom_data)
        logger.info(f"sbom was created to {output_filepath}")
    else:
        logger.critical("Failed to create SBOM.")

def parse_options():
    parser = argparse.ArgumentParser()

    parser.add_argument("--image", dest="image", help="EMLinux image name",
            metavar="IMAGENAME", required=True)
    parser.add_argument("--sbom-format", dest="sbom_format", help="spdx or cyclonedx",
            metavar="SBOMFORMAT", required=True)
    parser.add_argument("--distro", dest="distro", help="debian distro name(e.g. bookworm)",
            default="bookworm", metavar="DISTRO")
    parser.add_argument("--licenses", dest="user_defined_licenses", help="license yaml file",
            metavar="LICENSES")
    parser.add_argument("--license-mapping", dest="user_defined_license_mapping", help="license mapping yaml file",
            metavar="LICENSESMAPPING")
    parser.add_argument("--supplier", dest="supplier", help="Supplier name(e.g. company name)",
            metavar="SUPPLIER", required=True)
    parser.add_argument("--product", dest="product", help="Product name",
            metavar="PRODUCT", required=True)
    parser.add_argument("--verbose", dest="verbose_output", help="Enable verbose output",
            action="store_true")
    return parser.parse_args()

if __name__ == "__main__":
    main(parse_options())
