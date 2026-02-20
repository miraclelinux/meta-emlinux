#!/usr/bin/python3

#
# EMLinux CVE checker
#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

from lib.python.cve.plugin.eml_cve_plugin_base import EmlCvePlugin
import lib.python.cve.common_libs as cl
from lib.python.cve.nvd_lib import CveCheckMergedList, NvdCveInfoListCreator
from lib.python.cve.cve_reporter import CveReporter
from lib.python.package_info import PackageInfoHelper, PackageList
from lib.python.cve.cve_product import CveProductList
from lib.python.cve.kev_info import KevInfoList
import lib.python.cve.kev_cve as kev_cve
import lib.python.bitbake_runner as bitbake_runner

import argparse
import sys
import os, os.path
import yaml
from typing import Any
import pathlib
import traceback
import re
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(levelname)s: %(message)s")
logger = logging.getLogger("emlinux-cve-check")

import glob

import importlib.util
from concurrent.futures import ThreadPoolExecutor, as_completed


def create_ignore_list(
    emlinux_layer_dir: str,
    installed_packages: PackageList,
    debian_codename: str,
    extra_cve_check_ignore: str,
):
    name = f"{emlinux_layer_dir}/conf/cve/cve_check_ignore.yml"

    def read_ignore_list(filename):
        if filename is None:
            return {}

        try:
            with open(filename) as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warn(f"File {filename} is not found")
            return {}

    # 1. Read default ignore data
    tmp_merge_list = read_ignore_list(name)
    # 2. Read extra ignore list
    extra_data = read_ignore_list(extra_cve_check_ignore)

    # backward compatibility
    def make_backward_compatibility(data):
        tmp = {}
        for pkg in data:
            if type(data[pkg]) is list:
                tmp[pkg] = {"all": data[pkg]}
            else:
                tmp[pkg] = data[pkg]
        return tmp

    tmp_merge_list = make_backward_compatibility(tmp_merge_list)
    extra_data = make_backward_compatibility(extra_data)

    # 3. Merge default and extra list
    if extra_data:
        for pkg in extra_data:
            if pkg in tmp_merge_list:
                for ek in extra_data[pkg].keys():
                    if ek in tmp_merge_list[pkg]:
                        tmp_merge_list[pkg][ek] += extra_data[pkg][ek]
                    else:
                        tmp_merge_list[pkg][ek] = extra_data[pkg][ek]
            else:
                tmp_merge_list[pkg] = extra_data[pkg]

    # 4. Create complete ignore list
    # This step does not collect CVE IDs which are not target distribution/linux version.
    ignore_list = {}
    all_used = []
    for pkg in tmp_merge_list:
        d = tmp_merge_list[pkg]
        for version in d.keys():
            if debian_codename == version:
                ignore_list[pkg] = d[version]
            elif version == "all":
                if not pkg in ignore_list:
                    ignore_list[pkg] = []
                all_used.append(pkg)
            else:
                if not pkg in installed_packages:
                    continue
                pkg_version = str(installed_packages.get_upstream_version(pkg))
                if str(version) == pkg_version:
                    ignore_list[pkg] = d[version]
                    break

                ver_pattern = rf"\b{re.escape(str(version))}(?!\d)"
                m = re.search(ver_pattern, pkg_version)
                if m:
                    if not pkg in ignore_list:
                        ignore_list[pkg] = d[version]
                    else:
                        ignore_list[pkg].extend(d[version])

    for pkg in all_used:
        ignore_list[pkg].extend(tmp_merge_list[pkg]["all"])
    return ignore_list


def create_cve_check_merged_list(
    src_pkg_names: list[str], check_results: Any
) -> CveCheckMergedList:
    cve_check_merged_list = CveCheckMergedList()

    cve_ids = create_cve_id_list_by_src_pkg_name_from_check_result(
        src_pkg_names, check_results
    )
    for src_pkg_name in src_pkg_names:
        for cveid in cve_ids:
            for cr in check_results:
                vulns = cr[src_pkg_name]
                if vulns is None:
                    # Plugin doesn't have CVE information for the src_pkg_name
                    continue
                if cveid in vulns:
                    cve_check_merged_list.add_data(
                        src_pkg_name, cveid, vulns[cveid], cr.priority
                    )
                else:
                    # Plugin doesn't have CVE information for the CVE
                    pass
                    # logger.debug(f"{cveid} {src_pkg_name} is not found")
    return cve_check_merged_list


def create_cve_id_list_by_src_pkg_name_from_check_result(
    src_pkg_names: list[str], check_results: Any
) -> list[str]:
    tmp_cve_ids = []
    for src_pkg_name in src_pkg_names:
        for cr in check_results:
            ci = cr.cve_ids_by_src_pkg(src_pkg_name)
            if ci:
                tmp_cve_ids.extend(ci)
    return list(dict.fromkeys(tmp_cve_ids))


# make a source package name list which content has CVE information
def create_src_package_name_list_from_check_result(check_results: Any) -> list[str]:
    tmp_list = []
    for result in check_results:
        tmp_list.extend(result.src_pkg_names())
    return list(dict.fromkeys(tmp_list))


def read_recipe_source_info(deploy_dir: str) -> Any:
    filepath = deploy_dir + "/all-source-info.json"
    return cl.read_json(filepath)


def load_plugin(plugin_file: str) -> EmlCvePlugin:
    path = pathlib.Path(plugin_file).resolve()
    if not path.exists():
        logger.error(f"Failed to find plugin {plugin_file}")
        exit(1)

    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    if not spec or not spec.loader:
        logger.error(f"Fail to load spec from {plugin_file}")
        exit(1)

    mod = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        logger.error(e)
        traceback.print_exc()
        exit(1)

    for obj in vars(mod).values():
        if (
            isinstance(obj, type)
            and issubclass(obj, EmlCvePlugin)
            and obj is not EmlCvePlugin
        ):
            return obj

    logger.info(f"Plugin is not found in {plugin_file}")

    return None


def load_plugins(plugin_files: list[str]):
    plugins = []

    for plugin_file in plugin_files:
        logger.debug(f"loading {plugin_file}")
        obj = load_plugin(plugin_file)
        if obj:
            plugins.append(obj)

    return plugins


# Plugin file name convention:
# 1. Plugin file must be located in scripts/lib/python/cve/plugin directory
# 2. Plugin file name must be start with eml_cve_ then ends with _plugin.py
#    e.g. eml_cve_myplugin_plugin.py
def find_plugins(disable_plugins: list[str]) -> list[str]:
    layer_dirs = bitbake_runner.find_layers()
    plugins = []

    plugin_dir = "/scripts/lib/python/cve/plugin/"
    for ld in layer_dirs:
        d = ld + plugin_dir
        pattern = f"{d}/eml_cve_*_plugin.py"
        for plugin in glob.glob(pattern):
            p = os.path.splitext(os.path.basename(plugin))[0]
            if not p in disable_plugins:
                plugins.append(plugin)
            else:
                logger.info(f"Plugin '{p}' is disabled")

    return plugins


def cve_check_worker(plugin: EmlCvePlugin, args: Any):
    logger.debug(f"run {plugin.plugin_name}")

    if not args.skip_update:
        ret = plugin.update_database()
        if not ret:
            raise Exception(f"{plugin.plugin_name}: Failed to update datebase")

    if args.update_cve_databese_only:
        return {}

    return plugin.run_check()


def fetch_kev_data(cve_data_dir: str) -> KevInfoList:
    try:
        kev_json = kev_cve.fetch_kev_data(cve_data_dir)
        return KevInfoList(cl.read_json(kev_json))
    except:
        return KevInfoList({})


def create_disable_plugins_list(user_given_plugins: str) -> list[str]:
    if not user_given_plugins:
        return []

    disable_plugins = []

    do_not_disable = ["eml_cve_nvd_plugin"]
    disable_plugins_tmp = [p.strip() for p in user_given_plugins.split(",")]
    for p in disable_plugins_tmp:
        if p not in do_not_disable:
            disable_plugins.append(p)
        else:
            logger.warning(f"Plugin '{p}' cannot be disabeld")

    return disable_plugins


def main(args: dict):
    if args.verbose_output:
        logger.setLevel(logging.DEBUG)

    bitbakeinfo = bitbake_runner.get_bitbake_information(args.image_name)
    disable_plugins = create_disable_plugins_list(args.disable_plugins)

    dpkg_status_file = (
        bitbakeinfo["dpkg_status"]
        if not args.dpkg_status_file
        else args.dpkg_status_file
    )
    if not os.path.exists(dpkg_status_file):
        logger.error(f"File {dpkg_status_file} is not found")
        exit(1)

    debian_codename = args.debian_codename
    if not debian_codename:
        debian_codename = bitbakeinfo["image_distro"].split("-")[1]

    # Read dpkg file to get installed package information
    installed_packages = PackageInfoHelper.parse_dpkg_status_file(
        dpkg_status_file, debian_codename, target_source_package=args.target_source_package,
    )

    # Check recipe's source code provenance
    recipe_source_info = read_recipe_source_info(bitbakeinfo["deploy_image_dir"])
    installed_packages.merge_recipe_source_info(recipe_source_info)

    # Read cve product list
    cve_product_list = CveProductList()
    cve_product_list.create_product_list(
        installed_packages, bitbakeinfo["emlinux_layer_dir"], args.extra_cve_product
    )

    # Read ignore list
    ignore_list = create_ignore_list(
        bitbakeinfo["emlinux_layer_dir"],
        installed_packages,
        debian_codename,
        args.extra_cve_check_ignore,
    )

    cve_data_dir = f"{bitbakeinfo['dl_dir']}/CVE"
    cl.create_directory(cve_data_dir)

    # Find and load plugins
    plugin_files = find_plugins(disable_plugins)
    plugin_objs = load_plugins(plugin_files)

    # Create plugin instance
    plugins = []
    for obj in plugin_objs:
        o = obj(cve_data_dir, args, bitbakeinfo, installed_packages, cve_product_list)
        plugins.append(o)

    check_results = []
    max_workers = min(args.threads, len(plugins))

    # Run all plugins
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(cve_check_worker, p, args) for p in plugins]
        for f in as_completed(futures):
            try:
                check_results.append(f.result())
            except Exception as e:
                logger.error(f"error: {e}")
                traceback.print_exc()
                exit(1)

    if args.update_cve_databese_only:
        logger.info("Updating database finished.")
        exit(0)

    # Sort CVE data by plugin priority
    check_results = sorted(check_results, key=lambda d: d.priority)

    # Merge CVE results
    src_pkg_names = create_src_package_name_list_from_check_result(check_results)

    cve_check_merged_list = create_cve_check_merged_list(src_pkg_names, check_results)

    cve_check_merged_list.apply_ignore_list_info(ignore_list)

    # Load KEV data
    kev_info_list = fetch_kev_data(cve_data_dir)

    # Create CVE report data
    creator = NvdCveInfoListCreator(cve_data_dir, installed_packages, kev_info_list)
    creator.create_cve_info_list(cve_check_merged_list)

    cve_info_list = creator.get_nvd_info_list()

    # Write CVE report
    output_base_dir = (
        f"{bitbakeinfo['deploy_dir']}/cve/{bitbakeinfo['image_full_name']}"
    )
    # Use cve_check_ng scripts own directory for testing
    output_base_dir = f"{output_base_dir}/cve_check_ng"

    reporter = CveReporter(output_base_dir, bitbakeinfo["image_full_name"])
    reporter.write_report(args.output_format, cve_info_list, installed_packages)


def parse_options():
    parser = argparse.ArgumentParser()
    plugin_opts = parser.add_argument_group("arguments for plugins")
    cve_check_opts = parser.add_argument_group("arguments for cve check")

    # misc options
    parser.add_argument(
        "--verbose",
        dest="verbose_output",
        help="Enable verbose output",
        default=False,
        action="store_true",
    )

    # CVE check core options
    cve_check_opts.add_argument(
        "--debian-codename",
        dest="debian_codename",
        help="debian codename(bookworm, trixie, and etc)",
        metavar="DEBIANCODENAME",
    )
    cve_check_opts.add_argument(
        "--output-format",
        dest="output_format",
        help="output format. available formats are text, json. formats can be comma separated string(e.g. text,json)",
        default="text",
        metavar="OUTPUTFORMAT",
    )
    cve_check_opts.add_argument(
        "--cve-product",
        dest="extra_cve_product",
        help="User defined cve-product file",
        metavar="CVEPRODUCT",
    )
    cve_check_opts.add_argument(
        "--cve-ignore",
        dest="extra_cve_check_ignore",
        help="User defined cve-check-ignore file",
        metavar="CVEIGNORE",
    )
    cve_check_opts.add_argument(
        "--image-name",
        dest="image_name",
        help="EMLinux image name(e.g. emlinux-image-base, emlinux-image-weston)",
        metavar="IMAGENAME",
        required=True,
    )
    cve_check_opts.add_argument(
        "--target-source-package",
        dest="target_source_package",
        help="Only check given debian source package(e.g. bash, util-linux",
        metavar="DEBIAN SOURCE PACKAGE NAME",
    )
    cve_check_opts.add_argument(
        "--dpkg-status-file",
        dest="dpkg_status_file",
        help="Use specific dpkg_status file instead of default",
        metavar="DPKG STATUS FILE",
    )
    cve_check_opts.add_argument(
        "--threads", default=1, help="Number of thread for cve check"
    )

    # options for plugins
    plugin_opts.add_argument(
        "--nvd-api-key",
        dest="nvd_api_key",
        help="API key for NVD API",
        metavar="NVDAPIKEY",
    )
    plugin_opts.add_argument(
        "--cve-db-predownload",
        dest="cve_db_predownload",
        action="store_true",
        help="Enable CVE database predownload.URL should be defined by CVE_DB_PREDOWNLOAD_URL in conf/local.conf.",
    )
    plugin_opts.add_argument(
        "--update-cve-databese-only",
        dest="update_cve_databese_only",
        default=False,
        action="store_true",
        help="Do not run cve check. Update CVE database only.",
    )
    plugin_opts.add_argument(
        "--skip-update",
        default=False,
        action="store_true",
        help="Skip update CVE databases",
    )
    plugin_opts.add_argument(
        "--disable-plugins",
        help="List plugin names to be disabled without .py extension (comma separated). e.g. --disable-plugins eml_cve_debian_plugin,eml_cve_your_plugin",
    )
    return parser.parse_args()


if __name__ == "__main__":
    logger.info("|------------------------------|")
    logger.info("| This is experimental version |")
    logger.info("|------------------------------|")
    main(parse_options())
