import hashlib
import uuid

def package_name_hash(name, version):
    s = f"{name}@{version}".encode("utf-8")
    sha256sum = None
    sha256hash = hashlib.sha256()
    sha256hash.update(s)
    sha256sum = sha256hash.hexdigest()

    return sha256sum

