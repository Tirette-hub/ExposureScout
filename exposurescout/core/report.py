#!/usr/bin/python3
#coding:utf-8

"""
All about report data structures and objects and tools to export/import them.
Authors:
Nathan Amorison

Version:
0.0.1
"""

from .octets import VarInt

CREATED = 0
DELETED = 1
MODIFIED = 2
UNKNOWN = 3


def parse_snap_header(data):
	"""
	Parse the header of a snapshot binary file.

	Arguments:
		data (bytes): header as bytes to parse.

	Returns:
		A list of tupple containing the type of containers and their position in the file.
	"""
	# get the number of collectors in the header
	collectors_number_len = VarInt.get_len(data[0:1])
	collectors_number = VarInt.from_bytes(data[0:collectors_number_len])
	i = collectors_number_len

	# Get the information about the collectors from the header
	collectors_info = []
	for _ in range(collectors_number):
		collector_type = data[i:i+1]
		i += 1

		offset_len = VarInt.get_len(data[i:i+1])
		offset = VarInt.from_bytes(data[i:i+offset_len])
		i += offset_len

		collectors_info.append((collector_type, offset))

	return collectors_info


def parse_rpt_header(data):
	"""
	Parse the header of a report binary file.

	Arguments:
		data (bytes): header as bytes to parse.

	Returns:
		A tupple containing: 1. an ordered list of the snapshot id's of the compared snapshots in the report; 2. a list of tupple containing the type of containers and their position in the file.
	"""
	n = 0

	# Recover the 2 snapshots id
	id_a_len_size = VarInt.get_len(data[n:n+1])
	id_a_len = VarInt.from_bytes(data[n:n+id_a_len_size])
	n += id_a_len_size

	id_a = data[n:n+id_a_len].decode()
	n += id_a_len

	id_b_len_size = VarInt.get_len(data[n:n+1])
	id_b_len = VarInt.from_bytes(data[n:n+id_b_len_size])
	n += id_b_len_size
	
	id_b = data[n:n+id_b_len].decode()
	n += id_b_len

	run_ids = [id_a, id_b]

	# Parse the rest of the header such as with snapshot header
	collectors_info = parse_snap_header(data[n:])

	return (run_ids, collectors_info)


class AlreadyExistsException(Exception):
	pass

class UnknownValueException(Exception):
	pass

class DiffElement:
	"""
	Representation of an element that differs during a comparison.
	It can either be a new element or an element that has changed between two snapshots.

	Arguments:
		run_id (str): identifier of the snapshot the element is associated to.
		element (Object): the objects used by a collector to store what they collect. (e.g. User in UsersCollector to store users)
		type (int): type of modification that happened on the element. (Created, Deleted, Modified)

	Attributes:
		run_id (str): identifier of the snapshot the element is associated to.
		element (Object): the objects used by a collector to store what they collect. (e.g. User in UsersCollector to store users)
		type (int): type of modification that happened on the element. (Created, Deleted, Modified)
	"""
	def __init__(self, run_id, element, type):
		self.run_id = run_id
		self.element = element
		self.type = type

	def __eq__(self, o):
		if type(o) != DiffElement:
			return False

		if o.run_id != self.run_id:
			return False

		if o.type != self.type:
			return False

		if o.element == self.element:
			return True

		return False

	def __repr__(self):
		return f"<DiffElement : run_id = {self.run_id}, element = {self.element}, type = {self.type}>"

	def get_collectible_name(self):
		"""
		Get the name of the collectible being stored.

		Returns:
			The element_name of the stored collectible.
		"""
		return self.element.element_name

	def to_bytes(self, run_id_bytes):
		"""
		Encode an element of the tree of differences.

		Arguments:
			run_id_bytes (dict{str:bytes}): python dictionary mapping the run_id's used in the report to their respective byte identifier.

		Returns:
			A bytes stream represdenting the element.
		"""
		encoded_data = b""

		encoded_data += run_id_bytes[self.run_id]
		encoded_data += self.element.to_bytes()
		#encode the type of DiffElement
		encoded_data += VarInt.to_bytes(self.type)

		return encoded_data

	def from_bytes(data, run_ids, element_class):
		"""
		Decode an element of the tree of differences.

		Arguments:
			data (bytes): a bytes stream representing a DiffElement.
			run_ids (list[str]): the snapshot id's used for the report.
			element_class (Collectible): reference to the class of the element.

		Returns:
			A tupple containing: 1. a bytes stream represdenting the element; 2. the rest of the unread bytes that are not part of this DiffElement datastructure.
		"""
		run_id = data[0]

		element, rest = element_class.from_bytes(data[1:])

		type_len = VarInt.get_len(rest)
		type_val = VarInt.from_bytes(rest[0:type_len])
		rest = rest[type_len:]
		if rest == b'':
			rest = None

		obj = DiffElement(run_ids[run_id], element, type_val)

		return (obj, rest)

	def export_db(self, report_id, db_cursor):
		"""
		Insert the element into the database.

		Arguments:
			report_id (str): identifier of the report the element is linked to.
			db_cursor (Cursor): cursor pointing to the sqlite3 database.
		"""
		self.element.export_report_db(report_id, self.run_id, self.type, db_cursor)

class DiffReport:
	"""
	Report of the differences between two snapshots.

	Arguments:
		first_run_id (str): identifier of the first snapshot to compare with.
		second_run_id (str): identifier of the second snapshot to compare with.

	Attributes:
		first_run_id (str): identifier of the first snapshot to compare with.
		second_run_id (str): identifier of the second snapshot to compare with.
		diff_elements (dict{str : dict{str : list[DiffElement]}}): tree of differences.
	"""
	def __init__(self, first_run_id, second_run_id):
		self.first_run_id = first_run_id
		self.second_run_id = second_run_id
		self.diff_elemnts = {}

	def __eq__(self, o):
		if type(o) != DiffReport:
			return False

		if o.first_run_id != self.first_run_id and o.second_run_id != self.second_run_id:
			return False

		if o.diff_elemnts == self.diff_elemnts:
			return True

		return False

	def __repr__(self):
		return str(self.diff_elemnts)

	def get_collectors_names(self):
		"""
		Get a list of all the collectors' names in the tree of differences.

		Returns:
			A list of collector's names.
		"""
		return self.diff_elemnts.keys()

	def add_diff_element(self, element, collector_name):
		"""
		Add an element to the tree of differences.

		Arguments:
			element (DiffElement): the element to add in the tree.
			collector_name (str): the name of the collector that is compared.

		Raises:
			UnknownValueException: run ids do not match between the runs beeing compared and the run from which the element comes from.
		"""
		if element.run_id != self.first_run_id and element.run_id != self.second_run_id:
			raise UnknownValueException(f"Element is not from any of the snapshots used for this report. (received {element.run_id}, expected {self.first_run_id} or {self.second_run_id})")

		if collector_name in self.diff_elemnts.keys():
			if element.get_collectible_name() in self.diff_elemnts[collector_name].keys():
				self.diff_elemnts[collector_name][element.get_collectible_name()].append(element)
			else:
				self.diff_elemnts[collector_name][element.get_collectible_name()] = [element]
		else:
			self.diff_elemnts[collector_name] = {element.get_collectible_name() : [element]}

	def add_no_diff_element(self, collector_name, type):
		"""
		Add the name of an element type of a collector for which there were no changes between the two snapshots.
		(e.g. for LinUsersCollector, there could be a new user without new group or sudoer)

		Arguments:
			collector_name (str): the name of the collector that is compared.
			type (str): the name of the element type of the collector that is compared.

		Raises:
			AlreadyExistsException: the element type already is in the report for the given collector name.
		"""
		if collector_name not in self.diff_elemnts.keys():
			self.diff_elemnts[collector_name] = {type : []}
		else:
			if type in self.diff_elemnts[collector_name].keys():
				raise AlreadyExistsException(f"This element type is already in the report for this collector.")
			else:
				self.diff_elemnts[collector_name][type] = []

	def add_no_diff_collector(self, collector_name):
		"""
		Add the name of a collector that has not changed between the two snapshots.

		Arguments:
			collector_name (str): the name of the collector that is compared.

		Raises:
			AlreadyExistsException: the collecton name already is in the report.
		"""
		from ..modules import AVAILABLE_COLLECTORS as AC
		
		if collector_name in self.diff_elemnts.keys():
			raise AlreadyExistsException(f"This collector name is already in the report.")

		self.diff_elemnts[collector_name] = AC.get_collector_by_name(collector_name).get_report_tree_structure()

	def to_bytes(self):
		"""
		Encode the tree of differences.

		Returns:
			A bytes stream representing 1. the header with preliminar informations over the collectors in the tree, 2. the tree of differences.
		"""
		from ..modules import AVAILABLE_COLLECTORS as AC
		
		run_id_mapping = {self.first_run_id : b"\x00", self.second_run_id : b"\x01"}

		header = b""
		encoded_data = b""

		previous_len = 0

		# add the first and second run_id
		header += VarInt.to_bytes(len(self.first_run_id))
		header += self.first_run_id.encode()
		header += VarInt.to_bytes(len(self.second_run_id))
		header += self.second_run_id.encode()

		# add the number of collectors compared in the tree
		header += VarInt.to_bytes(len(self.diff_elemnts.keys()))

		# add every collector
		for collector_name in self.diff_elemnts.keys():
			# Add its type id
			collector_class = AC.get_collector_by_name(collector_name)
			collector_id = collector_class.snapshot_elemnt_id
			encoded_data += collector_id

			for element_name in self.diff_elemnts[collector_name].keys():
				# Add the number of elements
				element_number = len(self.diff_elemnts[collector_name][element_name])
				encoded_data += VarInt.to_bytes(element_number)

				for element in self.diff_elemnts[collector_name][element_name]:
					# encode it
					encoded_data += element.to_bytes(run_id_mapping)


			# notify in the header we use this collector
			header += collector_class.snapshot_elemnt_id
			header += VarInt.to_bytes(previous_len)
			# add its offset relative to the begining of the content (the end of the header)
			previous_len = len(encoded_data)

		return (header, encoded_data)

	def read_collector_from_bytes(self, data, run_ids, collector):
		"""
		Decode a bytes stream into a DiffReport for a single collector.

		Arguments:
			data (bytes): the bytes stream that represent the DiffReport.
			run_ids (list[str]): ordered list of the snapshot id's compared in the report. (order is the same as in the report file)
			collectors (list[Class]): ordered list of references to collectors classes used in the report. (order is the same as in the report file)

		Returns:
			True if the decoding was successful.

		Raises:
			ValueError: collectors do not match
		"""
		collector_type = data[0:1]

		if collector_type != collector.snapshot_elemnt_id:
			raise ValueError(f"Provided Collector do not match the byte stream in the report file.")

		return collector.import_diff_from_report(data[1:], run_ids, self)

	def export_db(self, report_id, db):
		"""
		Export the report in the specified database.

		Arguments:
			report_id (str): identifer of the report.
			db (str): path to the database.
		"""
		from ..modules import AVAILABLE_COLLECTORS as AC
		import sqlite3 as sql

		conn = sql.connect(db)
		cursor = conn.cursor()

		# creates the tables if they do not already exist
		cursor.execute("""CREATE TABLE IF NOT EXISTS reports(
			report_id TEXT PRIMARY KEY,
			run_id_a TEXT,
			run_id_b TEXT
			)""")
		cursor.execute("""CREATE TABLE IF NOT EXISTS reports_collectors(
			report_id TEXT,
			collector_type BLOB,
			PRIMARY KEY(report_id, collector_type)
			)""") # collector type is prefered as "collector_type" value compared to collector name because encoding is lighter with a BLOB of bytes than with a TEXT value

		# Insert the data
		query = f"""INSERT INTO reports VALUES (?, ?, ?)"""
		cursor.execute(query, (report_id, self.first_run_id, self.second_run_id))

		# Insert data for every collector data that is in the report
		for collector_name in self.diff_elemnts.keys():
			collector_class = AC.get_collector_by_name(collector_name)

			# list the collectors beeing compared in the report
			query = f"""INSERT INTO reports_collectors VALUES (?, ?)"""
			cursor.execute(query, (report_id, collector_class.snapshot_elemnt_id))

			# create the database report related tables for every collector type beeing used in the report
			collector_class.create_report_tables(cursor)

			# insert the data of every element of every collectible types of each collector that is in the report
			for collectible_data in self.diff_elemnts[collector_name].values():
				for element in collectible_data:
					element.export_db(report_id, cursor)

		conn.commit()