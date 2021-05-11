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
from datetime import datetime
import os

class Logger:
	"""Simple class to help log execution event to a log file to
	trace the timestamp of events - start and stops.
	"""
	
	@staticmethod
	def execution_log(started = True):
		"""Log that a program execution has started/stopped to `raspimon` logs

		Args:
			started (bool, optional): Set `True` on start, `False` on terminate. Defaults to True.
		"""
		dateTimeObj = datetime.now()
		timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
		msg = " - " + timestampStr + " -- " + "Execution " + ("started" if started else "finished")
		
		if not os.path.exists(ConfigLoader.Logging["base_dir"]):
			os.mkdir(ConfigLoader.Logging["base_dir"])
		elif os.path.isfile(ConfigLoader.Logging["base_dir"]):
			os.remove(ConfigLoader.Logging["base_dir"])
			os.mkdir(ConfigLoader.Logging["base_dir"])
		
		with open(	ConfigLoader.Logging["base_dir"] + "/" +\
					ConfigLoader.Logging["execution_log"], "a+") as exc_log:
			exc_log.write(msg + "\n")
