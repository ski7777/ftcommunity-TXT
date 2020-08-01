.PHONY: all
all: initramfs rootfs

.PHONY: clean
clean: buildroot-rootfs-clean buildroot-initramfs-clean

.PHONY: buildroot-rootfs-clean
buildroot-rootfs-clean: buildroot-rootfs/Makefile
	$(MAKE) -C buildroot-rootfs clean

.PHONY: buildroot-initramfs-clean
buildroot-initramfs-clean: buildroot-initramfs/Makefile
	$(MAKE) -C buildroot-initramfs clean

buildroot-rootfs/Makefile:
	git submodule update --init buildroot-rootfs

buildroot-initramfs/Makefile:
	git submodule update --init buildroot-initramfs

CONFIG_DEPENDS = \
  .gitmodules \
  board/fischertechnik/TXT/tisdk_am335x-fischertechnik_txt_defconfig

buildroot-rootfs/.config: $(CONFIG_DEPENDS) buildroot-rootfs/Makefile
	BR2_EXTERNAL=.. $(MAKE) -C buildroot-rootfs fischertechnik_TXT_defconfig

buildroot-initramfs/.config: $(CONFIG_DEPENDS) buildroot-initramfs/Makefile
	BR2_EXTERNAL=.. $(MAKE) -C buildroot-initramfs fischertechnik_TXT_initramfs_defconfig

.PHONY: rootfs
rootfs: buildroot-rootfs/.config
	$(MAKE) -C buildroot-rootfs

.PHONY: initramfs
initramfs: buildroot-initramfs/.config
	$(MAKE) -C buildroot-initramfs

imagedir := buildroot-rootfs/output/images
initramfs-imagedir := buildroot-initramfs/output/images

.PHONY: release
release: all
	$(eval version := $(shell cat buildroot-rootfs/output/target/etc/fw-ver.txt))
	$(eval zipfile := build/ftcommunity-txt-$(version).zip)
	mkdir -p build
	rm -f $(zipfile)
	zip -j $(zipfile) $(initramfs-imagedir)/am335x-kno_txt.dtb $(imagedir)/rootfs.img $(initramfs-imagedir)/uImage
