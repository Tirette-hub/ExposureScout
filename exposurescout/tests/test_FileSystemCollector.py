#!/usr/bin/python3
#coding:utf-8

"""
Run tests on the file system collector to check it works as planned.

Authors:
Nathan Amorison

Version:
0.1.0
"""

from .. import modules
from ..modules import FileSystemCollector as FSCollector
from ..core.octets import VarInt
from ..core import tools, report
import unittest
import os
import sqlite3 as sql

unittest.util._MAX_LENGTH=2000

class TestLinFileSystemCollector(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		print(f"\nBegining tests on the Linux/Unix File System Collector.")

		path = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir")

		test_file1 = os.path.join(path, "test_file1.txt")
		self.file1 = FSCollector.File(test_file1, None, 13, b"\x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X")
		
		# Hardcode metadata to make it work on every machine (depending on the machine, metadata will be different, so we do not collect them as in the module)
		self.file1.mode = 33188
		self.file1.inode = 968625
		self.file1.uid = 1001
		self.file1.gid = 1001
		self.file1.metadata_hash = b"\xd5oy\xa3f(\xa9\x001\xd9Z\xfbJ\xdf\xd3 "


		test_file2 = os.path.join(path, "test_file2.txt")
		self.file2 = FSCollector.File(test_file2, None, 13, b"\x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X")

		# Hardcode metadata to make it work on every machine (depending on the machine, metadata will be different, so we do not collect them as in the module)
		self.file2.mode = 33188
		self.file2.inode = 968595
		self.file2.uid = 1001
		self.file2.gid = 1001
		self.file2.metadata_hash = b"\xd9y\x96'\xba\x1b2\xf2\xbf,\xd4\xc9\xa9\xb4GK"


		test_directory = path
		self.directory = FSCollector.Directory(test_directory, None)
		self.directory.append_all([self.file1, self.file2])

		# Hardcode metadata to make it work on every machine (depending on the machine, metadata will be different, so we do not collect them as in the module)
		self.directory.mode = 16877
		self.directory.inode = 968624
		self.directory.uid = 1001
		self.directory.gid = 1001
		self.directory.size = 26
		self.directory.metadata_hash = b"\xde#\x1e\xf5\x06P\x0e\x92f\x1c/E\xef\x81\xe3`"

	@classmethod
	def setUp(self):
		print(f"testing new method...")

	@classmethod
	def tearDown(self):
		print(f"test has been performed.")

	@classmethod
	def tearDownClass(self):
		print(f"Tests ended on the Linux/Unix File System Collector.\n")

	def test_eq(self):
		"""
		[__eq__]
		"""
		path = os.path.join(os.path.dirname(__file__), "./test_FileSystemCollector_dir/")

		collector1 = FSCollector.LinFileSystemCollector()
		collector1.set_rule(path)
		collector1.run()

		collector2 = FSCollector.LinFileSystemCollector()
		collector2.set_rule(path)
		collector2.run()

		self.assertEqual(collector1, collector2)


		path = os.path.dirname(__file__)
		collector3 = FSCollector.LinFileSystemCollector()
		collector3.set_rule(path)
		collector3.run()

		self.assertNotEqual(collector1, collector3)


	def test_walk_through(self):
		"""
		[walk_through]
		"""
		path = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir/")

		collector = FSCollector.LinFileSystemCollector()
		result = collector.walk_through(path)

		metadata = os.lstat(path)
		expected = FSCollector.Directory(path, metadata)

		f_path = os.path.join(path, "test_file1.txt")
		metadata = os.lstat(f_path)
		file = FSCollector.File(f_path, metadata, 13, tools.get_file_hash(f_path))
		expected.append(file)

		f_path = os.path.join(path, "test_file2.txt")
		metadata = os.lstat(f_path)
		file = FSCollector.File(f_path, metadata, 13, tools.get_file_hash(f_path))
		expected.append(file)

		self.assertEqual(result, expected)

	def test__format(self):
		"""
		[_format]
		"""
		path = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir")

		collector = FSCollector.LinFileSystemCollector()
		collector.set_rule(path)
		collector.run()

		result = collector.export_bin()

		expected = b"\x01"

		test_file1 = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir/test_file1.txt")
		metadata = os.lstat(test_file1)
		file1 = FSCollector.File(test_file1, metadata, 13, tools.get_file_hash(test_file1))
		
		test_file2 = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir/test_file2.txt")
		metadata = os.lstat(test_file2)
		file2 = FSCollector.File(test_file2, metadata, 13, tools.get_file_hash(test_file2))
		
		test_directory = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir")
		metadata = os.lstat(test_directory)
		directory = FSCollector.Directory(test_directory, metadata)
		directory.append_all([file1, file2])

		expected += directory.to_bytes()

		self.assertEqual(result, expected)

	def test_import_bin(self):
		"""
		[import_bin]
		"""
		path = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir")

		data = b"\x01"
		data += VarInt.to_bytes(len(path))
		data += path.encode()
		data += b"@A\xedN\xc7\xb0#\xe8#\xe80\x00\xde#\x1e\xf5\x06P\x0e\x92f\x1c/E\xef\x81\xe4`\x02"
		data += b"\x0etest_file1.txt@\x81\xa4N\xc7\xb1#\xe8#\xe8\r\xd5oy\xa3f(\xa9\x001\xd9Z\xfbJ\xdf\xd4 \x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X"
		data += b"\x0etest_file2.txt@\x81\xa4N\xc7\x93#\xe8#\xe8\r\xd9y\x96'\xba\x1b2\xf2\xbf,\xd4\xc9\xa9\xb9GK\x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X"

		collector = FSCollector.LinFileSystemCollector()
		collector.import_bin(data)

		result = collector.raw_result

		path = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir/test_file1.txt")
		file1 = FSCollector.File(path, None, 13, b"\x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X")
		file1.mode = 33188
		file1.inode = 968625
		file1.uid = 1000
		file1.gid = 1000
		file1.metadata_hash = b"\xd5oy\xa3f(\xa9\x001\xd9Z\xfbJ\xdf\xd4 "

		test_file2 = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir/test_file2.txt")
		file2 = FSCollector.File(test_file2, None, 13, b"\x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X")

		# Hardcode metadata to make it work on every machine (depending on the machine, metadata will be different, so we do not collect them as in the module)
		file2.mode = 33188
		file2.inode = 968595
		file2.uid = 1000
		file2.gid = 1000
		file2.metadata_hash = b"\xd9y\x96'\xba\x1b2\xf2\xbf,\xd4\xc9\xa9\xb9GK"

		test_directory = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir")
		directory = FSCollector.Directory(test_directory, None)
		directory.append_all([file1, file2])

		# Hardcode metadata to make it work on every machine (depending on the machine, metadata will be different, so we do not collect them as in the module)
		directory.mode = 16877
		directory.inode = 968624
		directory.uid = 1000
		directory.gid = 1000
		directory.size = 4096
		directory.metadata_hash = b"\xde#\x1e\xf5\x06P\x0e\x92f\x1c/E\xef\x81\xe4`"

		expected = [directory]

		self.assertEqual(result, expected)

	def test_make_diff(self):
		"""
		[make_diff]
		"""
		run_id_a = "test_a"
		run_id_b = "test_b"

		collector_a = FSCollector.LinFileSystemCollector()


		# hard code values so we have control over values that are tested
		test_file1 = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir/test_file1.txt")
		metadata = os.lstat(test_file1)
		file1 = FSCollector.File(test_file1, metadata, 13, tools.get_file_hash(test_file1))
		file1.inode = 968625
		
		test_file2 = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir/test_file2.txt")
		metadata = os.lstat(test_file2)
		file2 = FSCollector.File(test_file2, metadata, 13, tools.get_file_hash(test_file2))
		file2.inode = 968595
		
		test_directory = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir")
		metadata = os.lstat(test_directory)
		directory = FSCollector.Directory(test_directory, metadata)
		directory.append_all([file1, file2])
		directory.inode = 968624

		collector_a.raw_result = [directory]


		expected = report.DiffReport(run_id_a, run_id_b)
		expected.diff_elemnts = {
			'File System Collector': {
				'File': [
					report.DiffElement(run_id_a, FSCollector.DiffFile(directory), report.DELETED),
					report.DiffElement(run_id_a, FSCollector.DiffFile(file1), report.DELETED),
					report.DiffElement(run_id_a, FSCollector.DiffFile(file2), report.DELETED),
				]
			}
		}

		result = report.DiffReport(run_id_a, run_id_b)
		FSCollector.LinFileSystemCollector.make_diff(run_id_a, run_id_b, collector_a, None, result)

		self.assertEqual(result, expected)

		collector_b = FSCollector.LinFileSystemCollector()
		collector_b.raw_result = [self.directory]

		expected.diff_elemnts = {
			'File System Collector': {
				'File': [
					report.DiffElement(run_id_a, FSCollector.DiffFile(directory), report.MODIFIED),
					report.DiffElement(run_id_b, FSCollector.DiffFile(self.directory), report.MODIFIED),
					report.DiffElement(run_id_a, FSCollector.DiffFile(file1), report.MODIFIED),
					report.DiffElement(run_id_b, FSCollector.DiffFile(self.file1), report.MODIFIED),
					report.DiffElement(run_id_a, FSCollector.DiffFile(file2), report.MODIFIED),
					report.DiffElement(run_id_b, FSCollector.DiffFile(self.file2), report.MODIFIED),
				]
			}
		}

		result = report.DiffReport(run_id_a, run_id_b)
		FSCollector.LinFileSystemCollector.make_diff(run_id_a, run_id_b, collector_a, collector_b, result)

		self.assertNotEqual(collector_a, collector_b)
		self.assertEqual(result, expected)

	def test_import_diff_from_report(self):
		"""
		[import_diff_from_report]
		"""
		run_id_a = "test_a"
		run_id_b = "test_b"

		collector_a = FSCollector.LinFileSystemCollector()


		# hard code values so we have control over values that are tested
		test_file1 = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir/test_file1.txt")
		metadata = os.lstat(test_file1)
		file1 = FSCollector.File(test_file1, metadata, 13, tools.get_file_hash(test_file1))
		file1.inode = 968625
		
		test_file2 = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir/test_file2.txt")
		metadata = os.lstat(test_file2)
		file2 = FSCollector.File(test_file2, metadata, 13, tools.get_file_hash(test_file2))
		file2.inode = 968595
		
		test_directory = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir")
		metadata = os.lstat(test_directory)
		directory = FSCollector.Directory(test_directory, metadata)
		directory.append_all([file1, file2])
		directory.inode = 968624

		collector_a.raw_result = [directory]

		expected = report.DiffReport(run_id_a, run_id_b)
		expected.diff_elemnts = {
			'File System Collector': {
				'File': [
					report.DiffElement(run_id_a, FSCollector.DiffFile(directory), report.MODIFIED),
					report.DiffElement(run_id_b, FSCollector.DiffFile(self.directory), report.MODIFIED),
					report.DiffElement(run_id_a, FSCollector.DiffFile(file1), report.MODIFIED),
					report.DiffElement(run_id_b, FSCollector.DiffFile(self.file1), report.MODIFIED),
					report.DiffElement(run_id_a, FSCollector.DiffFile(file2), report.MODIFIED),
					report.DiffElement(run_id_b, FSCollector.DiffFile(self.file2), report.MODIFIED),
				]
			}
		}

		result = report.DiffReport(run_id_a, run_id_b)

		data = b"\x06"

		data += b"\x00"
		data += FSCollector.DiffFile(directory).to_bytes()
		data += b"\x02"

		data += b"\x01"
		data += FSCollector.DiffFile(self.directory).to_bytes()
		data += b"\x02"

		data += b"\x00"
		data += FSCollector.DiffFile(file1).to_bytes()
		data += b"\x02"

		data += b"\x01"
		data += FSCollector.DiffFile(self.file1).to_bytes()
		data += b"\x02"

		data += b"\x00"
		data += FSCollector.DiffFile(file2).to_bytes()
		data += b"\x02"

		data += b"\x01"
		data += FSCollector.DiffFile(self.file2).to_bytes()
		data += b"\x02"

		FSCollector.LinFileSystemCollector.import_diff_from_report(data, [run_id_a, run_id_b], result)

		self.assertEqual(result, expected)

	def test__export_sql(self):
		"""
		[_export_sql]
		"""
		run_id = "test_a"

		path = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir")

		collector = FSCollector.LinFileSystemCollector()

		# hard code values so we have control over values that are tested
		test_file1 = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir/test_file1.txt")
		metadata = os.lstat(test_file1)
		file1 = FSCollector.File(test_file1, metadata, 13, tools.get_file_hash(test_file1))
		file1.inode = 968625
		
		test_file2 = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir/test_file2.txt")
		metadata = os.lstat(test_file2)
		file2 = FSCollector.File(test_file2, metadata, 13, tools.get_file_hash(test_file2))
		file2.inode = 968595
		
		test_directory = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir")
		metadata = os.lstat(test_directory)
		directory = FSCollector.Directory(test_directory, metadata)
		directory.append_all([file1, file2])
		directory.inode = 968624

		collector.raw_result = [directory]


		conn = sql.connect(":memory:")
		cursor = conn.cursor()

		collector._export_sql(cursor, run_id)
		conn.commit()

		query = f"""SELECT * FROM files"""
		request = cursor.execute(query)
		result = request.fetchall()

		conn.close()

		expected = [
			(run_id, directory.inode, directory.mode, directory.uid, directory.gid, directory.size, directory.path, None, directory.metadata_hash, None),
			(run_id, file1.inode, file1.mode, file1.uid, file1.gid, file1.size, file1.path, directory.inode, file1.metadata_hash, file1.content_hash),
			(run_id, file2.inode, file2.mode, file2.uid, file2.gid, file2.size, file2.path, directory.inode, file2.metadata_hash, file2.content_hash),
		]

		self.assertEqual(result, expected)

	def test_import_db(self):
		"""
		[import_db]
		"""
		run_id = "test_a"

		path = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir")

		collector_a = FSCollector.LinFileSystemCollector()
		collector_b = FSCollector.LinFileSystemCollector()

		# hard code values so we have control over values that are tested
		test_file1 = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir/test_file1.txt")
		metadata = os.lstat(test_file1)
		file1 = FSCollector.File(test_file1, metadata, 13, tools.get_file_hash(test_file1))
		file1.inode = 968625
		
		test_file2 = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir/test_file2.txt")
		metadata = os.lstat(test_file2)
		file2 = FSCollector.File(test_file2, metadata, 13, tools.get_file_hash(test_file2))
		file2.inode = 968595
		
		test_directory = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir")
		metadata = os.lstat(test_directory)
		directory = FSCollector.Directory(test_directory, metadata)
		directory.append_all([file1, file2])
		directory.inode = 968624

		collector_a.raw_result = [directory]


		conn = sql.connect(":memory:")
		cursor = conn.cursor()

		collector_a._export_sql(cursor, run_id)
		conn.commit()

		query = f"""SELECT * FROM files"""
		request = cursor.execute(query)
		result = request.fetchall()


		collector_b.import_db(cursor, run_id)


		conn.close()


		self.assertEqual(collector_a, collector_b)

	def test_import_diff_from_report_db(self):
		"""
		[import_diff_from_report_db]
		"""
		run_id_a = "test_a"
		run_id_b = "test_b"
		report_id = "test"

		collector_a = FSCollector.LinFileSystemCollector()
		collector_b = FSCollector.LinFileSystemCollector()
		collector_b.raw_result = [self.directory]


		# hard code values so we have control over values that are tested
		test_file1 = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir/test_file1.txt")
		metadata = os.lstat(test_file1)
		file1 = FSCollector.File(test_file1, metadata, 13, tools.get_file_hash(test_file1))
		file1.inode = 968625
		
		test_file2 = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir/test_file2.txt")
		metadata = os.lstat(test_file2)
		file2 = FSCollector.File(test_file2, metadata, 13, tools.get_file_hash(test_file2))
		file2.inode = 968595
		
		test_directory = os.path.join(os.path.dirname(__file__), "test_FileSystemCollector_dir")
		metadata = os.lstat(test_directory)
		directory = FSCollector.Directory(test_directory, metadata)
		directory.append_all([file1, file2])
		directory.inode = 968624

		collector_a.raw_result = [directory]

		expected = report.DiffReport(run_id_a, run_id_b)
		expected.diff_elemnts = {
			'File System Collector': {
				'File': [
					report.DiffElement(run_id_a, FSCollector.DiffFile(directory), report.MODIFIED),
					report.DiffElement(run_id_b, FSCollector.DiffFile(self.directory), report.MODIFIED),
					report.DiffElement(run_id_a, FSCollector.DiffFile(file1), report.MODIFIED),
					report.DiffElement(run_id_b, FSCollector.DiffFile(self.file1), report.MODIFIED),
					report.DiffElement(run_id_a, FSCollector.DiffFile(file2), report.MODIFIED),
					report.DiffElement(run_id_b, FSCollector.DiffFile(self.file2), report.MODIFIED),
				]
			}
		}

		result = report.DiffReport(run_id_a, run_id_b)


		conn = sql.connect(":memory:")
		cursor = conn.cursor()

		FSCollector.LinFileSystemCollector.create_report_tables(cursor)
		conn.commit()

		collector_a._export_sql(cursor, run_id_a)
		collector_b._export_sql(cursor, run_id_b)

		query = f"""INSERT INTO reports_files VALUES (?, ?, ?, ?)"""

		cursor.execute(query, (report_id, run_id_a, directory.inode, report.MODIFIED))
		cursor.execute(query, (report_id, run_id_b, self.directory.inode, report.MODIFIED))
		cursor.execute(query, (report_id, run_id_a, file1.inode, report.MODIFIED))
		cursor.execute(query, (report_id, run_id_b, self.file1.inode, report.MODIFIED))
		cursor.execute(query, (report_id, run_id_a, file2.inode, report.MODIFIED))
		cursor.execute(query, (report_id, run_id_b, self.file2.inode, report.MODIFIED))

		FSCollector.LinFileSystemCollector.import_diff_from_report_db(cursor, report_id, [run_id_a, run_id_b], result)

		conn.close()


		self.assertEqual(result, expected)

class TestFile(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		print(f"\nBegining tests on the Linux/Unix File System Collector.")
		test_file1 = "./exposurescout/tests/test_FileSystemCollector_dir/test_file1.txt"
		self.file1 = FSCollector.File(test_file1, None, 13, b"\x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X")
		
		# Hardcode metadata to make it work on every machine (depending on the machine, metadata will be different, so we do not collect them as in the module)
		self.file1.mode = 33188
		self.file1.inode = 968625
		self.file1.uid = 1000
		self.file1.gid = 1000
		self.file1.metadata_hash = b"\xd5oy\xa3f(\xa9\x001\xd9Z\xfbJ\xdf\xd4 "


		test_file2 = "./exposurescout/tests/test_FileSystemCollector_dir/test_file2.txt"
		self.file2 = FSCollector.File(test_file2, None, 13, b"\x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X")

		# Hardcode metadata to make it work on every machine (depending on the machine, metadata will be different, so we do not collect them as in the module)
		self.file2.mode = 33188
		self.file2.inode = 968595
		self.file2.uid = 1000
		self.file2.gid = 1000
		self.file2.metadata_hash = b"\xd9y\x96'\xba\x1b2\xf2\xbf,\xd4\xc9\xa9\xb9GK"


		test_directory = "./exposurescout/tests/test_FileSystemCollector_dir"
		self.directory = FSCollector.Directory(test_directory, None)
		self.directory.append_all([self.file1, self.file2])

		# Hardcode metadata to make it work on every machine (depending on the machine, metadata will be different, so we do not collect them as in the module)
		self.directory.mode = 16877
		self.directory.inode = 968624
		self.directory.uid = 1000
		self.directory.gid = 1000
		self.directory.metadata_hash = b"\xde#\x1e\xf5\x06P\x0e\x92f\x1c/E\xef\x81\xe4`"

	@classmethod
	def setUp(self):
		print(f"testing new method...")

	@classmethod
	def tearDown(self):
		print(f"test has been performed.")

	@classmethod
	def tearDownClass(self):
		print(f"Tests ended on the Linux/Unix File System Collector.\n")

	def test_eq(self):
		"""
		[__eq__]
		"""
		test_file1 = os.path.join(os.path.dirname(__file__), "./test_FileSystemCollector_dir/test_file1.txt")
		metadata = os.lstat(test_file1)
		file = FSCollector.File(test_file1, metadata, 13, tools.get_file_hash(test_file1))

		test_file2 = os.path.join(os.path.dirname(__file__), "./test_FileSystemCollector_dir/test_file2.txt")
		metadata = os.lstat(test_file2)
		file2 = FSCollector.File(test_file2, metadata, 13, tools.get_file_hash(test_file2))

		self.assertNotEqual(file, file2)

		test_directory = os.path.dirname(__file__)
		metadata = os.lstat(test_directory)
		directory = FSCollector.Directory(test_directory, metadata)

		self.assertNotEqual(file, directory)

	def test_to_bytes(self):
		"""
		[to_bytes] with files and directories.
		"""
		expected = b"\x20\x41./exposurescout/tests/test_FileSystemCollector_dir/test_file1.txt@\x81\xa4N\xc7\xb1#\xe8#\xe8\r\xd5oy\xa3f(\xa9\x001\xd9Z\xfbJ\xdf\xd4 \x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X"
		result = self.file1.to_bytes()

		self.assertEqual(expected, result)

		expected = b"\x20\x32./exposurescout/tests/test_FileSystemCollector_dir"
		expected += b"@A\xedN\xc7\xb0#\xe8#\xe8\x1a\xde#\x1e\xf5\x06P\x0e\x92f\x1c/E\xef\x81\xe4`\x02"

		expected += b"\x0etest_file1.txt@\x81\xa4N\xc7\xb1#\xe8#\xe8\r\xd5oy\xa3f(\xa9\x001\xd9Z\xfbJ\xdf\xd4 \x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X"
		expected += b"\x0etest_file2.txt@\x81\xa4N\xc7\x93#\xe8#\xe8\r\xd9y\x96'\xba\x1b2\xf2\xbf,\xd4\xc9\xa9\xb9GK\x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X"

		result = self.directory.to_bytes()

		self.assertEqual(expected, result)

	def test_from_bytes(self):
		"""
		[from_bytes] with files and directories.
		"""
		data = b"\x20\x41./exposurescout/tests/test_FileSystemCollector_dir/test_file1.txt@\x81\xa4N\xc7\xb1#\xe8#\xe8\r\xd5oy\xa3f(\xa9\x001\xd9Z\xfbJ\xdf\xd4 \x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X"

		result = FSCollector.File.from_bytes(data)

		expected = (self.file1, None)

		self.assertEqual(expected, result)

		data = b"\x20\x32./exposurescout/tests/test_FileSystemCollector_dir"
		data += b"@A\xedN\xc7\xb0#\xe8#\xe8\x1a\xde#\x1e\xf5\x06P\x0e\x92f\x1c/E\xef\x81\xe4`\x02"
		data += b"\x0etest_file1.txt@\x81\xa4N\xc7\xb1#\xe8#\xe8\r\xd5oy\xa3f(\xa9\x001\xd9Z\xfbJ\xdf\xd4 \x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X"
		data += b"\x0etest_file2.txt@\x81\xa4N\xc7\x93#\xe8#\xe8\r\xd9y\x96'\xba\x1b2\xf2\xbf,\xd4\xc9\xa9\xb9GK\x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X"


		result = FSCollector.File.from_bytes(data)

		expected = (self.directory, None)

		self.assertEqual(expected, result)

	def test_has(self):
		"""
		[has]
		"""
		result = self.directory.has(self.file1)

		self.assertTrue(result)

	def test_contains(self):
		"""
		[contains]
		"""
		result = self.directory.contains([self.file1, self.file2])

		self.assertTrue(result)

	def test_get_filename(self):
		"""
		[get_filename]
		"""
		result = self.file1.get_filename()
		expected = "test_file1.txt"

		self.assertEqual(result, expected)

		result = self.directory.get_filename()
		expected = "test_FileSystemCollector_dir"

		self.assertEqual(result, expected)

	def test_contains_filename(self):
		"""
		[contains_filename]
		"""
		result = self.directory.contains_filename("test_file1.txt")

		self.assertTrue(result)

		result = self.directory.contains_filename("test")

		self.assertFalse(result)

	def test_contains_inode(self):
		"""
		[contains_inode]
		"""
		result = self.directory.contains_inode(self.file1.inode)

		self.assertTrue(result)

		result = self.directory.contains_inode(2)

		self.assertFalse(result)

	def test_is_parent_of(self):
		"""
		[is_parent_of]
		"""
		result = self.directory.is_parent_of(self.file1)

		self.assertTrue(result)

	def test_make_diff(self):
		"""
		[make_diff]
		"""
		run_id_a = "test_a"
		run_id_b = "test_b"

		test_file1 = "./exposurescout/tests/test_FileSystemCollector_dir/test_file1.txt"
		file1 = FSCollector.File(test_file1, None, 13, b"\x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X")
		
		# Hardcode metadata to make it work on every machine (depending on the machine, metadata will be different, so we do not collect them as in the module)
		file1.mode = 33188
		file1.inode = 968625
		file1.uid = 1000
		file1.gid = 1000
		file1.metadata_hash = b"\xd5oy\xa3f(\xa9\x001\xd9Z\xfbJ\xdf\xd4 "


		test_file2 = "./exposurescout/tests/test_FileSystemCollector_dir/test_file2.txt"
		file2 = FSCollector.File(test_file2, None, 13, b"\x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X")

		# Hardcode metadata to make it work on every machine (depending on the machine, metadata will be different, so we do not collect them as in the module)
		file2.mode = 33188
		file2.inode = 968595
		file2.uid = 1000
		file2.gid = 1000
		file2.metadata_hash = b"\xd9y\x96'\xba\x1b2\xf2\xbf,\xd4\xc9\xa9\xb9GK"


		test_directory = "./exposurescout/tests/test_FileSystemCollector_dir"
		directory = FSCollector.Directory(test_directory, None)
		directory.append_all([file1, file2])

		# Hardcode metadata to make it work on every machine (depending on the machine, metadata will be different, so we do not collect them as in the module)
		directory.mode = 16877
		directory.inode = 968624
		directory.uid = 1000
		directory.gid = 1000
		directory.size = 4096
		directory.metadata_hash = b"\xde#\x1e\xf5\x06P\x0e\x92f\x1c/E\xef\x81\xe4`"

		expected = report.DiffReport(run_id_a, run_id_b)
		expected.add_no_diff_collector(FSCollector.LinFileSystemCollector.name)

		result = report.DiffReport(run_id_a, run_id_b)
		result.add_no_diff_collector(FSCollector.LinFileSystemCollector.name)
		FSCollector.File.make_diff(FSCollector.LinFileSystemCollector, run_id_a, run_id_b, self.directory, directory, result)

		self.assertEqual(result, expected)

		# artificially create a deleted file
		directory.content = [file1]

		expected = report.DiffReport(run_id_a, run_id_b)
		expected.diff_elemnts = {
			FSCollector.LinFileSystemCollector.name: {
				FSCollector.File.element_name : [
					report.DiffElement(run_id_a, FSCollector.DiffFile(self.file2), report.DELETED)
				]
			}
		}

		result = report.DiffReport(run_id_a, run_id_b)
		FSCollector.File.make_diff(FSCollector.LinFileSystemCollector, run_id_a, run_id_b, self.directory, directory, result)

		self.assertEqual(result, expected)

		# artificially create a created file
		directory.content = [file1]

		expected = report.DiffReport(run_id_a, run_id_b)
		expected.diff_elemnts = {
			FSCollector.LinFileSystemCollector.name: {
				FSCollector.File.element_name : [
					report.DiffElement(run_id_b, FSCollector.DiffFile(self.file2), report.CREATED)
				]
			}
		}

		result = report.DiffReport(run_id_a, run_id_b)
		FSCollector.File.make_diff(FSCollector.LinFileSystemCollector, run_id_a, run_id_b, directory, self.directory, result)

		self.assertEqual(result, expected)


class TestDiffFile(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		print(f"\nBegining tests on the Linux/Unix File System Collector.")
		test_file1 = "./exposurescout/tests/test_FileSystemCollector_dir/test_file1.txt"
		file1 = FSCollector.File(test_file1, None, 13, b"\x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X")
		
		# Hardcode metadata to make it work on every machine (depending on the machine, metadata will be different, so we do not collect them as in the module)
		file1.mode = 33188
		file1.inode = 968625
		file1.uid = 1000
		file1.gid = 1000
		file1.metadata_hash = b"\xd5oy\xa3f(\xa9\x001\xd9Z\xfbJ\xdf\xd4 "

		self.file1 = FSCollector.DiffFile(file1)


		test_file2 = "./exposurescout/tests/test_FileSystemCollector_dir/test_file2.txt"
		file2 = FSCollector.File(test_file2, None, 13, b"\x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X")

		# Hardcode metadata to make it work on every machine (depending on the machine, metadata will be different, so we do not collect them as in the module)
		file2.mode = 33188
		file2.inode = 968595
		file2.uid = 1000
		file2.gid = 1000
		file2.metadata_hash = b"\xd9y\x96'\xba\x1b2\xf2\xbf,\xd4\xc9\xa9\xb9GK"

		self.file2 = FSCollector.DiffFile(file2)


		test_directory = "./exposurescout/tests/test_FileSystemCollector_dir"
		directory = FSCollector.Directory(test_directory, None)
		directory.append_all([file1, file2])

		# Hardcode metadata to make it work on every machine (depending on the machine, metadata will be different, so we do not collect them as in the module)
		directory.mode = 16877
		directory.inode = 968624
		directory.uid = 1000
		directory.gid = 1000
		directory.size = 4096
		directory.metadata_hash = b"\xde#\x1e\xf5\x06P\x0e\x92f\x1c/E\xef\x81\xe4`"

		self.directory = FSCollector.DiffFile(directory)

	@classmethod
	def setUp(self):
		print(f"testing new method...")

	@classmethod
	def tearDown(self):
		print(f"test has been performed.")

	@classmethod
	def tearDownClass(self):
		print(f"Tests ended on the Linux/Unix File System Collector.\n")

	def test_to_bytes(self):
		"""
		[to_bytes] with files and directories.
		"""
		expected = b"\x20\x41./exposurescout/tests/test_FileSystemCollector_dir/test_file1.txt@\x81\xa4N\xc7\xb1#\xe8#\xe8\r\xd5oy\xa3f(\xa9\x001\xd9Z\xfbJ\xdf\xd4 \x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X"
		result = self.file1.to_bytes()

		self.assertEqual(expected, result)

		expected = b"\x20\x32./exposurescout/tests/test_FileSystemCollector_dir"
		expected += b"@A\xedN\xc7\xb0#\xe8#\xe80\x00\xde#\x1e\xf5\x06P\x0e\x92f\x1c/E\xef\x81\xe4`"

		#expected += b"\x0etest_file1.txt@\x81\xa4N\xc7\xb1#\xe8#\xe8\r\xd5oy\xa3f(\xa9\x001\xd9Z\xfbJ\xdf\xd4 \x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X"
		#expected += b"\x0etest_file2.txt@\x81\xa4N\xc7\x93#\xe8#\xe8\r\xd9y\x96'\xba\x1b2\xf2\xbf,\xd4\xc9\xa9\xb9GK\x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X"

		result = self.directory.to_bytes()

		self.assertEqual(expected, result)

	def test_from_bytes(self):
		"""
		[from_bytes] with files and directories.
		"""
		data = b"\x20\x41./exposurescout/tests/test_FileSystemCollector_dir/test_file1.txt@\x81\xa4N\xc7\xb1#\xe8#\xe8\r\xd5oy\xa3f(\xa9\x001\xd9Z\xfbJ\xdf\xd4 \x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X"

		result = FSCollector.DiffFile.from_bytes(data)

		expected = (self.file1, None)

		self.assertEqual(expected, result)

		data = b"\x20\x32./exposurescout/tests/test_FileSystemCollector_dir"
		data += b"@A\xedN\xc7\xb0#\xe8#\xe80\x00\xde#\x1e\xf5\x06P\x0e\x92f\x1c/E\xef\x81\xe4`"
		#data += b"\x0etest_file1.txt@\x81\xa4N\xc7\xb1#\xe8#\xe8\r\xd5oy\xa3f(\xa9\x001\xd9Z\xfbJ\xdf\xd4 \x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X"
		#data += b"\x0etest_file2.txt@\x81\xa4N\xc7\x93#\xe8#\xe8\r\xd9y\x96'\xba\x1b2\xf2\xbf,\xd4\xc9\xa9\xb9GK\x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X"


		result = FSCollector.DiffFile.from_bytes(data)

		expected = (self.directory, None)

		self.assertEqual(expected, result)