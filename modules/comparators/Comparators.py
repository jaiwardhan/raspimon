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
	"""Common numeric comparators for easy reference via codes
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

	"""Gets the most appropriate comparator based on the code

	Returns:
		func: Reference to the eligible comparator
	"""
	@staticmethod
	def get(code):
		cnc_map = NumericComparator.__get_map()
		return cnc_map[str(code)] if str(code) in cnc_map else NumericComparator.eq
	
	"""Check the passed code is supported by this comparator

	Returns:
		boolean: True if supported | False otherwise
	"""
	@staticmethod
	def supported(code):
		return str(code) in NumericComparator.__get_map()

class ServiceComparator:

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
		cssc_map = ServiceComparator.__get_map()
		return cssc_map[str(code)] if str(code) in cssc_map else ServiceComparator.up
	
	@staticmethod
	def supported(code):
		return str(code) in ServiceComparator.__get_map()
