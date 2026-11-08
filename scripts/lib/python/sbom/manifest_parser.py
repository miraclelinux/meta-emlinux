import os
import io
from debian.debfile import DebFile
from debian.copyright import Copyright, NotMachineReadableError

def find_manifest_files(deploy_dir, image_name, image_fstypes):
    ret = []

    fstypes = image_fstypes.split()
    for fstype in fstypes:
        manifest = f"{deploy_dir}/{image_name}.{fstype}.manifest"
        if os.path.exists(manifest):
            ret.append(manifest)
    return ret

def read_manifests(filepath):
    pkgs = {}

    with open(filepath) as f:
        contents = f.read().split()
    
        for line in contents:
            tmp = line.split("|")
            name = tmp[2].split(":")[0]

            pkgs[name] = {
                "source": tmp[0],
                "src_pkg_ver": tmp[1],
                "package": tmp[2],
                "version": tmp[3],
            }
            
    return pkgs

def collect_packages(manifests, imager_bom):
    imager_bom_pkgs = imager_bom.split()
    ret = {}

    for manifest in manifests:
        pkgs = read_manifests(manifest)
        for name in pkgs:
            if name in imager_bom_pkgs:
                ret[name] = pkgs[name]

    return ret

