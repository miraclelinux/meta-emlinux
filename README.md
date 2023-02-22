# Quick Start

## Supported build host

ELinux supported build host OS is Debian 11 or greater.

## Setup

### Setup host os development environment

Run following command to install required packages.

```
$ sudo apt install \
  binfmt-support \
  debootstrap \
  dosfstools \
  dpkg-dev \
  gettext-base \
  git \
  mtools \
  parted \
  python3 \
  quilt \
  qemu-user-static \
  reprepro \
  git-buildpackage \
  pristine-tar \
  sbuild \
  schroot \
  python3-distutils
```

### Setup user

1. Add user to the sbuild group

```
$ sudo gpasswd -a <username> sbuild
```

2. Setup sudo

Building EMLinux, user need to be able to run sudo command as root.

Please follow "Setup Sudo" section in ISAR user manual.

https://github.com/ilbers/isar/blob/master/doc/user_manual.md#setup-sudo

### Setup repositories

1. Create a directory

```
$ mkdir repos
```

2. Checkout meta-emlinux

```
$ git clone -b bookworm https://github.com/miraclelinux/meta-emlinux.git repos/meta-emlinux
```

3. Setup build directory

```
$ source repos/meta-emlinux/scripts/setup-emlinux build
```

### Build image

1.  Edit conf/local.conf

If you want to add package/change machine/etc edit conf/local.conf.
For example, if you want build qemuarm64 image that includes iproute2 package, add folloinwg lines in conf/local.conf.

```
MACHINE = "qemuarm64"
IMAGE_PREINSTALL = "iproute2"
```

2. Build image

```
$ bitbake emlinux-image-base
```

### Run image by qemu

#### Run qemuadm64 image

```
$ qemu-system-x86_64 \
 -drive file=./tmp/deploy/images/qemuamd64/emlinux-image-base-emlinux-bookworm-qemuamd64.wic,discard=unmap,if=none,id=disk,format=raw \
 -kernel ./tmp/deploy/images/qemuamd64/emlinux-image-base-emlinux-bookworm-qemuamd64-vmlinuz \
 -initrd ./tmp/deploy/images/qemuamd64/emlinux-image-base-emlinux-bookworm-qemuamd64-initrd.img \
 -m 1G \
 -serial mon:stdio \
 -netdev user,id=net,hostfwd=tcp:127.0.0.1:22222-:22 \
 -cpu qemu64 \
 -smp 4 \
 -machine q35,accel=kvm:tcg \
 -global ICH9-LPC.noreboot=off \
 -device virtio-net-pci,netdev=net \
 -device ide-hd,drive=disk \
 -nographic \
 -append "root=/dev/sda2 rw console=ttyS0 ip=dhcp"
```

#### Run qemuarm64 image

```
$ qemu-system-aarch64 \
 -device virtio-net-device,netdev=net0,mac=52:54:00:12:35:02 \
 -netdev user,id=net0,hostfwd=tcp::2222-:22,hostfwd=tcp::2323-:23,tftp=./tmp/deploy/images/qemuarm64 \
 -drive id=disk0,file=./tmp/deploy/images/qemuarm64/emlinux-image-base-emlinux-bookworm-qemuarm64.ext4,if=none,format=raw \
 -device virtio-blk-device,drive=disk0 -show-cursor -device VGA,edid=on \
 -device qemu-xhci \
 -device usb-tablet \
 -device usb-kbd \
 -object rng-random,filename=/dev/urandom,id=rng0 \
 -device virtio-rng-pci,rng=rng0  \
 -nographic \
 -machine virt \
 -cpu cortex-a57 \
 -m 512 \
 -serial mon:stdio \
 -serial null \
 -kernel ./tmp/deploy/images/qemuarm64/emlinux-image-base-emlinux-bookworm-qemuarm64-vmlinux \
 -initrd ./tmp/deploy/images/qemuarm64/emlinux-image-base-emlinux-bookworm-qemuarm64-initrd.img \
 -append 'root=/dev/vda rw highres=off  console=ttyS0 mem=512M ip=dhcp console=ttyAMA0 '
```

## Supported machine

EMLinux currently supports following machines.

- qemuamd64
- qemuarm64
