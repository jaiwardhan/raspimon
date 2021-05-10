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

class NumericComparator:
	"""Provides common numeric comparators for easy reference via codes
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
			"lt": NumericComparator.lt,
			"gt": NumericComparator.gt,
			"eq": NumericComparator.eq,
			"leq": NumericComparator.leq,
			"geq": NumericComparator.geq
		}

	@staticmethod
	def get(code):
		"""Gets the most appropriate comparator based on the code

		Args:
			code (str): The code corresponding to the comparator being
			looked upon.

		Returns:
			func: Reference to the eligible comparator
		"""
		cnc_map = NumericComparator.__get_map()
		return cnc_map[str(code)] if str(code) in cnc_map else NumericComparator.eq
	
	@staticmethod
	def supported(code):
		"""Check the passed code is supported by this comparator

		Args:
			code (str): The code being checked for its support

		Returns:
			boolean: True if supported | False otherwise
		"""
		return str(code) in NumericComparator.__get_map()

class ServiceComparator:
	"""Provides compartors for a service's status via codes
	"""

	@staticmethod
	def up(name):
		pass

	@staticmethod
	def down(name):
		pass

	@staticmethod
	def __get_map():
		return {
			"down": ServiceComparator.down,
			"up": ServiceComparator.up
		}
	
	@staticmethod
	def get(code):
		"""Get the most appropriate service comparator based on the code

		Args:
			code (str): The code corresponding to the comparator being
			looked upon.

		Returns:
			func: Reference to the eligible comparator
		"""
		cssc_map = ServiceComparator.__get_map()
		return cssc_map[str(code)] if str(code) in cssc_map else ServiceComparator.up
	
	@staticmethod
	def supported(code):
		"""Check the passed code is supported by this comparator

		Args:
			code (str): The code being checked for its support

		Returns:
			boolean: True if supported | False otherwise
		"""
		return str(code) in ServiceComparator.__get_map()
