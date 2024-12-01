#!/usr/bin/python3
#coding:utf-8

"""
This is a simple example on how to run a diff with the Analysis Manager and export, import and dump reports.

Authors:
Nathan Amorison

Version:
0.3.1
"""
from exposurescout.core import AnalysisManager
from exposurescout import modules

def main():
	manager = AnalysisManager()

	run_id_a = "test_a" # str(datetime.now())
	run_id_b = "test_b"
	report_id = "test"

	# run two snapshots

	manager.add_collector(modules.LinUsersCollector())
	# fscollector = modules.LinFileSystemCollector()
	# fscollector.set_rule("/home")
	# fscollector.set_rule("/home/test/", exclude=True)
	# manager.add_collector(fscollector)

	manager.run_snapshot(run_id_a)

	while manager.is_running():
		pass


	manager.add_collector(modules.LinUsersCollector())
	# fscollector = modules.LinFileSystemCollector()
	# fscollector.set_rule("/home")
	# fscollector.set_rule("/home/test/", exclude=True)
	# manager.add_collector(fscollector)

	manager.run_snapshot(run_id_b)

	while manager.is_running():
		pass

	# hardcode differences (if you want to)

	# new_user = modules.User(1001, "test", [1001])
	# new_group = modules.Group(1001, "test")
	# new_sudoer = modules.Sudoer(1001)

	# manager.runs[run_id_b][0].raw_result[modules.User.element_name].append(new_user)
	# manager.runs[run_id_b][0].raw_result[modules.Group.element_name].append(new_group)
	# manager.runs[run_id_b][0].raw_result[modules.Sudoer.element_name].append(new_sudoer)
	# manager.runs[run_id_b][0].raw_result["passwd_hash"] = b""
	# manager.runs[run_id_b][0].raw_result["group_hash"] = b""

	# make the diff between the two snapshots
	manager.make_diff(run_id_a, run_id_b, report_id)

	result = manager.export_report(report_id)
	if result:
		print("Report exported successfuly.")

		manager.dump_report(report_id)
		print("Report dumped successfuly.")

		result = manager.import_report(report_id)

		if result:
			print("Report loaded successfuly.")
			print(manager.diff_reports)
		else:
			print("failed to load the report")

	else:
		print("Failed to save.")

if __name__ == '__main__':
	main()