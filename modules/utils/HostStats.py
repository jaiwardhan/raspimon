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
    def get():
        """Return host stats and metrics. Can be extended
		to return extra and more complicated information which
		can be tuned with your alarm configuration to generate
		crisp alerts.

		Returns:
			dict: A KV pair dict containing the supported metrics
			as configured by you.
		"""
        supported_map = HostStats.__get_map()
        stats = {}
        for each_supported_stat in supported_map.keys():
            stats[each_supported_stat] = supported_map[each_supported_stat]()
        
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
