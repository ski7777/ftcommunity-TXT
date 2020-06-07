RPI_FIRMWARE_FIXES_VERSION := 1.0
RPI_FIRMWARE_FIXES_SOURCE =
RPI_FIRMWARE_FIXES_INSTALL_TARGET = NO
RPI_FIRMWARE_FIXES_INSTALL_IMAGES = YES
RPI_FIRMWARE_FIXES_DEPENDENCIES = rpi-firmware

ifeq ($(BR2_PACKAGE_RPI_FIRMWARE_FIXES), y)
	RPI_FIRMWARE_FIXES_DEPENDENCIES += rpi-bt-firmware
endif

define RPI_FIRMWARE_FIXES_BUILD_CMDS
	$(INSTALL) package/rpi-firmware/config.txt $(@D)
	if [ "$(BR2_PACKAGE_RPI_FIRMWARE_FIXES)" = "y" ]; then \
		echo -e "\n# fixes rpi (3B, 3B+, 3A+, 4B and Zero W) ttyAMA0 serial console\ndtoverlay=miniuart-bt" >> $(@D)/config.txt; \
	fi
endef

define RPI_FIRMWARE_FIXES_INSTALL_IMAGES_CMDS
	$(INSTALL) $(@D)/config.txt $(BINARIES_DIR)/rpi-firmware/config.txt
endef

$(eval $(generic-package))
