from packageurl import PackageURL

from cyclonedx.exception import MissingOptionalDependencyException
from cyclonedx.factory.license import LicenseFactory
from cyclonedx.model import OrganizationalEntity, HashType
from cyclonedx.model.bom import Bom
from cyclonedx.model.component import Component, ComponentType
from cyclonedx.model.bom_ref import BomRef
from cyclonedx.output.json import JsonV1Dot5
from cyclonedx.schema import SchemaVersion
from cyclonedx.validation.json import JsonStrictValidator
from cyclonedx.model.license import LicenseExpression

import json

import os.path
import sys
sys.path.append(os.path.dirname(__file__))
import sbom_common
import licensing

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

def make_license_info(factory, licenses, license_mapping):
    ret = []

    uniq_licenses = licensing.normalize_for_cyclonedx(licenses)
    for lic in uniq_licenses:
        tmp = factory["lc_factory"].make_with_name(lic)
        ret.append(tmp)

    return ret

def create_organization_entity(pkg):
    return OrganizationalEntity(
        name = pkg["maintainer"],
    )

def create_package_url(distro, pkg):
    return PackageURL("deb/debian",
            "",
            pkg["package"],
            pkg["version"], 
            {
                "arch": pkg["arch"], 
                "distro": distro,
            }
        )

def create_hashes_data(pkg):
    return [HashType.from_composite_str(f"sha256:{pkg['sha256sum']}")]

def create_component(factory, distro, pkg, license_mapping):
    # https://cyclonedx.org/docs/1.5/json/#components
    # https://github.com/package-url/purl-spec

    purl_info = create_package_url(distro, pkg)
    pkgname_hash = sbom_common.package_name_hash(pkg['package'], pkg['source'])

    return Component(
        type = debian_section_to_component_type(pkg["section"]),
        name = pkg["package"],
        group = pkg["source"],
        version = pkg["version"],
        licenses = make_license_info(factory, pkg["licenses"], license_mapping),
        supplier = create_organization_entity(pkg),
        bom_ref = BomRef(f"{pkg['package']}@{pkg['version']}-{pkgname_hash}"),
        purl = purl_info,
        hashes = create_hashes_data(pkg),
        description = pkg["description"],
    )

def create_meta(factory, product, image, supplier):
    license = factory["lc_factory"].make_from_string('MIT')
    
    product_name_hash = sbom_common.package_name_hash(product, "")

    factory["bom"].metadata.component = root_component = Component(
        name = image,
        type = ComponentType.OPERATING_SYSTEM,
        licenses = [ license ],
        bom_ref = BomRef(f"{product}-{product_name_hash}"),
        supplier = OrganizationalEntity(name = supplier),
    )

    return root_component

def create_sbom_json(bom):
    outputter = JsonV1Dot5(bom)
    serialized_json = outputter.output_as_string(indent = 2)
    validator = JsonStrictValidator(SchemaVersion.V1_5)

    try:
        validation_errors = validator.validate_str(serialized_json)
        if validation_errors:
            logger.debug('JSON invalid', 'ValidationError:', repr(validation_errors), sep='\n', file=sys.stderr)
            return None

        return json.loads(serialized_json)
    except MissingOptionalDependencyException as error:
        logger.debug('JSON-validation was skipped due to', error)
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

