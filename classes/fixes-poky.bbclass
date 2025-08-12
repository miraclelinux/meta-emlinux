# fixes-poky.bbclass
#
# This class fixes Poky's bbclass bugs by overwriting functions.
#

##################################################
# Overwrite poky/meta/classes/insane.bbclass.
# - def package_qa_check_buildpaths
# - python do_package_qa
##################################################
def package_qa_check_buildpaths(path, name, d, elf, messages):
    """
    Check for build paths inside target files and error if not found in the whitelist
    """
    # Ignore .debug files, not interesting
    if path.find(".debug") != -1:
        return

    # Ignore symlinks
    if os.path.islink(path):
        return

    # Ignore ipk and deb's CONTROL dir
    if path.find(name + "/CONTROL/") != -1 or path.find(name + "/DEBIAN/") != -1:
        return

    tmpdir = bytes(d.getVar('TMPDIR'), encoding="utf-8")
    with open(path, 'rb') as f:
        file_content = f.read()
        if tmpdir in file_content:
            package_qa_add_message(messages, "buildpaths", "File %s in package contained reference to tmpdir" % package_qa_clean_path(path,d))

# The PACKAGE FUNC to scan each package
python do_package_qa () {
    import subprocess
    import oe.packagedata

    bb.note("DO PACKAGE QA")

    bb.build.exec_func("read_subpackage_metadata", d)

    # Check non UTF-8 characters on recipe's metadata
    package_qa_check_encoding(['DESCRIPTION', 'SUMMARY', 'LICENSE', 'SECTION'], 'utf-8', d)

    logdir = d.getVar('T')
    pn = d.getVar('PN')

    # Check the compile log for host contamination
    compilelog = os.path.join(logdir,"log.do_compile")

    if os.path.exists(compilelog):
        statement = "grep -e 'CROSS COMPILE Badness:' -e 'is unsafe for cross-compilation' %s > /dev/null" % compilelog
        if subprocess.call(statement, shell=True) == 0:
            msg = "%s: The compile log indicates that host include and/or library paths were used.\n \
        Please check the log '%s' for more information." % (pn, compilelog)
            package_qa_handle_error("compile-host-path", msg, d)

    # Check the install log for host contamination
    installlog = os.path.join(logdir,"log.do_install")

    if os.path.exists(installlog):
        statement = "grep -e 'CROSS COMPILE Badness:' -e 'is unsafe for cross-compilation' %s > /dev/null" % installlog
        if subprocess.call(statement, shell=True) == 0:
            msg = "%s: The install log indicates that host include and/or library paths were used.\n \
        Please check the log '%s' for more information." % (pn, installlog)
            package_qa_handle_error("install-host-path", msg, d)

    # Scan the packages...
    pkgdest = d.getVar('PKGDEST')
    packages = set((d.getVar('PACKAGES') or '').split())

    global pkgfiles
    pkgfiles = {}
    for pkg in packages:
        pkgfiles[pkg] = []
        for walkroot, dirs, files in os.walk(os.path.join(pkgdest, pkg)):
            for file in files:
                pkgfiles[pkg].append(os.path.join(walkroot, file))

    # no packages should be scanned
    if not packages:
        return

    import re
    # The package name matches the [a-z0-9.+-]+ regular expression
    pkgname_pattern = re.compile(r"^[a-z0-9.+-]+$")

    taskdepdata = d.getVar("BB_TASKDEPDATA", False)
    taskdeps = set()
    for dep in taskdepdata:
        taskdeps.add(taskdepdata[dep][0])

    def parse_test_matrix(matrix_name):
        testmatrix = d.getVarFlags(matrix_name) or {}
        g = globals()
        warnchecks = []
        for w in (d.getVar("WARN_QA") or "").split():
            if w in skip:
               continue
            if w in testmatrix and testmatrix[w] in g:
                warnchecks.append(g[testmatrix[w]])

        errorchecks = []
        for e in (d.getVar("ERROR_QA") or "").split():
            if e in skip:
               continue
            if e in testmatrix and testmatrix[e] in g:
                errorchecks.append(g[testmatrix[e]])
        return warnchecks, errorchecks

    for package in packages:
        skip = set((d.getVar('INSANE_SKIP') or "").split() +
                   (d.getVar('INSANE_SKIP_' + package) or "").split())
        if skip:
            bb.note("Package %s skipping QA tests: %s" % (package, str(skip)))

        bb.note("Checking Package: %s" % package)
        # Check package name
        if not pkgname_pattern.match(package):
            package_qa_handle_error("pkgname",
                    "%s doesn't match the [a-z0-9.+-]+ regex" % package, d)

        warn_checks, error_checks = parse_test_matrix("QAPATHTEST")
        package_qa_walk(warn_checks, error_checks, package, d)

        warn_checks, error_checks = parse_test_matrix("QAPKGTEST")
        package_qa_package(warn_checks, error_checks, package, d)

        package_qa_check_rdepends(package, pkgdest, skip, taskdeps, packages, d)
        package_qa_check_deps(package, pkgdest, d)

    warn_checks, error_checks = parse_test_matrix("QARECIPETEST")
    package_qa_recipe(warn_checks, error_checks, pn, d)

    if 'libdir' in d.getVar("ALL_QA").split():
        package_qa_check_libdir(d)

    qa_sane = d.getVar("QA_SANE")
    if not qa_sane:
        bb.fatal("QA run found fatal errors. Please consider fixing them.")
    bb.note("DONE with PACKAGE QA")
}
