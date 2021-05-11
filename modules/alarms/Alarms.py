"""
jaiwardhan/Raspimon

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

from modules.comparators.Comparators import NumericComparator, ServiceComparator
from modules.utils.Stats import HostStats, ServiceStats
from modules.config.ConfigLoader import ConfigLoader
from modules.comms.TelegramRelay import PiMonBot
from modules.storage.Storage import Storage
from modules.errors.Errors import Errors
import json
import time
import sys


class Alarms:
	"""Alarm monitor for your host. Provides, maintains a store
	and triggers alerts based on your threshold configuration.
	Multiple alerts can be thrown if multiple threshold breaches
	are detected, but will be summarized into one single message.
	"""

	config = {}

	KEY_HOST = "host"
	KEY_PROCESSESES = "processes"
	KEY_SERVICES = "services"
	KEY_NAME = "name"
	KEY_THRESHOLDS = "thresholds"
	KEY_CONSEC = "consecutive"
	KEY_DESC = "description"
	KEY_INTERVAL = "interval"
	KEY_THRESHOLD = "threshold"
	KEY_TREND = "trend"
	KEY_PROCESS = "process"
	KEY_STATE = "state"

	@staticmethod
	def validate_config(debug=False):
		"""Configuration validator. Certain rules need to be maintained
		in your alarm configuration JSON to ensure that the program loads
		and works correctly as per expectation. Errors are replayed to
		your channel if validation produces errors.

		Args:
				debug (bool, optional): Set True to dry run and print. Defaults to False.
		"""

		errors = []
		if Alarms.config is None:
			errors.append(Errors("Configuration not loaded/present"))

		"""Validate all the alarms. Alarms can contain host level metrics
		or multiple service level alarms. Verify if the loaded configuration
		is correct and meets the norms.
		"""

		"""Validate: Host alarms"""
		if Alarms.config is not None and Alarms.KEY_HOST in Alarms.config:
			for alarm_name in Alarms.config[Alarms.KEY_HOST].keys():
				each_alarm = Alarms.config[Alarms.KEY_HOST][alarm_name]

				# Host alarms should contain a name field
				if Alarms.KEY_NAME not in each_alarm:
					errors.append(
						Errors(Alarms.KEY_NAME + " for alarm " + alarm_name))

				# Host alarms should contain `thresholds` to work
				if Alarms.KEY_THRESHOLDS not in each_alarm:
					errors.append(
						Errors(Alarms.KEY_THRESHOLDS + " for alarm " + alarm_name))
				else:
					for each_threshold in each_alarm[Alarms.KEY_THRESHOLDS]:

						# Each threshold alarm should contain a description
						if Alarms.KEY_DESC not in each_threshold:
							errors.append(
								Errors(Alarms.KEY_DESC + " in thresholds for alarm " + alarm_name))

						# Each threshold alarm should contain a threshold value
						if Alarms.KEY_THRESHOLD not in each_threshold:
							errors.append(Errors(
								"Threshold type in thresholds for alarm " + alarm_name,
								error_type=Errors.Types.UNRECOGNIZED
							))
						else:
							# Each alarm threshold should have a valid trend qualifier
							if Alarms.KEY_TREND not in each_threshold:
								errors.append(
									Errors(Alarms.KEY_TREND + " in thresholds for alarm " + alarm_name))
							elif not NumericComparator.supported(each_threshold[Alarms.KEY_TREND]):
								errors.append(Errors(
									"Trend " + each_threshold[Alarms.KEY_TREND] + " in thresholds for alarm " +
									alarm_name,
									error_type=Errors.Types.UNRECOGNIZED
								))

		"""Validate: Process alarms"""
		if Alarms.config is not None and Alarms.KEY_PROCESSESES in Alarms.config:
			for alarm_name in Alarms.config[Alarms.KEY_PROCESSESES].keys():
				each_alarm = Alarms.config[Alarms.KEY_PROCESSESES][alarm_name]
				# Service alarms should contain a name field
				if Alarms.KEY_NAME not in each_alarm:
					errors.append(
						Errors(Alarms.KEY_NAME + " for service alarm " + alarm_name))

				# Service alarms should name a process
				if Alarms.KEY_PROCESS not in each_alarm:
					errors.append(Errors(Alarms.KEY_PROCESS +
								  " for service alarm " + alarm_name))

				# Service alarms should contain `thresholds` to work
				if Alarms.KEY_THRESHOLDS not in each_alarm:
					errors.append(Errors(Alarms.KEY_THRESHOLDS +
								  " for service alarm " + alarm_name))
				else:
					for each_threshold in each_alarm[Alarms.KEY_THRESHOLDS]:

						# Each threshold alarm should contain a description
						if Alarms.KEY_DESC not in each_threshold:
							errors.append(
								Errors(Alarms.KEY_DESC + " in thresholds for service alarm " + alarm_name))

						# Each threshold alarm should have a valid state qualifier
						if Alarms.KEY_STATE not in each_threshold:
							errors.append(
								Errors(Alarms.KEY_STATE + " in thresholds for alarm " + alarm_name))
						elif not ServiceComparator.supported(each_threshold[Alarms.KEY_STATE]):
							errors.append(Errors("Service state " + each_threshold[Alarms.KEY_STATE] +
												 " in thresholds for alarm " + alarm_name,
												 error_type=Errors.Types.UNRECOGNIZED
												 ))

		# Non empty error list means we did encounter one
		# Report if we can and abort.
		if len(errors) > 0:
			message = ""
			for each_error in errors:
				message += Errors.format_obj(each_error) + "\n"
			if debug:
				print(message)
			else:
				PiMonBot.send(message)
			Errors.die("Illegal config. Abort.")

	@staticmethod
	def skim_configured_host_alarms():
		configured_alarms = []
		if Alarms.config is not None and Alarms.KEY_HOST in Alarms.config:
			configured_alarms = Alarms.config[Alarms.KEY_HOST].keys()
		return configured_alarms

	@staticmethod
	def skim_configured_service_alarms():
		configured_services = []
		if Alarms.config is not None and Alarms.KEY_PROCESSESES in Alarms.config:
			for alarm_name in Alarms.config[Alarms.KEY_PROCESSESES].keys():
				each_alarm = Alarms.config[Alarms.KEY_PROCESSESES][alarm_name]
				configured_services.append(each_alarm[Alarms.KEY_PROCESS])
		return configured_services

	@staticmethod
	def init():
		"""Initialize the alarming system. Additionally run some
		diagnostics to ensure the config is correctly set. Report
		if this manages to screw up.
		"""
		Alarms.config = ConfigLoader.load_alarms()
		Alarms.validate_config()

	@staticmethod
	def check():
		"""Analyze a KV metric dict. Correlates with the
		alarm configuration and generates alarm structures
		if one or more violations are encountered.

		Returns:
				list: A list containing alarm objects if one or
				more violations were encountered
		"""

		Alarms.init()
		Storage.refresh()

		# Fetch stats as per alarm configuration
		host_stats = HostStats.get(
			metrics=Alarms.skim_configured_host_alarms()
		)
		process_stats = ServiceStats.process_get(
			processes=Alarms.skim_configured_service_alarms()
		)

		alarms = []

		# Dump the current metrics to storage
		for each_stat_type in host_stats.keys():
			stat_value = host_stats[each_stat_type]
			Storage.add_telemetry(each_stat_type, stat_value)
		for each_stat_type in process_stats.keys():
			stat_value = process_stats[each_stat_type]
			Storage.add_process_telemetry(each_stat_type, stat_value)

		"""Scan the storage telemetry and see if a breach has occurred.
		If yes, then append an alarm object to the list which can be 
		used further.
		"""
		for each_telemetry_type in Storage.live[Storage.KEY_TELEMETRY]:
			# Skip if this telemetry is not being tracked anymore
			if each_telemetry_type not in Alarms.config[Alarms.KEY_HOST]:
				continue

			telemetry_name = Alarms.config[Alarms.KEY_HOST][each_telemetry_type][Alarms.KEY_NAME]
			thresholds = Alarms.config[Alarms.KEY_HOST][each_telemetry_type][Alarms.KEY_THRESHOLDS]
			telemetry_values = Storage.live[Storage.KEY_TELEMETRY][each_telemetry_type][Storage.KEY_VALUES]

			for each_threshold in thresholds:
				threshold_desc = each_threshold[Alarms.KEY_DESC]
				comparator = NumericComparator.get(
					each_threshold[Alarms.KEY_TREND])
				threshold_val = each_threshold[Alarms.KEY_THRESHOLD]

				# If in consecutive mode, then generate an alarm object IFF
				# the breach occurred in the specified interval and all recent
				# N data points were violations
				if Alarms.KEY_CONSEC in each_threshold and each_threshold[Alarms.KEY_CONSEC] > 0:
					# Confirm if interval data is present to treat it as not-missing, else skip
					last_time = int(time.time()) - \
						each_threshold[Alarms.KEY_INTERVAL]
					present = 0
					breaches = 0

					i_l = len(telemetry_values) - 1
					while i_l >= 0:
						if present == each_threshold[Alarms.KEY_CONSEC]:
							i_l = 0
						elif telemetry_values[i_l][Storage.KEY_TS] < last_time:
							i_l = 0
						else:
							present += 1
							breaches = (breaches + 1) if comparator(
								telemetry_values[i_l][Storage.KEY_VALUE], threshold_val) else breaches
						i_l -= 1

					if present >= each_threshold[Alarms.KEY_CONSEC] and breaches >= each_threshold[Alarms.KEY_CONSEC]:
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

		"""Scan the storage process telemetry and see if a breach has occurred.
		If yes, then append an alarm object to the list which can be 
		used further.
		"""
		for each_telemetry_type in Storage.live[Storage.KEY_PROCESSESES]:
			# Skip if this telemetry is not being tracked anymore
			if each_telemetry_type not in Alarms.config[Alarms.KEY_PROCESSESES]:
				continue

			telemetry_name = Alarms.config[Alarms.KEY_PROCESSESES][each_telemetry_type][Alarms.KEY_NAME]
			thresholds = Alarms.config[Alarms.KEY_PROCESSESES][each_telemetry_type][Alarms.KEY_THRESHOLDS]
			telemetry_values = Storage.live[Storage.KEY_PROCESSESES][each_telemetry_type][Storage.KEY_VALUES]

			for each_threshold in thresholds:
				threshold_desc = each_threshold[Alarms.KEY_DESC]
				comparator = ServiceComparator.get(
					code=each_threshold[Alarms.KEY_STATE]
				)

				# If in consecutive mode, then generate an alarm object IFF
				# the breach occurred in the specified interval and all recent
				# N data points were violations
				if Alarms.KEY_CONSEC in each_threshold and each_threshold[Alarms.KEY_CONSEC] > 0:
					# Confirm if interval data is present to treat it as not-missing, else skip
					last_time = int(time.time()) - \
						each_threshold[Alarms.KEY_INTERVAL]
					present = 0
					breaches = 0

					i_l = len(telemetry_values) - 1
					while i_l >= 0:
						if present == each_threshold[Alarms.KEY_CONSEC]:
							i_l = 0
						elif telemetry_values[i_l][Storage.KEY_TS] < last_time:
							i_l = 0
						else:
							present += 1
							breaches = (breaches + 1) if comparator(
								telemetry_values[i_l][Storage.KEY_VALUE]) else breaches
						i_l -= 1

					if present >= each_threshold[Alarms.KEY_CONSEC] and breaches >= each_threshold[Alarms.KEY_CONSEC]:
						# We have an alarm
						alarms.append({
							"telemetry_name": telemetry_name,
							"threshold_desc": threshold_desc,
							"threshold_val": each_threshold[Alarms.KEY_CONSEC],
							"found": breaches,
							"type": Alarms.KEY_PROCESS
						})

				# Else assume that only the most recent stat metric should be used
				# to see if a violation occurred.
				else:
					if comparator(telemetry_values[-1][Storage.KEY_VALUE]):
						# We have an alarm
						alarms.append({
							"telemetry_name": telemetry_name,
							"threshold_desc": threshold_desc,
							"threshold_val": 0,
							"found": 1,
							"type": Alarms.KEY_PROCESS
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

		message = "⚠️ ALARM: <code>" + HostStats.platform() + "</code>\n"
		message += "<i>Threshold limits breached</i>\n\n"
		message += "Details:\n------------------\n"
		_c = 1
		for i in alarms:
			message += str(_c) + ") <code>"
			message += "! Service Alert !\n" if "type" in i and i["type"] == Alarms.KEY_PROCESS else ""
			message += "Name: " + i["telemetry_name"] + "\n"
			message += "Desc: " + i["threshold_desc"] + "\n"
			message += "Threshold: " + str(i["threshold_val"]) + "\n"
			message += "Current: " + str(i["found"]) + "\n"
			message += "</code>\n"
			message += " -- \n"
			_c += 1

		message += "Please look at the affected host(s)"
		return message
