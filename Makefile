
all: buildroot/Makefile buildroot/.config
	make -C buildroot

clean:
	BR2_EXTERNAL=.. make -C buildroot clean

buildroot/Makefile:
	git submodule update --init buildroot

CONFIG_DEPENDS = \
  .gitmodules \
  board/fischertechnik/TXT/tisdk_am335x-fischertechnik_txt_defconfig

buildroot/.config: $(CONFIG_DEPENDS)
	BR2_EXTERNAL=.. make -C buildroot fischertechnik_TXT_defconfig

imagedir := buildroot/output/images

release: all
	$(eval version := $(shell cat buildroot/output/target/etc/fw-ver.txt))
	$(eval zipfile := ftcommunity-txt-$(version).zip)
	mkdir -p build
	rm -f $(zipfile)
	cp $(imagedir)/$(zipfile) build

prepare_defconfigs: buildroot/Makefile
	@for d in $(shell ls configs/fragments/txpi/); do \
		if [ "$${d}" != "common" ]; then \
			echo Building txpi$${d}_defconfig; \
			cat configs/fragments/txpi/$${d}/*.config configs/fragments/txpi/common/*.config > configs/txpi$${d}_defconfig; \
			BR2_EXTERNAL=.. make -C buildroot txpi$${d}_defconfig; \
			make -C buildroot savedefconfig; \
		fi \
	done

prepare_outputconfs: buildroot/Makefile
	@for d in $(shell ls board/ftCommunity/txpi/fragments/output.conf); do \
		if [ "$${d}" != "common" ]; then \
			echo Building output.conf for txpi$${d}; \
			cat board/ftCommunity/txpi/fragments/output.conf/$${d}/*.conf board/ftCommunity/txpi/fragments/output.conf/common/*.conf > board/ftCommunity/txpi/$${d}/output.conf; \
			sort -o board/ftCommunity/txpi/$${d}/output.conf board/ftCommunity/txpi/$${d}/output.conf; \
		fi \
	done
	
prepare: prepare_defconfigs prepare_outputconfs
