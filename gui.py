#!/usr/bin/python3
#coding:utf-8

"""
Authors:
Nathan Amorison

Version:
0.3.0
"""

from exposurescout.core import AnalysisManager
from exposurescout import modules

import tkinter as tk
from tkinter import ttk

import os

def on_help(url):
	import webbrowser
	webbrowser.open(url)

def get_status_by_id(status):
	if status == 0:
		return "Created"
	elif status == 1:
		return "Deleted"
	elif status == 2:
		return "Modified"
	elif status == 3:
		return "Unknown"
	else:
		return ValueError(f"Unknow status id {status}.")

class GUIApp(tk.Tk):
	def __init__(self, *args, am = AnalysisManager(),**kwargs):
		super(GUIApp, self).__init__(*args, **kwargs)
		self.manager = am
		self.minsize(950, 682)
		self.geometry("950x650")
		self.title("Exposure Scout")

		# import Available collectors
		self.collectors = modules.AVAILABLE_COLLECTORS

		# Menu bar
		menu = tk.Menu(self)

		file_menu = tk.Menu(menu, tearoff=0)
		file_menu.add_command(label="open", command=lambda: self.on_open())
		file_menu.add_separator()
		file_menu.add_command(label="quit", command=lambda: self.on_quit())

		edit_menu = tk.Menu(menu, tearoff=0)
		edit_menu.add_command(label="import snap", command=lambda: self.on_open(file="snap"))
		edit_menu.add_command(label="export snap", command=lambda: self.on_save(file="snap"))
		edit_menu.add_separator()
		edit_menu.add_command(label="import rpt", command=lambda: self.on_open(file="rpt"))
		edit_menu.add_command(label="export rpt", command=lambda: self.on_save(file="rpt"))
		edit_menu.add_separator()
		edit_menu.add_command(label="dump snap", command=lambda: self.on_dump(file="snap"))
		edit_menu.add_command(label="dump rpt", command=lambda: self.on_dump(file="rpt"))

		help_menu = tk.Menu(menu, tearoff=0)
		help_menu.add_command(label="Help Index", command=lambda :on_help("https://github.com/Tirette-hub/ExposureScout"))
		help_menu.add_command(label="About", command=lambda :on_help("https://github.com/Tirette-hub/ExposureScout"))

		menu.add_cascade(menu=file_menu, label="File")
		menu.add_cascade(menu=edit_menu, label="Edit")
		menu.add_cascade(menu=help_menu, label="Help")

		# Cut the app in 4 major frames
		self.snapshot_frame = tk.Frame(self, highlightbackground="black", highlightthickness=1)
		self.report_frame = tk.Frame(self, highlightbackground="black", highlightthickness=1)
		self.AM_snapshot_frame = tk.Frame(self, highlightbackground="black", highlightthickness=1)
		self.AM_report_frame = tk.Frame(self, highlightbackground="black", highlightthickness=1)

		# Add in every frame another frame that will contain all the data relative to what it is meant to show
		self.collectors_frame = tk.Frame(self.snapshot_frame, highlightbackground="black", highlightthickness=1)
		self.report_detail_frame = tk.Frame(self.report_frame)
		self.snapshots_mem_frame = tk.Frame(self.AM_snapshot_frame)
		self.reports_mem_frame = tk.Frame(self.AM_report_frame)

		# Static widgets dedicated to running new snapshots
		snapshot_label = tk.Label(self.snapshot_frame, text="Run id : ")
		self.run_id_var = tk.StringVar()
		run_id_entry = tk.Entry(self.snapshot_frame, textvariable=self.run_id_var)
		self.run_snapshot_btn = tk.Button(self.snapshot_frame, text="Run", command=lambda: self.on_run_snap())

		# Static widgets dedicated to run and inspect reports
		snap1_label = tk.Label(self.report_frame, text="Snapshot 1 : ")
		self.snap1_var = tk.StringVar()
		self.snap1_combobox = ttk.Combobox(self.report_frame, textvariable=self.snap1_var)

		vs_label = tk.Label(self.report_frame, text="vs")

		snap2_label = tk.Label(self.report_frame, text="Snapshot 2 : ")
		self.snap2_var = tk.StringVar()
		self.snap2_combobox = ttk.Combobox(self.report_frame, textvariable=self.snap2_var)

		report_id_label = tk.Label(self.report_frame, text="Report id : ")
		self.report_id_var = tk.StringVar()
		report_id_entry = tk.Entry(self.report_frame, textvariable=self.report_id_var)
		self.report_run = tk.Button(self.report_frame, text="Run", command=lambda: self.on_run_rpt())

		# Static widgets dedicated to snapshot management
		self.snap_send_btn = tk.Button(self.AM_snapshot_frame, text="<|", command=lambda: self.on_send(file="snap"))
		self.snap_import_btn = tk.Button(self.AM_snapshot_frame, text="Import", command=lambda: self.on_open(file="snap"))
		self.snap_dump_btn = tk.Button(self.AM_snapshot_frame, text="Dump", command=lambda: self.on_dump(file="snap"))
		self.snap_export_btn = tk.Button(self.AM_snapshot_frame, text="Export", command=lambda: self.on_save(file="snap"))

		# Static widgets dedicated to snapshot management
		self.rpt_send_btn = tk.Button(self.AM_report_frame, text="<|", command=lambda: self.on_send(file="rpt"))
		self.rpt_import_btn = tk.Button(self.AM_report_frame, text="Import", command=lambda: self.on_open(file="rpt"))
		self.rpt_dump_btn = tk.Button(self.AM_report_frame, text="Dump", command=lambda: self.on_dump(file="rpt"))
		self.rpt_export_btn = tk.Button(self.AM_report_frame, text="Export", command=lambda: self.on_save(file="rpt"))

		# Snapshot AM treeview
		self.snap_mem_tv = ttk.Treeview(self.snapshots_mem_frame)
		#self.snap_mem_tv["columns"]=("snapshot run id",)
		self.snap_mem_tv.heading("# 0", text="snapshot run id")
		self.snap_mem_scroll = ttk.Scrollbar(self.snapshots_mem_frame, command=self.snap_mem_tv.yview)

		# Report AM treeview
		self.rpt_mem_tv = ttk.Treeview(self.reports_mem_frame)
		#self.rpt_mem_tv["columns"]=("diff report id",)
		self.rpt_mem_tv.heading("# 0", text="diff report id")
		self.rpt_mem_scroll = ttk.Scrollbar(self.reports_mem_frame, command=self.rpt_mem_tv.yview)

		# Report details treeview
		self.selected_report = tk.StringVar()
		columns = ("data", "snapshot id", "status")
		self.report_detail_tv = ttk.Treeview(self.report_detail_frame, columns=columns, show="tree headings")
		#self.report_detail_tv["columns"]=("diff report details",)
		self.report_detail_tv.heading("# 0", text="elements")
		for i, col in enumerate(columns, 1):
			self.report_detail_tv.heading(f"# {i}", text=col)
		self.report_detail_tv.tag_bind("open_tag", "<<TreeviewOpen>>", lambda x: self.on_tv_open(x))
		self.report_detail_scroll = ttk.Scrollbar(self.report_detail_frame, command=self.report_detail_tv.yview)

		# set them all on the app
		self.config(menu=menu)

		self.grid_rowconfigure(0, weight=2)
		self.grid_rowconfigure(1, weight=3)
		self.grid_columnconfigure(0, weight=4)
		self.grid_columnconfigure(1, weight=1)

		self.snapshot_frame.grid(row=0, column=0, sticky=tk.NSEW)
		self.AM_snapshot_frame.grid(row=0, column=1, sticky=tk.NSEW)
		self.report_frame.grid(row=1, column=0, sticky=tk.NSEW)
		self.AM_report_frame.grid(row=1, column=1, sticky=tk.NSEW)


		self.snapshot_frame.grid_rowconfigure(0, weight=5)
		self.snapshot_frame.grid_rowconfigure(1, weight=1)
		self.snapshot_frame.grid_columnconfigure(0, weight=1)
		self.snapshot_frame.grid_columnconfigure(1, weight=1)
		self.snapshot_frame.grid_columnconfigure(2, weight=2)
		# self.snapshot_frame.grid_columnconfigure(3, weight=0)

		self.collectors_frame.grid(row=0, column=0, columnspan=4, sticky=tk.NSEW, padx=5, pady=5)

		self.run_snapshot_btn.grid(row=1, column=3, sticky=tk.E, padx=5, pady=5)
		run_id_entry.grid(row=1, column=2, sticky=tk.EW, pady=5)
		snapshot_label.grid(row=1, column=1, sticky=tk.E, pady=5)


		self.report_frame.grid_rowconfigure(0, weight=1)
		self.report_frame.grid_rowconfigure(1, weight=1)
		self.report_frame.grid_rowconfigure(2, weight=10)
		self.report_frame.grid_columnconfigure(0, weight=1)
		self.report_frame.grid_columnconfigure(1, weight=2)
		self.report_frame.grid_columnconfigure(2, weight=1)
		self.report_frame.grid_columnconfigure(3, weight=1)
		self.report_frame.grid_columnconfigure(4, weight=2)
		# self.report_frame.grid_columnconfigure(5, weight=0)

		snap1_label.grid(row=0, column=0, sticky=tk.W, pady=5)
		self.snap1_combobox.grid(row=0, column=1, sticky=tk.EW, pady=5)
		vs_label.grid(row=0, column=2, pady=5)
		snap2_label.grid(row=0, column=3, sticky=tk.E, pady=5)
		self.snap2_combobox.grid(row=0, column=4, sticky=tk.EW, pady=5)

		report_id_label.grid(row=1, column=3, sticky=tk.E)
		report_id_entry.grid(row=1, column=4, sticky=tk.EW)
		self.report_run.grid(row=1, column=5, sticky=tk.E, padx=5)

		self.report_detail_frame.grid(row=2, column=0, columnspan=6, sticky=tk.NSEW, padx=5, pady=5)
		self.report_detail_frame.grid_rowconfigure(0, weight=1)
		self.report_detail_frame.grid_columnconfigure(0, weight=1)
		self.report_detail_frame.grid_columnconfigure(1)
		self.report_detail_tv.grid(row=0, column=0, sticky=tk.NSEW)
		self.report_detail_scroll.grid(row=0, column=1, sticky=tk.NS+tk.E)


		self.AM_snapshot_frame.grid_rowconfigure(0, weight=1)
		self.AM_snapshot_frame.grid_rowconfigure(1, weight=2)
		self.AM_snapshot_frame.grid_rowconfigure(2, weight=2)
		self.AM_snapshot_frame.grid_rowconfigure(3, weight=2)
		self.AM_snapshot_frame.grid_rowconfigure(4, weight=1)
		self.AM_snapshot_frame.grid_columnconfigure(0, weight=1)
		self.AM_snapshot_frame.grid_columnconfigure(1, weight=2)
		self.AM_snapshot_frame.grid_columnconfigure(2, weight=2)
		self.AM_snapshot_frame.grid_columnconfigure(3, weight=2)

		self.snap_send_btn.grid(row=1, column=0, padx=5)
		self.snapshots_mem_frame.grid(row=0, column=1, rowspan=3, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
		self.snapshots_mem_frame.grid_rowconfigure(0, weight=1)
		self.snapshots_mem_frame.grid_columnconfigure(0, weight=1)
		self.snapshots_mem_frame.grid_columnconfigure(1)
		self.snap_mem_tv.grid(row=0, column=0, sticky=tk.NSEW)
		self.snap_mem_var = tk.StringVar()
		self.snap_mem_tv.tag_bind("snap_selection_tag", "<<TreeviewSelect>>", lambda event: self.on_tv_select(self.snap_mem_var, event))
		self.snap_mem_scroll.grid(row=0, column=1, sticky=tk.E+tk.NS)
		self.snap_import_btn.grid(row=4, column=1, padx=5, pady=5)
		self.snap_dump_btn.grid(row=4, column=2, padx=5, pady=5)
		self.snap_export_btn.grid(row=4, column=3, padx=5, pady=5)


		self.AM_report_frame.grid_rowconfigure(0, weight=1)
		self.AM_report_frame.grid_rowconfigure(1, weight=2)
		self.AM_report_frame.grid_rowconfigure(2, weight=2)
		self.AM_report_frame.grid_rowconfigure(3, weight=2)
		self.AM_report_frame.grid_rowconfigure(4, weight=1)
		self.AM_report_frame.grid_columnconfigure(0, weight=1)
		self.AM_report_frame.grid_columnconfigure(1, weight=2)
		self.AM_report_frame.grid_columnconfigure(2, weight=2)
		self.AM_report_frame.grid_columnconfigure(3, weight=2)

		self.rpt_send_btn.grid(row=1, column=0, rowspan=5, padx=5)
		self.reports_mem_frame.grid(row=0, column=1, rowspan=4, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
		self.reports_mem_frame.grid_rowconfigure(0, weight=1)
		self.reports_mem_frame.grid_columnconfigure(0, weight=1)
		self.reports_mem_frame.grid_columnconfigure(1)
		self.rpt_mem_tv.grid(row=0, column=0, sticky=tk.NSEW)
		self.rpt_mem_var = tk.StringVar()
		self.rpt_mem_tv.tag_bind("rpt_selection_tag", "<<TreeviewSelect>>", lambda event: self.on_tv_select(self.rpt_mem_var, event))
		self.rpt_mem_scroll.grid(row=0, column=1, sticky=tk.E+tk.NS)
		self.rpt_import_btn.grid(row=4, column=1, padx=5, pady=5)
		self.rpt_dump_btn.grid(row=4, column=2, padx=5, pady=5)
		self.rpt_export_btn.grid(row=4, column=3, padx=5, pady=5)


		#create check box for collectors
		self.collector_vars = []
		for i, collector in enumerate(self.collectors):
			var = tk.IntVar()
			check_btn = tk.Checkbutton(self.collectors_frame, text=collector.name, variable=var, onvalue=i+1, offvalue=0) # /!\ value is +1 compared to the list index!
			check_btn.grid(row=i, column=0, padx=15, pady=15, sticky=tk.W)
			self.collector_vars.append(var)

		# Setup treeview with the manager content (if provided, otherwize it just passes)
		for run_id in self.manager.runs.keys():
			self.snap_mem_tv.insert("", tk.END, text=run_id, tags=("snap_selection_tag",))

		for report_id in self.manager.diff_reports.keys():
			self.rpt_mem_tv.insert("", tk.END, text=report_id, tags=("rpt_selection_tag",))

		# set combobox with possible values
		self.snap1_combobox['values'] = list(self.manager.runs.keys())
		self.snap2_combobox['values'] = list(self.manager.runs.keys())
		# for run_id in self.manager.runs.keys():
		# 	self.snap1_combobox['values'] += [run_id]
		# 	self.snap2_combobox['values'] += [run_id]


	def on_dump(self, file):
		"""
		Arguments:
			file (str): file type beeing saved. Must be either 'snap' or 'rpt'.
		"""
		if file == 'snap':
			if self.snap_mem_var.get() != "" and self.snap_mem_var.get() != None:
				self.manager.dump(self.snap_mem_var.get())
				selected_item = self.snap_mem_tv.selection()
				if selected_item != ():
					selected_item = selected_item[0]
					self.snap_mem_tv.delete(selected_item)

					# remove the possibility to select it from the diff making panel
					items = list(self.snap1_combobox['values'])
					items.remove(self.snap_mem_var.get())
					self.snap1_combobox['values'] = items

					items = list(self.snap2_combobox['values'])
					items.remove(self.snap_mem_var.get())
					self.snap2_combobox['values'] = items

		elif file == 'rpt':
			if self.rpt_mem_var.get() != "" and self.rpt_mem_var.get() != None:
				self.manager.dump_report(self.rpt_mem_var.get())
				selected_item = self.rpt_mem_tv.selection()
				if selected_item != ():
					selected_item = selected_item[0]
					self.rpt_mem_tv.delete(selected_item)
				
		else:
			raise ValueError(f"Unknown file format. Expected 'snap' or 'rpt', but received '{file}'.")

	def on_run_snap(self):
		run_id = self.run_id_var.get()
		if run_id != "" or run_id != None:
			if run_id in self.manager.runs.keys():
				# show info on duplicated run_id
				pass

			else:
				for c in self.collector_vars:
					if c.get() > 0:
						collector = self.collectors[c.get()-1]()

						if collector.name == "File System Collector":
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

						#print(f"Adding collector {c.get()-1}: {collector}")
						self.manager.add_collector(collector)

				self.manager.run_snapshot(run_id)
				self.snap_mem_tv.insert("", tk.END, text=run_id, tags=("snap_selection_tag",))

				# add it to the diff making available snapshots list
				if len(self.snap1_combobox['values']) == 0:
					self.snap1_combobox['values'] = [run_id]
				else:
					self.snap1_combobox['values'] += (run_id,)
					
				if len(self.snap2_combobox['values']) == 0:
					self.snap2_combobox['values'] = [run_id]
				else:
					self.snap2_combobox['values'] += (run_id,)

	def on_run_rpt(self):
		name = self.report_id_var.get()
		snap1 = self.snap1_var.get()
		snap2 = self.snap2_var.get()

		if snap1 == "" or snap1 == None or snap2 == "" or snap2 == None:
			#TODO: alert/info
			print("alert")
			pass
		else:
			print("do it")
			if name == "" or name == None:
				name = snap1 + " vs " + snap2

			# run report
			self.manager.make_diff(snap1, snap2, report_id=name)
			# add it to the memory treeview
			self.rpt_mem_tv.insert("", tk.END, text=name, tags=("rpt_selection_tag",))

	def on_open(self, file="both"):
		"""
		Callback when open file buttons are triggered.

		Arguments:
			file (str): kind of files to open. values are "snap", "rpt" or "both". (default = "both")
		"""
		if file != "both" and file != "snap" and file != "rpt":
			raise ValueError(f"File type unknown. Expected 'snap' or 'rpt' or 'both', but received {file}")

		bg_frame = tk.Frame(self, bg='white')
		#frame.attributes("-alpha", 0.5)
		bg_frame.grid(row=0, column=0, rowspan=2, columnspan=2, sticky=tk.NSEW)

		frame = tk.Frame(bg_frame, width=300, height=200)
		frame.place(relx=.5, rely=.5, anchor=tk.CENTER)

		frame.grid_rowconfigure(0, weight=6)
		frame.grid_rowconfigure(1, weight=1)
		frame.grid_columnconfigure(0, weight=1)
		frame.grid_columnconfigure(1, weight=1)
		frame.grid_rowconfigure(2, weight=1)

		listing = ttk.Treeview(frame)
		listing.heading("# 0", text="file")
		listing.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
		var = tk.StringVar()
		listing.tag_bind("selection_tag", "<<TreeviewSelect>>", lambda event: self.on_tv_select(var, event))

		for f in os.listdir("reports/"):
			if file == 'both' or file == 'snap':
				if f.endswith('.snap'):
					item = listing.insert("", tk.END, text=f, tags=("selection_tag",))
					#listing.selection_add(item)

			if file == 'both' or file == 'rpt':
				if f.endswith('.rpt'):
					item = listing.insert("", tk.END, text=f, tags=("selection_tag",))
					#listing.selection_add(item)


		button_cancel = tk.Button(frame, text="Cancel", width="30", command=bg_frame.destroy)
		button_cancel.grid(row=1, column=0, padx=10)

		button_ok = tk.Button(frame, text="OK", width="30", command=lambda:self.on_import(bg_frame, var))
		button_ok.grid(row=1, column=1, padx=10)

		tk.Label(frame, text="").grid(row=2, column=0, columnspan=2)

	def on_tv_select(self, variable, event):
		"""
		Arguments:
			variable (tkinter.StringVar): Variable storing the selected entry in the Treeview.
			event (tkinter.Event): Event triggered by the Treeview when selecting an item.
		"""
		tv = event.widget
		variable.set(tv.item(tv.selection()[0])["text"])

	def on_tv_open(self, event):
		"""

		"""
		report_id = self.selected_report.get()
		item_id = self.report_detail_tv.selection()[0]
		collector = self.report_detail_tv.item(item_id)["text"]
		for element in self.manager.diff_reports[report_id].diff_elemnts[collector]:
			self.report_detail_tv.insert(item_id, tk.END, text = str(element))

	def on_import(self, bg_frame, variable):
		"""
		Arguments:
			frame (tkinter.Frame): Frame that will be destroyed after the import has been performed.
			variable (tkinter.StringVar): Variable storing the file name to import.
		"""
		file = variable.get()

		if file.endswith('.snap'):
			if file.replace(".snap", "") not in self.manager.runs.keys():
				self.snap_mem_tv.insert("", tk.END, text=file.replace(".snap", ""), tags=("snap_selection_tag",))
				self.manager.load(file.replace(".snap", ""))

				# add it to the diff making available snapshots list
				if len(self.snap1_combobox['values']) == 0:
					self.snap1_combobox['values'] = [file.replace(".snap", "")]
				else:
					self.snap1_combobox['values'] += (file.replace(".snap", ""),)

				if len(self.snap2_combobox['values']) == 0:
					self.snap2_combobox['values'] = [file.replace(".snap", "")]
				else:
					self.snap2_combobox['values'] += (file.replace(".snap", ""),)

			else:
				# show info
				pass

		elif file.endswith('.rpt'):
			if file.replace(".rpt", "") not in self.manager.diff_reports.keys():
				self.rpt_mem_tv.insert("", tk.END, text=file.replace(".rpt", ""), tags=("rpt_selection_tag",))
				self.manager.import_report(file.replace(".rpt", ""))
			else:
				# show info
				pass

		else:
			raise ValueError(f"Unknown file format. Expected '*.snap' or '*.rpt', but received '{file}'.")

		bg_frame.destroy()

	def on_save(self, file):
		"""
		Arguments:
			file (str): file type beeing saved. Must be either 'snap' or 'rpt'.
		"""
		# TODO check if the file already exists + notify if no name provided
		if file == 'snap':
			if self.snap_mem_var.get() != "" and self.snap_mem_var.get() != None:
				self.manager.save(self.snap_mem_var.get())
			else:
				pass

		elif file == 'rpt':
			if self.rpt_mem_var.get() != "" and self.rpt_mem_var.get() != None:
				self.manager.export_report(self.rpt_mem_var.get())
			else:
				pass

		else:
			raise ValueError(f"Unknown file format. Expected 'snap' or 'rpt', but received '{file}'.")

	def on_send(self, file):
		"""
		Arguments:
			file (str): file type beeing saved. Must be either 'snap' or 'rpt'.
		"""
		if file == 'snap':
			print(f"[WIP] on_send: {file}")

		elif file == 'rpt':
			for item in self.report_detail_tv.get_children():
				#clear any previous data in the TreeView
				self.report_detail_tv.delete(item)
			# get the selected report_id
			# set the selected_report string var
			# fill the report_detail_tv with collectors names
			report_id = self.rpt_mem_var.get()
			self.report_id_var.set(report_id)
			if report_id != "" and report_id != None:
				self.selected_report.set(report_id)
				for collector in self.manager.diff_reports[report_id].diff_elemnts.keys():
					collector_item = self.report_detail_tv.insert("", tk.END, text=collector)#, tags=("open_tag",))
					for collectible in self.manager.diff_reports[report_id].diff_elemnts[collector].keys():
						collectible_item = self.report_detail_tv.insert(collector_item, tk.END, text=collectible + " collectibles")
						for data in self.manager.diff_reports[report_id].diff_elemnts[collector][collectible]:
							val = (str(data.element), data.run_id, get_status_by_id(data.type))
							self.report_detail_tv.insert(collectible_item, tk.END, text=collectible, values=val)
			else:
				pass
		else:
			raise ValueError(f"Unknown file format. Expected 'snap' or 'rpt', but received '{file}'.")

	def on_quit(self):
		print("quit")


def main():
	app = GUIApp()

	app.mainloop()


if __name__ == '__main__':
	main()