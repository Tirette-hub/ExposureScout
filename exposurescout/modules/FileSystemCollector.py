#!/usr/bin/python3
#coding:utf-8

"""
Implementation of the File System collector to gather files on the machine. This collector inherits from the abstract Collector class.
It also contains the data structures used for the different collectibles which inherit from the abstract Collectible class.

Authors:
Nathan Amorison

Version:
0.1.0
"""


from .Collector import ACollector, ACollectible
from ..core.tools import get_file_hash, xor_list, ResultThread
from ..core.octets import VarInt
from ..core.report import DiffElement, AlreadyExistsException, CREATED, DELETED, MODIFIED

import subprocess
import threading
import sqlite3 as sql
import os
import stat
from hashlib import md5


class File(ACollectible):
	"""
	Datastructure used to represent a Linux/Unix File.

	Arguments:
		path (str): path to the file.
		metadata (os.stat_result): matadata of the file.
		content_hash (bytes): hash of the file's content.

	Attributes:
		element_name (str): name used to identify this collectible.

		path (str): path to the file.
		mode (int): matadata.st_mode.
		inode (int): metadata.st_ino.
		uid (int): metadata.st_uid.
		gid (int): metadata.st_gid.
		size (int): metadata.st_size.
		metadata_hash (bytes): hash of the metadata.
		content_hash (bytes): hash of the file's content.
	"""

	element_name = "File"

	def __init__(self, path, metadata, content_hash):
		super(File, self).__init__()
		self.path = path

		if metadata:
			self.mode = metadata.st_mode
			self.inode = metadata.st_ino
			self.uid = metadata.st_uid
			self.gid = metadata.st_gid
			self.size = metadata.st_size

			hash_val = md5()
			hash_val.update(self.path.encode())
			hash_val.update(f"{self.mode}".encode())
			hash_val.update(f"{self.inode}".encode())
			hash_val.update(f"{self.uid}".encode())
			hash_val.update(f"{self.gid}".encode())
			hash_val.update(f"{self.size}".encode())
			self.metadata_hash = hash_val.digest()

		else:
			self.mode = None
			self.inode = None
			self.uid = None
			self.gid = None
			self.size = None

			self.metadata_hash = None

		self.content_hash = content_hash

	def __repr__(self):
		return str(self)

	def __str__(self):
		return f"""<{self.element_name}: path = {self.path}>"""

	def __eq__(self, o):
		if type(o) != File:
			return False

		if self.metadata_hash == o.metadata_hash and self.content_hash == o.content_hash:
			return True

		return False

	def to_bytes(self, *args):
		"""
		Converts this File datastructure to a byte string used to store it.

		Returns:
			A bytes stream.
		"""
		encoded = b""

		known_path = None

		if args:
			known_path, *_ = args

		name = os.path.split(self.path)[-1]

		if known_path and os.path.join(known_path, name) == self.path:
			name_len = len(name)
			encoded += VarInt.to_bytes(name_len)
			encoded += name.encode()
		else:
			name_len = len(self.path)
			encoded += VarInt.to_bytes(name_len)
			encoded += self.path.encode()
		encoded += VarInt.to_bytes(self.mode)
		encoded += VarInt.to_bytes(self.inode)
		encoded += VarInt.to_bytes(self.uid)
		encoded += VarInt.to_bytes(self.gid)
		encoded += VarInt.to_bytes(self.size)
		encoded += self.metadata_hash

		if stat.S_ISDIR(self.mode):
			content_len = len(self.content)
			encoded += VarInt.to_bytes(content_len)
			for f in self.content:
				encoded += f.to_bytes(self.path)
		elif stat.S_ISREG(self.mode):
			encoded += self.content_hash

		return encoded

	def from_bytes(data, *args):
		"""
		Convert bytes to a File datastructure.

		Arguments:
			data (bytes): a bytes stream begining with the encoded data of a File datastructure.

		Returns:
			A tupple containing: 1. the File data structure recovered from the bytes stream; 2. the rest of the unread bytes that are not part of this group data structure.
		"""
		known_path = None
		if args:
			known_path, *_ = args

		# first bytes represents the length of the path encoded then the path
		i = 0
		path_len_size = VarInt.get_len(data[0:1])
		path_len = VarInt.from_bytes(data[0:path_len_size])
		i += path_len_size
		path = data[i:i+path_len].decode()
		i += path_len

		if known_path:
			path = os.path.join(known_path, path)

		# recover metadata: mode, inode, uid, gid and size
		mode_len = VarInt.get_len(data[i:i+1])
		mode = VarInt.from_bytes(data[i:i+mode_len])
		i += mode_len

		inode_len = VarInt.get_len(data[i:i+1])
		inode = VarInt.from_bytes(data[i:i+inode_len])
		i += inode_len

		uid_len = VarInt.get_len(data[i:i+1])
		uid = VarInt.from_bytes(data[i:i+uid_len])
		i += uid_len

		gid_len = VarInt.get_len(data[i:i+1])
		gid = VarInt.from_bytes(data[i:i+gid_len])
		i += gid_len

		size_len = VarInt.get_len(data[i:i+1])
		size = VarInt.from_bytes(data[i:i+size_len])
		i += size_len

		# recover metadata hash
		metadata_hash = data[i:i+16]
		i += 16

		# verify metadata hash is correct
		# hash_val = md5()
		# hash_val.update(path.encode())
		# hash_val.update(f"{mode}".encode())
		# hash_val.update(f"{inode}".encode())
		# hash_val.update(f"{uid}".encode())
		# hash_val.update(f"{gid}".encode())
		# hash_val.update(f"{size}".encode())
		# metadata_hash_verif = hash_val.digest()

		# if metadata_hash != metadata_hash_verif:
		# 	raise ValueError(f"Metadata hash does not match the metadata, data might have been corrupted.")

		# check the type of file beeing gathered and recover their specific data
		if stat.S_ISDIR(mode):
			file_number_len = VarInt.get_len(data[i:i+1])
			file_number = VarInt.from_bytes(data[i:i+file_number_len])
			i += file_number_len

			content = []
			rest = data[i:]
			for file_count in range(file_number):
				new_file, rest = File.from_bytes(rest, path)
				content.append(new_file)

			file = Directory(path, None)
			file.append_all(content)

		elif stat.S_ISREG(mode):
			content_hash = data[i:i+16]
			i += 16

			rest = data[i:]

			file = File(path, None, content_hash)

		file.mode = mode
		file.inode = inode
		file.uid = uid
		file.gid = gid
		file.size = size
		file.metadata_hash = metadata_hash

		if rest == b"":
			rest = None

		return (file, rest)

	def export_report_db(self, report_id, run_id, status, db_cursor):
		"""
		"""
		pass

class Directory(File):
	"""
	Datastructure used to represent a Linux/Unix Directory.
	Since a directory is also a file in Linux/Unix, it fully inherits from the File data structures. However it does not require the content hash since the content are the files themselves.

	Arguments:
		path (str): path to the directory.
		metadata (os.stat_result): matadata of the directory.

	Attributes:
		element_name (str): name used to identify this collectible.

		path (str): path to the directory.
		mode (int): matadata.st_mode.
		inode (int): metadata.st_ino.
		uid (int): metadata.st_uid.
		gid (int): metadata.st_gid.
		size (int): metadata.st_size.
		metadata_hash (bytes): hash of the metadata.
		content_hash (bytes): (set to None here: not used)
		content (File/Directory): list of files and directories it contains.
	"""

	element_name = "Directory"

	def __init__(self, path, metadata):
		super(Directory, self).__init__(path, metadata, None)
		self.content = []

	def __str__(self):
		return f"""<{self.element_name}: path = {self.path}, content = [{",".join(list(str(f) for f in self.content))}]>"""

	def __eq__(self, o):
		if type(o) != Directory:
			return False

		if self.metadata_hash == o.metadata_hash:
			return True

		return False

	def get_content(self):
		"""
		Get the content of the directory.

		Returns:
			A list containing Directories and Files.
		"""
		return self.content

	def append(self, file):
		"""
		Append a file or a directory to this directory.

		Arguments:
			file (File): File or Directory object to add in this directory.
		"""
		self.content.append(file)

	def append_all(self, file_list):
		"""
		Append a list of files and directories to this directory.

		Arguments:
			file_list (list[File]): list of File or Directory object to add in this directory.
		"""
		self.content += file_list

	def has(self, file):
		"""
		Verify if a file or a directory is in this directory.

		Arguments:
			file (File): File or Directory object to check.
		"""
		return file in self.content

	def contains(self, file_list):
		"""
		Verify if a list of file or a directory is contained in this directory.

		Arguments:
			file_list (list[File]): list of File or Directory object to check.
		"""
		result = True

		for file in file_list:
			result = self.has(file)

			if not result:
				return False

		return result


class LinFileSystemCollector(ACollector):
	"""
	Linux/Unix FileSystem collector.
	Inherits from ACollector.

	Attributes:
		Inherits from ACollector
	"""

	snapshot_elemnt_id = "\x01"
	name = "File System Collector"
	description = """
			For Linux/Unix platforms only.
			This module collects the entire File System of this machine.
			"""

	def __init__(self):
		super(LinFileSystemCollector, self).__init__()
		self.rules = []

	def __eq__(self, o):
		if type(o) != LinFileSystemCollector:
			return False

		if self.raw_result:
			if len(self.raw_result) != len(o.raw_result):
				return False
		else:
			return False

		for d in self.raw_result:
			if d not in o.raw_result:
				return False

		return True

	def set_rule(self, rule):
		"""
		Add directory to walk.

		Arguments:
			rules (str): path to the directory to walk.
		"""
		self.rules.append(rule)

	def set_rules(self, rules):
		"""
		Add a list of directories to walk.

		Arguments:
			rules (list[str]): list of path to the directories to walk.
		"""
		self.rules = rules

	def import_bin(self, data):
		"""
		Import method to recover data of a previous run. Those data can then be previewed.

		Arguments:
			data (bytes): raw data with the first bytes representing this collector.

		Returns:
			The rest of raw bytes unrelated to this collector.
		"""
		i = 0
		file_number_len = VarInt.get_len(data[i:i+1])
		file_number = VarInt.from_bytes(data[i:i+file_number_len])
		i += file_number_len

		# recover the files and directory
		rest = data[i:]
		files = []
		for file in range(file_number):
			file, rest = File.from_bytes(rest)
			files.append(file)

		self.raw_result = files

	def import_db(self, db_cursor, run_id):
		"""
		"""
		pass

	def _export_sql(self, db, run_id):
		"""
		Private method to export the result in a db after running the module.
		"""
		pass

	def _format(self):
		"""
		Private method to format raw collected data of a run to exportable data.
		"""
		encoded_data = b""

		# store the number of files/directories collected
		file_number = len(self.raw_result)
		encoded_data += VarInt.to_bytes(file_number)

		# for every file collected, encode it
		for file in self.raw_result:
			encoded_data += file.to_bytes()

		self.result = encoded_data

	def walk_through(self, path):
		"""
		"""
		# get the metadata
		metadata = os.lstat(path)
		
		if os.path.isfile(path):
			# create the File data structure
			content_hash = get_file_hash(path)
			file = File(path, metadata, content_hash)

		else:
			directories = []
			files = []

			# create the Directory data structure
			file = Directory(path, metadata)

			# scan the directory to get what it contains
			with os.scandir(path) as it:
				for entry in it:
					# sort them by directory and file
					if entry.is_dir():
						directories.append(entry)
					elif entry.is_file():
						directories.append(entry)

			# walk through every directory
			directories.sort(key=lambda x:x.name)
			for directory in directories:
				new_path = os.path.join(path, directory.name)
				file.append(self.walk_through(new_path))

			# create every File object
			files.sort(key=lambda x:x.name)
			for new_file in files:
				new_path = os.path.join(path, new_file.name)
				metadata = os.lstat(new_path)
				content_hash = get_file_hash(new_path)
				file.append(File(new_path, metadata, content_hash))

		return file

	def _run(self):
		"""
		Private method collecting the raw data.
		"""
		directories = self.rules
		threads = []

		for d in directories:
			t = ResultThread(target = self.walk_through, args = (d,))
			threads.append(t)

		for t in threads:
			t.start()

		for t in threads:
			t.join()


		self.raw_result = []
		for t in threads:
			self.raw_result.append(t.result)

	def make_diff(run_id_a, run_id_b, a, b, report):
		"""
		Static method used to get the difference between two "Linux/Unix File System" collectors.

		Arguments:
			run_id_a (str): run_id of the first collector.
			run_id_b (str): run_id of the second collector.
			a (LinFileSystemCollector): the first collectors.
			b (LinFileSystemCollector): the second collector.
			report (DiffReport): the report where to add the differences.
		"""
		pass


	def import_diff_from_report(data, run_ids, report):
		"""
		Extract LinFileSystemCollector's diff elements from a report file.

		Arguments:
			data (bytes): a bytes stream representing the elements associated to this collector in the report.
			run_ids (list[str]): the ordered list of the snapshot ids from which come the report elements.
			report (DiffReport): datastructure in which to store the recovered data.

		Returns:
			True if the Diff Elements associated to LinFileSystemCollector data have been successfully imported.
		"""
		pass

	def import_diff_from_report_db(db_cursor, report_id, run_ids, report):
		"""
		Extract LinFileSystemCollector's diff elements from a database.

		Arguments:
			db_cursor (Cursor): pointer to the database.
			report_id (str): identifier of the report being imported.
			run_ids (list[str]): the ordered list of the snapshot ids from which come the report elements.
			report (DiffReport): datastructure in which to store the recovered data.
		"""
		pass

	def get_report_tree_structure():
		"""
		Get the structure of the Collector used for the report.

		Returns:
			A python dict with an empty list of Directories.
		"""
		return {File.element_name : []}

	def create_report_tables(db_cursor):
		"""
		Static method used to create the different tables used by this collector for report structure in the specified database.
		Note: modifications are not committed here.

		Arguments:
			db_cursor (Cursor): sqlite3 cursor pointing to the database in which the tables must be created.
		"""
		pass