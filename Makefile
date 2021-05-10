.PHONY: install_run

install_run: 
    bash install.sh $(BOT_TOKEN) $(CHANNEL_ID)

install: before_run

target: install
