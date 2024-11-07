#!/usr/bin/python3
#coding:utf-8

"""
Implementation of the File System collector to gather files on the machine. This collector inherits from the abstract Collector class.
It also contains the data structures used for the different collectibles which inherit from the abstract Collectible class.

Authors:
Nathan Amorison

Version:
0.1.3
"""


from .Collector import ACollector, ACollectible
from ..core.tools import get_file_hash, xor_list, ResultThread
from ..core.octets import VarInt
from ..core.report import DiffElement, AlreadyExistsException, CREATED, DELETED, MODIFIED, UNKNOWN

import subprocess
import threading
import sqlite3 as sql
import os
import stat
from hashlib import md5


class DiffFile(ACollectible):
	"""
	Datastructure used to store files in reports.

	Arguments:
		file (File): file data structure to convert.

	Attributes:
		element_name (str): name used to identify this collectible.

		path (str): path to the file.
		mode (int): matadata.st_mode.
		inode (int): metadata.st_ino.
		uid (int): metadata.st_uid.
		gid (int): metadata.st_gid.
		size (int): file size.
		metadata_hash (bytes): hash of the metadata.
		content_hash (bytes): hash of the file's content.
	"""

	element_name = "File" # same as the one of File

	def __init__(self, file):
		super(DiffFile, self).__init__()

		self.path = file.path
		self.mode = file.mode
		self.inode = file.inode
		self.uid = file.uid
		self.gid = file.gid
		self.size = file.size
		self.metadata_hash = file.metadata_hash
		self.content_hash = file.content_hash

	def __repr__(self):
		return str(self)

	def __str__(self):
		return f"""<{self.element_name}: path = {self.path}>"""

	def __eq__(self, o):
		if type(o) != DiffFile:
			return False

		if self.path == o.path and self.mode == o.mode and self.inode == o.inode and self.uid == o.uid and self.gid == o.gid and self.size == o.size and self.metadata_hash == o.metadata_hash and self.content_hash == o.content_hash:
			return True

		return False

	def to_bytes(self):
		"""
		Converts this DiffFile datastructure to a byte string used to store it.

		Returns:
			A bytes stream.
		"""
		encoded = b""

		name_len = len(self.path)
		encoded += VarInt.to_bytes(name_len)
		encoded += self.path.encode()
		encoded += VarInt.to_bytes(self.mode)
		encoded += VarInt.to_bytes(self.inode)
		encoded += VarInt.to_bytes(self.uid)
		encoded += VarInt.to_bytes(self.gid)
		encoded += VarInt.to_bytes(self.size)
		encoded += self.metadata_hash

		if stat.S_ISREG(self.mode):
			encoded += self.content_hash
		# else: pass # no need to encode the entire sub-tree

		return encoded

	def from_bytes(data):
		"""
		Convert bytes to a DiffFile datastructure.

		Arguments:
			data (bytes): a bytes stream begining with the encoded data of a DiffFile datastructure.

		Returns:
			A tupple containing: 1. the File data structure recovered from the bytes stream; 2. the rest of the unread bytes that are not part of this group data structure.
		"""

		# first bytes represents the length of the path encoded then the path
		i = 0
		path_len_size = VarInt.get_len(data[0:1])
		path_len = VarInt.from_bytes(data[0:path_len_size])
		i += path_len_size
		path = data[i:i+path_len].decode()
		i += path_len

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
			file = Directory(path, None)

		elif stat.S_ISREG(mode):
			content_hash = data[i:i+16]
			i += 16

			file = File(path, None, 0, content_hash)

		file.mode = mode
		file.inode = inode
		file.uid = uid
		file.gid = gid
		file.size = size
		file.metadata_hash = metadata_hash

		rest = data[i:]

		if rest == b"":
			rest = None

		return (DiffFile(file), rest)

	def export_report_db(self, report_id, run_id, status, db_cursor):
		"""
		Export a DiffFile data structure that is part of a diff report into the specified database.

		Arguments:
			report_id (str): identifer of the report the element is linked to.
			run_id (str): identifier of the snapshot run the element comes from.
			status (int): value of the element's status in the diff report (created, deleted, modified, ...).
			db_cursor (Cursor): sqlite3 cursor that points to the database.
		"""
		query = f"""INSERT INTO report_files VALUES (?, ?, ?, ?)"""
		db_cursor.execute(query, (report_id, run_id, self.inode, status))


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
		size (int): file size.
		metadata_hash (bytes): hash of the metadata.
		content_hash (bytes): hash of the file's content.
	"""

	element_name = "File"

	def __init__(self, path, metadata, size, content_hash):
		super(File, self).__init__()
		self.path = path

		self.size = size

		if metadata:
			self.mode = metadata.st_mode
			self.inode = metadata.st_ino
			self.uid = metadata.st_uid
			self.gid = metadata.st_gid

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

	def get_filename(self):
		"""
		Get the name of the file.

		Returns:
			The name of the file.
		"""
		i = 0
		while True:
			i -= 1
			name = os.path.split(self.path)[i]
			if name != '':
				return name

	def get_metadata(self):
		"""
		Get the metadata values (except size).

		Returns:
			A tupples containing the file's mode, inode, uid and gid.
		"""
		# size must not be referenced since its checked by the content hash for a file and via content list for directories
		return (self.mode, self.inode, self.uid, self.gid)

	def is_dir(self):
		"""
		Check if the file is a directory.

		Returns:
			True if the file is a directory, False otherwize.
		"""
		return stat.S_ISDIR(self.mode)

	def is_file(self):
		"""
		Check if the file is a regular file.

		Returns:
			True if the file is a regular file, False otherwize.
		"""
		return stat.S_ISREG(self.mode)

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

			file = File(path, None, 0, content_hash)

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
		Export a File data structure into the specified database for a report.
		Note: This data structure is not directly exported but it is first converted to a DiffFile

		Arguments:
			report_id (str): identifer of the report the element is linked to.
			run_id (str): identifier of the snapshot run the element comes from.
			status (int): value of the element's status in the diff report (created, deleted, modified, ...).
			db_cursor (Cursor): sqlite3 cursor that points to the database.
		"""
		elmnt = DiffFile(self)
		elmnt.export_report_db(report_id, run_id, status, db_cursor)

	def make_diff(collector, run_id_a, run_id_b, a, b, report):
		"""
		Run a deep recursive diff.

		Arguments:
			collector (ACollector): the reference to the File System collector class definition.
			run_id_a (str): run_id of the first collector.
			run_id_b (str): run_id of the second collector.
			a (File): the first file or directory (optional).
			b (File): the second file or directory (optional).
			report (DiffReport): the report where to add the differences.

		Raises:
			ValueError: No file or directory provided.
			ValueError: Two files or directories provided but their inode do not match.
		"""
		# Every File or Directory object must be converted to a DiffFile object prior to be added in the report.

		if a and not b:
			element = DiffElement(run_id_a, DiffFile(a), DELETED)
			report.add_diff_element(element, collector.name)

			if stat.S_ISDIR(a.mode):
				# the file is a directory so we need to find all its content
				for file in a.get_content():
					Directory.make_diff(collector, run_id_a, run_id_b, file, None, report)


		elif b and not a:
			element = DiffElement(run_id_b, DiffFile(b), CREATED)
			report.add_diff_element(element, collector.name)

			if stat.S_ISDIR(b.mode):
				# the file is a directory so we need to find all its content
				for file in b.get_content():
					Directory.make_diff(collector, run_id_a, run_id_b, None, file, report)

		elif a and b:
			if a.inode != b.inode:
				raise ValueError(f"Impossible to compare two files or directories which inode do not match. {a.inode} != {b.inode}.")

			if stat.S_ISDIR(a.mode) and stat.S_ISDIR(b.mode):
				# both a and b are directories
				unique_files_a, unique_files_b = xor_list(a.get_content(), b.get_content())

				# search for the changes in the files both directories have
				for a_file in unique_files_a:
					new_file = True
					for b_file in unique_files_b:
						if a_file.inode == b_file.inode:
							# We found two files that share the same inode, so they are the same file. It must have been modified
							if stat.S_ISDIR(a_file.mode) and stat.S_ISDIR(a_file.mode):
								# the files are directories
								if a_file.get_metadata() == b_file.get_metadata() and a_file.get_filename() == b_file.get_filename():
									# it changed because its content changed, but not because the directory itself has been modified
									# we need to find what did change here
									Directory.make_diff(collector, run_id_a, run_id_b, a_file, b_file, report)

								elif a_file.get_content() == b_file.get_content():
									# name or data in metadata changed but not the content, we only need to record this change
									element_a = DiffElement(run_id_a, DiffFile(a_file), MODIFIED)
									element_b = DiffElement(run_id_b, DiffFile(b_file), MODIFIED)
									report.add_diff_element(element_a, collector.name)
									report.add_diff_element(element_b, collector.name)

								else:
									# name changed and content as well. we need to record both
									element_a = DiffElement(run_id_a, DiffFile(a_file), MODIFIED)
									element_b = DiffElement(run_id_b, DiffFile(b_file), MODIFIED)
									report.add_diff_element(element_a, collector.name)
									report.add_diff_element(element_b, collector.name)
									Directory.make_diff(collector, run_id_a, run_id_b, a_file, b_file, report)

							else:
								# file is a regular file or link file
								element_a = DiffElement(run_id_a, DiffFile(a_file), MODIFIED)
								element_b = DiffElement(run_id_b, DiffFile(b_file), MODIFIED)
								report.add_diff_element(element_a, collector.name)
								report.add_diff_element(element_b, collector.name)

							new_file = False
							unique_files_b.remove(b_file)
							# we removed from uniques_files_b all the files that are not really unique and therefore have been already processed
							# unique_files_b shall therefore contain only the files that are strictly unique to the b collector

					if new_file:
						# elements that were in a but not in b anymore were deleted between the two snapshots
						element_a = DiffElement(run_id_a, DiffFile(a_file), DELETED)
						report.add_diff_element(element_a, collector.name)

				for b_file in unique_files_b:
					if stat.S_ISDIR(b_file.mode):
						# the file is a directory so we need to find all the new files
						Directory.make_diff(collector, run_id_a, run_id_b, None, b_file, report)
					else:
						# just add the new file
						element_b = DiffElement(run_id_b, DiffFile(b_file), CREATED)
						report.add_diff_element(element_b, collector.name)

			elif stat.S_ISDIR(a.mode):
				# b is not a directory
				element_a = DiffElement(run_id_a, DiffFile(a), MODIFIED)
				element_b = DiffElement(run_id_b, DiffFile(b), MODIFIED)
				report.add_diff_element(element_a, collector.name)
				report.add_diff_element(element_b, collector.name)

				File.make_diff(collector, run_id_a, run_id_b, a, None, report)

			elif stat.S_ISDIR(b.mode):
				# a is not a directory
				element_a = DiffElement(run_id_a, DiffFile(a), MODIFIED)
				element_b = DiffElement(run_id_b, DiffFile(b), MODIFIED)
				report.add_diff_element(element_a, collector.name)
				report.add_diff_element(element_b, collector.name)

				File.make_diff(collector, run_id_a, run_id_b, None, b, report)

			else:
				# both a and b are files
				element_a = DiffElement(run_id_a, DiffFile(a), MODIFIED)
				element_b = DiffElement(run_id_b, DiffFile(b), MODIFIED)
				report.add_diff_element(element_a, collector.name)
				report.add_diff_element(element_b, collector.name)

		else:
			raise ValueError('At least one file or directory should be provided to be able to make the diff between the two.')

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
		super(Directory, self).__init__(path, metadata, 0, None)
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
		self.size += file.size

		# recompute everything
		hash_val = md5()
		hash_val.update(self.path.encode())
		hash_val.update(f"{self.mode}".encode())
		hash_val.update(f"{self.inode}".encode())
		hash_val.update(f"{self.uid}".encode())
		hash_val.update(f"{self.gid}".encode())
		hash_val.update(f"{self.size}".encode())
		self.metadata_hash = hash_val.digest()

	def append_all(self, file_list):
		"""
		Append a list of files and directories to this directory.

		Arguments:
			file_list (list[File]): list of File or Directory object to add in this directory.
		"""
		for file in file_list:
			self.append(file)

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

	def contains_filename(self, filename):
		"""
		Verify if the directory contains a file with the given name.

		Arguments:
			filename (str): name to check.

		Returns:
			True if the directory contains a file or a directory with the given name, False otherwise.
		"""
		for f in self.content:
			if f.get_filename() == filename:
				return True

		return False

	def contains_inode(self, inode):
		"""
		verify if the directory contains a file with the given inode.

		Arguments:
			inode (int): inode to check.

		Returns:
			True if the directory contains a file or a directory with the given inode, False otherwise.
		"""
		for f in self.content:
			if f.inode == inode:
				return True

		return False

	def is_parent_of(self, file):
		"""
		Verify that this directory is a parent or an ancestor of a given file.

		Returns:
			True if file is in the sub-tree
		"""
		if os.path.normpath(file.path).startswith(os.path.normpath(self.path)):
			return True

		return False


class LinFileSystemCollector(ACollector):
	"""
	Linux/Unix FileSystem collector.
	Inherits from ACollector.

	Attributes:
		Inherits from ACollector
	"""

	snapshot_elemnt_id = b"\x01"
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

		if self.raw_result and o.raw_result:
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
			rule (str): path to the directory to walk.
		"""
		self.rules.append(rule)

	def set_rules(self, rules):
		"""
		Add a list of directories to walk.

		Arguments:
			rules (list[str]): list of path to the directories to walk.
		"""
		self.rules = rules

	def get_content(self):
		"""
		Get the list of File System collector root files and directories it contains.

		Returns:
			A list of files or directories.
		"""
		return self.raw_result

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
		Import method to recover data of a previous run stored in DB. Those data can then be previewed.
		Note: must already been connected to the database.

		Arguments:
			db_cursor (Cursor): pointer to the database.
			run_id (str): id used to store the collected data in the db of a specific run.
		"""
		def macro(db_cursor, run_id, parent):
			query = f"""SELECT inode, mode, uid, gid, size, path, metadata_hash, content_hash FROM files WHERE run_id=? AND parent IS ?"""
			request = db_cursor.execute(query, (run_id, parent))
			files = request.fetchall()

			content = []

			for inode, mode, uid, gid, size, path, metadata_hash, content_hash in files:
				if stat.S_ISDIR(mode):
					file = Directory(path, None)
					result = macro(db_cursor, run_id, inode)
					file.content = result
				else:
					file = File(path, None, size, content_hash)

				file.inode = inode
				file.mode = mode
				file.uid = uid
				file.gid = gid
				file.size = size
				file.metadata_hash = metadata_hash

				content.append(file)

			return content

		self.raw_result = macro(db_cursor, run_id, None)

	def _export_sql(self, db_cursor, run_id):
		"""
		Private method to export the result in a db after running the module.
		"""
		# creates the tables if they do not already exist
		db_cursor.execute("""CREATE TABLE IF NOT EXISTS snapshots(
			run_id TEXT,
			collector_type BLOB,
			PRIMARY KEY(run_id, collector_type)
			)""") # collector type is prefered as "collector_type" value compared to collector name because encoding is lighter with a BLOB of bytes than with a TEXT value
		db_cursor.execute("""CREATE TABLE IF NOT EXISTS files(
			run_id TEXT,
			inode INTEGER,
			mode INTEGER,
			uid INTEGER,
			gid INTEGER,
			size INTEGER,
			path TEXT,
			parent INTEGER,
			metadata_hash BLOB,
			content_hash BLOB,
			PRIMARY KEY(run_id, inode),
			FOREIGN KEY(run_id, parent) REFERENCES files(run_id, inode)
			)""")

		# Add the collector type in the list of collectors that were run during the snapshot
		query = f"""INSERT INTO snapshots VALUES (?, ?)"""
		db_cursor.execute(query, (run_id, self.snapshot_elemnt_id))

		# Add the files
		query = f"""INSERT INTO files VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

		for file in self.raw_result:
			directories = []
			if file.is_dir():
				directories.append(file)

				db_cursor.execute(query, (run_id, file.inode, file.mode, file.uid, file.gid, file.size, file.path, None, file.metadata_hash, None))

				# go deep in the tree
				while len(directories) > 0:
					directory = directories.pop(0)
					for f in directory.get_content():
						if f.is_dir():
							directories.append(f)
							db_cursor.execute(query, (run_id, f.inode, f.mode, f.uid, f.gid, f.size, f.path, directory.inode, f.metadata_hash, None))
						else:
							db_cursor.execute(query, (run_id, f.inode, f.mode, f.uid, f.gid, f.size, f.path, directory.inode, f.metadata_hash, f.content_hash))
			else:
				db_cursor.execute(query, (run_id, file.inode, file.mode, file.uid, file.gid, file.size, file.path, None, file.metadata_hash, file.content_hash))

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
		Walk through a given path to collect all the data it contains. If the path points to a directory, it therefore also collects all the directories and files it contains.

		Arguments:
			path (str): path to walk through.

		Returns:
			The File or Directory object collected that represent the one pointed by the given path on the machine File System.
		"""
		# get the metadata
		metadata = os.lstat(path)
		
		if os.path.isfile(path):
			# create the File data structure
			content_hash = get_file_hash(path)
			size = os.path.getsize(path)
			file = File(path, metadata, size, content_hash)

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
		if a:
			a_content = a.get_content()

		if b:
			b_content = b.get_content()

		if a and not b:
			for file in a_content:
				File.make_diff(LinFileSystemCollector, run_id_a, run_id_b, file, None, report)

		elif b and not a:
			for file in b_content:
				File.make_diff(LinFileSystemCollector, run_id_a, run_id_b, None, file, report)

		elif a and b:
			has_changed = False

			# check if the main files and directories the collector collected do not strictly match together
			unique_files_a, unique_files_b = xor_list(a_content, b_content)

			# search for the changes
			for a_file in unique_files_a:
				new_file = True
				for b_file in unique_files_b:
					if a_file.inode == b_file.inode:
						new_file = False
						# We found two files that share the same inode, so they are the same file. It must have been modified
						if stat.S_ISDIR(a_file.mode) and stat.S_ISDIR(b_file.mode):
							# the files are directories
							if a_file.get_metadata() == b_file.get_metadata() and a_file.get_filename() == b_file.get_filename():
								# it changed because its content changed, but not because the directory itself has been modified
								# we need to find what did change here
								File.make_diff(LinFileSystemCollector, run_id_a, run_id_b, a_file, b_file, report)

							elif a_file.get_content() == b_file.get_content():
								# name or another data part of metadata changed but not the content, we only need to record this change
								element_a = DiffElement(run_id_a, DiffFile(a_file), MODIFIED)
								element_b = DiffElement(run_id_b, DiffFile(b_file), MODIFIED)
								report.add_diff_element(element_a, LinFileSystemCollector.name)
								report.add_diff_element(element_b, LinFileSystemCollector.name)

							else:
								# name changed and content as well. we need to record both
								element_a = DiffElement(run_id_a, DiffFile(a_file), MODIFIED)
								element_b = DiffElement(run_id_b, DiffFile(b_file), MODIFIED)
								report.add_diff_element(element_a, LinFileSystemCollector.name)
								report.add_diff_element(element_b, LinFileSystemCollector.name)
								File.make_diff(LinFileSystemCollector, run_id_a, run_id_b, a_file, b_file, report)

						else:
							# file is a regular file or link file
							element_a = DiffElement(run_id_a, DiffFile(a_file), MODIFIED)
							element_b = DiffElement(run_id_b, DiffFile(b_file), MODIFIED)
							report.add_diff_element(element_a, LinFileSystemCollector.name)
							report.add_diff_element(element_b, LinFileSystemCollector.name)

						unique_files_b.remove(b_file)
						# we removed from uniques_files_b all the files that are not really unique and therefore have been already processed
						# unique_files_b shall therefore contain only the files that are strictly unique to the b collector

					elif stat.S_ISDIR(a_file.mode) and a_file.is_parent_of(b_file):
						new_file = False
						# find the moment we can start the diff, for all the previous data that a_file contains we don't see with b_file, then mark them as unknown
						found = False
						directory = a_file
						directories = [directory]

						element_a = DiffElement(run_id_a, DiffFile(directory), UNKNOWN)
						report.add_diff_element(element_a, LinFileSystemCollector.name)

						while len(directories) > 0:
							directory = directories.pop(0)
							for file in directory.get_content():
								if file.inode != b_file.inode:
									element_a = DiffElement(run_id_a, DiffFile(file), UNKNOWN)
									report.add_diff_element(element_a, LinFileSystemCollector.name)
									if stat.S_ISDIR(file.mode):
										directories.append(file)
								else:
									found = True
									# we found the elements that are similar
									if stat.S_ISDIR(file.mode) and stat.S_ISDIR(b_file.mode):
										# the files are directories
										if file.get_metadata() == b_file.get_metadata() and file.get_filename() == b_file.get_filename():
											# it changed because its content changed, but not because the directory itself has been modified
											# we need to find what did change here
											File.make_diff(LinFileSystemCollector, run_id_a, run_id_b, file, b_file, report)

										elif file.get_content() == b_file.get_content():
											# name or another data part of metadata changed but not the content, we only need to record this change
											element_a = DiffElement(run_id_a, DiffFile(file), MODIFIED)
											element_b = DiffElement(run_id_b, DiffFile(b_file), MODIFIED)
											report.add_diff_element(element_a, LinFileSystemCollector.name)
											report.add_diff_element(element_b, LinFileSystemCollector.name)

										else:
											# name changed and content as well. we need to record both
											element_a = DiffElement(run_id_a, DiffFile(file), MODIFIED)
											element_b = DiffElement(run_id_b, DiffFile(b_file), MODIFIED)
											report.add_diff_element(element_a, LinFileSystemCollector.name)
											report.add_diff_element(element_b, LinFileSystemCollector.name)
											File.make_diff(LinFileSystemCollector, run_id_a, run_id_b, file, b_file, report)

									else:
										# file is a regular file or link file
										element_a = DiffElement(run_id_a, DiffFile(file), MODIFIED)
										element_b = DiffElement(run_id_b, DiffFile(b_file), MODIFIED)
										report.add_diff_element(element_a, LinFileSystemCollector.name)
										report.add_diff_element(element_b, LinFileSystemCollector.name)

						if found:
							unique_files_b.remove(b_file)
							# we removed from uniques_files_b all the files that are not really unique and therefore have been already processed
							# unique_files_b shall therefore contain only the files that are strictly unique to the b collector

					elif stat.S_ISDIR(b_file.mode) and b_file.is_parent_of(a_file):
						# find the moment we can start the diff, for all the previous data that b_file contains we don't see with a_file, then mark them as unknown
						found = False
						directory = b_file
						directories = [directory]

						element_b = DiffElement(run_id_b, DiffFile(directory), UNKNOWN)
						report.add_diff_element(element_b, LinFileSystemCollector.name)

						while len(directories) > 0:
							directory = directories.pop(0)
							for file in directory.get_content():
								if file.inode != a_file.inode:
									element_b = DiffElement(run_id_b, DiffFile(file), UNKNOWN)
									report.add_diff_element(element_b, LinFileSystemCollector.name)
									if stat.S_ISDIR(file.mode):
										directories.append(file)
								else:
									found = True
									# we found the elements that are similar
									if stat.S_ISDIR(file.mode) and stat.S_ISDIR(a_file.mode):
										# the files are directories
										if file.get_metadata() == a_file.get_metadata() and file.get_filename() == a_file.get_filename():
											# it changed because its content changed, but not because the directory itself has been modified
											# we need to find what did change here
											File.make_diff(LinFileSystemCollector, run_id_a, run_id_b, a_file, file, report)

										elif file.get_content() == a_file.get_content():
											# name or another data part of metadata changed but not the content, we only need to record this change
											element_a = DiffElement(run_id_a, DiffFile(a_file), MODIFIED)
											element_b = DiffElement(run_id_b, DiffFile(file), MODIFIED)
											report.add_diff_element(element_a, LinFileSystemCollector.name)
											report.add_diff_element(element_b, LinFileSystemCollector.name)

										else:
											# name changed and content as well. we need to record both
											element_a = DiffElement(run_id_a, DiffFile(a_file), MODIFIED)
											element_b = DiffElement(run_id_b, DiffFile(file), MODIFIED)
											report.add_diff_element(element_a, LinFileSystemCollector.name)
											report.add_diff_element(element_b, LinFileSystemCollector.name)
											File.make_diff(LinFileSystemCollector, run_id_a, run_id_b, a_file, file, report)

									else:
										# file is a regular file or link file
										element_a = DiffElement(run_id_a, DiffFile(a_file), MODIFIED)
										element_b = DiffElement(run_id_b, DiffFile(file), MODIFIED)
										report.add_diff_element(element_a, LinFileSystemCollector.name)
										report.add_diff_element(element_b, LinFileSystemCollector.name)

						if found:
							unique_files_b.remove(b_file)
							# we removed from uniques_files_b all the files that are not really unique and therefore have been already processed
							# unique_files_b shall therefore contain only the files that are strictly unique to the b collector

				if new_file:
					# elements that were in a but not in b anymore were deleted between the two snapshots
					element_a = DiffElement(run_id_a, DiffFile(a_file), DELETED)
					report.add_diff_element(element_a, LinFileSystemCollector.name)

			for b_file in unique_files_b:
				if stat.S_ISDIR(b_file.mode):
					# the file is a directory so we need to find all the new files
					Directory.make_diff(LinFileSystemCollector, run_id_a, run_id_b, None, b_file, report)
				else:
					# just add the new file
					element_b = DiffElement(run_id_b, DiffFile(b_file), CREATED)
					report.add_diff_element(element_b, LinFileSystemCollector.name)

		else:
			raise ValueError('At least one collector should be provided to be able to make the diff between the two.')

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
		rest = data

		file_number_len = VarInt.get_len(rest[0:1])
		file_number = VarInt.from_bytes(rest[0:file_number_len])

		rest = rest[file_number_len:]

		if file_number:
			for i in range(file_number):
				file, rest = DiffElement.from_bytes(rest, run_ids, DiffFile)
				report.add_diff_element(file, LinFileSystemCollector.name)
		else:
			report.add_no_diff_element(LinFileSystemCollector.name, DiffFile.element_name)

		return True

	def import_diff_from_report_db(db_cursor, report_id, run_ids, report):
		"""
		Extract LinFileSystemCollector's diff elements from a database.

		Arguments:
			db_cursor (Cursor): pointer to the database.
			report_id (str): identifier of the report being imported.
			run_ids (list[str]): the ordered list of the snapshot ids from which come the report elements.
			report (DiffReport): datastructure in which to store the recovered data.
		"""
		for run_id in run_ids:
			# search for every DiffFile associated to this report and run
			query = f"""SELECT inode, status FROM reports_files WHERE report_id=? AND run_id=?"""
			request = db_cursor.execute(query, (report_id, run_id))
			files = request.fetchall()

			print(files)

			if files and files != []:
				for inode, status in files:
					query = f"""SELECT mode, uid, gid, size, path, metadata_hash, content_hash FROM files WHERE run_id=? AND inode=?"""
					request = db_cursor.execute(query, (run_id, inode))
					data = request.fetchall()
					for mode, uid, gid, size, path, metadata_hash, content_hash, *_ in data:
						if stat.S_ISDIR(mode):
							file = Directory(path, None)
							file.size = size
						else:
							file = File(path, None, size, content_hash)

						file.inode = inode
						file.mode = mode
						file.uid = uid
						file.gid = gid
						file.metadata_hash = metadata_hash

						report.add_diff_element(DiffElement(run_id, DiffFile(file), status), LinFileSystemCollector.name)

			else:
				try:
					report.add_no_diff_element(LinFileSystemCollector.name, DiffFile.element_name)
				except AlreadyExistsException as e:
					# we are reading the second run_id and the first one had values to add where the send had none. Just discard the error, it is controlled.
					pass

	def get_report_tree_structure():
		"""
		Get the structure of the Collector used for the report.

		Returns:
			A python dict with an empty list of Directories.
		"""
		return {DiffFile.element_name : []}

	def create_report_tables(db_cursor):
		"""
		Static method used to create the different tables used by this collector for report structure in the specified database.
		Note: modifications are not committed here.

		Arguments:
			db_cursor (Cursor): sqlite3 cursor pointing to the database in which the tables must be created.
		"""
		db_cursor.execute("""CREATE TABLE IF NOT EXISTS reports_files(
			report_id TEXT,
			run_id TEXT,
			inode INTEGER,
			status INTEGER,
			PRIMARY KEY(report_id, run_id, inode),
			FOREIGN KEY(run_id, inode) REFERENCES files
			)""")