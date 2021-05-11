############################################
# jaiwardhan/raspimon
#
# Makefile with install targets
############################################
.PHONY: install_run

install_run: 
	bash install.sh $(BOT_TOKEN) $(CHANNEL_ID)

install: install_run

target: install
