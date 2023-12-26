def normalize_licenses(lics, license_mapping):
    new_licenses = []

    for lic in lics:
        if lic in license_mapping:
            new_licenses.append(license_mapping[lic])
        else:
            new_licenses.append(lic)
    return new_licenses

def split_licenses(lic, sep):
    arr = []

    lics = lic.split(sep)
    for l in lics:
        arr.append(l.strip())

    return arr


def split_licesense_and_normalize(lic, license_mapping):
    """
    Normalize license string based on https://scancode-licensedb.aboutcode.org/
    """
    lics = []
    
    if lic in license_mapping:
        return [license_mapping[lic]]

    if "~" in lic:
        lic = lic.replace("~", "")

    if " exception" in lic:
        lic = lic.replace(" exception", "-exception")

    if ", and " in lic:
        lics += normalize_licenses(split_licenses(lic, ", and "), license_mapping)
    elif "/" in lic:
        tmp = normalize_licenses(split_licenses(lic, "/"), license_mapping)
        lics.append("-".join(tmp))
    elif " with " in lic:
        tmp = normalize_licenses(split_licenses(lic, " with "), license_mapping)
        lics.append(" WITH ".join(tmp))
    elif "-WITH-" in lic:
        tmp = normalize_licenses(split_licenses(lic, "-WITH-"), license_mapping)
        lics.append(" WITH ".join(tmp))
    elif " and/or " in lic:
        tmp = normalize_licenses(split_licenses(lic, "and/or"), license_mapping)
        lics.append("-and-or-".join(" and-or ", "-and-or-"))
    elif " and-or " in lic:
        tmp = normalize_licenses(split_licenses(lic, " and-or "), license_mapping)
        lics.append("-and-or-".join(tmp))
    else:
        lics += normalize_licenses([lic], license_mapping)

    return lics

def split_licenses_simple(licenses):
    ret = []
    splited = False

    for lic in licenses:
        if ", and " in lic:
            ret += lic.split(", and ")
            splited = True
        elif " and " in lic:
            ret += lic.split(" and ")
            splited = True
        elif " or " in lic:
            ret += lic.split(" or ")
            splited = True
        elif " OR " in lic:
            ret += lic.split(" OR ")
            splited = True
        else:
            ret.append(lic)

    if splited:
        return split_licenses_simple(ret)
    
    return ret

def normalize_for_spdx(licenses, license_mapping):
    tmp = []
    normalized = []

    lics = split_licenses_simple(licenses)
    for lic in lics:
        tmp += split_licesense_and_normalize(lic, license_mapping)

    for lic in tmp:
        if " " in lic:
            normalized.append(lic.replace(" ", "-"))
        else:
            normalized.append(lic)

    return list(set(normalized))

def normalize_for_cyclonedx(licenses):
    return split_licenses_simple(licenses)

