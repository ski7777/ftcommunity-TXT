.PHONY: all
all: initramfs rootfs

.PHONY: clean
clean: buildroot-rootfs-clean buildroot-initramfs-clean

.PHONY: prepare
prepare:
	mkdir -p build

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

.PHONY: rootfs-build
rootfs-build: buildroot-rootfs/.config
	$(MAKE) -C buildroot-rootfs

.PHONY: rootfs
rootfs: rootfs-build initramfs
	rm -rf buildroot-rootfs/output/target/lib/modules/*
	cp -r build/modules/* buildroot-rootfs/output/target/lib/modules
	$(MAKE) rootfs-build

.PHONY: initramfs
initramfs: buildroot-initramfs/.config
	mkdir -p build/modules
	$(MAKE) -C buildroot-initramfs

rootfs-imagedir := buildroot-rootfs/output/images
initramfs-imagedir := buildroot-initramfs/output/images

.PHONY: copy-build
copy-build: all prepare
	mkdir -p build/images
	cp $(initramfs-imagedir)/am335x-kno_txt.dtb $(initramfs-imagedir)/uImage $(rootfs-imagedir)/rootfs.img build/images

.PHONY: release
release: copy-build
	$(eval version := $(shell cat buildroot-rootfs/output/target/etc/fw-ver.txt))
	$(eval zipfile := build/ftcommunity-txt-$(version).zip)
	zip -j -X $(zipfile) build/images/am335x-kno_txt.dtb build/images/rootfs.img build/images/uImage
