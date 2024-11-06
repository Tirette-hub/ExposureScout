#!/usr/bin/python3
#coding:utf-8

"""
Implementation of the users collector to gather users, groups and sudoers on the machine. This collector inherits from the abstract Collector class.
It also contains the data structures used for the different collectibles which inherit from the abstract Collectible class.

Authors:
Nathan Amorison

Version:
0.1.0
"""


from .Collector import ACollector, ACollectible
from ..core.tools import get_file_hash, xor_list
from ..core.octets import VarInt
from ..core.report import DiffElement, AlreadyExistsException, CREATED, DELETED, MODIFIED

import subprocess
import threading
import sqlite3 as sql
import os

class User(ACollectible):
	"""
	Datastructure used to represent a Linux/Unix User.

	Arguments:
		uid (int): user id.
		name (str): user's name.
		groups (list[int]): list of groups' gid the user is in.

	Attributes:
		element_name (str): name used to identify this collectible.

		uid (int): user id.
		name (str): user's name.
		groups (list[int]): list of groups' gid the user is in.
	"""

	#snapshot_elemnt_id = b'\x00' #byte used for byte convertions to identify the next bytes represent a User
	element_name = "User"

	def __init__(self, uid, name, groups):
		self.uid = uid
		self.name = name
		self.groups = groups

	def __str__(self):
		return f"<User: uid={self.uid}, name={self.name}, groups={','.join(list(str(g) for g in self.groups))}>"

	def __repr__(self):
		return str(self)

	def __eq__(self, o):
		if type(o) != User:
			return False

		if o.uid == self.uid and o.name == self.name and o.groups == self.groups:
			return True

		return False

	def to_bytes(self):
		"""
		Converts this user datastructure to a byte string used to store it.

		Returns:
			A bytes stream.
		"""
		uid_as_bytes = VarInt.to_bytes(self.uid)
		name_size = len(self.name)
		name_as_bytes = VarInt.to_bytes(name_size) + self.name.encode()
		groups_size = len(self.groups)
		groups_as_bytes = VarInt.to_bytes(groups_size) + b"".join(list(VarInt.to_bytes(g) for g in self.groups))

		return uid_as_bytes + name_as_bytes + groups_as_bytes # User.snapshot_elemnt_id + uid_as_bytes + name_as_bytes + groups_as_bytes

	def from_bytes(data):
		"""
		Convert bytes into a User datastructure.

		Arguments:
			data (bytes): a bytes stream begining with the encoded data of a User datastructure.

		Returns:
			A tupple containing: 1. the User datastructure recovered from the bytes stream; 2. the rest of the unread bytes that are not part of this user datastructure.
		"""
		n = 0

		# recover the user's uid
		uid_len = VarInt.get_len(data[0:1])
		uid = VarInt.from_bytes(data[0:uid_len])
		n += uid_len

		# recover the user's name
		name_size_len = VarInt.get_len(data[n:n+1])
		name_size = VarInt.from_bytes(data[n:n+name_size_len])
		n += name_size_len

		name = data[n:n+name_size].decode()
		n += name_size

		# recover the number of groups the user is in
		groups_size_len = VarInt.get_len(data[n:n+1])
		groups_size = VarInt.from_bytes(data[n:n+groups_size_len])
		n += groups_size_len

		# recover those groups
		groups = []
		for i in range(groups_size):
			gid_len = VarInt.get_len(data[n:n+1])
			gid = VarInt.from_bytes(data[n:n+gid_len])
			groups.append(gid)
			n += gid_len

		# build the user datastructure and get the rest of the byte stream
		user = User(uid, name, groups)
		rest = data[n:]

		if rest == b"":
			return (user, None)

		return (user, rest)

	def export_report_db(self, report_id, run_id, status, db_cursor):
		"""
		Export a User data structure that is part of a diff report into the specified database.

		Arguments:
			report_id (str): identifer of the report the element is linked to.
			run_id (str): identifier of the snapshot run the element comes from.
			status (int): value of the element's status in the diff report (created, deleted, modified, ...).
			db_cursor (Cursor): sqlite3 cursor that points to the database.
		"""
		query = f"""INSERT INTO reports_users VALUES (?, ?, ?, ?)"""
		db_cursor.execute(query, (report_id, run_id, self.uid, status))

class Group(ACollectible):
	"""
	Datastructure used to represent a Linux/Unix Group.

	Arguments:
		gid (int): group id.
		name (str): group's name.

	Attributes:
		element_name (str): name used to identify this collectible.

		gid (int): group id.
		name (str): group's name.
	"""

	#snapshot_elemnt_id = b'\x01' #byte used for byte convertions to identify the next bytes represent a Group
	element_name = "Group"

	def __init__(self, gid, name):
		self.gid = gid
		self.name = name

	def __str__(self):
		return f"<Group: gid={self.gid}, name={self.name}>"

	def __repr__(self):
		return str(self)

	def __eq__(self, o):
		if type(o) != Group:
			return False

		if o.gid == self.gid and o.name == self.name:
			return True

		return False

	def to_bytes(self):
		"""
		Converts this group datastructure to a byte string used to store it.

		Returns:
			A bytes stream.
		"""
		gid_as_bytes = VarInt.to_bytes(self.gid)
		name_size = len(self.name)
		name_as_bytes = VarInt.to_bytes(name_size) + self.name.encode()

		return gid_as_bytes + name_as_bytes # Group.snapshot_elemnt_id + gid_as_bytes + name_as_bytes

	def from_bytes(data):
		"""
		Convert bytes to a Group datastructure.

		Arguments:
			data (bytes): a bytes stream begining with the encoded data of a Group datastructure.

		Returns:
			A tupple containing: 1. the Group data structure recovered from the bytes stream; 2. the rest of the unread bytes that are not part of this group data structure.
		"""
		n = 0

		# recover the group's gid
		gid_len = VarInt.get_len(data[0:1])
		gid = VarInt.from_bytes(data[0:gid_len])
		n += gid_len

		# recover the group's name
		name_size_len = VarInt.get_len(data[n:n+1])
		name_size = VarInt.from_bytes(data[n:n+name_size_len])
		n += name_size_len

		name = data[n:n+name_size].decode()
		n += name_size

		# build the group datastructure and get the rest of the byte stream
		group = Group(gid, name)
		rest = data[n:]

		if rest == b"":
			return (group, None)

		return (group, rest)

	def export_report_db(self, report_id, run_id, status, db_cursor):
		"""
		Export a Group data structure that is part of a diff report into the specified database.

		Arguments:
			report_id (str): identifer of the report the element is linked to.
			run_id (str): identifier of the snapshot run the element comes from.
			status (int): value of the element's status in the diff report (created, deleted, modified, ...).
			db_cursor (Cursor): sqlite3 cursor that points to the database.
		"""
		query = f"""INSERT INTO reports_groups VALUES (?, ?, ?, ?)"""
		db_cursor.execute(query, (report_id, run_id, self.gid, status))

class Sudoer(ACollectible):
	"""
	Datastructure used to represent the sudoers.

	Arguments:
		uid (int): sudoer's user id.

	Attributes:
		element_name (str): name used to identify this collectible.

		uid (int): sudoer's user id.
	"""
	element_name = "Sudoer"

	def __init__(self, uid):
		self.uid = uid

	def __str__(self):
		return f"<Sudoer: {self.uid}>"

	def __repr__(self):
		return str(self)

	def __eq__(self, o):
		if type(o) != Sudoer:
			return False

		if o.uid == self.uid:
			return True

		return False

	def to_bytes(self):
		"""
		Converts this sudoer datastructure to a byte string used to store it.

		Returns:
			A bytes stream.
		"""
		uid_as_bytes = VarInt.to_bytes(self.uid)

		return uid_as_bytes

	def from_bytes(data):
		"""
		Convert bytes to a Sudoer datastructure.

		Arguments:
			data (bytes): a bytes stream begining with the encoded data of a Sudoer datastructure.

		Returns:
			A tupple containing: 1. the Sudoer datastructure recovered from the bytes stream; 2. the rest of the unread bytes that are not part of this sudoer datastructure.
		"""
		n = 0

		# recover the sudoer's uid
		uid_len = VarInt.get_len(data[0:1])
		uid = VarInt.from_bytes(data[0:uid_len])
		n += uid_len

		# build the sudoer datastructure and get the rest of the byte stream
		sudoer = Sudoer(uid)
		rest = data[n:]

		if rest == b"":
			return (sudoer, None)

		return (sudoer, rest)

	def export_report_db(self, report_id, run_id, status, db_cursor):
		"""
		Export a Sudoer data structure that is part of a diff report into the specified database.

		Arguments:
			report_id (str): identifer of the report the element is linked to.
			run_id (str): identifier of the snapshot run the element comes from.
			status (int): value of the element's status in the diff report (created, deleted, modified, ...).
			db_cursor (Cursor): sqlite3 cursor that points to the database.
		"""
		query = f"""INSERT INTO reports_sudoers VALUES (?, ?, ?, ?)"""
		db_cursor.execute(query, (report_id, run_id, self.uid, status))


def parse_user_line(line):
	"""
	Parse a line representing a user after running the collector bash script to extract data so it is easier to fill in the User data structure.

	Arguments:
		line (str): the string line to parse.

	Returns:
		A tupple with the uid, the user name, and the groups id it's in.
	"""
	user, groups = line.split(":")
	uid, uname = user.split("(")
	uid = int(uid)
	uname = uname.replace(")", "")
	groups = list(int(g) for g in groups.split(","))

	return (uid, uname, groups)

def parse_group_line(line):
	"""
	Parse a line representing a group after running the collector bash script to extract data so it is easier to fill in the Group data structure.

	Arguments:
		line (str): the string line to parse.

	Returns:
		A tupple with the gid, the group name.
	"""
	gname, gid = line.split(":")
	return (int(gid), gname)


class LinUsersCollector(ACollector):
	"""
	Users, Groups and Sudoers collector.
	Inherits from ACollector.

	Attributes:
		Inherits from ACollector
	"""
	name = "Users Collector"
	descr = """
			For Linux/Unix platforms only.
			This module collects all the users and groups as well as sudoers available on this machine.
			"""
	snapshot_elemnt_id = b"\x00"

	def __init__(self):
		super(LinUsersCollector, self).__init__()

	def __eq__(self, o):
		if type(o) != LinUsersCollector:
			return False

		if not o.raw_result or not self.raw_result:
			return False

		if o.get_hashes() == self.get_hashes():
			return True

		return False

	def get_users(self):
		"""
		Get the list of collected users.

		Returns:
			A list of Users. (None if collector has not run yet)
		"""
		if not self.raw_result:
			return None

		return self.raw_result[0]

	def get_groups(self):
		"""
		Get the list of collected groups.

		Returns:
			A list of Groups. (None if collector has not run yet)
		"""
		if not self.raw_result:
			return None

		return self.raw_result[1]

	def get_sudoers(self):
		"""
		Get the list of collected sudoers.

		Returns:
			A list of Sudoers. (None if collector has not run yet)
		"""
		if not self.raw_result:
			return None

		return self.raw_result[2]

	def get_hashes(self):
		"""
		Get the two collected hashes (passwd, group).

		Returns:
			A tupple with both hashes.
		"""
		if not self.raw_result:
			return None

		return (self.raw_result[3], self.raw_result[4])

	def import_bin(self, data):
		"""
		Import method to recover data of a previous run. Those data can then be previewed.

		Arguments:
			data (bytes): raw data with the first bytes representing this collector.

		Returns:
			The rest of raw bytes unrelated to this collector.
		"""
		#first bytes are Users related
		users_number_len = VarInt.get_len(data[0:1])
		users_number = VarInt.from_bytes(data[0:users_number_len])

		#recover the users 
		rest = data[users_number_len:]
		users = []
		for i in range(users_number):
			user, rest = User.from_bytes(rest)
			#print("user =", user)
			users.append(user)

		#bytes are Groups related
		groups_number_len = VarInt.get_len(rest[0:1])
		groups_number = VarInt.from_bytes(rest[0:groups_number_len])

		#print("read", users)

		#recover the groups
		rest = rest[groups_number_len:]
		groups = []
		for i in range(groups_number):
			group, rest = Group.from_bytes(rest)
			#print("group =", group)
			groups.append(group)

		#bytes are sudoers related
		sudoers_number_len = VarInt.get_len(rest[0:1])
		sudoers_number = VarInt.from_bytes(rest[0:sudoers_number_len])

		#print("read", groups)

		#recover the groups
		rest = rest[sudoers_number_len:]
		sudoers = []
		for i in range(sudoers_number):
			sudoer, rest = Sudoer.from_bytes(rest)
			#print("sudoer =", sudoer)
			sudoers.append(sudoer)

		#print("read", sudoers)

		#bytes are md5 relates
		passwd_hash = rest[0:16]
		group_hash = rest[16:32]

		#store the recovered data
		self.raw_result = [users, groups, sudoers, passwd_hash, group_hash]

		#return the rest of unread bytes
		rest = rest[32:]
		if rest == b"":
			return None
		return rest

	def import_db(self, db_cursor, run_id):
		"""
		Import method to recover data of a previous run stored in DB. Those data can then be previewed.
		Note: must already been connected to the database.

		Arguments:
			db_cursor (Cursor): pointer to the database.
			run_id (str): id used to store the collected data in the db of a specific run.
		"""
		# search for the 2 hashes
		query = f"""SELECT passwd_md5, group_md5 FROM user_collector WHERE run_id=?"""
		request = db_cursor.execute(query, (run_id,))
		hashes = request.fetchone()
		passwd_hash, group_hash = hashes

		# search for the users
		query = f"""SELECT uid, name FROM users WHERE run_id=?"""
		request = db_cursor.execute(query, (run_id,))
		db_users = request.fetchall()
		users = []
		for uid, uname in db_users:
			uid = int(uid)
			query = f"""SELECT gid FROM groups_list where run_id=? AND uid=?"""
			request = db_cursor.execute(query, (run_id, uid))
			db_groups = request.fetchall()

			# needed since db_groups is of the form [('%gid%',), ... , ('%gid%',)]
			groups = []
			for gid, *_ in db_groups:
				groups.append(int(gid))

			user = User(uid, uname, groups)
			users.append(user)

		# search for the groups
		query = f"""SELECT gid, name FROM groups WHERE run_id=?"""
		request = db_cursor.execute(query, (run_id,))
		db_groups = request.fetchall()
		groups = []
		for gid, gname in db_groups:
			gid = int(gid)

			group = Group(gid, gname)
			groups.append(group)

		# search for the sudoers
		query = f"""SELECT uid FROM sudoers WHERE run_id=?"""
		request = db_cursor.execute(query, (run_id,))
		db_sudoers = request.fetchall()
		sudoers = []
		for uid, *_ in db_sudoers:
			uid = int(uid)

			sudoers.append(Sudoer(uid))	

		# store the recovered data
		self.raw_result = [users, groups, sudoers, passwd_hash, group_hash]

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
		db_cursor.execute("""CREATE TABLE IF NOT EXISTS user_collector(
			run_id TEXT PRIMARY KEY,
			passwd_md5 BLOB,
			group_md5 BLOB
			)""")
		db_cursor.execute("""CREATE TABLE IF NOT EXISTS users(
			run_id TEXT,
			uid INTEGER,
			name TEXT,
			PRIMARY KEY(run_id, uid)
			)""")
		db_cursor.execute("""CREATE TABLE IF NOT EXISTS groups(
			run_id TEXT,
			gid INTEGER,
			name TEXT,
			PRIMARY KEY(run_id, gid)
			)""")
		db_cursor.execute("""CREATE TABLE IF NOT EXISTS groups_list(
			run_id INTEGER,
			gid TEXT,
			uid INTEGER,
			PRIMARY KEY(run_id, gid, uid),
			FOREIGN KEY(run_id, gid) REFERENCES groups(run_id, gid),
			FOREIGN KEY(run_id, uid) REFERENCES users(run_id, uid)
			)""")
		db_cursor.execute("""CREATE TABLE IF NOT EXISTS sudoers(
			run_id TEXT,
			uid INTEGER,
			PRIMARY KEY(run_id, uid),
			FOREIGN KEY(run_id, uid) REFERENCES users(run_id, uid)
			)""")

		# Add the collector type in the list of collectors that were run during the snapshot
		query = f"""INSERT INTO snapshots VALUES (?, ?)"""
		db_cursor.execute(query, (run_id, self.snapshot_elemnt_id))

		# Add the user collector general data
		query = f"""INSERT INTO user_collector VALUES (?, ?, ?)"""
		db_cursor.execute(query, (run_id, self.raw_result[3], self.raw_result[4]))

		# Add the users and their groups list
		for user in self.raw_result[0]:
			for gid in user.groups:
				query = f"""INSERT INTO groups_list VALUES (?, ?, ?)"""
				db_cursor.execute(query, (run_id, gid, user.uid))
			query = f"""INSERT INTO users VALUES (?, ?, ?)"""
			db_cursor.execute(query, (run_id, user.uid, user.name))

		# Add the groups to the db
		for group in self.raw_result[1]:
			query = f"""INSERT INTO groups VALUES (?, ?, ?)"""
			db_cursor.execute(query, (run_id, group.gid, group.name))

		# Add the sudoers
		for sudoer in self.raw_result[2]:
			query = f"""INSERT INTO sudoers VALUES (?, ?)"""
			db_cursor.execute(query, (run_id, sudoer.uid))

	def _format(self):
		"""
		Private method to format raw collected data of a run to exportable data.
		"""
		encoded_data = b""

		# for each user, encode it
		user_number = len(self.raw_result[0])
		encoded_data += VarInt.to_bytes(user_number)
		for user in self.raw_result[0]:
			encoded_data += user.to_bytes()

		# for each group, encode it
		group_number = len(self.raw_result[1])
		encoded_data += VarInt.to_bytes(group_number)
		for group in self.raw_result[1]:
			encoded_data += group.to_bytes()

		# for each sudoer, encode it
		sudoers_number = len(self.raw_result[2])
		encoded_data += VarInt.to_bytes(sudoers_number)
		for sudoer in self.raw_result[2]:
			encoded_data += sudoer.to_bytes()

		# encode the passwd file md5 hash
		encoded_data += self.raw_result[3]

		# encode the group file md5 hash
		encoded_data += self.raw_result[4]

		encoded_data_len = len(encoded_data)

		self.result = LinUsersCollector.snapshot_elemnt_id + VarInt.to_bytes(encoded_data_len) + encoded_data

	def collect_users(self):
		"""
		Executes the bash script that will collect all the users.
		"""
		bash_file = os.path.join(os.path.dirname(__file__), "../scripts/Users.sh")
		try:
			command = subprocess.run([bash_file], capture_output=True)
			output = command.stdout.decode()
			users = list(output.split("\n"))
			raw_data = []
			for userline in users:
				if userline == "":
					continue
				uid, uname, groups = parse_user_line(userline)
				user = User(uid, uname, groups)
				raw_data.append(user)

			self.raw_result[0] = raw_data
		except PermissionError:
			print(f"Cannot execute {bash_file}. Please check the permissions.")

	def collect_groups(self):
		"""
		Executes the bash script that will collect all the groups.
		"""
		bash_file = os.path.join(os.path.dirname(__file__), "../scripts/Groups.sh")
		try:
			command = subprocess.run([bash_file], capture_output=True)
			output = command.stdout.decode()
			groups = list(output.split("\n"))
			raw_data = []
			for groupline in groups:
				if groupline == "":
					continue
				gid, gname = parse_group_line(groupline)
				group = Group(gid, gname)
				raw_data.append(group)

			self.raw_result[1] = raw_data
		except PermissionError:
			print(f"Cannot execute {bash_file}. Please check the permissions.")

	def collect_sudoers(self):
		"""
		Executes the bash script that will collect the list of sudoers.
		"""
		bash_file = os.path.join(os.path.dirname(__file__), "../scripts/Sudoers.sh")
		try:
			command = subprocess.run([bash_file], capture_output=True)
			output = command.stdout.decode()
			raw_data = list(Sudoer(int(uid)) for uid in output.split("\n") if uid != "")

			self.raw_result[2] = raw_data
		except PermissionError:
			print(f"Cannot execute {bash_file}. Please check the permissions.")

	def collect_passwd_hash(self):
		"""
		Computes the /etc/passwd file md5 hash.
		"""
		passwd_file = "/etc/passwd"
		try:
			hash_value = get_file_hash(passwd_file)

			self.raw_result[3] = hash_value
		except PermissionError:
			print(f"Cannot read {passwd_file}. Please check the permissions.")

	def collect_group_hash(self):
		"""
		Computes the /etc/group file md5 hash.
		"""
		group_file = "/etc/group"
		try:
			hash_value = get_file_hash(group_file)

			self.raw_result[4] = hash_value
		except PermissionError:
			print(f"Cannot read {group_file}. Please check the permissions.")

	def _run(self):
		"""
		Private method collecting the raw data.
		"""
		self.raw_result = [None, None, None, None, None]

		t_u = threading.Thread(target=self.collect_users, args=())
		t_g = threading.Thread(target=self.collect_groups, args=())
		t_s = threading.Thread(target=self.collect_sudoers, args=())
		t_md5_passwd = threading.Thread(target=self.collect_passwd_hash, args=())
		t_md5_group = threading.Thread(target=self.collect_group_hash, args=())
		
		t_u.start()
		t_g.start()
		t_s.start()
		t_md5_passwd.start()
		t_md5_group.start()

		t_u.join()
		t_g.join()
		t_s.join()
		t_md5_passwd.join()
		t_md5_group.join()

	def make_diff(run_id_a, run_id_b, a, b, report):
		"""
		Static method used to get the difference between two "Linux/Unix users" collectors. SHOULD be used only if the two hashes have been checked and are different between both the collectors.

		Arguments:
			run_id_a (str): run_id of the first collector.
			run_id_b (str): run_id of the second collector.
			a (LinUsersCollector): the first collectors.
			b (LinUsersCollector): the second collector.
			report (DiffReport): the report where to add the differences.
		"""
		# create local macro for adding elements in the report
		def _add_in_report(run_id, elements, element_type, type):
			if len(elements) > 0:
				for e in elements:
					elemnt = DiffElement(run_id, e, element_type)
					report.add_diff_element(elemnt, LinUsersCollector.name)
			else:
				try:
					report.add_no_diff_element(LinUsersCollector.name, type)
				except AlreadyExistsException:
					# if this custom error occurs, then type already in the report so we do not care about it
					pass


		if not a:
			if not b:
				raise ValueError(f"There should be at least one Collector to be able to make a diff!")
			
			# there is the second collector but not the first one
			# We first check that the provided collector type is correct to avoid uncontrolled errors
			if type(b) != LinUsersCollector:
				raise ValueError(f"Type of the second collector is not valid. (provided: {type(b)}, expected: {LinUsersCollector})")

			# We now can compare the list of users that are different between both snapshots
			users_b = b.get_users()

			# We add them in the report as a report element
			_add_in_report(run_id_b, users_b, CREATED, User.element_name)

			# We do the same with groups
			groups_b = b.get_groups()

			_add_in_report(run_id_b, groups_b, CREATED, Group.element_name)

			# We do the same with sudoers
			sudoers_b = b.get_sudoers()
			_add_in_report(run_id_b, sudoers_b, CREATED, Sudoer.element_name)

		elif not b:
			# there is the first collector but not the second one
			# We first chech that the provided collector type is correct to avoid uncontrolled errors
			if type(a) != LinUsersCollector:
				raise ValueError(f"Type of the first collector is not valid. (provided: {type(a)}, expected: {LinUsersCollector})")

			# We now can compare the list of users that are different between both snapshots
			users_a = a.get_users()

			# We add them in the report as a report element
			_add_in_report(run_id_a, users_a, CREATED, User.element_name)

			# We do the same with groups
			groups_a = a.get_groups()

			_add_in_report(run_id_a, groups_a, CREATED, Group.element_name)

			# We do the same with sudoers
			sudoers_a = a.get_sudoers()
			_add_in_report(run_id_a, sudoers_a, CREATED, Sudoer.element_name)

		else:
			# there are two collectors
			# We first check that the provided collectors are of the same type to avoid uncontrolled errors
			if type(a) != LinUsersCollector:
				raise ValueError(f"Type of the first collector is not valid. (provided: {type(a)}, expected: {LinUsersCollector})")
			elif type(b) != LinUsersCollector:
				raise ValueError(f"Type of the second collector is not valid. (provided: {type(b)}, expected: {LinUsersCollector})")

			# We now can compare the list of users that are different between both snapshots
			users_a = a.get_users()
			users_b = b.get_users()

			unique_users_a, unique_users_b = xor_list(users_a, users_b)
			# We add them in the report as a report element
			modified = False
			for element_a in unique_users_a:
				for element_b in unique_users_b:
					if element_a.uid == element_b.uid:
						elemnt = DiffElement(run_id_a, element_a, MODIFIED)
						report.add_diff_element(elemnt, LinUsersCollector.name)
						elemnt = DiffElement(run_id_b, element_b, MODIFIED)
						report.add_diff_element(elemnt, LinUsersCollector.name)

						unique_users_a.remove(element_a)
						unique_users_b.remove(element_b)

						modified = True

						break

			if len(unique_users_a) > 0:
				for element_a in unique_users_a:
					element = DiffElement(run_id_a, element_a, DELETED)
					report.add_diff_element(element, LinUsersCollector.name)
					modified = True

			if len(unique_users_b) > 0:
				for element_b in unique_users_b:
					element = DiffElement(run_id_b, element_b, CREATED)
					report.add_diff_element(element, LinUsersCollector.name)
					modified = True

			if not modified:
				try:
					report.add_no_diff_element(LinUsersCollector.name, User.element_name)
				except AlreadyExistsException:
					pass


			# We do the same with groups
			groups_a = a.get_groups()
			groups_b = b.get_groups()

			unique_groups_a, unique_groups_b = xor_list(groups_a, groups_b)
			#print("unique groups a:", unique_groups_a)
			#print("unique groups b:", unique_groups_b)
			modified = False
			for element_a in unique_groups_a:
				for element_b in unique_groups_b:
					if element_a.gid == element_b.gid:
						elemnt = DiffElement(run_id_a, element_a, MODIFIED)
						report.add_diff_element(elemnt, LinUsersCollector.name)
						elemnt = DiffElement(run_id_b, element_b, MODIFIED)
						report.add_diff_element(elemnt, LinUsersCollector.name)

						unique_groups_a.remove(element_a)
						unique_groups_b.remove(element_b)

						modified = True

						break

			if len(unique_groups_a) > 0:
				for element_a in unique_groups_a:
					element = DiffElement(run_id_a, element_a, DELETED)
					report.add_diff_element(element, LinUsersCollector.name)
					modified = True

			if len(unique_groups_b) > 0:
				for element_b in unique_groups_b:
					element = DiffElement(run_id_b, element_b, CREATED)
					report.add_diff_element(element, LinUsersCollector.name)
					modified = True

			if not modified:
				try:
					report.add_no_diff_element(LinUsersCollector.name, Group.element_name)
				except AlreadyExistsException:
					pass
					

			# We do the same with sudoers
			sudoers_a = a.get_sudoers()
			sudoers_b = b.get_sudoers()

			unique_sudoers_a, unique_sudoers_b = xor_list(sudoers_a, sudoers_b)
			#print("unique sudoers a:", unique_sudoers_a)
			#print("unique sudoers b:", unique_sudoers_b)
			modified = False
			for element_a in unique_sudoers_a:
				for element_b in unique_sudoers_b:
					if element_a.uid == element_b.uid:
						elemnt = DiffElement(run_id_a, element_a, MODIFIED)
						report.add_diff_element(elemnt, LinUsersCollector.name)
						elemnt = DiffElement(run_id_b, element_b, MODIFIED)
						report.add_diff_element(elemnt, LinUsersCollector.name)

						unique_sudoers_a.remove(element_a)
						unique_sudoers_b.remove(element_b)

						modified = True

						break

			if len(unique_sudoers_a) > 0:
				for element_a in unique_sudoers_a:
					element = DiffElement(run_id_a, element_a, DELETED)
					report.add_diff_element(element, LinUsersCollector.name)
					modified = True

			if len(unique_sudoers_b) > 0:
				for element_b in unique_sudoers_b:
					element = DiffElement(run_id_b, element_b, CREATED)
					report.add_diff_element(element, LinUsersCollector.name)
					modified = True

			if not modified:
				try:
					report.add_no_diff_element(LinUsersCollector.name, Sudoer.element_name)
				except AlreadyExistsException:
					pass
					

	def import_diff_from_report(data, run_ids, report):
		"""
		Extract LinUsersCollector's diff elements from a report file.

		Arguments:
			data (bytes): a bytes stream representing the elements associated to this collector in the report.
			run_ids (list[str]): the ordered list of the snapshot ids from which come the report elements.
			report (DiffReport): datastructure in which to store the recovered data.

		Returns:
			True if the Diff Elements associated to LinUsersCollector data have been successfully imported.
		"""
		rest = data

		# read the users
		users_number_len = VarInt.get_len(rest[0:1])
		users_number = VarInt.from_bytes(rest[0:users_number_len])

		rest = rest[users_number_len:]

		if users_number:
			for i in range(users_number):
				user, rest = DiffElement.from_bytes(rest, run_ids, User)
				report.add_diff_element(user, LinUsersCollector.name)
		else:
			report.add_no_diff_element(LinUsersCollector.name, User.element_name)

		# read the groups
		groups_number_len = VarInt.get_len(rest[0:1])
		groups_number = VarInt.from_bytes(rest[0:groups_number_len])

		rest = rest[groups_number_len:]

		if groups_number:
			for i in range(groups_number):
				group, rest = DiffElement.from_bytes(rest, run_ids, Group)
				report.add_diff_element(group, LinUsersCollector.name)
		else:
			report.add_no_diff_element(LinUsersCollector.name, Group.element_name)

		# read the sudoers
		sudoers_number_len = VarInt.get_len(rest[0:1])
		sudoers_number = VarInt.from_bytes(rest[0:sudoers_number_len])

		rest = rest[sudoers_number_len:]

		if sudoers_number:
			for i in range(sudoers_number):
				sudoer, rest = DiffElement.from_bytes(rest, run_ids, Sudoer)
				report.add_diff_element(sudoer, LinUsersCollector.name)
		else:
			report.add_no_diff_element(LinUsersCollector.name, Sudoer.element_name)

		return True

	def import_diff_from_report_db(db_cursor, report_id, run_ids, report):
		"""
		Extract LinUsersCollector's diff elements from a database.

		Arguments:
			db_cursor (Cursor): pointer to the database.
			report_id (str): identifier of the report being imported.
			run_ids (list[str]): the ordered list of the snapshot ids from which come the report elements.
			report (DiffReport): datastructure in which to store the recovered data.
		"""
		for run_id in run_ids:
			# search for users linked to that report
			query = f"""SELECT uid, status FROM reports_users WHERE report_id=? AND run_id=?"""
			request = db_cursor.execute(query, (report_id, run_id))
			users = request.fetchall()

			if users and users != []:
				for uid, status in users:
					query = f"""SELECT name FROM users WHERE run_id=? AND uid=?"""
					request = db_cursor.execute(query, (run_id, uid))
					names = request.fetchall()
					for uname, *_ in names:
						uid = int(uid)
						query = f"""SELECT gid FROM groups_list where run_id=? AND uid=?"""
						request = db_cursor.execute(query, (run_id, uid))
						db_groups = request.fetchall()

						# needed since db_groups is of the form [('%gid%',), ... , ('%gid%',)]
						groups = []
						for gid, *_ in db_groups:
							groups.append(int(gid))

						user = User(uid, uname, groups)
						
						report.add_diff_element(DiffElement(run_id, user, status), LinUsersCollector.name)

			else:
				try:
					report.add_no_diff_element(LinUsersCollector.name, User.element_name)
				except AlreadyExistsException as e:
					# we are reading the second run_id and the first one had values to add where the send had none. Just discard the error, it is controlled.
					pass

			# search for groups linked to that report
			query = f"""SELECT gid, status FROM reports_groups WHERE report_id=? AND run_id=?"""
			request = db_cursor.execute(query, (report_id, run_id))
			groups = request.fetchall()

			if groups and groups != []:
				for gid, status in groups:
					query = f"""SELECT name FROM groups WHERE run_id=? AND gid=?"""
					request = db_cursor.execute(query, (run_id, int(gid)))
					names = request.fetchall()
					for gname, *_ in names:
						gid = int(gid)

						group = Group(gid, gname)
						
						# add the recovered group to the report
						report.add_diff_element(DiffElement(run_id, group, status), LinUsersCollector.name)

			else:
				try:
					report.add_no_diff_element(LinUsersCollector.name, Group.element_name)
				except AlreadyExistsException:
					# we are reading the second run_id and the first one had values to add where the send had none. Just discard the error, it is controlled.
					pass

			# search for sudoers linked to that report
			query = f"""SELECT uid, status FROM reports_sudoers WHERE report_id=? AND run_id=?"""
			request = db_cursor.execute(query, (report_id, run_id))
			sudoers = request.fetchall()

			if sudoers and sudoers != []:
				for uid, status in sudoers:
					uid = int(uid) # no need to do another query since we already have the uid of the sudoer

					sudoer = Sudoer(uid)
					
					# add the recovered sudoer to the report
					report.add_diff_element(DiffElement(run_id, sudoer, status), LinUsersCollector.name)

			else:
				try:
					report.add_no_diff_element(LinUsersCollector.name, Sudoer.element_name)
				except AlreadyExistsException:
					# we are reading the second run_id and the first one had values to add where the send had none. Just discard the error, it is controlled.
					pass
		

	def get_report_tree_structure():
		"""
		Get the structure of the Collector used for the report.

		Returns:
			A python dict with an empty list of users, an empty list of groups, and an empty list of sudoers.
		"""
		return {User.element_name : [], Group.element_name : [], Sudoer.element_name : []}

	def create_report_tables(db_cursor):
		"""
		Static method used to create the different tables used by this collector for report structure in the specified database.
		Note: modifications are not committed here.

		Arguments:
			db_cursor (Cursor): sqlite3 cursor pointing to the database in which the tables must be created.
		"""
		db_cursor.execute("""CREATE TABLE IF NOT EXISTS reports_users(
			report_id TEXT,
			run_id TEXT,
			uid INTEGER,
			status INTEGER,
			PRIMARY KEY(report_id, run_id, uid),
			FOREIGN KEY(run_id, uid) REFERENCES users
			)""")
		db_cursor.execute("""CREATE TABLE IF NOT EXISTS reports_groups(
			report_id TEXT,
			run_id TEXT,
			gid INTEGER,
			status INTEGER,
			PRIMARY KEY(report_id, run_id, gid),
			FOREIGN KEY(run_id, gid) REFERENCES groups
			)""")
		db_cursor.execute("""CREATE TABLE IF NOT EXISTS reports_sudoers(
			report_id TEXT,
			run_id TEXT,
			uid INTEGER,
			status INTEGER,
			PRIMARY KEY(report_id, run_id, uid),
			FOREIGN KEY(run_id, uid) REFERENCES sudoers
			)""")