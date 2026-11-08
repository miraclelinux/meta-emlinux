#!/usr/bin/python3

import argparse
import sys
import os, os.path
import io
from debian import copyright
import debian.debfile
from debian.deb822 import Packages
import json
import yaml
import glob
import hashlib
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), "lib/python"))
sys.path.append(os.path.join(os.path.dirname(__file__), "lib/python/sbom"))

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(levelname)s: %(message)s")
logger = logging.getLogger("emlinux-sbom-creator")

import bitbake_runner
import sbom_cyclonedx
import sbom_spdx
import licensing
import recipe_license_parser
import manifest_parser

# Only show critical error from debian copyright library
copyright.logger.setLevel(logging.CRITICAL)

def merge_package_data(installed_pkgs, packages_info):
    for pkg in installed_pkgs:
        if pkg in packages_info:
            installed_pkgs[pkg].update(packages_info[pkg])


def find_deb_packages(dl_dir, repo_isar_dir, distro, image_distro):
    targets = [
        f"{dl_dir}/deb/debian-{distro}/*.deb",
        f"{repo_isar_dir}/{image_distro}/pool/**/*.deb",
    ]

    ret = []

    for target in targets:
        ret += glob.glob(target, recursive=True)

    return ret


def parse_copyright_text(pkgname, copyright_text):
    licenses = {}

    try:
        c = copyright.Copyright(io.StringIO(copyright_text), strict=False)
    except Exception:
        logger.debug(
            f"Failed to parse copyright text for {pkgname}. May be this file uses old foromat."
        )
    else:
        for p in c.all_files_paragraphs():
            if p.license and p.license.synopsis:
                licenses.setdefault("synopsis", []).append(p.license.synopsis)
                if len(p.license.text) > 0:
                    licenses.setdefault("text", {})[
                        p.license.synopsis
                    ] = p.license.text
        for text in c.all_license_paragraphs():
            if text.license:
                licenses.setdefault("text", {})[
                    text.license.synopsis
                ] = text.license.text

    return licenses


def get_synopsis_and_copyright_text_from_copyright_text(pkgname, installed_pkgs, user_defined_licenses):
    # When failed to parse copyright file or package name is in user defined license file,
    # set license from license defined file
    if not "licenses" in installed_pkgs[pkgname] or pkgname in user_defined_licenses:
        logger.debug(f"Check user defined mapping file for {pkgname}")
        if pkgname in user_defined_licenses:
            logger.debug(f"found {pkgname} in user defined license file")
            synopsis = user_defined_licenses[pkgname]["synopsis"]

            installed_pkgs[pkgname]["licenses"] = {
               "synopsis": synopsis,
                "text": {},
            }

            for lic_name in user_defined_licenses[pkgname]["license_data"]:
                lic_data = user_defined_licenses[pkgname]["license_data"][lic_name]
                installed_pkgs[pkgname]["licenses"]["text"][lic_name] = lic_data["text"]

    if not "licenses" in installed_pkgs[pkgname]:
        installed_pkgs[pkgname]["licenses"] = {
            "synopsis": ["NOASSERTION"], 
            "text": {}
        }
    
        return False

    return True


def parse_copyright_text_to_license_info(rootfs, installed_pkgs, user_defined_licenses, package_map):
    rechecks = []

    for pkg in installed_pkgs:
        logger.debug(f"Checking copyright for {pkg}")

        copyright_text = installed_pkgs[pkg]["copyright_text"]
        if copyright_text:
            licenses = parse_copyright_text(pkg, copyright_text)
            if bool(licenses):
                installed_pkgs[pkg]["licenses"] = licenses
        # else:
        #    logger.warning(f"Packge {pkg} does not contain copyright file")

        if not get_synopsis_and_copyright_text_from_copyright_text(pkg, installed_pkgs, user_defined_licenses):
            rechecks.append(pkg)

    # Set license from same source package.
    for pkg in rechecks:
        srcpkg = installed_pkgs[pkg]["source"]
        for p in package_map[srcpkg]:
            if p in rechecks:
                continue

            installed_pkgs[pkg]["licenses"] = installed_pkgs[p]["licenses"]

    for pkgname in installed_pkgs:
        licenses = installed_pkgs[pkgname]["licenses"]
        if "NOASSERTION" in licenses["synopsis"]:
            logger.warning(f"Package {pkgname} contains NOASSERTION license please check correct license")
 
def read_package_info_from_deb_file(debfile, distro_arch, 
                                    imager_bom_src_pkgs,
                                    imager_bom_bin_pkgs,
                                    rootfs_pkgs):
    pkgname = None
    ret = {}

    with debian.debfile.DebFile(debfile) as deb:
        control = deb.debcontrol()

        pkgname = control.get("Package", "Unknown")
        version = control.get("Version", "Unknown")

        installed_version = None
        if pkgname in imager_bom_src_pkgs:
            installed_version = imager_bom_src_pkgs[pkgname]["version"]
        elif pkgname in imager_bom_bin_pkgs:
            installed_version = imager_bom_bin_pkgs[pkgname]["version"]
        elif pkgname in rootfs_pkgs:
            installed_version = rootfs_pkgs[pkgname]["version"]

        if not installed_version == version:
            return None

        arch = control.get("Architecture", "Unknown")
        source = control.get("Source", None)
        if source is None:
            source = pkgname

        desc = control.get("Description", "No description")
        maintainer = control.get("Maintainer", "Unknown")
        homepage = control.get("Homepage", "Unknown")
        section = control.get("Section", "Unknown")

        # Ignore packages which are not installed to rootfs or wic
        if arch == distro_arch or arch == "all" \
                or pkgname in imager_bom_src_pkgs \
                or pkgname in imager_bom_bin_pkgs:

            copyright_text = None
            path = f"usr/share/doc/{pkgname}/copyright"
            if deb.data.has_file(path):
                copyright_text = deb.data.get_content(path).decode("utf-8")

            sha256sum = None
            sha256hash = hashlib.sha256()
            with open(debfile, "rb") as f:
                for block in iter(lambda: f.read(4096), b""):
                    sha256hash.update(block)
                    sha256sum = sha256hash.hexdigest()
            ret[pkgname] = {
                "package": pkgname,
                "source": source,
                "arch": arch,
                "section": section,
                "maintainer": maintainer,
                "sha256sum": sha256sum,
                "description": desc,
                "version": version,
                "copyright_text": copyright_text,
            }

    return ret


def get_package_info_from_deb_file(
    dl_dir, repo_isar_dir,
    distro, image_distro,
    distro_arch,
    imager_bom_src_pkgs,
    imager_bom_bin_pkgs,
    rootfs_pkgs
):
    ret = {}

    debs = find_deb_packages(dl_dir, repo_isar_dir, distro, image_distro)
    for debfile in debs:
        pkgdata = read_package_info_from_deb_file(debfile, distro_arch, imager_bom_src_pkgs, imager_bom_bin_pkgs, rootfs_pkgs)
        if pkgdata:
            ret.update(pkgdata)

    return ret


def parse_dpkg_status(dpkgstatus):
    ret = {}

    with open(dpkgstatus, "r") as f:
        for pkg in Packages.iter_paragraphs(f, use_apt_pkg=False):
            d = {}

            d["package"] = pkg.get("Package")
            d["source"] = pkg.get("Source")
            if d["source"] is None:
                d["source"] = d["package"]
            d["version"] = pkg.get("Version")
            #d["maintainer"] = pkg.get("Maintainer")
            #d["section"] = pkg.get("Section")
            #d["homepage"] = pkg.get("Homepage", "No Homepage")
            #d["arch"] = pkg.get("Architecture")
            #d["description"] = pkg.get("Description", "No description")
            
            ret[d["package"]] = d

    return ret

def make_user_defined_license_data(yml_file_name):
    license_data = {}
    data = None
    with open(yml_file_name, "r") as f:
        data = yaml.safe_load(f)

    if data is None:
        return license_data

    for pkg in data:
        license_data[pkg] = {"license_data": {}, "synopsis": {}}

        pkg_data = data[pkg]
        typename = type(pkg_data["licenses"])
        # logger.debug(f"{pkg} data type {typename}")
        if typename == dict:
            for synopsis in pkg_data["licenses"]["license"]:
                lic_text_path = None
                lic_text = None

                licenses = licensing.split_synopsis_tokens_only(synopsis)
                for lic_name in licenses:
                    if lic_name in pkg_data["licenses"]["text"]:
                        lic_text_path = pkg_data["licenses"]["text"].get(lic_name)

                    if lic_text_path is not None:
                        lic_text_path = Path(lic_text_path)
                        if not lic_text_path.is_absolute():
                            lic_text_path = yml_file_name.parent.joinpath(
                                "license_texts", lic_text_path
                            )

                        if not lic_text_path.exists():
                            logger.error(
                                f"License file  {lic_text_path} for {pkg} doesn't exist"
                            )
                            exit(1)
                        logger.debug(
                            f"{pkg} read license {lic_name} text from {lic_text_path}"
                        )
                        with open(lic_text_path) as f:
                            lic_text = f.read()

                    license_data[pkg]["license_data"][lic_name] = {
                        "synopsis": synopsis,
                        "licenses": licenses,
                        "text": lic_text,
                    }

        elif typename == list:
            for lic_name in pkg_data["licenses"]:
                license_data[pkg]["license_data"][lic_name] = {
                    "synopsis": lic_name,
                    "licenses": licensing.split_synopsis_tokens_only(lic_name),
                    "text": None,
                }
        elif typename == str:
            lic_name = pkg_data["licenses"]
            license_data[pkg]["license_data"][lic_name] = {
                "synopsis": lic_name,
                "licenses": licensing.split_synopsis_tokens_only(lic_name),
                "text": None,
            }

        synopsis = []
        for lic_name in license_data[pkg]["license_data"]:
            s = license_data[pkg]["license_data"][lic_name]["synopsis"]
            if not s in synopsis:
                synopsis.append(s)

        license_data[pkg]["synopsis"] = synopsis

    return license_data


def find_pre_defined_file_common(layers, target_path):
    ret = []

    meta_emlinux_file = None
    for layer in layers:
        layer_name = os.path.basename(layer)
        filepath = Path(f"{layer}/{target_path}")
        if os.path.exists(filepath):
            if layer_name == "meta-emlinux":
                meta_emlinux_file = filepath.absolute()
            else:
                ret.append(filepath.absolute())

    # meta-emlinux layer is always first
    if meta_emlinux_file:
        ret.insert(0, meta_emlinux_file)
    return ret


def find_pre_defined_license_mapping_files(layers):
    return find_pre_defined_file_common(layers, "conf/licenses/license-mapping.yml")


def find_pre_defined_licenses_files(layers):
    return find_pre_defined_file_common(layers, "conf/licenses/licenses.yml")


def read_pre_defined_license_files(files):
    license_data = {}
    for filepath in files:
        license_data.update(make_user_defined_license_data(filepath))

    return license_data


def read_user_defined_license_file(user_defined_license_files):
    license_data = {}
    if user_defined_license_files:
        tmp = make_user_defined_license_data(user_defined_license_files)
        license_data.update(tmp)

    return license_data


def read_pre_defined_license_mapping_file(files):
    license_data = {}
    for filepath in files:
        with open(filepath) as f:
            license_data.update(yaml.safe_load(f))

    return license_data


def read_user_defined_license_mapping_file(user_defined_license_mapping):
    license_data = {}

    if user_defined_license_mapping:
        with open(user_defined_license_mapping, "r") as f:
            tmp = yaml.safe_load(f)
            if tmp:
                license_data.update(tmp)
    return license_data


def read_license_files(layers, user_defined_license_file):
    license_data = {}
    files = find_pre_defined_licenses_files(layers)
    license_data.update(read_pre_defined_license_files(files))
    license_data.update(read_user_defined_license_file(user_defined_license_file))

    return license_data


def read_license_mapping_files(layers, user_defined_license_mapping_file):
    license_data = {}
    files = find_pre_defined_license_mapping_files(layers)
    license_data.update(read_pre_defined_license_mapping_file(files))
    license_data.update(
        read_user_defined_license_mapping_file(user_defined_license_mapping_file)
    )
    return license_data


def write_sbom_json(output_filepath, sbom_data):
    with open(output_filepath, "w") as f:
        json.dump(sbom_data, f, indent=4, sort_keys=True)


def create_license_data(installed_pkgs, license_mapping):
    for pkg in installed_pkgs:
        logger.debug(f"Create data for {pkg}")
        licenses = installed_pkgs[pkg]["licenses"]
        installed_pkgs[pkg]["normalized_licenses"] = []

        for synopsis in installed_pkgs[pkg]["licenses"]["synopsis"]:
            license_data = licensing.debian_synopsis_to_spdx_license_id(
                pkg, synopsis, licenses.get("text"), license_mapping
            )
            # do not append duplicated data.
            if not license_data in installed_pkgs[pkg]["normalized_licenses"]:
                installed_pkgs[pkg]["normalized_licenses"].append(license_data)

        # licenses is no longer needed.
        del installed_pkgs[pkg]["licenses"]
        license_id_text = licensing.create_single_line_license_id_text(
            installed_pkgs[pkg]["normalized_licenses"]
        )
        installed_pkgs[pkg]["license_id_text"] = license_id_text


def create_license_data_for_recipe_build_package(target_pkgs, license_mapping):
     for pkg in target_pkgs:
        licenses = recipe_license_parser.split_license_for_imager_bom_pkgs(target_pkgs[pkg]["license"])
        normalized_text = recipe_license_parser.normalize_licese_field(licenses, license_mapping)
        target_pkgs[pkg]["normalized_license"] = normalized_text
        synopsis = recipe_license_parser.parse_to_license_array(normalized_text)

        target_pkgs[pkg]["licenses"] = {
            "synopsis": synopsis,
            "text": {},
        }
        del target_pkgs[pkg]["license"]


def convert_source_info_to_package_data(pkgname, data):
    d = {}

    package = pkgname
    try:
        idx = data["provides"].index(pkgname)
        package = data["provides"][idx]
    except:
        pass

    d["package"] = package
    d["source"] = data["source_package_name"]
    d["version"] = data["version"]
    d["maintainer"] = data["maintainer"]
    d["section"] = data["section"]
    d["homepage"] = data["homepage"]
    d["arch"] = data["arch"]
    d["source"] = pkgname
    d["description"] = data["description"]
    d["license"] = data["license"]

    return d

def get_build_from_reciepe_packages(srcinfo_json):
    srcinfo = {}
    with open(srcinfo_json) as f:
        srcinfo = json.load(f)

    return srcinfo


def get_build_package_data(target_pkgs, srcinfo_pkgs):
    srcinfo_keys = set([k for k in srcinfo_pkgs.keys()])
    pkgs = set(target_pkgs.strip().split(" "))

    pkg_names = pkgs & srcinfo_keys

    pkgs = {}
    for name in pkg_names:
        pkgs[name] = convert_source_info_to_package_data(name, srcinfo_pkgs[name])

    return pkgs


def create_package_map(installed_pkgs):
    pkg_map = {}

    for pkgname in installed_pkgs:
        p = installed_pkgs[pkgname]
        source = p["source"]
        pkg_map.setdefault(source, []).append(pkgname)

    return pkg_map

def main(args):
    if args.verbose_output:
        logger.setLevel(logging.DEBUG)

    bitbakeinfo = bitbake_runner.get_bitbake_information(args.image)
    rootfs = bitbakeinfo["rootfs_dir"]
    dpkg_status = bitbakeinfo["dpkg_status"]

    imager_bom = bitbakeinfo["imager_bom"]
    image_install_pkgs = bitbakeinfo["image_install_pkgs"]

    distro = args.distro
    if not distro:
        distro = bitbakeinfo["image_distro"].split("-")[1]

    rootfs_pkgs = parse_dpkg_status(dpkg_status)

    layers = bitbake_runner.find_layers()
    user_defined_licenses = read_license_files(layers, args.user_defined_licenses)
    license_mapping = read_license_mapping_files(
        layers, args.user_defined_license_mapping
    )

    image_deploy_dir = f"{bitbakeinfo['deploy_dir']}/images/{bitbakeinfo['machine']}"
    srcinfo_json = f"{image_deploy_dir}/all-source-info.json"
    srcinfo_pkgs = get_build_from_reciepe_packages(srcinfo_json)

    imager_bom_src_pkgs = get_build_package_data(imager_bom, srcinfo_pkgs)
    image_install_build_pkgs = get_build_package_data(image_install_pkgs, srcinfo_pkgs)

    image_manifests = manifest_parser.find_manifest_files(image_deploy_dir, bitbakeinfo["image_full_name"], bitbakeinfo["image_fstypes"])
    imager_bom_bin_pkgs = manifest_parser.collect_packages(image_manifests, imager_bom)

    create_license_data_for_recipe_build_package(imager_bom_src_pkgs, license_mapping)
    create_license_data_for_recipe_build_package(image_install_build_pkgs, license_mapping)

    packages_info = get_package_info_from_deb_file(
        bitbakeinfo["dl_dir"],
        bitbakeinfo["repo_isar_dir"],
        distro,
        bitbakeinfo["image_distro"],
        bitbakeinfo["distro_arch"],
        imager_bom_src_pkgs,
        imager_bom_bin_pkgs,
        rootfs_pkgs,
    )

    installed_pkgs = {}
    installed_pkgs.update(rootfs_pkgs)
    installed_pkgs.update(imager_bom_bin_pkgs)
    installed_pkgs.update(imager_bom_src_pkgs)
    installed_pkgs.update(image_install_build_pkgs)
    
    merge_package_data(installed_pkgs, packages_info)

    package_map = create_package_map(installed_pkgs)

    parse_copyright_text_to_license_info(rootfs, installed_pkgs, user_defined_licenses, package_map)
    
    create_license_data(installed_pkgs, license_mapping)


    output_dir = f"{bitbakeinfo['deploy_dir']}/sbom/{bitbakeinfo['image_full_name']}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_filepath = f"{output_dir}/{args.image}-{args.sbom_format}.json"

    sbom_data = None

    logger.info(f"Create {args.sbom_format} format sbom for {args.image}")

    if args.sbom_format == "cyclonedx":
        sbom_data = sbom_cyclonedx.create_cyclonedx_sbom(
            args.product,
            args.image,
            distro,
            installed_pkgs,
            args.supplier,
            license_mapping,
        )
    else:
        sbom_data = sbom_spdx.create_spdx_sbom(
            args.product, args.image, distro, installed_pkgs, args.supplier
        )

    if sbom_data:
        write_sbom_json(output_filepath, sbom_data)
        logger.info(f"sbom was created to {output_filepath}")
    else:
        logger.critical("Failed to create SBOM.")


def parse_options():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--image",
        dest="image",
        help="EMLinux image name",
        metavar="IMAGENAME",
        required=True,
    )
    parser.add_argument(
        "--sbom-format",
        dest="sbom_format",
        help="spdx or cyclonedx",
        metavar="SBOM_FORMAT",
        required=True,
    )
    parser.add_argument(
        "--distro",
        dest="distro",
        help="debian distro name(e.g. bookworm)",
        metavar="DISTRO",
    )
    parser.add_argument(
        "--licenses",
        dest="user_defined_licenses",
        help="license yaml file",
        metavar="FILE",
    )
    parser.add_argument(
        "--license-mapping",
        dest="user_defined_license_mapping",
        help="license mapping yaml file",
        metavar="FILE",
    )
    parser.add_argument(
        "--supplier",
        dest="supplier",
        help="Supplier name(e.g. company name)",
        metavar="SUPPLIER",
        required=True,
    )
    parser.add_argument(
        "--product",
        dest="product",
        help="Product name",
        metavar="PRODUCT",
        required=True,
    )
    parser.add_argument(
        "--verbose",
        dest="verbose_output",
        help="Enable verbose output",
        action="store_true",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_options())
