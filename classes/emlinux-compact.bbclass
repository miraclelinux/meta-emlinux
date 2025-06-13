do_make_emlinux_compact_rootfs[network] = "${TASK_USE_SUDO}"

EMLINUX_IMAGE_COMPACT_WORK_DIR="emlinux-work"
EMLINUX_IMAGE_COMPACT_SETUP_SCRIPTS_DIR="${EMLINUX_IMAGE_COMPACT_WORK_DIR}/scripts/setup"
EMLINUX_IMAGE_COMPACT_BUSYBOX_TMP_DIR="${EMLINUX_IMAGE_COMPACT_WORK_DIR}/busybox-tmp"
EMLINUX_IMAGE_COMPACT_BUSYBOX_PREPARE_SCRIPT="prepare-busybox.sh"
EMLINUX_COMPACT_IMAGE_BUSYBOX_TMP_PATH="${EMLINUX_IMAGE_COMPACT_BUSYBOX_TMP_DIR}/bin:${EMLINUX_IMAGE_COMPACT_BUSYBOX_TMP_DIR}/sbin:${EMLINUX_IMAGE_COMPACT_BUSYBOX_TMP_DIR}/usr/bin:${EMLINUX_IMAGE_COMPACT_BUSYBOX_TMP_DIR}/usr/sbin"

def create_replace_script(d):
    import yaml
    import os

    files = []
    busybox_cmds = {}

    workdir = d.getVar("WORKDIR")
    for f in os.listdir(workdir):
         if f.startswith("compact-image-replace-") and f.endswith(".yml"):
            files.append(f"{workdir}/{f}")

    for f in files:
        with open(f) as yml:
            data = yaml.safe_load(yml)
            busybox_cmds.update(data)

    image_preinstall = d.getVar("IMAGE_PREINSTALL").strip().split()
    image_install = d.getVar("IMAGE_INSTALL").strip().split()
    
    user_specified_install_pkgs = image_preinstall + image_install
    pinned_pkgs = []

    if d.getVar("EMLINUX_IMAGE_COMPACT_USE_SYSTEMD") == "1":
        d.setVar("EMLINUX_COMPACT_IMAGE_REMOVE_UTIL_LINUX", "")
        d.setVar("EMLINUX_COMPACT_IMAGE_REMOVE_MOUNT", "")
        d.setVar("EMLINUX_COMPACT_IMAGE_REMOVE_PAM", "")
        d.setVar("EMLINUX_COMPACT_IMAGE_REMOVE_LIBGPG_ERROR", "")

    remove_candidate = d.getVar("EMLINUX_COMPACT_IMAGE_REMOVE_PAKCAGES").strip().split()
    remove_candidate_new = []

    for pkg in remove_candidate:
        if pkg in user_specified_install_pkgs:
            bb.note(f"{pkg} is user specified install package. Do not remove")
        else:
            if not pkg in remove_candidate_new:
                remove_candidate_new.append(pkg)

    d.setVar("EMLINUX_COMPACT_IMAGE_REMOVE_PAKCAGES", " ".join(remove_candidate_new))

    replace_target = []
    tmp_replace_targets = remove_candidate_new
    for t in tmp_replace_targets:
        if t in busybox_cmds:
            replace_target.append(t)

    tmp_install_dir = d.getVar("EMLINUX_IMAGE_COMPACT_BUSYBOX_TMP_DIR")
    script = f"{d.getVar('WORKDIR')}/{d.getVar('EMLINUX_IMAGE_COMPACT_BUSYBOX_PREPARE_SCRIPT')}"
    with open(script, "w") as f:
        f.write("#!/bin/sh -x\n")
        for target in replace_target:
            bb.note(f"replace: {target}")
            for cmd in busybox_cmds[target]["cmds"]:
                f.write(f"ln -s /bin/busybox /{tmp_install_dir}{cmd}\n")

    
setup_make_compact_image() {
    if [ -d "${ROOTFSDIR}/${EMLINUX_IMAGE_COMPACT_WORK_DIR}/" ]; then
        sudo rm -fr "${ROOTFSDIR}/${EMLINUX_IMAGE_COMPACT_WORK_DIR}/"
    fi

    sudo mkdir "${ROOTFSDIR}/${EMLINUX_IMAGE_COMPACT_WORK_DIR}/"
    sudo mkdir -p "${ROOTFSDIR}/${EMLINUX_IMAGE_COMPACT_SETUP_SCRIPTS_DIR}/"
    sudo mkdir "${ROOTFSDIR}/${EMLINUX_IMAGE_COMPACT_BUSYBOX_TMP_DIR}"
    sudo mkdir "${ROOTFSDIR}/${EMLINUX_IMAGE_COMPACT_BUSYBOX_TMP_DIR}/bin"
    sudo mkdir "${ROOTFSDIR}/${EMLINUX_IMAGE_COMPACT_BUSYBOX_TMP_DIR}/sbin"
    sudo mkdir "${ROOTFSDIR}/${EMLINUX_IMAGE_COMPACT_BUSYBOX_TMP_DIR}/usr"
    sudo mkdir "${ROOTFSDIR}/${EMLINUX_IMAGE_COMPACT_BUSYBOX_TMP_DIR}/usr/bin"
    sudo mkdir "${ROOTFSDIR}/${EMLINUX_IMAGE_COMPACT_BUSYBOX_TMP_DIR}/usr/sbin"

    sudo -E chroot "${ROOTFSDIR}" \
        /usr/sbin/usermod -s /bin/sh root
}

prepare_busybox() {
    sudo cp  "${WORKDIR}/${EMLINUX_IMAGE_COMPACT_BUSYBOX_PREPARE_SCRIPT}" "${ROOTFSDIR}/${EMLINUX_IMAGE_COMPACT_SETUP_SCRIPTS_DIR}/."

    sudo -E chroot "${ROOTFSDIR}" /bin/sh <<EOL
/bin/sh /emlinux-work/scripts/setup/prepare-busybox.sh
EOL
}

remove_packages() {
    sudo -E chroot "${ROOTFSDIR}" /bin/dash <<EOL
export PATH=${EMLINUX_COMPACT_IMAGE_BUSYBOX_TMP_PATH}:${PATH}
dpkg -P --force-all ${EMLINUX_COMPACT_IMAGE_REMOVE_PAKCAGES}
EOL
}

replace_packages() {
    sudo -E chroot "${ROOTFSDIR}" /bin/dash <<EOL
export PATH=${EMLINUX_COMPACT_IMAGE_BUSYBOX_TMP_PATH}:${PATH}

busybox cp -a /${EMLINUX_IMAGE_COMPACT_BUSYBOX_TMP_DIR}/bin/* /bin/ || true
busybox cp -a /${EMLINUX_IMAGE_COMPACT_BUSYBOX_TMP_DIR}/sbin/* /sbin/ || true
busybox cp -a /${EMLINUX_IMAGE_COMPACT_BUSYBOX_TMP_DIR}/usr/bin/* /usr/bin/ || true
busybox cp -a /${EMLINUX_IMAGE_COMPACT_BUSYBOX_TMP_DIR}/usr/sbin/* /usr/sbin/ || true
EOL

    # Replace dash to busybox shell
    sudo -E chroot "${ROOTFSDIR}" /bin/busybox sh <<EOL
export PATH=${EMLINUX_COMPACT_IMAGE_BUSYBOX_TMP_PATH}:${PATH}
/bin/busybox ln -sf /bin/busybox /bin/sh
EOL

    if [ "${EMLINUX_IMAGE_COMPACT_REMOVE_PERL}" = "1" ]; then
      sudo -E chroot "${ROOTFSDIR}" /bin/busybox sh <<EOL
        export PATH=${EMLINUX_COMPACT_IMAGE_BUSYBOX_TMP_PATH}:${PATH}
        dpkg -P --force-all ${EMLINUX_COMPACT_IMAGE_REMOVE_PERL}
EOL
    fi

    if [ "${EMLINUX_IMAGE_COMPACT_USE_SYSTEMD}" != "1" ]; then
        # Install AMA0 setting to inittab.d/
        sudo mkdir ${ROOTFSDIR}/etc/inittab.d
        sudo sh -c "echo 'AMA0:12345:respawn:/sbin/getty 115200 ttyAMA0' >> ${ROOTFSDIR}/etc/inittab.d/ama0.tab"
        sudo sh -c "echo 'S0:12345:respawn:/sbin/getty 115200 ttyS0' >> ${ROOTFSDIR}/etc/inittab.d/ttyS0.tab"
        sudo sh -c "echo 'S1:12345:respawn:/sbin/getty 115200 ttyS1' >> ${ROOTFSDIR}/etc/inittab.d/ttyS1.tab"
        # Comment out following line added by isar/meta/conf/distro/debian-configscript.sh
        sudo sh -c "sed -i 's;^T0:23:respawn:/sbin/getty;#T0:23:respawn:/sbin/getty;' ${ROOTFSDIR}/etc/inittab"
        sudo sh -c "sed -i 's;--noclear;;g' ${ROOTFSDIR}/etc/inittab"
    fi

    if [ "${EMLINUX_IMAGE_COMPACT_REMOVE_BOOT_DIR}" = "1" ]; then
      sudo -E chroot "${ROOTFSDIR}" /bin/busybox sh <<EOL
rm -fr /boot/System.map-* /boot/config-* /boot/vmlinux-* /boot/initrd* || true
rm -fr /initrd.img /initrd.img.old /vmlinuz /vmlinuz.old || true
EOL
    fi
 
    if [ "${EMLINUX_IMAGE_COMPACT_REMOVE_MAN}" = "1" ]; then
      sudo rm -fr "${ROOTFSDIR}/usr/share/man"
    fi

    if [ "${EMLINUX_IMAGE_COMPACT_REMOVE_DTB}" = "1" ]; then
        linuxdir=$(find "${ROOTFSDIR}/usr/lib" -type d -a -name 'linux-image*')
        sudo rm -fr "${linuxdir}"
    fi
 
    sudo mkdir -p "${ROOTFSDIR}/etc/apt/sources.list.d"
    sudo rm -fr "${ROOTFSDIR}/${EMLINUX_IMAGE_COMPACT_WORK_DIR}"
}

python do_make_emlinux_compact_rootfs() {
    pn = d.getVar("PN")
    if pn.endswith("-sdk"):
        bb.note(f"pn is {pn} skip")
        return

    bb.note("Create compact image")
    bb.build.exec_func("setup_make_compact_image", d)
    create_replace_script(d)
    bb.build.exec_func("prepare_busybox", d)
    bb.build.exec_func("remove_packages", d)
    bb.build.exec_func("replace_packages", d)
}

addtask make_emlinux_compact_rootfs before do_rootfs_finalize after do_generate_initramfs

