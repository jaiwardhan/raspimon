"""
jaiwardhan/raspimon

Simple host metric capture and alerting tool for Raspberry Pi.
Collect metrics, define thresholds and extend tool capabilities
to do powerful alerting via Telegram straight to your mobile
devices without the hassle of signing up phone numbers. Lightweight
equivalent of AWS's Cloudwatch agent with you in complete control.

Get notified about your Raspberry Pi's (or virtually any Host)
performance alerts into your Channel. Plug it to a cron or an
OpenMediaVault NAS server job without having to periodically
run htop.

@author: Jaiwardhan Swarnakar
Copyright 2021-present
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

from modules.comms.TelegramRelay import PiMonBot
from modules.logger.Logger import Logger
from modules.utils.HostStats import HostStats
from modules.alarms.Alarms import Alarms
from modules.storage.Storage import Storage

# ------------------------------------------------ MAIN exec --
if __name__ == "__main__":
	Logger.execution_log()
	Storage.refresh()
	Alarms.init()

	system_statistics = HostStats.get()
	alarms = Alarms.check( stats=system_statistics )
	# print(PiAlarms.summarize( alarms=alarms ))
	if alarms is not None and len(alarms) > 0:
		PiMonBot.send(msg=Alarms.summarize( 
			alarms=alarms
		))

	Logger.execution_log(False)
