#!/usr/bin/python3
#coding:utf-8

"""
Run tests on report related objects for diff.

Authors:
Nathan Amorison

Version:
0.1.4
"""

from ..modules import LinUsersCollector, User, Group, Sudoer
from ..core.report import DiffElement, DiffReport, CREATED, DELETED, MODIFIED
from ..core import tools
from ..core.octets import VarInt
import unittest

class TestDiffElement(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		print(f"\nBegining tests on the DiffElement method.")

	@classmethod
	def setUp(self):
		print(f"testing new method...")

	@classmethod
	def tearDown(self):
		print(f"test has been performed.")

	@classmethod
	def tearDownClass(self):
		print(f"Tests ended on the DiffElement methods.\n")

	def test_eq(self):
		"""
		testing the __eq__ method.
		"""
		element_a = DiffElement("test_a", "test_a", "string")
		element_b = DiffElement("test_b", "test_b", "string")

		self.assertNotEqual(element_a, element_b)

		element_b = DiffElement("test_a", "test_a", "string")

		self.assertEqual(element_a, element_b)

	def test_to_bytes(self):
		"""
		[to_bytes]
		"""
		run_id = "test"
		user = User(1001, "test", [1001])
		element = DiffElement(run_id, user, CREATED)

		result = element.to_bytes({run_id:b"\x00"})

		expected = b"\x00\x23\xe9\x04test\x01\x23\xe9\x00"

		self.assertEqual(result, expected)

	def test_from_bytes(self):
		"""
		[from_bytes]
		"""
		run_id = "test"
		user = User(1001, "test", [1001])
		expected = DiffElement(run_id, user, CREATED)

		data = b"\x00\x23\xe9\x04test\x01\x23\xe9\x00"

		result, rest = DiffElement.from_bytes(data, [run_id], User)

		self.assertEqual(result, expected)
		self.assertEqual(rest, None)


class TestDiffReport(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		print(f"\nBegining tests on the DiffElement method.")

	@classmethod
	def setUp(self):
		print(f"testing new method...")

	@classmethod
	def tearDown(self):
		print(f"test has been performed.")

	@classmethod
	def tearDownClass(self):
		print(f"Tests ended on the DiffElement methods.\n")

	def test_eq(self):
		"""
		testing the __eq__ method.
		"""
		run_id_a = "test_a"
		run_id_b = "test_b"

		uc_a = LinUsersCollector()
		uc_b = LinUsersCollector()

		users = [
			User(1000, "user", [1000,24,25,27,29])
		]
		groups = [
			Group(1000, "user"),
			Group(0, "root"),
			Group(24, "cdrom"),
			Group(25, "floppy"),
			Group(27, "sudo"),
			Group(29, "audio"),
		]
		sudoers = [Sudoer(1000)]
		md5 = tools.get_file_hash("./exposurescout/tests/hash_test_file.txt")

		uc_a.raw_result = {User.element_name:users.copy(), Group.element_name:groups.copy(), Sudoer.element_name:sudoers.copy(), "passwd_hash":md5, "group_hash":md5}
		uc_b.raw_result = {User.element_name:users.copy(), Group.element_name:groups.copy(), Sudoer.element_name:sudoers.copy(), "passwd_hash":md5, "group_hash":md5}

		result = DiffReport(run_id_a, run_id_b)

		LinUsersCollector.make_diff(run_id_a, run_id_b, uc_a, uc_b, result)

		expected = DiffReport(run_id_a, run_id_b)
		expected.diff_elemnts = {LinUsersCollector.name : {User.element_name:[], Group.element_name: [], Sudoer.element_name: []}}

		self.assertEqual(result, expected)

		new_user = User(1001, "test", [1001])
		new_group = Group(1001, "test")
		new_sudoer = Sudoer(1001)

		uc_b.raw_result[User.element_name].append(new_user)
		uc_b.raw_result[Group.element_name].append(new_group)
		uc_b.raw_result[Sudoer.element_name].append(new_sudoer)

		LinUsersCollector.make_diff(run_id_a, run_id_b, uc_a, uc_b, result)

		expected = DiffReport(run_id_a, run_id_b)
		expected.diff_elemnts = {
			LinUsersCollector.name : {
				User.element_name:[
					DiffElement(run_id_b, new_user, CREATED),
				],
				Group.element_name: [
					DiffElement(run_id_b, new_group, CREATED),
				],
				Sudoer.element_name: [
					DiffElement(run_id_b, new_sudoer, CREATED),
				]
			}
		}

		self.assertEqual(result, expected)


		result = DiffReport(run_id_a, run_id_b)

		uc_a.raw_result = {User.element_name:[User(1000, "user", [1000,24,25,27,29])], Group.element_name:groups.copy(), Sudoer.element_name:sudoers.copy(), "passwd_hash":md5, "group_hash":md5}
		uc_b.raw_result = {User.element_name:[User(1000, "user", [1000,24,25,27,29])], Group.element_name:groups.copy(), Sudoer.element_name:sudoers.copy(), "passwd_hash":md5, "group_hash":md5}

		new_user = User(1001, "test", [1001])
		new_group = Group(1001, "test")
		new_sudoer = Sudoer(1001)

		uc_a.raw_result[User.element_name].append(new_user)
		uc_a.raw_result[Group.element_name].append(new_group)
		uc_a.raw_result[Sudoer.element_name].append(new_sudoer)
		uc_b.raw_result[User.element_name][0].groups.append(1001)

		LinUsersCollector.make_diff(run_id_a, run_id_b, uc_a, uc_b, result)

		expected = DiffReport(run_id_a, run_id_b)
		expected.diff_elemnts = {
			LinUsersCollector.name : {
				User.element_name:[
					DiffElement(run_id_a, users[0], MODIFIED),
					DiffElement(run_id_b, uc_b.raw_result[User.element_name][0], MODIFIED),
					DiffElement(run_id_a, new_user, DELETED),
				],
				Group.element_name: [
					DiffElement(run_id_a, new_group, DELETED),
				],
				Sudoer.element_name: [
					DiffElement(run_id_a, new_sudoer, DELETED),
				]
			}
		}

		self.assertEqual(result, expected)

	def test_to_bytes(self):
		"""
		[to_bytes]
		"""
		collector = LinUsersCollector.name

		user = User(1001, "test", [1001])
		group = Group(1001, "test")
		sudoer = Sudoer(1001)

		run_id_a = "test_a"
		run_id_b = "test_b"

		diff_report = DiffReport(run_id_a, run_id_b)
		diff_report.diff_elemnts = {
			collector : {
				User.element_name:[
					DiffElement(run_id_b, user, CREATED),
				],
				Group.element_name: [
					DiffElement(run_id_b, group, CREATED),
				],
				Sudoer.element_name: [
					DiffElement(run_id_b, sudoer, CREATED),
				]
			}
		}

		expected = b"\x11\x06test_a\x06test_b\x01\x00\x00\x00\x01\x01\x23\xe9\x04test\x01\x23\xe9\x00\x01\x01\x23\xe9\x04test\x00\x01\x01\x23\xe9\x00"

		header, report = diff_report.to_bytes()
		result = VarInt.to_bytes(len(header)) + header + report

		self.assertEqual(result, expected)

	def test_to_bytes_empty(self):
		"""
		[to_bytes] with no differences between two snapshots.
		"""
		collector = LinUsersCollector.name

		run_id_a = "test_a"
		run_id_b = "test_b"

		diff_report = DiffReport(run_id_a, run_id_b)
		diff_report.diff_elemnts = {
			collector : {
				User.element_name:[],
				Group.element_name: [],
				Sudoer.element_name: []
			}
		}

		expected = b"\x11\x06test_a\x06test_b\x01\x00\x00\x00\x00\x00\x00"

		header, report = diff_report.to_bytes()
		result = VarInt.to_bytes(len(header)) + header + report

		self.assertEqual(result, expected)

	def test_read_collector_from_bytes(self):
		"""
		[read_collector_from_bytes]
		"""
		collector = LinUsersCollector.name

		user = User(1001, "test", [1001])
		group = Group(1001, "test")
		sudoer = Sudoer(1001)

		run_id_a = "test_a"
		run_id_b = "test_b"

		expected = DiffReport(run_id_a, run_id_b)
		expected.diff_elemnts = {
			collector : {
				User.element_name:[
					DiffElement(run_id_b, user, CREATED),
				],
				Group.element_name: [
					DiffElement(run_id_b, group, CREATED),
				],
				Sudoer.element_name: [
					DiffElement(run_id_b, sudoer, CREATED),
				]
			}
		}

		data = b"\x00\x01\x01\x23\xe9\x04test\x01\x23\xe9\x00\x01\x01\x23\xe9\x04test\x00\x01\x01\x23\xe9\x00"

		result = DiffReport(run_id_a, run_id_b)
		result.read_collector_from_bytes(data,[run_id_a, run_id_b], LinUsersCollector)

		self.assertEqual(result, expected)

	def test_read_collector_from_bytes_Exception(self):
		"""
		[read_collector_from_bytes] with ValueError exception because the collectors do not match
		"""
		collector = LinUsersCollector.name

		user = User(1001, "test", [1001])
		group = Group(1001, "test")
		sudoer = Sudoer(1001)

		run_id_a = "test_a"
		run_id_b = "test_b"

		expected = DiffReport(run_id_a, run_id_b)
		expected.diff_elemnts = {
			collector : {
				User.element_name:[
					DiffElement(run_id_b, user, CREATED),
				],
				Group.element_name: [
					DiffElement(run_id_b, group, CREATED),
				],
				Sudoer.element_name: [
					DiffElement(run_id_b, sudoer, CREATED),
				]
			}
		}

		data = b"\x01\x01\x01\x23\xe9\x04test\x01\x23\xe9\x00\x01\x01\x23\xe9\x04test\x00\x01\x01\x23\xe9\x00"

		diff_report = DiffReport(run_id_a, run_id_b)
		result = lambda : diff_report.read_collector_from_bytes(data,[run_id_a, run_id_b], LinUsersCollector)

		self.assertRaises(ValueError, result)


if __name__ == '__main__':
	unittest.main()