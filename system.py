import common
import os
import urllib


def chroot(command: str) -> None:
    common.execute(f"chroot /mnt/root /bin/bash <<\"EOT\"\n{command}\nEOT")


def post_install() -> None:
    chroot("chown xenia:xenia /home/xenia")


def install_bootloader() -> None:
    chroot("""grub-install --modules=lvm --target="x86_64-efi" --efi-directory="/boot/efi" --boot-directory="/boot/efi"
grub-mkconfig -o /boot/efi/grub/grub.cfg""")


def download_root(url: str) -> None:
    if os.path.exists("/mnt/gentoo/root.img"):
        os.remove("/mnt/gentoo/root.img")

    urllib.request.urlretrieve(url, "/mnt/gentoo/root.img")


def mount_roots() -> None:
    if not os.path.exists("/mnt/gentoo"):
        os.mkdir("/mnt/gentoo")

    common.info("Mounting roots on /mnt/gentoo")
    common.execute("mount -L ROOTS /mnt/gentoo")


def mount() -> None:
    if not os.path.exists("/mnt/root"):
        os.mkdir("/mnt/root")

    common.info("Mounting root.img on /mnt/root")
    common.execute("mount -o ro,loop -t squashfs /mnt/gentoo/root.img /mnt/root")

    common.info("Mounting ESP on /mnt/root/boot/efi")
    common.execute("mount -L EFI /mnt/root/boot/efi")

    common.info("Mounting special filesystems")
    common.execute("mount -t proc /proc /mnt/gentoo/proc")
    common.execute("mount --rbind /dev /mnt/gentoo/dev")
    common.execute("mount --rbind /sys /mnt/gentoo/sys")
    common.execute("mount --bind /run /mnt/gentoo/run")
    common.execute("mount --make-slave /mnt/gentoo/run")