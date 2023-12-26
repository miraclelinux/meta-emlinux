from datetime import datetime
from typing import List

from spdx_tools.spdx.constants import DOCUMENT_SPDX_ID
from spdx_tools.common.spdx_licensing import spdx_licensing
from spdx_tools.spdx.model import (
    Actor,
    ActorType,
    CreationInfo,
    Document,
    ExternalPackageRef,
    ExternalPackageRefCategory,
    Package,
    PackagePurpose,
    Relationship,
    RelationshipType,
)
from spdx_tools.spdx.validation.document_validator import validate_full_spdx_document
from spdx_tools.spdx.validation.validation_message import ValidationMessage
from spdx_tools.spdx.writer.write_anything import write_file
from spdx_tools.spdx.model.spdx_none import SpdxNone

import re
import json
import tempfile
from urllib.parse import quote
import uuid

import logging
logger = logging.getLogger("emlinux-sbom-creator")

import os.path
import sys
sys.path.append(os.path.dirname(__file__))
import sbom_common
import licensing

def debian_section_to_component_type(section):
    if section == "libs" or section == "oldlibs":
        return PackagePurpose.LIBRARY
    elif section == "fonts":
        return PackagePurpose.OTHER
    elif section == "doc":
        return PackagePurpose.FILE
    elif section == "kernel":
        return PackagePurpose.OPERATING_SYSTEM

    return PackagePurpose.APPLICATION

def get_maintainer_name_and_email(pkg):
    s = pkg["maintainer"]

    email_pattern = r"<([^>]+)>"
    email_match = re.search(email_pattern, s)
    email = ""

    if email_match:
        email = email_match.group(1)

    name_pattern = r"^(.*?)\s+\S+@\S+$"
    name_match = re.search(name_pattern, s)
    name = ""

    if name_match:
        name = name_match.group(1)

    return email, name

def create_uniq_list(data):
    return list(set(data))

def split_licenses(lic, sep):
    arr = []

    lics = lic.split(sep)
    for l in lics:
        arr.append(l.strip())

    return arr

def create_license_string(pkg, license_mapping):
    arr = []
    s = ""

    licenses = licensing.normalize_for_spdx(create_uniq_list(pkg["licenses"]), license_mapping)

    s = " AND ".join(licenses)
    return spdx_licensing.parse(s)

def create_package_info(pkg, distro, license_mapping):
    email, name = get_maintainer_name_and_email(pkg)

    licenses = create_license_string(pkg, license_mapping)
    purl_str = quote(f"pkg:deb/debian/{pkg['package']}@{pkg['version']}?arch={pkg['arch']}&distro={distro}", safe = "@=&/:?")

    pkg_name_hash = sbom_common.package_name_hash(pkg["package"], pkg["version"])

    spdxid = f"SPDXRef-Package-{pkg_name_hash}"

    package = Package(
        name = pkg["package"],
        spdx_id = spdxid,
        download_location = SpdxNone(),
        version = pkg["version"],
        source_info = f"build from: {pkg['source']} {pkg['version']}",
        supplier = Actor(ActorType.ORGANIZATION, name, email),
        license_concluded = licenses,
        license_declared = licenses,
        primary_package_purpose = debian_section_to_component_type(pkg["section"]),
        external_references = [
            ExternalPackageRef(
                category = ExternalPackageRefCategory.PACKAGE_MANAGER,
                reference_type = "purl",
                locator = purl_str,
            )
        ],
        files_analyzed = False,
        attribution_texts = [ f"PkgID: {pkg['package']}@{pkg['version']}" ],
        description = pkg["description"],
    )

    return spdxid, package

def create_meta(product, image, supplier):
    today = datetime.now()
    spdxid = DOCUMENT_SPDX_ID
    doc_name = f"{product}"

    ci = CreationInfo(
        spdx_version = "SPDX-2.3",
        spdx_id = spdxid,
        name = doc_name,
        data_license = "CC0-1.0",
        # see https://spdx.github.io/spdx-spec/v2.3/document-creation-information/#65-spdx-document-namespace-field
        document_namespace = f"https://github.com/miraclelinux/meta-emlinux/spdx/{doc_name}-{uuid.uuid4()}",
        creators = [Actor(ActorType.ORGANIZATION, supplier)],
        created = datetime(today.year, today.month, today.day, today.hour, today.minute, today.second),
    )

    return spdxid, Document(ci)

def create_spdx_sbom(product, image, distro, packages, supplier, license_mapping):
    doc_spdxid, doc = create_meta(product, image, supplier)

    for name in packages:
        pkg_spdxid, package = create_package_info(packages[name], distro, license_mapping)
        doc.packages.append(package)
        doc.relationships.append(Relationship(doc_spdxid, RelationshipType.DESCRIBES, pkg_spdxid))
    
    validation_messages = validate_full_spdx_document(doc)

    if validation_messages:
        logger.debug("SPDX Validation message")
        for vm in validation_messages:
            logger.debug(f"- {vm.validation_message}")
    
    tempname = f"{tempfile.mktemp()}.json"

    write_file(doc, tempname, False)
    sbom_data = None
    with open(tempname, "r") as f:
        sbom_data = json.loads(f.read())

    return sbom_data
