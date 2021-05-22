################################################################################
#
# roboheart
#
################################################################################

ROBOHEART_BUILD_TARGETS = roboheart.go

define ROBOHEART_INSTALL_TARGET_CMDS
    $(INSTALL) -m 0755 $(@D)/bin/roboheart.go $(TARGET_DIR)/usr/sbin/roboheart
endef

define ROBOHEART_BUILD_CMDS
		$(foreach d,$(ROBOHEART_BUILD_TARGETS),\
			cd $(@D); \
			$(HOST_GO_TARGET_ENV) \
				$(ROBOHEART_GO_ENV) \
				$(GO_BIN) build -v $(ROBOHEART_BUILD_OPTS) \
				-o $(@D)/bin/$(or $(ROBOHEART_BIN_NAME),$(notdir $(d))) \
				$(d) \
		)
endef

$(eval $(golang-package))
