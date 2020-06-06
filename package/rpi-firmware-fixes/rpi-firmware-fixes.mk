RPI_FIRMWARE_FIXES_VERSION := 1.0
RPI_FIRMWARE_FIXES_SOURCE =
RPI_FIRMWARE_FIXES_INSTALL_TARGET = NO
RPI_FIRMWARE_FIXES_INSTALL_IMAGES = YES
RPI_FIRMWARE_FIXES_DEPENDENCIES = rpi-firmware

ifeq ($(BR2_PACKAGE_RPI_FIRMWARE_FIXES), y)
	RPI_FIRMWARE_FIXES_DEPENDENCIES += rpi-bt-firmware
endif

define RPI_FIRMWARE_FIXES_INSTALL_IMAGES_CMDS
	if [ "$(BR2_PACKAGE_RPI_FIRMWARE_FIXES)" = "y" ]; then \
		echo "Adding 'dtoverlay=miniuart-bt' to config.txt (fixes ttyAMA0 serial console)."; \
		cat $(BR2_EXTERNAL_FTCOMMUNITY_TXT_PATH)/package/rpi-firmware-fixes/miniuart-bt.config >> $(BINARIES_DIR)/rpi-firmware/config.txt; \
	fi
endef

$(eval $(generic-package))
