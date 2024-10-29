#!/usr/bin/python3
#coding:utf-8

"""
Authors:
Nathan Amorison

Version:
0.1.0
"""


#ADD YOUR OWN NEW MODULES HERE
from .UsersCollector import LinUsersCollector, User, Group, Sudoer
from .Collector import RunningError, FormattingError, AbstractMethodException
from .FileSystemCollector import LinFileSystemCollector, File, Directory

from ..core.tools import xor_list, and_list


class CollectorList:
	"""
	"""
	def __init__(self, collectors = []):
		self.collectors = collectors
		self.names = list(c.name for c in self.collectors)
		self.types = list(c.snapshot_elemnt_id for c in self.collectors)

	def __iter__(self):
		self.index = 0
		return self

	def __next__(self):
		if self.index < len(self.collectors):
			result = self.collectors[self.index]
			self.index += 1
			return result
		else:
			raise StopIteration

	def __getitem__(self, item):
		return self.collectors[item]

	def append(self, collector):
		"""
		Append a collector to the list.

		Arguments:
			collector (Collector): the collector to append in the list.
		"""
		self.collectors.append(collector)
		self.names.append(collector.name)

	def get_collector_by_name(self, name):
		"""
		Get the collector by its name.

		Arguments:
			name (str): name of the collector.

		Returns:
			The Collector.
		"""
		index = self.names.index(name)

		return self.collectors[index]

	def get_collector_by_type(self, type):
		index = self.types.index(type)

		return self.collectors[index]

	def XOR(a, b):
		"""
		Make the disjunction (by their names) between 2 list of collectors.

		Arguments:
			a (CollectorList): the first list to compare with.
			b (CollectorList): the second list to compare with.

		Returns:
			A list of the different collectors name.
		"""
		return xor_list(a.names, b.names)

	def AND(a, b):
		"""
		Make the junction (by their names) between 2 list of collectors.

		Arguments:
			a (CollectorList): the first list to compare with.
			b (CollectorList): the second list to compare with.

		Returns:
			A list of the same collectors name.
		"""
		return and_list(a.names, b.names)

#DON'T FORGET TO ADD YOUR MODULE IN THE AVAILABLE MODULES LIST
AVAILABLE_COLLECTORS = CollectorList([
	LinUsersCollector,
	LinFileSystemCollector,
	])
#we could set a rule here if we want to be cross platform to only set the available modules for a specific platform
#e.g. LinUsersCollector is Linux oriented but we could create a WinUsersCollector and depending on the platform we are running on, the available module would be one or the other.
