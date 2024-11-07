#!/usr/bin/python3
#coding:utf-8

"""
Run tests on the users collector to check it works as planned.

Authors:
Nathan Amorison

Version:
0.1.4
"""

from .. import modules
from ..modules import UsersCollector
from ..core.octets import VarInt
from ..core import tools
import unittest

class TestUsersCollector(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		print(f"\nBegining tests on the UsersCollector static methods.")

	@classmethod
	def setUp(self):
		print(f"testing new method...")

	@classmethod
	def tearDown(self):
		print(f"test has been performed.")

	@classmethod
	def tearDownClass(self):
		print(f"Tests ended on the UsersCollector static methods.\n")

	def test_parse_user_line(self):
		"""
		[parse_user_line] well formed.
		"""
		line = "1000(user):1000,24,25,27,29"
		expected = (1000, "user", [1000,24,25,27,29])

		result = UsersCollector.parse_user_line(line)

		self.assertEqual(result, expected)

	def test_parse_user_line_single_group(self):
		"""
		[parse_user_line] well formed with single group.
		"""
		line = "1000(user):1000"
		expected = (1000, "user", [1000])

		result = UsersCollector.parse_user_line(line)

		self.assertEqual(result, expected)

	def test_parse_group_line(self):
		"""
		[parse_group_line] well formed.
		"""
		line = "user:1000"
		expected = (1000, "user")

		result = UsersCollector.parse_group_line(line)

		self.assertEqual(result, expected)

class TestLinUsersCollector(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		print(f"\nBegining tests on the LinUsersCollector collector object.")

	@classmethod
	def setUp(self):
		print(f"testing new method...")

	@classmethod
	def tearDown(self):
		print(f"test has been performed.")

	@classmethod
	def tearDownClass(self):
		print(f"Tests ended on the UsersCollectors collector object\n")

	def test__format(self):
		"""
		[_format]
		"""
		collector = UsersCollector.LinUsersCollector()
		users = [
			UsersCollector.User(1000, "user", [1000, 24, 25, 27, 29]),
			UsersCollector.User(0, "root", [0]),
			]
		groups = [
			UsersCollector.Group(1000, "user"),
			UsersCollector.Group(0, "root"),
			UsersCollector.Group(24, "cdrom"),
			UsersCollector.Group(25, "floppy"),
			UsersCollector.Group(27, "sudo"),
			UsersCollector.Group(29, "audio"),
		]
		sudoers = [UsersCollector.Sudoer(1000)]
		md5 = tools.get_file_hash("./exposurescout/tests/hash_test_file.txt")

		collector.raw_result = {UsersCollector.User.element_name:users, UsersCollector.Group.element_name:groups, UsersCollector.Sudoer.element_name:sudoers, "passwd_hash":md5, "group_hash":md5}

		expected = b"\x00\x20\x64\x02\x23\xe8\x04user\x05\x23\xe8\x18\x19\x1b\x1d\x00\x04root\x01\x00\x06\x23\xe8\x04user\x00\x04root\x18\x05cdrom\x19\x06floppy\x1b\x04sudo\x1d\x05audio\x01\x23\xe8\x8d\xdd\x8b\xe4\xb1\x79\xa5\x29\xaf\xa5\xf2\xff\xae\x4b\x98\x58\x8d\xdd\x8b\xe4\xb1\x79\xa5\x29\xaf\xa5\xf2\xff\xae\x4b\x98\x58"

		collector._format()
		result = collector.result

		self.assertEqual(expected, result)

class TestUser(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		print(f"\nBegining tests on the User data structure.")

	@classmethod
	def setUp(self):
		print(f"testing new method...")

	@classmethod
	def tearDown(self):
		print(f"test has been performed.")

	@classmethod
	def tearDownClass(self):
		print(f"Tests ended on the User data structure.\n")

	def test_to_bytes(self):
		"""
		[to_bytes] with a basic user DS.
		"""
		user = UsersCollector.User(1000, "user", [1000,24,25,27,29])
		expected = b"\x23\xe8\x04user\x05\x23\xe8\x18\x19\x1b\x1d"
		result = user.to_bytes()

		self.assertEqual(expected, result)

	def test_from_bytes(self):
		"""
		[from_bytes] with a basic user DS.
		"""
		expected = (UsersCollector.User(1000, "user", [1000,24,25,27,29]), None)
		user = b"\x23\xe8\x04user\x05\x23\xe8\x18\x19\x1b\x1d"
		result = UsersCollector.User.from_bytes(user)

		self.assertEqual(expected, result)

class TestGroup(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		print(f"\nBegining tests on the Group data structure")

	@classmethod
	def setUp(self):
		print(f"testing new method...")

	@classmethod
	def tearDown(self):
		print(f"test has been performed.")

	@classmethod
	def tearDownClass(self):
		print(f"Tests ended on the Group data structure\n")

	def test_to_bytes(self):
		"""
		[to_bytes] with a basic group DS.
		"""
		group = UsersCollector.Group(1000, "user")
		expected = b"\x23\xe8\x04user"
		result = group.to_bytes()

		self.assertEqual(expected, result)

	def test_from_bytes(self):
		"""
		[from_bytes] with a basic group DS.
		"""
		expected = (UsersCollector.Group(1000, "user"), None)
		group = b"\x23\xe8\x04user"
		result = UsersCollector.Group.from_bytes(group)

		self.assertEqual(expected, result)

class TestSudoers(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		print(f"\nBegining tests on the Sudoers data structure.")

	@classmethod
	def setUp(self):
		print(f"testing new method...")

	@classmethod
	def tearDown(self):
		print(f"test has been performed.")

	@classmethod
	def tearDownClass(self):
		print(f"Tests ended on the Sudoers data structure.\n")

	def test_to_bytes(self):
		"""
		[to_bytes] with a basic sudoer DS.
		"""
		sudoer = UsersCollector.Sudoer(1000)
		expected = b"\x23\xe8"
		result = sudoer.to_bytes()

		self.assertEqual(expected, result)

	def test_from_bytes(self):
		"""
		[from_bytes] with a basic sudoer DS.
		"""
		expected = (UsersCollector.Sudoer(1000), None)
		sudoer = b"\x23\xe8"
		result = UsersCollector.Sudoer.from_bytes(sudoer)

		self.assertEqual(expected, result)

if __name__ == '__main__':
	unittest.main()