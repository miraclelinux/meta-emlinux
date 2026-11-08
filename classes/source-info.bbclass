
python do_collect_source_info() {
    import json

    log_file = f"{d.getVar('T')}/source-info.json"

    source_info = d.getVar("EMLINUX_SOURCE_FROM")
    if source_info is None:
        # if EMLINUX_SOURCE_FROM is not set, we should set unknown to reduce false positive.
        source_info = "unknown"

    license = d.getVar("LICENSE")
    if license is None:
        license = "NOASSERTION"

    description = d.getVar("DESCRIPTION")
    if description is None:
        description = "no description"

    maintainer = d.getVar("MAINTAINER")
    if maintainer is None:
        maintainer = "Unknown user"

    pv = d.getVar("PV")
    if pv is None:
        pv = "Unknown version"

    pn = d.getVar("PN")
    if pn is None:
        pn = "Unknown package name"

    arch = d.getVar("DISTRO_ARCH")
    if arch is None:
        arch = "Unknown architecture"

    provides = d.getVar("PROVIDES")
    if provides is None:
        provides = pn
    else:
        provides = provides.split()

    section = d.getVar("SECTION")
    if section is None:
        section = "unknown"

    homepage = d.getVar("HOMEPAGE")
    if homepage is None:
        homepage = "No Homepage"

    data = {
        "source_package_name": pn,
        "source_from": source_info,
        "maintainer": maintainer,
        "license": license,
        "description": description,
        "version": pv,
        "arch": arch,
        "provides": provides,
        "section": section,
        "homepage": homepage,
    }

    with open(log_file, "w") as f:
        json.dump(data, f, indent=4)
}

python do_merge_source_info() {
    import glob
    import json

    distro = d.getVar("DISTRO")
    distro_arch = d.getVar("DISTRO_ARCH")

    tmpdir = d.getVar("TMPDIR")

    basepath = f"{tmpdir}/work/{distro}-{distro_arch}"
    search_path = f"{basepath}/*/*/temp/source-info.json"

    source_info = {}

    for file in glob.glob(search_path):
        with open(file) as f:
            data = json.load(f)
            pkg = data["source_package_name"]
            source_info[pkg] = data

    source_info = dict(sorted(source_info.items(), key=lambda x: x[0], reverse=False))

    source_info_file = d.getVar("DEPLOY_DIR_IMAGE") + "/all-source-info.json"

    with open(source_info_file, "w") as f:
        json.dump(source_info, f, indent=4)

}

addtask collect_source_info after do_dpkg_source before do_dpkg_build
addtask merge_source_info after do_image before do_deploy
