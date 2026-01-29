
python do_collect_source_info() {
    import json

    log_file = f"{d.getVar('T')}/source-info.json"

    source_info = d.getVar("EMLINUX_SOURCE_FROM")
    if source_info is None:
        # if EMLINUX_SOURCE_FROM is not set, we should set unknown to reduce false positive.
        source_info = "unknown"

    data = {
        "source_package_name": d.getVar("PN"),
        "source_from": source_info,
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
