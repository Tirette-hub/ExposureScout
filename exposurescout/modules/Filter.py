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

	def __init__(self, id, name):
		self.id = id
		self.name = name

	def __eq__(self, o):
		if type(o) != type(self):
			return False

		if self.id == o.id:
			return True

		return False

CollectorLevel = Level(0, "CollectorLevel")
ElementLevel = Level(1, "ElementLevel")

class Command:

	def __init__(self, id, name):
		self.id = id
		self.name = name

	def __repr__(self):
		return str(self)

	def __str__(self):
		return self.name

	def __eq__(self, o):
		if type(o) != type(self):
			return False

		if self.id == o.id:
			return True

		return False

Include = Command(0, "Include")
Exclude = Command(1, "Exclude")

class Rule:
	"""
	Regular expression rule used by filters.

	Arguments:
		level (Level): Level were the filter must stop. Either at Collector Level or at Element Level.
		collector (str): name of the collector concerned by the filter.
		element_name (str): name of the element on which the rule will be applied on (can be either a collector name or a collectible name).
		target (str): name of the attribute targeted by the rule.
		rule (rstr): regular expression to use as filter.
	"""
	def __init__(self, command, level, collector, element_name, target, rule):
		self.command = command
		self.level = level
		self.collector = collector
		self.element_name = element_name
		self.target = target
		self.rule = rule

	def __repr__(self):
		return str(self)

	def __str__(self):
		return f"<Rule: command={self.command.name}, element={self.element_name}, target=\"{self.target}\", rule={self.rule}>"

	def __eq__(self, o):
		if not isinstance(o, Rule):
			return False

		if self.command == o.command:
			if self.level == o.level:
				if self.collector == o.collector:
					if self.element_name == o.element_name:
						if self.target == o.target:
							if self.rule == o.rule:
								return True

		return False

	def run(self, o):
		"""
		Check if the rule applies to a given value.

		Arguments:
			o (dict{str:dict{str:list[DiffElement]}}): object on which to apply the rule.

		Returns:
			True if the value match with the given rule pattern, False otherwize.

		Raises:
			ValueError: provided object does not match the targeted attribute on which the filter rule must be applied.
		"""
		if hasattr(o, self.target):
			return re.match(self.rule, getattr(o, self.target))
		
		raise ValueError(f"Rule can not be applied: target not found.")

# class Include(Rule):
# 	def __init__(self, collector, element_name, target, rule):
# 		super(Include, self).__init__(collector, element_name, target, rule)

class Filter:
	"""
	Filter object that will contain all the rules to apply for filtering.

	Attributes:
		rules (dict{Level:list[Rule]}): list of rules that will be applied. NOTE: the order DOES matter.
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
		Add a rule to the set of rules. NOTE: the order DOES matter: the first set rule will be the first to be applied
		"""
		if level in self.rules.keys():
			self.rules[level].append(rule)
		else:
			self.rules[level] = [rule]

	def apply_on_report(self, report):
		"""
		Apply the filter to the given report.
		"""
		result = {}

		rules_level = self.rules.keys()
		
		# check for collectors
		if CollectorLevel in rules_level:
			for rule in self.rules[CollectorLevel]:
				for collector in report.diff_elemnts:
					verif = False
					try:
						verif = rule.run(collector)
					except ValueError as e:
						continue

					if verif:
						if rule.command == Include:
							if collector not in result.keys():
								result[collector] = report.diff_elemnts[collector]
							else:
								pass # should never happen

						elif rule.command == Exclude:
							if collector not in result.keys():
								pass
							else:
								result.pop(collector, None)

		if ElementLevel in rules_level:
			for rule in self.rules[ElementLevel]:
				pass

		return result

	def apply_on_collector(self, collector):
		"""
		Apply the filter to the given collector.
		"""
		result = {}
		
		for rule in self.rules:
			pass

		return result
