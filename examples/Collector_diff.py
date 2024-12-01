#!/usr/bin/python3
#coding:utf-8

"""
This is a simple example on how to run a diff on a collector.

Authors:
Nathan Amorison

Version:
0.3.1
"""
from exposurescout.modules import LinUsersCollector, User, Group, Sudoer
from exposurescout.core import DiffReport
from exposurescout import modules

def main():
	uc_a = LinUsersCollector()
	uc_b = LinUsersCollector()

	# Run two collectors to represent a snapshot (should be the same collected data)
	uc_a.run()
	uc_b.run()

	# hardcode differences
	new_user = User(1001, "test", [1000])
	new_group = Group(1001, "test")
	new_sudoer = Sudoer(1001)

	uc_b.raw_result[User.element_name].append(new_user)
	uc_b.raw_result[Group.element_name].append(new_group)
	uc_b.raw_result[Sudoer.element_name].append(new_sudoer)

	run_id_a = "test_a"
	run_id_b = "test_b"

	# initialise the report between the two snapshots
	diff_report_a = DiffReport(run_id_a, run_id_b)
	#diff_report_b = report.DiffReport(run_id_a, run_id_b)

	# make the difference between the two collectors
	LinUsersCollector.make_diff(run_id_a, run_id_b, uc_a, uc_b, diff_report_a)
	#LinUsersCollector.make_diff(run_id_a, run_id_b, uc_a, None, diff_report_a)
	#LinUsersCollector.make_diff(run_id_a, run_id_b, None, uc_b, diff_report_b)

	# print the result
	print(diff_report_a)


if __name__ == '__main__':
	main()