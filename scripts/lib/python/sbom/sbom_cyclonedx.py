from packageurl import PackageURL

from cyclonedx.exception import MissingOptionalDependencyException
from cyclonedx.factory.license import LicenseFactory
from cyclonedx.model import HashType, AttachedText
from cyclonedx.model.bom import Bom
from cyclonedx.model.component import Component, ComponentType
from cyclonedx.model.contact import OrganizationalEntity
from cyclonedx.model.bom_ref import BomRef
from cyclonedx.output.json import JsonV1Dot5
from cyclonedx.schema import SchemaVersion
from cyclonedx.validation.json import JsonStrictValidator
from cyclonedx.model.license import LicenseExpression, DisjunctiveLicense

import json
import re
import os.path
import sys

sys.path.append(os.path.dirname(__file__))
import sbom_common

import logging

logger = logging.getLogger("emlinux-sbom-creator")

def debian_section_to_component_type(section):
    """
    ComponentType is defined in following url.
    https://cyclonedx-python-library.readthedocs.io/en/latest/autoapi/cyclonedx/model/component/index.html#cyclonedx.model.component.ComponentType.APPLICATION

    Debian's package categories is in following url.
    https://packages.debian.org/stable/
    """
    if section == "libs" or section == "oldlibs":
        return ComponentType.LIBRARY
    elif section == "fonts":
        return ComponentType.DATA
    elif section == "doc":
        return ComponentType.FILE
    elif section == "kernel":
        return ComponentType.OPERATING_SYSTEM

    return ComponentType.APPLICATION


def create_organization_entity(pkg):
    return OrganizationalEntity(
        name=pkg["maintainer"],
    )


def create_package_url(distro, pkg):
    return PackageURL(
        "deb/debian",
        "",
        pkg["package"],
        pkg["version"],
        {
            "arch": pkg["arch"],
            "distro": distro,
        },
    )


def create_hashes_data(pkg):
    return [HashType.from_composite_str(f"sha256:{pkg['sha256sum']}")]


def build_cyclonedx_licenses(pkg):
    """
    Builds a list of CycloneDX license objects from package metadata.
    Handles the distinction between standard SPDX IDs and custom LicenseRef identifiers.
    """
    licenses_string = pkg.get("license_id_text", "")
    has_license_ref = "LicenseRef-" in licenses_string

    # Pattern 1: No custom licenses found (all are standard SPDX IDs)
    # -> Unify into a single LicenseExpression to avoid schema validation errors.
    if not has_license_ref:
        if licenses_string:
            return [LicenseExpression(value=licenses_string)]
        return []

    # Pattern 2: Custom licenses found (LicenseRef-xxx exists)
    # -> Unify everything into a list of DisjunctiveLicense objects to avoid mixed-type errors.
    cdx_licenses = []

    for norm_lic in pkg.get("normalized_licenses", []):
        synopsis = norm_lic.get("parsed_synopsis", "").strip()
        if not synopsis:
            continue

        # Split partially-parsed elements that contain operators (AND/OR) or parentheses
        # e.g., "(BSD-4-clause-UC AND LicenseRef-bash-MIT-like...)"
        #       -> ["BSD-4-clause-UC", "LicenseRef-bash-MIT-like..."]
        raw_identifiers = re.split(r"[\s()]+(?:AND|OR)?[\s()]*|[\s()]+", synopsis)
        identifiers = [
            id_str
            for id_str in raw_identifiers
            if id_str and id_str not in ("AND", "OR", "and", "or")
        ]

        for single_id in identifiers:
            # 2-A. For custom identifiers (LicenseRef-xxx)
            if single_id.startswith("LicenseRef-"):
                text_map = norm_lic.get("extracted_texts_map", {})
                license_text = (
                    text_map.get(single_id) or text_map.get(synopsis) or "PUBLIC DOMAIN"
                )

                cdx_licenses.append(
                    DisjunctiveLicense(
                        name=single_id,
                        text=AttachedText(
                            content=license_text, content_type="text/plain"
                        ),
                    )
                )
            # 2-B. For standard SPDX IDs when custom licenses coexist in the same array
            # -> Store in the 'name' field instead of 'id' to bypass strict schema validation rules.
            else:
                cdx_licenses.append(DisjunctiveLicense(name=single_id))

    return cdx_licenses


def create_component(factory, distro, pkg, license_mapping):
    # https://cyclonedx.org/docs/1.5/json/#components
    # https://github.com/package-url/purl-spec

    purl_info = create_package_url(distro, pkg)
    pkgname_hash = sbom_common.package_name_hash(pkg["package"], pkg["source"])

    return Component(
        type=debian_section_to_component_type(pkg["section"]),
        name=pkg["package"],
        group=pkg["source"],
        version=pkg["version"],
        licenses=build_cyclonedx_licenses(pkg),
        supplier=create_organization_entity(pkg),
        bom_ref=BomRef(f"{pkg['package']}@{pkg['version']}-{pkgname_hash}"),
        purl=purl_info,
        hashes=create_hashes_data(pkg),
        description=pkg["description"],
    )


def create_meta(factory, product, image, supplier):
    license = factory["lc_factory"].make_from_string("MIT")

    product_name_hash = sbom_common.package_name_hash(product, "")

    factory["bom"].metadata.component = root_component = Component(
        name=image,
        type=ComponentType.OPERATING_SYSTEM,
        licenses=[license],
        bom_ref=BomRef(f"{product}-{product_name_hash}"),
        supplier=OrganizationalEntity(name=supplier),
    )

    return root_component


def create_sbom_json(bom):
    outputter = JsonV1Dot5(bom)
    serialized_json = outputter.output_as_string(indent=2)
    validator = JsonStrictValidator(SchemaVersion.V1_5)

    try:
        validation_errors = validator.validate_str(serialized_json)
        if validation_errors:
            logger.debug("CycloneDX Validation message")
            logger.debug(validation_errors)
            return None

        return json.loads(serialized_json)
    except MissingOptionalDependencyException as error:
        logger.debug("JSON-validation was skipped due to", error)
        return None

    return None


def init_bom():
    return {
        "lc_factory": LicenseFactory(),
        "bom": Bom(),
    }


def create_cyclonedx_sbom(product, image, distro, packages, supplier, license_mapping):
    factory = init_bom()

    root = create_meta(factory, product, image, supplier)
    components = []

    for name in packages:
        component = create_component(factory, distro, packages[name], license_mapping)
        factory["bom"].components.add(component)
        components.append(component)

    factory["bom"].register_dependency(root, components)

    return create_sbom_json(factory["bom"])
