#!/usr/bin/python3
#coding:utf-8

"""
Run tests on the filter module to check it works as planned.

Authors:
Nathan Amorison

Version:
0.2.0
"""

from .. import modules
from ..modules import Filter
from ..core.octets import VarInt
from ..core import tools, report
import unittest

class TestRule(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		print(f"\nBegining tests on the Rule object.")

	@classmethod
	def setUp(self):
		print(f"testing new method...")

	@classmethod
	def tearDown(self):
		print(f"test has been performed.")

	@classmethod
	def tearDownClass(self):
		print(f"Tests ended on the Rule object.\n")

	def test_eq(self):
		"""
		[eq]
		"""
		r1 = Filter.Rule(Filter.Include, "test_level", "test_collector","test_element", "test_target", r"")
		r2 = Filter.Rule(Filter.Include, "test_level", "test_collector","test_element", "test_target", r"")
		r3 = Filter.Rule(Filter.Exclude, "test_level", "test_collector","test_element", "test_target", r"")

		print(r1 == r2)
		print(isinstance(r1, Filter.Rule))
		print(isinstance(r2, Filter.Rule))

		self.assertEqual(r1, r2)
		self.assertNotEqual(r1, r3)

	def test_run(self):
		"""
		[run]
		"""
		rule = Filter.Rule(Filter.Include, Filter.ElementLevel, modules.LinUsersCollector, modules.User.element_name, "name", r"[a-zA-Z]*[0-9]+[a-zA-Z]*")
		# rule = ```INCLUDE any USER having numbers in its NAME```

		print(rule)
		user1 = modules.User(42, "liveis42", [42])
		user2 = modules.User(1001, "test", [1001])

		result = rule.run(user1)
		self.assertTrue(result)
		result = rule.run(user2)
		self.assertFalse(result)

	def test_run_error(self):
		"""
		[run] with errors
		"""
		rule = Filter.Rule(Filter.Include, Filter.ElementLevel, modules.LinUsersCollector, modules.Sudoer.element_name, "gid", r"[a-zA-Z]*[0-9]+[a-zA-Z]*")
		
		sudoer = modules.Sudoer(42)

		self.assertRaises(ValueError, lambda:rule.run(sudoer))



class TestFilter(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		print(f"\nBegining tests on the Linux/Unix File System Collector.")

	@classmethod
	def setUp(self):
		print(f"testing new method...")

	@classmethod
	def tearDown(self):
		print(f"test has been performed.")

	@classmethod
	def tearDownClass(self):
		print(f"Tests ended on the Linux/Unix File System Collector.\n")

	# def test_eq(self):
	# 	"""
	# 	[__eq__]
	# 	"""
	# 	pass