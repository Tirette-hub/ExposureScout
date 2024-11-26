#!/usr/bin/python3
#coding:utf-8

"""
Authors:
Nathan Amorison

Version:
0.2.0
"""

HEADER = """


oooooooooooo                                                                                .oooooo..o                                     .   
`888'     `8                                                                               d8P'    `Y8                                   .o8   
 888         oooo    ooo oo.ooooo.   .ooooo.   .oooo.o oooo  oooo  oooo d8b  .ooooo.       Y88bo.       .ooooo.   .ooooo.  oooo  oooo  .o888oo 
 888oooo8     `88b..8P'   888' `88b d88' `88b d88(  "8 `888  `888  `888""8P d88' `88b       `"Y8888o.  d88' `"Y8 d88' `88b `888  `888    888   
 888    "       Y888'     888   888 888   888 `"Y88b.   888   888   888     888ooo888           `"Y88b 888       888   888  888   888    888   
 888       o  .o8"'88b    888   888 888   888 o.  )88b  888   888   888     888    .o      oo     .d8P 888   .o8 888   888  888   888    888 . 
o888ooooood8 o88'   888o  888bod8P' `Y8bod8P' 8""888P'  `V88V"V8P' d888b    `Y8bod8P'      8""88888P'  `Y8bod8P' `Y8bod8P'  `V88V"V8P'   "888" 
                          888                                                                                                                  
                         o888o                                                                                                                 
                                                                                                                                               


"""

from exposurescout import modules
from exposurescout import core

from multiprocessing import Process
from datetime import datetime
import time
import os

START=0
SNAP=1
DIFF=2
MEM=3
MEM_INSPECT = 4
RUN=5


class Application:
	def __init__(self):
		self.quit = False
		self.state = START
		self.manager = core.AnalysisManager()
		self.collectors = modules.CollectorList()

	def menu(self):
		if self.state==START:
			print(f"You currently have {len(self.manager.runs)} snapshots and {len(self.manager.diff_reports)} diff reports in memory.")
			print("1. Open GUI app")
			print("2. Run snapshot")
			print("3. Compare two snapshots")
			print("4. Manage Memory of the Analysis Manager")
			print("5. Quit")

		elif self.state==SNAP:
			print("Select a collector that will be used for your snapshot or launch the one you selected.")
			for i, c in enumerate(modules.AVAILABLE_COLLECTORS, 1):
				print(f"{i}. {c.name}")

			print(f"{i+1}. Show already selected collectors")
			print(f"{i+2}. Run the snapshot with the given set")
			print(f"{i+3}. Return to menu")
			print(f"{i+4}. Quit")

		elif self.state==DIFF:
			print("Select a collector that will be used for your diff.")
			for i, s in enumerate(self.manager.runs.keys(), 1):
				print(f"{i}. {s}")

			print(f"{i+1}. Show already selected snapshot")
			print(f"{i+2}. Return to menu")
			print(f"{i+3}. Quit")


		elif self.state==MEM:
			print(f"You currently have {len(self.manager.runs)} snapshots and {len(self.manager.diff_reports)} diff reports in memory.")
			print(f"1. Show loaded snapshots")
			print(f"2. Show loaded reports")
			print(f"3. Import snapshot")
			print(f"4. Export snapshot")
			print(f"5. Import report")
			print(f"6. Export report")
			print(f"7. Dump snapshot")
			print(f"8. Dump report")
			print(f"9. Return to menu")
			print(f"10. Quit")

		elif self.state==MEM_INSPECT:
			print("Select the report")
			i=0
			for i, r in enumerate(self.manager.diff_reports.keys(), 1):
				print(f"{i}. {r}")

			print(f"{i+1}. Return to menu")
			print(f"{i+2}. Quit")

		elif self.state==RUN:
			print("WIP")

		else:
			raise ValueError(f"Unknown state provided ({self.state}).")

	def run(self):
		print(HEADER)
		print("Welcome to Exposure Scout. (https://github.com/Tirette-hub/ExposureScout)")

		while not self.quit:
			self.menu()
			try:
				i = int(input("Choose an action index: "))
				print()
			except ValueError:
				print("Please use only integer values!")
				continue

			if self.state == START:
				if i < 1 or i > 5:
					print("Please enter value proposed by the application.")
					print()
					continue

				elif i == 1:
					from exposurescout import gui
					app = Process(target = gui.GUIApp(am = self.manager).mainloop)
					self.quit = True
					app.start()
					print("WIP")
					print()

				elif i == 2:
					self.state = SNAP
					self.temp_list = modules.AVAILABLE_COLLECTORS

				elif i == 3:
					if len(self.manager.runs) < 2:
						print(f"Not enough runs have been loaded. At least 2 snapshots must be loaded, you currently have only {len(self.manager.runs)}.")
					else:
						self.temp_list = []
						self.state = DIFF

				elif i == 4:
					self.state = MEM

				elif i == 5:
					self.quit = True

			elif self.state == SNAP:
				if i < 1 or i > len(modules.AVAILABLE_COLLECTORS)+4:
					print("Please enter value proposed by the application.")
					print()
					continue

				elif i < len(modules.AVAILABLE_COLLECTORS)+1:
					c = modules.AVAILABLE_COLLECTORS[i-1]
					if c.name in self.collectors:
						print("This collector has already been added to the list.")
					else:
						collector = c()
						if c.name == "File System Collector":
							collector.set_rule("/dev")
							collector.set_rule("/home")
							collector.set_rule("/media")
							collector.set_rule("/mnt")
							collector.set_rule("/opt")
							collector.set_rule("/srv")
							# collector.set_rule("/sys")
							collector.set_rule("/usr")
							collector.set_rule("/var")

							collector.set_rule("/var/run", exclude=True)
							#collector.set_rule("/sys/block", exclude=True)

						self.collectors.append(c)
						self.manager.add_collector(collector)
						print("Adding this collector to the list.")

					print()

				elif i == len(modules.AVAILABLE_COLLECTORS)+1:
					print("[" + ",".join(list(c.name for c in self.collectors)) + "]")
					print()

				elif i == len(modules.AVAILABLE_COLLECTORS)+2:
					if len(self.collectors) == 0:
						print("Please provide at least one collector for the snapshot to run.")
						print()
					else:
						print("Snapshot will run with: ", "[" + ",".join(list(c.name for c in self.collectors)) + "]")
						snap_run = input("How do you want to name this run (default=date)? ")
						if snap_run == "":
							snap_run = str(datetime.now())

						self.manager.run_snapshot(snap_run)
						self.collectors = []

						pt_num = 0
						while self.manager.is_running():
							print(f"\rRunning snapshot{'.'*(pt_num+1)}", end="")
							time.sleep(1)
							pt_num += 1

						print("Job done.")
						print()
						self.temp_list = []
						self.collectors = []
						self.state = START

				elif i == len(modules.AVAILABLE_COLLECTORS)+3:
					self.temp_list = []
					self.collectors = []
					self.state = START

				elif i == len(modules.AVAILABLE_COLLECTORS)+4:
					self.quit = True

			elif self.state == DIFF:
				if i < 1 or i > len(self.manager.runs)+3:
					print("Please enter value proposed by the application.")
					print()
					continue

				elif i < len(self.manager.runs)+1:
					if len(self.temp_list) < 2:
						self.temp_list.append(list(self.manager.runs.keys())[i-1])

					if len(self.temp_list) == 2:
						report_id = input("How do you want to name this report (default='run_id1 vs run_id2')? ")
						if report_id == "":
							report_id = None

						self.manager.make_diff(self.temp_list[0], self.temp_list[1], report_id = report_id)

						self.state = START
						self.temp_list = []

				elif i == len(self.manager.runs)+1:
					print(self.temp_list)
					print()

				elif i == len(self.manager.runs)+2:
					self.temp_list = []
					self.collectors = []
					self.state = START

				elif i == len(self.manager.runs)+3:
					self.quit = True

			elif self.state == MEM:
				if i < 1 or i > 10:
					print("Please enter value proposed by the application.")
					print()
					continue

				elif i == 1:
					print(f"You currently have {len(self.manager.runs)} snapshots in memory.")
					for run_id in self.manager.runs.keys():
						print(run_id)
					print()

				elif i == 2:
					print(f"You currently have {len(self.manager.diff_reports)} diff reports in memory.")
					self.state = MEM_INSPECT

				elif i == 3:
					files = [f for f in os.listdir("reports/") if f.endswith(".snap")]
					print("Select the snapshot to load")

					n = 0
					for n, f in enumerate(files, 1):
						print(f"{n}. {f}")

					print(f"{n+1}. Return to menu")
					print(f"{n+2}. Quit")

					stop = False
					while not stop:
						try:
							val = int(input("Choose the file index: "))
							if val < 1 or val > len(files)+2:
								raise ValueError("Value not in range.")
						except ValueError:
							print("Please use only integer values provided just above!")
							continue

						stop = True

						if val < len(files)+1:
							self.manager.load(files[val-1][:-5])
							self.state = START
							print()

						elif val == len(files)+1:
							self.state = START

						elif val == len(files)+2:
							self.quit = True

				elif i == 4:
					if len(self.manager.runs) > 0:
						print("Select the snapshot to save")

						n = 0
						for n, s in enumerate(self.manager.runs.keys(), 1):
							print(f"{n}. {s}")

						print(f"{n+1}. Return to menu")
						print(f"{n+2}. Quit")

						stop = False
						while not stop:
							try:
								val = int(input("Choose the snapshot index: "))
								if val < 1 or val > len(self.manager.runs.keys())+2:
									raise ValueError("Value not in range.")
							except ValueError:
								print("Please use only integer values provided just above!")
								continue

							stop = True

							if val < len(self.manager.runs.keys())+1:
								self.manager.save(list(self.manager.runs.keys())[val-1])
								self.state = START
								print()

							elif val == len(self.manager.runs.keys())+1:
								self.state = START

							elif val == len(self.manager.runs.keys())+2:
								self.quit = True

					else:
						print("You should have at least one snapshot saved to be able to save it. You currently have none.\n")

				elif i == 5:
					files = [f for f in os.listdir("reports/") if f.endswith(".rpt")]
					print("Select the report to load")

					n = 0
					for n, f in enumerate(files, 1):
						print(f"{n}. {f}")

					print(f"{n+1}. Return to menu")
					print(f"{n+2}. Quit")

					stop = False
					while not stop:
						try:
							val = int(input("Choose the file index: "))
							if val < 1 or val > len(files)+2:
								raise ValueError("Value not in range.")
						except ValueError:
							print("Please use only integer values provided just above!")
							continue

						stop = True

						if val < len(files)+1:
							self.manager.import_report(files[val-1][:-4])
							self.state = START
							print()

						elif val == len(files)+1:
							self.state = START

						elif val == len(files)+2:
							self.quit = True

				elif i == 6:
					if len(self.manager.diff_reports) > 0:
						print("Select the report to save")

						n = 0
						for n, s in enumerate(self.manager.diff_reports.keys(), 1):
							print(f"{n}. {s}")

						print(f"{n+1}. Return to menu")
						print(f"{n+2}. Quit")

						stop = False
						while not stop:
							try:
								val = int(input("Choose the report index: "))
								if val < 1 or val > len(self.manager.diff_reports.keys())+2:
									raise ValueError("Value not in range.")
							except ValueError:
								print("Please use only integer values provided just above!")
								continue

							stop = True

							if val < len(self.manager.diff_reports.keys())+1:
								self.manager.export_report(list(self.manager.diff_reports.keys())[val-1])
								self.state = START
								print()

							elif val == len(self.manager.diff_reports.keys())+1:
								self.state = START

							elif val == len(self.manager.diff_reports.keys())+2:
								self.quit = True

					else:
						print("You should have at least one report saved to be able to save it. You currently have none.\n")

				elif i == 7:
					if len(self.manager.runs) > 0:
						print("Select the snapshot to dump")


						n = 0
						for n, s in enumerate(self.manager.runs.keys(), 1):
							print(f"{n}. {s}")

						print(f"{n+1}. Return to menu")
						print(f"{n+2}. Quit")

						stop = False
						while not stop:
							try:
								val = int(input("Choose the snapshot index: "))
								if val < 1 or val > len(self.manager.runs.keys())+2:
									raise ValueError("Value not in range.")
							except ValueError:
								print("Please use only integer values provided just above!")
								continue

							stop = True

							if val < len(self.manager.runs.keys())+1:
								self.manager.dump(list(self.manager.runs.keys())[val-1])
								self.state = START
								print()

							elif val == len(self.manager.runs.keys())+1:
								self.state = START

							elif val == len(self.manager.runs.keys())+2:
								self.quit = True

					else:
						print("You should have at least one snapshot saved to be able to save it. You currently have none.\n")

				elif i == 8:
					if len(self.manager.diff_reports) > 0:
						print("Select the report to dump")

						n = 0
						for n, s in enumerate(self.manager.diff_reports.keys(), 1):
							print(f"{n}. {s}")

						print(f"{n+1}. Return to menu")
						print(f"{n+2}. Quit")

						stop = False
						while not stop:
							try:
								val = int(input("Choose the report index: "))
								if val < 1 or val > len(self.manager.diff_reports.keys())+2:
									raise ValueError("Value not in range.")
							except ValueError:
								print("Please use only integer values provided just above!")
								continue

							stop = True

							if val < len(self.manager.diff_reports.keys())+1:
								self.manager.dump_report(list(self.manager.diff_reports.keys())[val-1])
								self.state = START
								print()

							elif val == len(self.manager.diff_reports.keys())+1:
								self.state = START

							elif val == len(self.manager.diff_reports.keys())+2:
								self.quit = True

					else:
						print("You should have at least one report saved to be able to save it. You currently have none.\n")

				elif i == 9:
					self.state = START

				elif i == 10:
					self.quit = True

			elif self.state == MEM_INSPECT:
				if i < 1 or i > len(self.manager.diff_reports.keys())+2:
					print("Please enter a value proposed by the application.")
					print()
					continue

				elif i < len(self.manager.diff_reports.keys())+1:
					print(self.manager.diff_reports[list(self.manager.diff_reports.keys())[i-1]])
					print()
					self.state = START

				elif i == len(self.manager.diff_reports.keys())+1:
					self.state = START

				elif i == len(self.manager.diff_reports.keys())+2:
					self.quit = True

			else:
				print("Unknown command. Soft quit.")
				self.quit = True

			if self.quit == True:
				if len(self.manager.runs) > 0 or len(self.manager.diff_reports) > 0:
					val = input("You still have loaded snapshots or reports. Are you sure you want to leave? If you did not save them, they will be forever lost. [Yes|No] ")
					if val.lower() != "yes" and val.lower() != "y":
						self.quit = False
						print()
						continue

				print("Goodbye!")

if __name__ == '__main__':
	app = Application()
	app.run()
	os._exit(0)