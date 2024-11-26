#!/usr/bin/python3
#coding:utf-8

"""
Authors:
Nathan Amorison

Version:
0.3.0
"""

from ..core.analysis_manager import AnalysisManager

import tkinter as tk
from tkinter import ttk

def main():
	app = GUIApp()

	app.mainloop()

def on_help(url):
	import webbrowser
	webbrowser.open(url)

class GUIApp(tk.Tk):
	def __init__(self, *args, am = AnalysisManager(),**kwargs):
		super(GUIApp, self).__init__(*args, **kwargs)
		self.manager = am
		self.minsize(950, 682)
		self.geometry("950x650")
		self.title("Exposure Scout")

		from .. import modules
		# import Available collectors
		self.collectors = modules.AVAILABLE_COLLECTORS

		# Menu bar
		menu = tk.Menu(self)

		file_menu = tk.Menu(menu, tearoff=0)
		file_menu.add_command(label="open", command=self.on_open)
		file_menu.add_separator()
		file_menu.add_command(label="quit", command=self.on_quit)

		edit_menu = tk.Menu(menu, tearoff=0)
		edit_menu.add_command(label="import snap", command=self.on_open)
		edit_menu.add_command(label="export snap", command=self.on_save)
		edit_menu.add_separator()
		edit_menu.add_command(label="import snap", command=self.on_open)
		edit_menu.add_command(label="export snap", command=self.on_save)
		edit_menu.add_separator()
		edit_menu.add_command(label="dump snap", command=self.on_dump)
		edit_menu.add_command(label="dump rpt", command=self.on_dump)

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
		self.run_snapshot_btn = tk.Button(self.snapshot_frame, text="Run", command=self.on_run_snap)

		# Static widgets dedicated to run and inspect reports
		snap1_label = tk.Label(self.report_frame, text="Snapshot 1 : ")
		self.snap1_var = tk.StringVar()
		snap1_entry = tk.Entry(self.report_frame, textvariable=self.snap1_var)

		vs_label = tk.Label(self.report_frame, text="vs")

		snap2_label = tk.Label(self.report_frame, text="Snapshot 2 : ")
		self.snap2_var = tk.StringVar()
		snap2_entry = tk.Entry(self.report_frame, textvariable=self.snap2_var)

		report_id_label = tk.Label(self.report_frame, text="Report id : ")
		self.report_id_var = tk.StringVar()
		report_id_entry = tk.Entry(self.report_frame, textvariable=self.report_id_var)
		self.report_run = tk.Button(self.report_frame, text="Run", command=self.on_run_rpt)

		# Static widgets dedicated to snapshot management
		self.snap_send_btn = tk.Button(self.AM_snapshot_frame, text="<|", command=self.on_send)
		self.snap_import_btn = tk.Button(self.AM_snapshot_frame, text="Import", command=self.on_open)
		self.snap_dump_btn = tk.Button(self.AM_snapshot_frame, text="Dump", command=self.on_dump)
		self.snap_export_btn = tk.Button(self.AM_snapshot_frame, text="Export", command=self.on_save)

		# Static widgets dedicated to snapshot management
		self.rpt_send_btn = tk.Button(self.AM_report_frame, text="<|", command=self.on_send)
		self.rpt_import_btn = tk.Button(self.AM_report_frame, text="Import", command=self.on_open)
		self.rpt_dump_btn = tk.Button(self.AM_report_frame, text="Dump", command=self.on_dump)
		self.rpt_export_btn = tk.Button(self.AM_report_frame, text="Export", command=self.on_save)

		# Snapshot AM treeview
		self.snap_mem_tv = ttk.Treeview(self.snapshots_mem_frame)
		self.snap_mem_scroll = ttk.Scrollbar(self.snapshots_mem_frame, command=self.snap_mem_tv.yview)

		# Report AM treeview
		self.rpt_mem_tv = ttk.Treeview(self.reports_mem_frame)
		self.rpt_mem_scroll = ttk.Scrollbar(self.reports_mem_frame, command=self.rpt_mem_tv.yview)

		# Report details treeview
		self.report_detail_tv = ttk.Treeview(self.report_detail_frame)
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
		snap1_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
		vs_label.grid(row=0, column=2, pady=5)
		snap2_label.grid(row=0, column=3, sticky=tk.E, pady=5)
		snap2_entry.grid(row=0, column=4, sticky=tk.EW, pady=5)

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
		self.rpt_mem_scroll.grid(row=0, column=1, sticky=tk.E+tk.NS)
		self.rpt_import_btn.grid(row=4, column=1, padx=5, pady=5)
		self.rpt_dump_btn.grid(row=4, column=2, padx=5, pady=5)
		self.rpt_export_btn.grid(row=4, column=3, padx=5, pady=5)


		#create check box for collectors
		self.collector_vars = []
		for i, collector in enumerate(self.collectors):
			var = tk.IntVar()
			check_btn = tk.Checkbutton(self.collectors_frame, text=collector.name, variable=var, onvalue=i+1, offvalue=0)
			check_btn.grid(row=i, column=0, padx=15, pady=15, sticky=tk.W)



	def on_dump(self):
		print("on_dump")

	def on_run_snap(self):
		print("on_run_snap")

	def on_run_rpt(self):
		print("on_run_rpt")

	def on_open(self):
		print("on_open")

	def on_save(self):
		print("on_save")

	def on_send(self):
		print("on_send")

	def on_quit(self):
		print("quit")



if __name__ == '__main__':
	main()