from spdx_tools.common.spdx_licensing import spdx_licensing

from license_expression import (
    ExpressionParseError,
    ExpressionError,
)

import hashlib
import re

import logging

logger = logging.getLogger("emlinux-sbom-creator")

def create_licenseref_id(pkgname, lic):
    m = hashlib.sha256()
    m.update(b"{pkgname}-{lic}")
    h = m.hexdigest()
    return f"LicenseRef-{pkgname}-{lic}-{h}"


def split_synopsis(synopsis):
    s = synopsis
    s = re.sub(r"\s+and/or\s+", " OR ", s, flags=re.IGNORECASE)
    s = re.sub(r",\s+and\s+", " AND ", s, flags=re.IGNORECASE)
    s = re.sub(r",\s+or\s+", " OR ", s, flags=re.IGNORECASE)

    return re.split(
        r"(\s+\bAND\b\s+|\s+\bOR\b\s+|\s+\band\b\s+|\s+\bor\s+|\s*,\s*)",
        s,
        flags=re.IGNORECASE,
    )


def split_synopsis_tokens_only(synopsis):
    raw_tokens = split_synopsis(synopsis)

    tokens = [
        t.strip()
        for t in raw_tokens
        if t and t.strip() and t.strip().upper() not in ["AND", "OR", ","]
    ]

    return tokens


def sanitize_spdx_idstring(text: str) -> str:
    # Replace invalid charcters for SPDX license ID to "-"
    sanitized = re.sub(r"[^A-Za-z0-9.-]", "-", text)
    if not text == sanitized:
        logger.debug(f"Convert {text} to {sanitized}")
    sanitized = re.sub(r"-+", "-", sanitized)

    return sanitized.strip(".-")


def get_license_text_by_name(license_texts, licence_name):
    if license_texts.get(licence_name) is None:
        return "No license information is available."

    return license_texts[licence_name]


def debian_synopsis_to_spdx_license_id(
    pkgname, synopsis, license_texts, license_mapping
):
    license_data = {}
    extracted_texts_map = {}

    tokens = split_synopsis(synopsis)
    processed_tokens = []
    has_operator = False

    for token in tokens:
        if not token:
            continue

        token_strip = token.strip().upper()

        if token_strip in ["AND", "OR"] or "," in token:
            has_operator = True
            if token_strip == "AND":
                processed_tokens.append(" AND ")
            elif token_strip == "OR":
                processed_tokens.append(" OR ")
            elif "," in token:
                processed_tokens.append(" AND ")
            continue

        lic = token.strip()
        license_id = None

        try:
            if lic in license_mapping:
                lic = license_mapping[lic]
            spdx_licensing.parse(lic)
            error = spdx_licensing.validate(lic)
            if error and len(error.errors) > 0:
                raise ExpressionError(error.errors)
            license_id = lic

        except Exception as e:
            sanitaized_lic = lic

            # logger.warning(f"Exception type is {type(e)}")
            if type(e) == ExpressionError or type(e) == ExpressionParseError:
                # "NTP~legal-disclaimer" : this type of license is thrown as ExpressionError
                # "LGPL-2.1+ with OpenSSL exception" : this type of license is thrown as ExpressionParseError
                sanitaized_lic = sanitize_spdx_idstring(lic)

            if lic in license_texts:
                license_id = create_licenseref_id(pkgname, sanitaized_lic)
                logger.debug(
                    f"License token is in license texts. Token '{lic}' -> Create extracted_license {license_id}"
                )
                extracted_texts_map[license_id] = get_license_text_by_name(
                    license_texts, lic
                )
            elif synopsis in license_texts:
                license_id = create_licenseref_id(pkgname, sanitaized_lic)
                logger.debug(
                    f"Synopsis is in license texts. Synopsis {synopsis} -> Create extracted_license {license_id}"
                )
                extracted_texts_map[license_id] = get_license_text_by_name(
                    license_texts, synopsis
                )
            else:
                if lic == "public-domain" or lic == "PublicDomain":
                    license_id = create_licenseref_id(pkgname, sanitaized_lic)
                    logger.debug("Set dummy Extracted text for public domain lincense")
                    extracted_texts_map[license_id] = "PUBLIC DOMAIN"
                elif not lic == "NOASSERTION":
                    logger.warning(
                        f"{pkgname}: Cannot understand licence {lic} so set 'NOASSERTION'"
                    )
                    license_id = "NOASSERTION"
                else:
                    license_id = "NOASSERTION"

        processed_tokens.append(license_id)

    parsed_licenses = "".join(processed_tokens)
    parsed_licenses = re.sub(r"\s+", " ", parsed_licenses).strip()

    if has_operator and not (
        parsed_licenses.startswith("(") and parsed_licenses.endswith(")")
    ):
        parsed_licenses = f"({parsed_licenses})"

    license_data["parsed_synopsis"] = parsed_licenses
    license_data["extracted_texts_map"] = extracted_texts_map

    return license_data


def create_single_line_license_id_text(licenses):
    ret = None
    for license in licenses:
        synopsis = license["parsed_synopsis"]
        if ret is None:
            ret = synopsis
        else:
            ret = f"{ret} AND {synopsis}"

    return ret
