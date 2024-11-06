#!/usr/bin/python3
#coding:utf-8

"""
Authors:
Nathan Amorison

Version:
0.1.0
"""

import time

class AbstractMethodException(Exception):
	pass

class FormattingError(Exception):
	pass

class RunningError(Exception):
	pass

class ACollectible:
	"""
	Abstract class from which every collectible element of a Collector should derive.

	Attributes:
		element_name (str): name of the collectible.
	"""
	element_name = None

	def __init__(self):
		pass

	def to_bytes(self):
		"""
		Converts the collectible to a byte string used to store it. MUST always been rewritten for every new module.

		Returns:
			A bytes stream.
		"""
		raise AbstractMethodException("You should not use the abstracted class method in your module for to_bytes. Please implement it properly.")

	def from_bytes(data):
		"""
		Convert bytes into a Collectible. MUST always been rewritten for every new module.

		Arguments:
			data (bytes): a bytes stream begining with the encoded data of the collectible.

		Returns:
			A tupple containing: 1. the collectible data structure recovered from the bytes stream; 2. the rest of the unread bytes that are not part of this collectible data structure.
		"""
		raise AbstractMethodException("You should not use the abstracted class method in your module for from_bytes. Please implement it properly.")

	def export_report_db(self, report_id, run_id, status, db_cursor):
		"""
		Export a collectible data structure that is part of a diff report into the specified database.

		Arguments:
			report_id (str): identifer of the report the element is linked to.
			run_id (str): identifier of the snapshot run the element comes from.
			status (int): value of the element's status in the diff report (created, deleted, modified, ...).
			db_cursor (Cursor): sqlite3 cursor that points to the database.
		"""
		raise AbstractMethodException("You should not use the abstracted class method in your module for from_bytes. Please implement it properly.")

class ACollector:
	"""
	Abstract class from which every analysis/collector module should derive.

	Attributes:
		name (str): name of the Collector module.
		descr (str): description of what the module does and what it was created for.
		snapshot_elemnt_id (byte): byte used to identify the collector in the binary file.

		result (bytes): formated data collected by the collector so it can be exported. (default: None)
		raw_result (dict{str : ACollectible}): data collected by the collector before to be formated for export. (default: None)
		running (bool): flag repesenting whether the module is running or not. (default: None)
	"""
	name = None
	descr = None
	snapshot_elemnt_id = None

	def __init__(self):
		self.result = None
		self.raw_result = None
		self.running = False

	def __repr__(self):
		"""
		Gives an overview of the module.
		"""
		return f"""<Module {self.name}, status: {"running" if self.running else "not running"}, size: {len(self.raw_result) if self.raw_result else 0}>"""

	def is_running(self):
		"""
		Allows to check if the module is runing or not.

		Returns:
			True if the module is running, False otherwize.
		"""
		return self.running

	def help(self):
		"""
		Get the description of the module.

		Returns:
			The description of the module.
		"""
		return self.descr

	def _format(self):
		"""
		Private method to format raw collected data of a run to exportable data. MUST always been rewritten for every new module.
		"""
		raise AbstractMethodException("You should not use the abstracted class method in your module for _format. Please implement it properly.")

	def _export(self):
		"""
		Private method to export the result after running the module. SHOULD not be rewritten for every new module.
		"""
		if self.result:
			return self.result
		elif self.raw_result:
			raise FormattingError("Data have not been formatted to be exported.")
		elif self.running:
			raise RunningError("Module is still running, please wait until the end before trying to export the result.")
		else:
			raise RunningError("You should first run the module before to be able to export its result.")

	def export_bin(self):
		"""
		Public method to export the result after running the module. It is mainly used by the AnalysisManager of the "core" python project module.
		"""
		if self.running:
			raise RunningError("Module is still running, please wait until the end before trying to export the result.")

		self._format()
		return self._export()

	def _export_sql(self, db_cursor, run_id):
		"""
		Private method to export the result in a db after running the module. MUST be rewritten for every new module.
		"""
		raise AbstractMethodException("You should not use the abstracted class method in your module for _export_sql. Please implement it properly.")

	def export_db(self, db_cursor, run_id):
		"""
		Public method to export the result in a db after running the module. It is mainly used by the CollectorManager of the "core" python project module.
		"""
		if self.running:
			raise RunningError("Module is still running, please wait until the end before trying to export the result.")

		self._export_sql(db_cursor, run_id)

	def import_bin(self, data):
		"""
		Import method to recover data of a previous run. Those data can then be previewed.

		Arguments:
			data (bytes): raw data with the first bytes representing this collector.

		Returns:
			The rest of raw bytes unrelated to this collector.
		"""
		raise AbstractMethodException("You should not use the abstracted class method in your module for import_bin. Please implement it properly.")

	def import_db(self, db_cursor, run_id):
		"""
		Import method to recover data of a previous run stored in DB. Those data can then be previewed.
		Note: must already been connected to the database.

		Arguments:
			db_cursor (Cursor): pointer to the database.
			run_id (str): id used to store the collected data in the db of a specific run.
		"""
		raise AbstractMethodException("You should not use the abstracted class method in your module for import_db. Please implement it properly.")

	def _start_running(self):
		"""
		Private method used when starting the collector. SHOULD not be rewritten for every new module.
		"""
		self.running = True

	def _stop_running(self):
		"""
		Private method used when collector finished running. SHOULD not be rewritten for every new module.
		"""
		self.running = False

	def _run(self):
		"""
		Private method used to run the collector. MUST be rewritten for every new module since every module/collector works differently.
		"""
		raise AbstractMethodException("You should not use the abstracted class method in your module for run. Please implement it properly.")

	def run(self):
		"""
		Public method used to run the collector. It is mainly used by the CollectorManager of the "core" python project module.
		"""
		self._start_running()
		self._run()
		self._stop_running()

	def make_diff(run_id_a, run_id_b, a, b, report):
		"""
		Static method used to get the difference between two collectors of the same type. MUST be rewritten for every new module since every module/collecor works differently.

		Arguments:
			run_id_a (str): run_id of the first collector.
			run_id_b (str): run_id of the second collector.
			a (Collector): one of the collectors.
			b (Collector): the other collector.
			report (DiffReport): the report where to add the differences.
		"""
		raise AbstractMethodException("You should not use the abstracted class method in your module for make_diff. Please implement it properly.")

	def import_diff_from_report(data, run_ids, report):
		"""
		Static method used to import the values of report that are related to a given collector from a bin file. MUST be rewritten for every new module since every module/collecor works differently.

		Arguments:
			data (bytes): a bytes stream representing the elements associated to this collector in the report.
			run_ids (list[str]): the ordered list of the snapshot ids from which come the report elements.
			report (DiffReport): datastructure in which to store the recovered data.
		"""
		raise AbstractMethodException("You should not use the abstracted class method in your module for import_diff_from_report. Please implement it properly.")

	def import_diff_from_report_db(db_cursor, run_ids, report):
		"""
		Static method used to import the values of report that are related to a given collector from a database. MUST be rewritten for every new module since every module/collecor works differently.

		Arguments:
			db_cursor (Cursor): pointer to the database.
			run_ids (list[str]): the ordered list of the snapshot ids from which come the report elements.
			report (DiffReport): datastructure in which to store the recovered data.
		"""
		raise AbstractMethodException("You should not use the abstracted class method in your module for import_diff_from_report_db. Please implement it properly.")

	def get_report_tree_structure():
		"""
		Get the structure of the Collector used for the report. MUST be rewritten for every new module since every module/collecor works differently.
		"""
		raise AbstractMethodException("You should not use the abstracted class method in your module for get_report_tree_structure. Please implement it properly.")

	def create_report_tables(db_cursor):
		"""
		Static method used to create the different tables used by this collector for report structure in the specified database.
		Note: modifications are not committed here. MUST be rewritten for every new module since every module/collecor works differently.

		Arguments:
			db_cursor (Cursor): sqlite3 cursor pointing to the database in which the tables must be created.
		"""
		raise AbstractMethodException("You should not use the abstracted class method in your module for create_report_tables. Please implement it properly.")