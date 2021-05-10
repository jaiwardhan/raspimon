.PHONY: install_run

install_run: 
	install.sh $(BOT_TOKEN) $(CHANNEL_ID)

install: before_run

target: install
