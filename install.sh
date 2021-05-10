#!/bin/bash

####################################################
# jaiwardhan/raspimon
#
# Installs raspimon service, embed environment vars.
####################################################

set -e

# Replace bot tokens
sed -s "s/TELEGRAM_BOT_TOKEN/$1/g" ./scripts/raspimon_profile.sh > /tmp/raspimon_profile.sh
sudo sed -s "s/TELEGRAM_CHANNEL_ID/$2/g" /tmp/raspimon_profile.sh > /etc/profile.d/raspimon.sh

# Copy the service file
sudo cp ./scripts/raspimon /etc/init.d/
sudo systemctl enable raspimon
chmod +x run.sh