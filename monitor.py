"""
jaiwardhan/Raspimon

Simple host metric capture and alerting tool for Raspberry Pi.
Collect metrics, define thresholds and extend tool capabilities
to do powerful alerting via Telegram straight to your mobile
devices without the hassle of signing up phone numbers. Lightweight
equivalent of AWS's Cloudwatch agent with you in complete control.

Get notified about your Raspberry Pi's (or virtually any Host)
performance alerts into your Channel. Plug it to a cron or an
OpenMediaVault NAS server job without having to periodically
run htop.

@author: Jaiwardhan Swarnakar, 2021
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

import psutil
import os
import telegram
import json
import time
import platform
import sys
from datetime import datetime

class ExecutionLog:
	"""Simple class to help log execution event to a log file to
	trace the timestamp of events - start and stops.
	"""
	base_path = "logs.txt"
	@staticmethod
	def log(started = True):
		dateTimeObj = datetime.now()
		timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
		msg = " - " + timestampStr + " -- " + "Execution " + ("started" if started else "finished")
		with open(ExecutionLog.base_path, "a+") as exc_log:
			exc_log.write(msg + "\n")

class CustomNumericCompare:
	"""Common numeric comparators for easy refernce via codes
	"""

	@staticmethod
	def lt(a, b):
		return a < b
	
	@staticmethod
	def gt(a, b):
		return a > b
	
	@staticmethod
	def eq(a, b):
		return a == b
	
	@staticmethod
	def leq(a, b):
		return a <= b
	
	@staticmethod
	def geq(a, b):
		return a >= b
	
	@staticmethod
	def __get_map():
		return {
			"lt": CustomNumericCompare.lt,
			"gt": CustomNumericCompare.gt,
			"eq": CustomNumericCompare.eq,
			"leq": CustomNumericCompare.leq,
			"geq": CustomNumericCompare.geq
		}

	"""Gets the most appropriate comparator based on the code

	Returns:
		func: Reference to the eligible comparator
	"""
	@staticmethod
	def get(code):
		cnc_map = CustomNumericCompare.__get_map()
		return cnc_map[str(code)] if str(code) in cnc_map else CustomNumericCompare.eq
	
	"""Check the passed code is supported by this comparator

	Returns:
		boolean: True if supported | False otherwise
	"""
	@staticmethod
	def supported(code):
		return str(code) in CustomNumericCompare.__get_map()

class Storage:
	"""A storage class to maintain in-memory copy of the telemetry
	data on runtime. Occasionally sync back to the disk.
	"""

	base_path = "monitoring_telemetry.json"
	live = {}

	KEY_TELEMETRY = "telemetry"
	KEY_VALUES = "values"
	KEY_VALUE = "value"
	KEY_MOVING_AVG = "mavg"
	KEY_LAST_UPD = "lupd"
	KEY_TS = "ts"

	CONST_VALUE_MAXVALUES = 20
	
	@staticmethod
	def refresh():
		"""Refresh the storage contents back from the disk to memory"""
		# Create database if not exists
		if not os.path.exists(Storage.base_path) or not os.path.isfile(Storage.base_path):
			with open(Storage.base_path, "w+") as storage_file:
				storage_file.write("{}")
		# Read database and retain instance
		with open(Storage.base_path) as storage_file:
			Storage.live = json.loads(storage_file.read())

	@staticmethod
	def flush():
		"""Flush the in-memory storage contents back to disk - full overwrite"""
		with open(Storage.base_path, "w+") as storage_file:
			storage_file.write(json.dumps(Storage.live))
	
	@staticmethod
	def add_telemetry(telemetry_type, value):
		"""Add a telemetry metric to the storage. Additionally maintain moving
		average, timestamps and last N values with overflow purging"""
		if Storage.live is None or len(Storage.live.keys()) == 0:
			Storage.refresh()
		if Storage.KEY_TELEMETRY not in Storage.live:
			Storage.live[Storage.KEY_TELEMETRY] = {}
		if telemetry_type not in Storage.live[Storage.KEY_TELEMETRY]:
			Storage.live[Storage.KEY_TELEMETRY][telemetry_type] = {
				Storage.KEY_VALUES: [],
				Storage.KEY_MOVING_AVG: 0.0,
				Storage.KEY_LAST_UPD: 0
			}
		
		# Add the value with ts to the buffer
		Storage.live[Storage.KEY_TELEMETRY][telemetry_type][Storage.KEY_VALUES].append({
			Storage.KEY_VALUE: value,
			Storage.KEY_TS: int(time.time())
		})

		# Prune if overflow
		if len(Storage.live[Storage.KEY_TELEMETRY][telemetry_type][Storage.KEY_VALUES]) > Storage.CONST_VALUE_MAXVALUES:
			Storage.live[Storage.KEY_TELEMETRY][telemetry_type][Storage.KEY_VALUES].pop(0)
		
		# Recalc moving avg
		_avg = 0.0
		for each_val in Storage.live[Storage.KEY_TELEMETRY][telemetry_type][Storage.KEY_VALUES]:
			_avg += (1.0* each_val[Storage.KEY_VALUE])
		Storage.live[Storage.KEY_TELEMETRY][telemetry_type][Storage.KEY_MOVING_AVG] = _avg / len(Storage.live[Storage.KEY_TELEMETRY][telemetry_type][Storage.KEY_VALUES])
		
		# Last TS update
		Storage.live[Storage.KEY_TELEMETRY][telemetry_type][Storage.KEY_LAST_UPD] = int(time.time())
		
		# Sync
		Storage.flush()
		

class PiMonBot:
	"""Uses Telegram bot service recognized by the BOT TOKEN 
	to post alerts to a channel identified by the CHANNEL ID.
	
	To crete and obtain your BOT TOKEN, contact BotFather at
	https://web.telegram.org/#/im?p=@BotFather

	To obtain your channel id, simply create a channel and add
	the bot. Open your channel in Telegram web and follow these
	instructions: https://gist.github.com/mraaroncruz/e76d19f7d61d59419002db54030ebe35

	Expose your bot credentials via environment variables PI_BOT_TOKEN
	and PI_CHANNEL_ID
	"""
	
	bot = None
	BOT_TOKEN=os.getenv('PI_BOT_TOKEN')
	CHANNEL_ID=os.getenv('PI_CHANNEL_ID')

	@staticmethod
	def init(reinit=False):
		"""Initialize the telegram bot with credentials. Once
		created it can only be overridden with a True reinit

		Args:
			reinit (bool, optional): Set to True to force reinitialize
			the bot instance. Defaults to False.
		"""
		if not reinit and PiMonBot.bot is not None:
			return
		PiMonBot.bot = telegram.Bot(token=PiMonBot.BOT_TOKEN)

	@staticmethod
	def send(msg=''):
		"""Send a message string to a channel using HTML parse mode

		Args:
			msg (str, optional): The message to post in plain text or
			supported HTML format. Defaults to ''.
		"""
		if msg is None or len(str(msg)) == 0:
			return
		msg = str(msg)
		if PiMonBot.bot is None:
			PiMonBot.init()
		PiMonBot.bot.sendMessage(parse_mode='html', chat_id=PiMonBot.CHANNEL_ID, text=msg)

class PiAlarms:
	"""Alarm monitor for your host. Provides, maintains a store
	and triggers alerts based on your threshold configuration.
	Multiple alerts can be thrown if multiple threshold breaches
	are detected, but will be summarized into one single message.
	"""

	config = None
	base_path = "alarm_config.json"

	KEY_ALARMS = "alarms"
	KEY_NAME = "name"
	KEY_THRESHOLDS = "thresholds"
	KEY_CONSEC = "consecutive"
	KEY_DESC = "description"
	KEY_INTERVAL = "interval"
	KEY_THRESHOLD = "threshold"
	KEY_TREND = "trend"

	@staticmethod
	def validate_config():
		"""Configuration validator. Certain rules need to be maintained
		in your alarm configuration JSON to ensure that the program loads
		and works correctly as per expectation. Errors are replayed to
		your channel if validation produces errors.
		"""

		errors = []
		if PiAlarms.config is None:
			errors.append("🔥 Monitoring configuration not loaded/present")
		
		# Validate all alarms
		if PiAlarms.config is not None and PiAlarms.KEY_ALARMS in PiAlarms.config:
			errors = []
			for alarm_name in PiAlarms.config[PiAlarms.KEY_ALARMS].keys():
				each_alarm = PiAlarms.config[PiAlarms.KEY_ALARMS][alarm_name]
				if PiAlarms.KEY_NAME not in each_alarm:
					errors.append("🔥 Illegal: Missing " + PiAlarms.KEY_NAME + " for alarm " + alarm_name)
				if PiAlarms.KEY_THRESHOLDS not in each_alarm:
					errors.append("🔥 Illegal: Missing " + PiAlarms.KEY_THRESHOLDS + " for alarm " + alarm_name)
				else:
					for each_threshold in each_alarm[PiAlarms.KEY_THRESHOLDS]:
						if PiAlarms.KEY_DESC not in each_threshold:
							errors.append("🔥 Illegal: Missing " + PiAlarms.KEY_DESC + " in thresholds for alarm " + alarm_name)
						if PiAlarms.KEY_TREND not in each_threshold:
							errors.append("🔥 Illegal: Missing " + PiAlarms.KEY_TREND + " in thresholds for alarm " + alarm_name)
						elif not CustomNumericCompare.supported(each_threshold[PiAlarms.KEY_TREND]):
							errors.append("🔥 Illegal: Unsupported trend " + each_threshold[PiAlarms.KEY_TREND] + " in thresholds for alarm " + alarm_name)

		# Non empty error list means we did encounter one,
		# report and abort.
		if len(errors) > 0:
			message = ""
			for each_error in errors:
				message += each_error + "\n"
			PiMonBot.send(message)
			sys.exit("Illegal config, runtime error")
			

	@staticmethod
	def init():
		"""Initialize the alarming system. Additionally run some
		diagnostics to ensure the config is correctly set. Report
		if this manages to screw up.
		"""
		if PiAlarms.config is None:
			with open(PiAlarms.base_path) as config_file:
				try:
					PiAlarms.config = json.loads(config_file.read())
					PiAlarms.validate_config()
				except:
					PiMonBot.send("🔥 Illegal: INVALID CONFIGURATION")
					sys.exit("Illegal config, runtime error")

	@staticmethod
	def get_stats():
		"""Return host stats and metrics. Can be extended
		to return extra and more complicated information which
		can be tuned with your alarm configuration to generate
		crisp alerts.

		Returns:
			dict: A KV pair dict containing the supported metrics
			as configured by you.
		"""
		PiAlarms.init()
		status = {
			"cpu": psutil.cpu_percent(),
			"mem": psutil.virtual_memory().percent
		}
		return status
	
	@staticmethod
	def check(stats):
		"""Analyze a KV metric dict. Correlates with the
		alarm configuration and generates alarm structures
		if one or more violations are encountered.

		Args:
			stats (dict): The systems stats, preferably the
			output of get_stats method.

		Returns:
			list: A list containing alarm objects if one or
			more violations were encountered
		"""

		PiAlarms.init()
		if stats is None:
			return
		
		alarms = []
		Storage.refresh()

		# Dump the current metrics to storage
		for each_stat_type in stats.keys():
			stat_value = stats[each_stat_type]
			Storage.add_telemetry(each_stat_type, stat_value)
		
		# Now start scanning the storage telemetry and see if
		# a breach has occurred. If yes, then append an alarm
		# object to the list which can be used further.
		for each_telemetry_type in Storage.live[Storage.KEY_TELEMETRY]:
			telemetry_name = PiAlarms.config[PiAlarms.KEY_ALARMS][each_telemetry_type][PiAlarms.KEY_NAME]
			thresholds = PiAlarms.config[PiAlarms.KEY_ALARMS][each_telemetry_type][PiAlarms.KEY_THRESHOLDS]
			telemetry_values = Storage.live[Storage.KEY_TELEMETRY][each_telemetry_type][Storage.KEY_VALUES]

			for each_threshold in thresholds:
				threshold_desc = each_threshold[PiAlarms.KEY_DESC]
				comparator = CustomNumericCompare.get(each_threshold[PiAlarms.KEY_TREND])
				threshold_val = each_threshold[PiAlarms.KEY_THRESHOLD]
				
				# If in consecutive mode, then generate an alarm object IFF
				# the breach occurred in the specified interval and all recent
				# N data points were violations
				if PiAlarms.KEY_CONSEC in each_threshold and each_threshold[PiAlarms.KEY_CONSEC] > 0:
					# Confirm if interval data is present to treat it as not-missing, else skip
					last_time = int(time.time()) - each_threshold[PiAlarms.KEY_INTERVAL]
					present = 0
					breaches = 0

					i_l = len(telemetry_values) - 1
					while i_l >= 0:
						if present == each_threshold[PiAlarms.KEY_CONSEC]:
							i_l = 0
						elif telemetry_values[i_l][Storage.KEY_TS] < last_time:
							i_l = 0
						else:
							present += 1
							breaches = (breaches + 1) if comparator(telemetry_values[i_l][Storage.KEY_VALUE], threshold_val) else breaches
						i_l -= 1

					if present >= each_threshold[PiAlarms.KEY_CONSEC] and breaches >= each_threshold[PiAlarms.KEY_CONSEC]:
						# We have an alarm
						alarms.append({
							"telemetry_name": telemetry_name,
							"threshold_desc": threshold_desc,
							"threshold_val": threshold_val,
							"found": telemetry_values[-1][Storage.KEY_VALUE]
						})
					
				# Else assume that only the most recent stat metric should be used
				# to see if a violation occurred.
				else:
					if comparator(telemetry_values[-1][Storage.KEY_VALUE], threshold_val):
						# We have an alarm
						alarms.append({
							"telemetry_name": telemetry_name,
							"threshold_desc": threshold_desc,
							"threshold_val": threshold_val,
							"found": telemetry_values[-1][Storage.KEY_VALUE]
						})

		# Return the alarms for further processing
		return alarms

	@staticmethod
	def summarize(alarms):
		"""Generates an alarm summary from a list of alarm
		objects in HTML parse format glued in a string for
		easy transport.

		Args:
			alarms (list): A list of alarm objects as issued
			by the `check` method

		Returns:
			(String|None): An HTML encoded String if alarms found | None otherwise
		"""

		if len(alarms) == 0:
			return None

		message  = "⚠️ ALARM: <code>" + platform.node() + "</code>\n"
		message += "<i>Threshold limits breached</i>\n\n"
		message += "Details:\n------------------\n"
		_c = 1
		for i in alarms:
			message += str(_c) + ") <code>"
			message += "Name: " + i["telemetry_name"] + "\n"
			message += "Desc: " + i["threshold_desc"] + "\n"
			message += "Threshold: " + str(i["threshold_val"]) + "\n"
			message += "Current: " + str(i["found"]) + "\n"
			message += "</code>\n"
			message += " -- \n"
			_c += 1
		
		message += "Please look at the affected host(s)"
		return message


# ------------------------------------------------ MAIN exec --
if __name__ == "__main__":
	ExecutionLog.log()
	Storage.refresh()
	PiAlarms.init()

	system_statistics = PiAlarms.get_stats()
	alarms = PiAlarms.check( stats=system_statistics )
	# print(PiAlarms.summarize( alarms=alarms ))
	if alarms is not None and len(alarms) > 0:
		PiMonBot.send(msg=PiAlarms.summarize( 
			alarms=alarms
		))

	ExecutionLog.log(False)
