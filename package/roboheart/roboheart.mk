ROBOHEART_VERSION = 05c38e72490d2afe0f56022a2f54e9e0edd42726
ROBOHEART_SITE = $(call github,ftCommunity,roboheart,$(ROBOHEART_VERSION))
ROBOHEART_LICENSE = GPL-3.0-only
ROBOHEART_SRC_SUBDIR = github.com/ftCommunity/roboheart
ROBOHEART_BUILD_TARGETS = cmd/roboheart

define ROBOHEART_POST_CONFIGURE_SET_BUILD_OPTIONS
	if [ "$(BR2_PACKAGE_SERVICE_ACM)" == "y" ]; then \
		sed -i -E "s/(\"acm\":\s*)(true|false)/\1true/" $(@D)/internal/servicemanager/services.go; \
	else \
		sed -i -E "s/(\"acm\":\s*)(true|false)/\1false/" $(@D)/internal/servicemanager/services.go; \
	fi
	if [ "$(BR2_PACKAGE_SERVICE_CONFIG)" == "y" ]; then \
		sed -i -E "s/(\"config\":\s*)(true|false)/\1true/" $(@D)/internal/servicemanager/services.go; \
	else \
		sed -i -E "s/(\"config\":\s*)(true|false)/\1false/" $(@D)/internal/servicemanager/services.go; \
	fi
	if [ "$(BR2_PACKAGE_SERVICE_FWVER)" == "y" ]; then \
		sed -i -E "s/(\"fwver\":\s*)(true|false)/\1true/" $(@D)/internal/servicemanager/services.go; \
	else \
		sed -i -E "s/(\"fwver\":\s*)(true|false)/\1false/" $(@D)/internal/servicemanager/services.go; \
	fi
	if [ "$(BR2_PACKAGE_SERVICE_LOCALE)" == "y" ]; then \
		sed -i -E "s/(\"locale\":\s*)(true|false)/\1true/" $(@D)/internal/servicemanager/services.go; \
	else \
		sed -i -E "s/(\"locale\":\s*)(true|false)/\1false/" $(@D)/internal/servicemanager/services.go; \
	fi
	if [ "$(BR2_PACKAGE_SERVICE_RELVER)" == "y" ]; then \
		sed -i -E "s/(\"relver\":\s*)(true|false)/\1true/" $(@D)/internal/servicemanager/services.go; \
	else \
		sed -i -E "s/(\"relver\":\s*)(true|false)/\1false/" $(@D)/internal/servicemanager/services.go; \
	fi
	if [ "$(BR2_PACKAGE_SERVICE_POWER)" == "y" ]; then \
		sed -i -E "s/(\"power\":\s*)(true|false)/\1true/" $(@D)/internal/servicemanager/services.go; \
	else \
		sed -i -E "s/(\"power\":\s*)(true|false)/\1false/" $(@D)/internal/servicemanager/services.go; \
	fi
	if [ "$(BR2_PACKAGE_SERVICE_WEB)" == "y" ]; then \
		sed -i -E "s/(\"web\":\s*)(true|false)/\1true/" $(@D)/internal/servicemanager/services.go; \
	else \
		sed -i -E "s/(\"web\":\s*)(true|false)/\1false/" $(@D)/internal/servicemanager/services.go; \
	fi
	if [ "$(BR2_PACKAGE_SERVICE_VNCSERVER)" == "y" ]; then \
		sed -i -E "s/(\"vncserver\":\s*)(true|false)/\1true/" $(@D)/internal/servicemanager/services.go; \
	else \
		sed -i -E "s/(\"vncserver\":\s*)(true|false)/\1false/" $(@D)/internal/servicemanager/services.go; \
	fi
endef

define ROBOHEART_POST_CONFIGURE_CHECK_SERVICE_DEPENDENCIES
	cd $(@D) && go run cmd/checkdeps/main.go
endef

ROBOHEART_POST_CONFIGURE_HOOKS += ROBOHEART_POST_CONFIGURE_SET_BUILD_OPTIONS ROBOHEART_POST_CONFIGURE_CHECK_SERVICE_DEPENDENCIES

define ROBOHEART_PRE_BUILD_VENDORING
    cd $(@D) && go mod vendor
endef

ROBOHEART_PRE_BUILD_HOOKS += ROBOHEART_PRE_BUILD_VENDORING

$(eval $(golang-package))
