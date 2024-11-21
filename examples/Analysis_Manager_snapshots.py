#!/usr/bin/python3
#coding:utf-8

"""
This is an example on how to run, export, import and dump snapshots from within the Analysis Manager.

Authors:
Nathan Amorison

Version:
0.2.0
"""
from exposurescout.core import AnalysisManager
from exposurescout import modules

def main():
	manager = AnalysisManager()

	run_id = "test" # str(datetime.now())

	manager.add_collector(modules.LinUsersCollector())
	# fscollector = modules.LinFileSystemCollector()
	# fscollector.set_rule("/home")
	# fscollector.set_rule("/home/test/", exclude=True)
	# manager.add_collector(fscollector)

	result = manager.run_snapshot(run_id)

	while manager.is_running():
		pass

	result = manager.save(run_id)
	if result:
		print("Snapshot exported successfuly.")

		manager.dump(run_id)
		print("Snapshot dumped successfuly.")

		manager.load(run_id)
		print("Snapshot loaded successfuly.")

		print(manager.runs[run_id][0])

	else:
		print("Failed to save.")

if __name__ == '__main__':
	main()