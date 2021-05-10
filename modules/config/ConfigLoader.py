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

from modules.errors.Errors import Errors
import json
import os

class ConfigLoader:

	Alarms = {
		"base_path": "configs/alarms.json",
		"config": {}
	}

	Logging = {
		"base_dir": "/var/log/raspimon",
		"execution_log": "execution.log"
	}

	Telemetry = {
		"base_dir": "storage",
		"base_path": "storage/monitoring_telemetry.json",
		"config": {}
	}

	@staticmethod
	def load_alarms():
		alarms = ""
		contents = ""

		if not os.path.exists(ConfigLoader.Alarms["base_path"]) or\
			not os.path.isfile(ConfigLoader.Alarms["base_path"]):
			Errors.throw(
				category=Errors.Categories.ILLEGAL,
				type=Errors.Types.RESOURCE_MISSING,
				msg="Missing config at path " + ConfigLoader.Alarms["base_path"]
			)
		
		with open(ConfigLoader.Alarms["base_path"]) as f:
			contents = f.read()
		alarms = json.loads(contents)
		ConfigLoader.Alarms["config"] = alarms
		return alarms
	
	@staticmethod
	def load_telemetry():
		telemetry_data = {}
		contents = ""

		if not os.path.exists(ConfigLoader.Telemetry["base_path"]) or\
			not os.path.isfile(ConfigLoader.Telemetry["base_path"]):
			Errors.throw(
				category=Errors.Categories.ILLEGAL,
				type=Errors.Types.RESOURCE_MISSING,
				msg="Missing telemetry data at path " + ConfigLoader.Telemetry["base_path"]
			)
		
		with open(ConfigLoader.Telemetry["base_path"]) as f:
			contents = f.read()
		telemetry_data = json.loads(contents)
		ConfigLoader.Telemetry["config"] = telemetry_data
		return telemetry_data
