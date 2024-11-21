#!/usr/bin/python3
#coding:utf-8

"""
This is the heart of the application. It manages all the collectors, the snapshots ran or loaded and the reports of diff.
You can use it as a "Memory Manager" of the application and you should use it to perform all commands since it implements all the application features.

Authors:
Nathan Amorison

Version:
0.1.5
"""

import time
import threading
import os

from . import tools
from .octets import VarInt
from .report import DiffReport, parse_rpt_header, parse_snap_header
from .. import modules

BIN = 0
DB = 1


class AnalysisManager:
	"""
	Core module used to manage all the different runs and make analysis between them.
	It can also manage the memory used by the different runs (you can dump runs to free memory, otherwize every run is kept in memory either they have been saved ot not so it is faster if you want to make analysis between those runs).

	Attributes:
		runs (dict{str:CollectorList}): the different runs in memory that are ready to use (to be analyzed or to be stored). Every run is identified by its run id as a string and its collectors.
		running_snapshot (str): used to know what snapshot is running, using its run_id.
		running_snapshot_threads (list[threading.Thread]): list of all the threads running for the running snapshot.
		snapshot_paused (bool): flag used to know if the running snapshot has been paused or not.
		awaiting_collectors (list[Collector]): list of collectors awaiting to be run.
		diff_reports (dict{str : DiffReport}): list of reports of differences between two snapshots that have been performed.
	"""
	def __init__(self):
		self.runs = {}
		self.running_snapshot = None
		self.running_snapshot_threads = None
		self.snapshot_paused = False

		self.awaiting_collectors = []

		self.diff_reports = {}

	def is_running(self):
		"""
		Get the running status.

		Returns:
			True if a snapshot is beeing run.
		"""
		if self.running_snapshot != None:
			return True
		else:
			return False

	def get_running_snapshot(self):
		"""
		Get the collectors of the running snapshot.

		Returns:
			The list of collectors being run, None if no snapshot is running.
		"""
		if self.running_snapshot:
			return self.runs[self.running_snapshot]

		return None

	def save(self, run_id, method = BIN, db = None, buf_size = 64):
		"""
		Export a snapshot.

		Arguments:
			run_id (str): the run identifier.
			method (int): the method used to export the data (binary: 0, sqlite3 db: 1). (default = BIN = 0)
			db (str): path to the database. (MUST be used ONLY if method is set to 1 (DB), default = None)
			buf_size (int): buffer size in kB used while writing a snap file. (default = 64)

		Returns:
			True if the export succeeded, False otherwize.

		Raises:
			ValueError: unknown method provided.
			ValueError: method is set to 1 (DB) but no path to the database provided.
		"""

		if method == BIN:
			# export all the collectors
			try:
				collectors = list(c.export_bin() for c in self.runs[run_id])
			except Exception as e:
				print(e)
				return False

			# build the header
			header = b""
			previous_len = 0
			for c in collectors:
				# add the collector type and compute its offset before to add it as well
				header += c[0:1]
				offset = previous_len
				header += VarInt.to_bytes(offset)
				previous_len += len(c)

			collectors_number = len(collectors)
			header = VarInt.to_bytes(collectors_number) + header

			header_len = len(header)
			header = VarInt.to_bytes(header_len) + header

			# save it in a file
			filename = os.path.join(os.path.dirname(__file__), f"../../reports/{run_id}.snap")
			with open(filename, "wb") as f:
				# write the header
				f.write(header)
				# write the collectors
				for c in collectors:
					f.write(c)

		elif method == DB:
			if db:
				import sqlite3 as sql

				conn = sql.connect(db)
				cursor = conn.cursor()

				for collector in self.runs[run_id]:
					collector.export_db(cursor, run_id)
					conn.commit()

				conn.close()
			else:
				raise ValueError(f"No database path was set. Please provide a proper path.")

		else:
			raise ValueError(f"Export method {method} is unknown. please select a valid option between: 0 (BIN) for binary file data export or 1 (DB) for sqlite3 db data export")

		return True

	def load(self, run_id, method = BIN, db = None, buf_size = 64):
		"""
		Import a snapshot.

		Arguments:
			run_id (str): the run identifier.
			method (int): the method used to export the data (binary: 0, sqlite3 db: 1). (default = BIN = 0)
			db (str): path to the database. (MUST be used ONLY if method is set to 1 (DB), default = None)
			buf_size (int): buffer size in kB used while reading a snap file. (default = 64)

		Returns:
			True if the loading was successful, False if it has already been loaded.

		Raises:
			ValueError: unknown method provided.
			ValueError: method is set to 1 (DB) but no path to the database provided.
			IOError: corrupted file (header and content do not match together).
			IOError: impossible to parse the file content.
			FileNotFoundError: incorrect path to the file (based on the run_id).
		"""
		collectors = []

		if run_id in self.runs.keys():
			return False

		if method == BIN:
			filename = fn = os.path.join(os.path.dirname(__file__), f"../../reports/{run_id}.snap")
			with open(filename, "rb") as f:
				# Read the header
				data = f.read(1)
				header_size_len = VarInt.get_len(data)
				data += f.read(header_size_len-1)
				header_size = VarInt.from_bytes(data)

				header = f.read(header_size)

				# Parse the header
				collectors_info = parse_snap_header(header)

				# We can now read the content
				cursor_position = 0
				collector_index = 0
				buffer = f.read(buf_size*1024)
				while buffer:
					collector_type, offset = collectors_info[collector_index]
					if cursor_position <= offset < cursor_position + len(buffer):
						relative_offset = 0

						if cursor_position < offset:
							# go to the first byte of the collector
							cursor_position = offset
							relative_offset = cursor_position % buf_size*1024

						# we can read the collector
						# first byte should be the identifier of the collector class
						first_byte = buffer[relative_offset:relative_offset+1]
						if first_byte == collector_type:
							# we need to know the length of the collector so we can load it in the buffer and then import its data
							cursor_position += 1
							relative_offset += 1
							collector_size_len = VarInt.get_len(buffer[relative_offset:relative_offset+1])
							collector_size = VarInt.from_bytes(buffer[relative_offset:relative_offset+collector_size_len])
							cursor_position += collector_size_len
							relative_offset += collector_size_len
							while len(buffer) - relative_offset < collector_size:
								data = f.read(buf_size*1024)
								if data:
									buffer += data

							# we loaded all the necessary data for the collector, we can now build it with the imported data
							collector_class = modules.AVAILABLE_COLLECTORS.get_collector_by_type(collector_type)
							collector = collector_class()
							buffer = collector.import_bin(buffer[relative_offset:])
							collectors.append(collector)

							# update the cursor
							cursor_position += collector_size_len
							collector_index += 1

							#update the buffer by reading more
							data = f.read(buf_size*1024)
							if data:
								buffer += data
						else:
							# SHOULD never happen since the header lists the collectors in the correct order and the collectors themselve provide their id in the binary format.
							# Otherwize, the error resides in the header.
							raise IOError(f"Impossible to read {filename} because content and header do not match. (expected collector type = 0x{collector_type.hex()}, read = 0x{buffer.hex()})")
					elif cursor_position > offset:
						# SHOULD never happen since the header lists the collectors in the correct order. Otherwize, the error resides in the header.
						raise IOError(f"Failed to parse {filename} for some reason.")
					else:
						# for some reason, there is padding. SHOULD not happen unless explicitly introduced by a new module.
						buffer = f.read(buf_size*1024)
						cursor_position += buf_size*1024

		elif method == DB:
			if db:
				import sqlite3 as sql

				conn = sql.connect(db)
				cursor = conn.cursor()

				query = f"""SELECT collector_type FROM snapshots WHERE run_id=?"""
				request = cursor.execute(query, (run_id,))

				result = request.fetchall()

				if not result or result == []:
					return False

				for collector_type, *_ in result:
					collector_class = modules.AVAILABLE_COLLECTORS.get_collector_by_type(collector_type)
					collector = collector_class()
					collector.import_db(cursor, run_id)
					collectors.append(collector)

				conn.close()

			else:
				raise ValueError(f"No database path was set. Please provide a proper path.")

		else:
			raise ValueError(f"Import method {method} is unknown. please select a valid option between: 0 (BIN) for binary file data import or 1 (DB) for sqlite3 db data import")

		self.runs[run_id] = modules.CollectorList(collectors)
		return True

	def dump(self, run_id):
		"""
		Free the memory by dumping a run.

		Arguments:
			run_id (str): the run identifier.
		"""
		self.runs.pop(run_id, None)

	def dump_report(self, report_id):
		"""
		Free the memory by dumping a report.

		Arguments:
			report_id (str): the report identifier.
		"""
		self.diff_reports.pop(report_id, None)

	def pause_running(self):
		"""
		Pauses the running snapshot.
		"""
		pass

	def resume_running(self):
		"""
		Resume the paused snapshot.
		"""
		pass

	def quit_running(self):
		"""
		Stops the running snapshot before it ends. It drops all the collected data.
		"""
		pass

	def show_running_status(self):
		"""
		Get the status of the runnong snapshot and all its collectors.
		"""
		pass

	def add_collector(self, collector):
		"""
		Append a collector to the list of awaiting collectors before to run it.
		"""
		self.awaiting_collectors.append(collector)

	def run_snapshot(self, run_id):
		"""
		Runs collectors for a snapshot.

		Arguments:
			run_id (str): identifier of the snapshot.

		Raises:
			ValueError: No collector to be run in the list.
		"""
		running_snapshot = run_id

		threads = []

		# create the collectors
		if len(self.awaiting_collectors) == 0:
			raise ValueError("Not enough collectors to run a snapshot. You must provide at least one collector.")
		# add the run in the run list
		self.runs[run_id] = modules.CollectorList(self.awaiting_collectors)
		# run the collectors
		for collector in self.awaiting_collectors:
			t = threading.Thread(target = collector.run, args = ())
			threads.append(t)
		for t in threads:
			t.start()

		#wait for the collector to finish collecting the data
		for t in threads:
			t.join()

		running_snapshot = None

	def make_diff(self, first_run, second_run, report_id = None):
		"""
		Analyze the difference between two snapshots.

		Arguments:
			first_run (str): run_id of the first run to compare.
			second_run (str): run_id of the second run to compare.
			report_id (str): identifies the report. (default: None; if None, then combines the first and second snapshot id's)
		"""
		if first_run not in self.runs.keys() :
			raise ValueError(f"{first_run} is not loaded in the Snapshot Manager. Please check this is a valid id then try to load it beafore trying to make the difference with another snapshot.")
		elif second_run not in self.runs.keys():
			raise ValueError(f"{second_run} is not loaded in the Snapshot Manager. Please check this is a valid id then try to load it beafore trying to make the difference with another snapshot.")

		if report_id:
			if report_id in self.diff_reports.keys():
				raise ValueError(f"{report_id} already exist. please try to use another id or dump the existing report.")
		else:
			report_id = first_run + " vs " + second_run

		run_a = self.runs[first_run]
		run_b = self.runs[second_run]

		# get the names of the collectors that are in one snapshot but not on the other
		unique_collectors_a, unique_collectors_b = modules.CollectorList.XOR(run_a, run_b)
		# get the names of the collectors that are in both snapshots
		same_collectors = modules.CollectorList.AND(run_a, run_b)

		diff_report = DiffReport(first_run, second_run)
		self.diff_reports[report_id] = diff_report

		if len(unique_collectors_a) > 0:
			# The collector was run on the first snapshot but not on the second one.
			for collector_name in unique_collectors_a:
				c = run_a.get_collector_by_name(collector_name)
				collector_class = modules.AVAILABLE_COLLECTORS.get_collector_by_type(c.snapshot_elemnt_id)
				collector_class.make_diff(first_run, second_run, c, None, diff_report)

		if len(unique_collectors_b) > 0:
			# The collector was run on the second snapshot but not on the first one.
			for collector_name in unique_collectors_b:
				c = run_b.get_collector_by_name(collector_name)
				collector_class = modules.AVAILABLE_COLLECTORS.get_collector_by_type(c.snapshot_elemnt_id)
				collector_class.make_diff(first_run, second_run, None, c, diff_report)


		if len(same_collectors) > 0:
			# Make the diff between the collectors that are in both snapshots
			for collector_name in same_collectors:
				c1 = run_a.get_collector_by_name(collector_name)
				c2 = run_b.get_collector_by_name(collector_name)
				if not c1 == c2: # if the hashes do not match, we can make a diff!
					collector_class = modules.AVAILABLE_COLLECTORS.get_collector_by_type(c1.snapshot_elemnt_id)
					collector_class.make_diff(first_run, second_run, c1, c2, diff_report)
				else: # there was no differences between those two collecors so we simply add the name of the collector in the report without any data related to it.
					# doing so helps to read the report so we know the collector was run in both snapshots.
					diff_report.add_no_diff_collector(collector_name)

	def export_report(self, report_id, method = BIN, db = None, buf_size = 64):
		"""
		Export a report.

		Arguments:
			report_id (str): identifier of the report.
			method (int): the method used to export the data (binary: 0, sqlite3 db: 1). (default = BIN = 0)
			db (str): path to the database. (MUST be used ONLY if method is set to 1 (DB), default = None)
			buf_size (int): buffer size in kB used while writing a rpt file.. (default = 64)

		Returns:
			True if the export succeeded, False otherwize.

		Raises:
			ValueError: unknown method provided.
			ValueError: method is set to 1 (DB) but no path to the database provided.
		"""
		filename = os.path.join(os.path.dirname(__file__), f"../../reports/{report_id}.rpt")

		if method == BIN:
			header, report = self.diff_reports[report_id].to_bytes()
			header = VarInt.to_bytes(len(header)) + header
			with open(filename, "wb") as f:
				f.write(header)
				f.write(report)

		elif method == DB:
			if db:
				self.diff_reports[report_id].export_db(report_id, db)

			else:
				raise ValueError(f"No database path was set. Please provide a proper path.")

		else:
			raise ValueError(f"Export method {method} is unknown. please select a valid option between: 0 (BIN) for binary file data export or 1 (DB) for sqlite3 db data export")

		return True

	def import_report(self, report_id, method = BIN, db = None, buf_size = 64):
		"""
		import a report.

		Arguments:
			report_id (str): identifier of the report.
			method (int): the method used to export the data (binary: 0, sqlite3 db: 1). (default = BIN = 0)
			db (str): path to the database. (MUST be used ONLY if method is set to 1 (DB), default = None)
			buf_size (int): buffer size in kB used while reading a rpt file. (default = 64)

		Returns:
			True if the loading was successful, False if it has already been loaded.

		Raises:
			ValueError: unknown method provided.
			ValueError: method is set to 1 (DB) but no path to the database provided.
			FileNotFoundError: incorrect path to the file (based on the run_id).
			IOError: unexpected bytes at the end of the file.
		"""
		if report_id in self.diff_reports.keys():
			return False

		if method == BIN:
			filename = fn = os.path.join(os.path.dirname(__file__), f"../../reports/{report_id}.rpt")
			threads = []
			with open(filename, "rb") as f:
				# Read the header
				data = f.read(1)
				header_size_len = VarInt.get_len(data)
				data += f.read(header_size_len-1)
				header_size = VarInt.from_bytes(data)

				header = f.read(header_size)

				# Parse the header
				run_ids, collectors_info = parse_rpt_header(header)

				diff_report = DiffReport(run_ids[0], run_ids[1])

				# We can now read the content
				cursor_position = 0
				collector_index = 0
				buffer = f.read(buf_size*1024)
				while buffer:
					collector_type, offset = collectors_info[collector_index]
					if cursor_position <= offset < cursor_position + len(buffer):
						relative_offset = 0 # relative index of the cursor in the buffer

						if cursor_position < offset:
							# go to the first byte of the collector
							cursor_position = offset
							relative_offset = cursor_position % buf_size*1024

						if collector_index < len(collectors_info)-1:
							_, next_offset = collectors_info[collector_index+1]
							collector_len = next_offset - offset
							while len(buffer) < collector_len + relative_offset:
								data = f.read(buf_size*1024)
								if data:
									buffer += data

							t = tools.ResultThread(target = diff_report.read_collector_from_bytes, args = (buffer[relative_offset: relative_offset + collector_len], run_ids, modules.AVAILABLE_COLLECTORS.get_collector_by_type(collector_type)))
							threads.append(t)
							t.start()
							# diff_report.read_collector_from_bytes(buffer[relative_offset: relative_offset + collector_len], run_ids, modules.AVAILABLE_COLLECTORS.get_collector_by_type(collector_type))

							# update the buffer since we do not need those bytes anymore
							buffer = buffer[relative_offset + collector_len:]
							# update the cursors
							cursor_position += collector_len
							collector_index += 1

							#update the buffer by reading more
							data = f.read(buf_size*1024)
							if data:
								buffer += data

						else:
							read_data = f.read(buf_size*1024)
							while read_data:
								buffer += read_data

							collector_len = len(buffer) - relative_offset

							t = tools.ResultThread(target = diff_report.read_collector_from_bytes, args = (buffer[relative_offset: relative_offset + collector_len], run_ids, modules.AVAILABLE_COLLECTORS.get_collector_by_type(collector_type)))
							threads.append(t)
							t.start()
							# diff_report.read_collector_from_bytes(buffer[relative_offset: relative_offset + collector_len], run_ids, modules.AVAILABLE_COLLECTORS.get_collector_by_type(collector_type))

							# update the cursors
							cursor_position += collector_len
							collector_index += 1

							# update the buffer since we do not need those bytes anymore
							buffer = buffer[relative_offset + collector_len:]
							if buffer == b"":
								buffer = None
							else:
								raise IOError(f"Unexpected bytes at the end of the file. (from byte number {cursor_position} untill the EOF)")

					elif cursor_position > offset:
						# SHOULD never happen since the header lists the collectors in the correct order. Otherwize, the error resides in the header.
						raise IOError(f"Failed to parse {filename} for some reason.")

					else:
						# for some reason, there is padding. SHOULD not happen unless explicitly introduced by a new module.
						buffer = f.read(buf_size*1024)
						cursor_position += buf_size*1024

				for t in threads:
					t.join()

				for t in threads:
					if not t.result:
						return False

		elif method == DB:
			if db:
				import sqlite3 as sql

				conn = sql.connect(db)
				cursor = conn.cursor()

				query = f"""SELECT run_id_a, run_id_b FROM reports WHERE report_id=?"""
				request = cursor.execute(query, (report_id,))

				result = request.fetchone()

				if not result or result == () :
					return False

				run_id_a, run_id_b = result
				diff_report = DiffReport(run_id_a, run_id_b)

				# For every collector that were compared in te report, import the data
				query = f"""SELECT collector_type FROM reports_collectors WHERE report_id=?"""
				request = cursor.execute(query, (report_id,))

				collectors_type = request.fetchall()

				# for every collector, recover its class and import report data relative to the collectibles it collected
				for collector_type, *_ in collectors_type:
					collector_class = modules.AVAILABLE_COLLECTORS.get_collector_by_type(collector_type)

					collector_class.import_diff_from_report_db(cursor, report_id, [run_id_a, run_id_b], diff_report)

				conn.close()

			else:
				raise ValueError(f"No database path was set. Please provide a proper path.")

		else:
			raise ValueError(f"Export method {method} is unknown. please select a valid option between: 0 (BIN) for binary file data export or 1 (DB) for sqlite3 db data export")

		self.diff_reports[report_id] = diff_report
		return True



"""

		def terminal():
			paused = False
			while running_snapshot:
				if not paused:
					user_input = input("\rSnapshot is running ... (p|s|q|h)")
					if user_input.lower() == "p" or user_input.lower() == "pause":
						paused = True
						# MAKE THE COLLECTORS PAUSE
						pass
					elif user_input.lower() == "h" or user_input.lower() == "help":
						print(\"""
							p(ause)\tpause the running snapshot.
							s(how)\tshow the status of the running snapshot and its collectors.
							q(uit)\tstop and quit the running snapshot.
							h(elp)\tshow this help message.
							\""")
				else:
					user_input = input("\rSnapshot paused ... (r|s|q|h)")
					if user_input.lower() == "r" or user_input.lower() == "resume":
						paused = False
						# MAKE THE COLLECTORS PAUSE
						pass
					elif user_input.lower() == "h" or user_input.lower() == "help":
						print(\"""
							r(esume)\tresume the paused snapshot.
							s(how)\tshow the status of the running snapshot and its collectors.
							q(uit)\tstop and quit the running snapshot.
							h(elp)\tshow this help message.
							\""")

				if user_input.lower() == "s" or user_input.lower() == "show":
					#show the status for every collector
					pass
				elif user_input.lower() == "q" or user_input.lower() == "quit":
					user_input = input("Are you sure you want to quit the snapshot? (if yes, collected data will not be saved and therefore will be lost) [Y(es)|N(o)] ")
					if user_input == "" or user_input.lower() == "y" or user_input.lower() == "yes":
						# stop the analysis
						pass
						running_snapshot == False
					# elif user_input == "n" or user_input.lower() == "no":
					# 	pass

"""