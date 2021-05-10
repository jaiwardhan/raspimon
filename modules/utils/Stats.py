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

from modules.utils.Exec import Exec
import psutil
import platform

class HostStats:
	"""Utility class to get collect host stat metrics
	"""

	@staticmethod
	def cpu():
		return psutil.cpu_percent()
	
	@staticmethod
	def mem():
		return psutil.virtual_memory().percent

	@staticmethod
	def __get_map():
		return {
			"cpu": HostStats.cpu,
			"mem": HostStats.mem
		}

	@staticmethod
	def get(metrics):
		"""Return host stats and metrics. Can be extended
		to return extra and more complicated information which
		can be tuned with your alarm configuration to generate
		crisp alerts.

		Args:
			metrics (list): A list of metrics to fetch. Unsupported metrics will 
			be skipped and wont be notified.
		
		Returns:
			dict: A KV pair dict containing the supported metrics as configured.
		"""        

		supported_map = HostStats.__get_map()
		stats = {}
		for each_metric in metrics:
			if each_metric in supported_map:
				stats[each_metric] = supported_map[each_metric]()
		
		return stats
	
	@staticmethod
	def supported(code):
		"""Whether a stat code is supported by this module

		Args:
			code (str): The stat code being looked up to

		Returns:
			bool: True if supported | False otherwise
		"""
		return str(code) in HostStats.__get_map()
	
	@staticmethod
	def platform():
		"""Get the host platform - generally the `hostname`

		Returns:
			str: Generally the `hostname` of the host
		"""
		return platform.node()

class ServiceStats:
	"""Utility class to get collect service stat metrics
	"""

	@staticmethod
	def psaux():
		process_desc = []
		running_processes_str, _, __ = Exec.shell("ps aux", True)
		running_processes = str(running_processes_str).split("\n")
		# Filter empty lines
		running_processes = list(filter(None, running_processes))
		# For every process, trim extra spaces in between
		for i in range(0, len(running_processes)):
			rpi = list(filter(None, running_processes[i].split(" ")))
			owner = rpi[0]
			pid = rpi[1]
			cpu = rpi[2]
			mem = rpi[3]
			uptime = rpi[9]
			command = " ".join(rpi[10:])
			base_command = rpi[10]
			process_desc.append({
				"command": command,
				"owner": owner,
				"pid": pid,
				"cpu": cpu,
				"mem": mem,
				"uptime": uptime
			})
		return process_desc

	@staticmethod
	def process_get(processes):
		"""Return host stats and metrics. Can be extended
		to return extra and more complicated information which
		can be tuned with your alarm configuration to generate
		crisp alerts.

		Args:
			processes (list): Service process names to be `ps aux`-ed

		Returns:
			dict: A KV pair dict containing the supported metrics
			as configured by you.
		"""        

		running_processes = ServiceStats.psaux()
		stats = {}
		for each_process in processes:
			stats[each_process] = "down"
			for each_running_process in running_processes:
				if each_process in each_running_process["command"]:
					stats[each_process] = "up"
					break
		return stats
	
	@staticmethod
	def supported(code):
		"""Whether a stat code is supported by this module

		Args:
			code (str): The stat code being looked up to

		Returns:
			bool: True if supported | False otherwise
		"""
		return str(code) in {
			"up": "up",
			"down": "down"
		}
	
	@staticmethod
	def platform():
		"""Get the host platform - generally the `hostname`

		Returns:
			str: Generally the `hostname` of the host
		"""
		return platform.node()
