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

from modules.config.ConfigLoader import ConfigLoader
import json
import time
import os

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
		if  not os.path.exists(ConfigLoader.Telemetry["base_path"]) or \
			not os.path.isfile(ConfigLoader.Telemetry["base_path"]):
			with open(ConfigLoader.Telemetry["base_path"], "w+") as storage_file:
				storage_file.write("{}")
		
		# Read database and retain instance
		Storage.live = ConfigLoader.load_telemetry()

	@staticmethod
	def flush():
		"""Flush the in-memory storage contents back to disk - full overwrite"""
		with open(ConfigLoader.Telemetry["base_path"], "w+") as storage_file:
			storage_file.write(json.dumps(Storage.live))
		Storage.live = ConfigLoader.load_telemetry()
	
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
		
		# Re-calc moving avg
		_avg = 0.0
		for each_val in Storage.live[Storage.KEY_TELEMETRY][telemetry_type][Storage.KEY_VALUES]:
			_avg += (1.0* each_val[Storage.KEY_VALUE])
		Storage.live[Storage.KEY_TELEMETRY][telemetry_type][Storage.KEY_MOVING_AVG] = _avg / len(Storage.live[Storage.KEY_TELEMETRY][telemetry_type][Storage.KEY_VALUES])
		
		# Last TS update
		Storage.live[Storage.KEY_TELEMETRY][telemetry_type][Storage.KEY_LAST_UPD] = int(time.time())
		
		# Sync
		Storage.flush()
