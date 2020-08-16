CLOUDFLARED_VERSION = 2020.8.0
CLOUDFLARED_SITE = $(call github,cloudflare,cloudflared,$(CLOUDFLARED_VERSION))
CLOUDFLARED_LICENSE_FILES = LICENSE
CLOUDFLARED_SRC_SUBDIR = github.com/cloudflare/cloudflared
CLOUDFLARED_BUILD_TARGETS = cmd/cloudflared

$(eval $(golang-package))
