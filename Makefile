.PHONY: install_run

install_run: 
	install.sh $(BOT_TOKEN) $(CHANNEL_ID)

install: install_run

target: install
