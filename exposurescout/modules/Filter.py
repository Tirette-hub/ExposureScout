#!/usr/bin/python3
#coding:utf-8

"""
Filter Module that enhance easier searching in and manipulation of a report or a snapshot.

Authors:
Nathan Amorison

Version:
0.2.0
"""

import re

class Level:
	def __init__(self, id):
		self.id = id

	def __eq__(self, o):
		if type(o) != type(self):
			return False

		if self.id == o.id:
			return True

		return False

class CollectorLevel(Level):
	def __init__(self):
		super(CollectorLevel, self).__init__(0)

class ElementLevel(Level):
	def __init__(self):
		super(CollectorLevel, self).__init__(1)

class RuleType:
	def __init__(self, id):
		self.id = id

	def __eq__(self, o):
		if type(o) != type(self):
			return False

		if self.id == o.id:
			return True

		return False

class Include(RuleType):
	def __init__(self):
		super(Include, self).__init__(0)

class Exclude(RuleType):
	def __init__(self):
		super(Exclude, self).__init__(1)

class Rule:
	"""
	Regular expression rule used by filters.

	Arguments:
		rule_type (RuleType): type of behavior to use when applying this rule (can be either include or exclude).
		element_name (str): name of the element on which the rule will be applied on (can be either a collector name or a collectible name).
		rule (str): regular expression to use as filter.
	"""
	def __init__(self, rule_type, element_name, rule):
		self.rule_type = rule_type
		self.element_name = element_name
		self.rule = rule

	def __eq__(self, o):
		if type(o) != Rule:
			return False

		if self.element_name == o.element_name:
			if self.rule == o.rule:
				return True

		return False

class Filter:
	"""
	Filter object that will contain all the rules to apply for filtering.

	Attributes:
		rules (dict{Level:list[Rule]}): list of rules that will be applied
	"""
	def __init__(self):
		self.rules = {}

	def __eq__(self, o):
		if type(o) != Filter:
			return False

		if self.rules == o.rules:
			return True

		return False

	def reset(self):
		"""
		Remove all the filters.
		"""
		self.rules = {}

	def add_rule(self, level, rule):
		"""
		Add a rule to the set of rules
		"""
		if level in self.rules.keys():
			self.rules[level].append(rule)
		else:
			self.rules[level] = [rule]

	def apply_on_report(self, report):
		"""
		Apply the filter to the given report.
		"""
		pass

	def apply_on_collector(self, collector):
		"""
		Apply the filter to the given collector.
		"""
		pass
