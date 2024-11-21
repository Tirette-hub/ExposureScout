# analysis_manager
This is the heart of the application. It manages all the collectors, the snapshots ran or loaded and the reports of diff. You can use it as a "Memory Manager" of the application and you should use it to perform all commands since it implements all the application features.

---------------------------------------------------
## Index
* [analysis_manager](#analysis_manager)
    - [AnalysisManager](#analysismanager)
        - [is_running](#is_running)
        - [get_running_snapshot](#get_running_snapshot)
        - [save](#saverun_id-method--bin-db--none-buf_size--64)
        - [load](#loadrun_id-method--bin-db--none-buf_size--64)
        - [dump](#dumprun_id)
        - [dump_report](#dump_reportreport_id)
        - [pause_running](#pause_running)
        - [resume_running](#resume_running)
        - [quit_running](#quit_running)
        - [show_running_status](#show_running_status)
        - [add_collector](#add_collectorcollector)
        - [run_snapshot](#run_snapshotrun_id)
        - [make_diff](#make_difffirst_run-second_run-report_id--none)
        - [export_report](#export_reportreport_id-method--bin-db--none-buf_size--64)
        - [import_report](#import_reportreport_id-method--bin-db--none-buf_size--64)
---------------------------------------------------

## AnalysisManager()
Core module used to manage all the different runs and make analysis between them.\
It can also manage the memory used by the different runs (you can dump runs to free memory, otherwize every run is kept in memory either they have been saved ot not so it is faster if you want to make analysis between those runs).

*Attributes*:
- runs (dict{str:[CollectorList](./MODULES.md#collectorlist)}): the different runs in memory that are ready to use (to be analyzed or to be stored). Every run is identified by its run id as a string and its collectors.
- running_snapshot (str): used to know what snapshot is running, using its run_id.
- running_snapshot_threads (list\[[threading.Thread](https://docs.python.org/3/library/threading.html#threading.Thread)\]): list of all the threads running for the running snapshot.
- snapshot_paused (bool): flag used to know if the running snapshot has been paused or not.
- awaiting_collectors (list\[[ACollector](./COLLECTOR.md#acollector)\]): list of collectors awaiting to be run.
- diff_reports (dict{str : [DiffReport](./REPORT.md#diffreportfirst_run_id-second_run_id)}): list of reports of differences between two snapshots that have been performed.

### is_running()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Get the running status.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;True if a snapshot is beeing run.

### get_running_snapshot()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Get the collectors of the running snapshot.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The list of collectors being run, None if no snapshot is running.

### save(_**run_id, method = BIN, db = None, buf_size = 64**_)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Export a snapshot.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_run_id_ (str): the run identifier.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_method_ (int): the method used to export the data (binary: 0, sqlite3 db: 1). (default = BIN = 0)\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_db_ (str): path to the database. (MUST be used ONLY if method is set to 1 (DB), default = None)\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_buf_size_ (int): buffer size in kB used while writing a snap file. (default = 64)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;True if the export succeeded, False otherwize.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Raises*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_ValueError_: unknown method provided.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_ValueError_: method is set to 1 (DB) but no path to the database provided.

### load(_**run_id, method = BIN, db = None, buf_size = 64**_)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Import a snapshot.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_run_id_ (str): the run identifier.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_method_ (int): the method used to export the data (binary: 0, sqlite3 db: 1). (default = BIN = 0)\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_db_ (str): path to the database. (MUST be used ONLY if method is set to 1 (DB), default = None)\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_buf_size_ (int): buffer size in kB used while reading a snap file. (default = 64)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;True if the loading was successful, False if it has already been loaded.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Raises*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_ValueError_: unknown method provided.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_ValueError_: method is set to 1 (DB) but no path to the database provided.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_IOError_: corrupted file (header and content do not match together).\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_IOError_: impossible to parse the file content.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_FileNotFoundError_: incorrect path to the file (based on the run_id).

### dump(_**run_id**_)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Free the memory by dumping a run/snapshot.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_run_id_ (str): the run identifier.

### dump_report(_**report_id**_)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Free the memory by dumping a report.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_report_id_ (str): the report identifier.

### pause_running()
_WIP_

### resume_running()
_WIP_

### quit_running()
_WIP_

### show_running_status()
_WIP_

### add_collector(_**collector**_):
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Append a collector to the list of awaiting collectors before to run it.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_collector_ ([ACollector](./COLLECTOR.md#acollector)): collector to add in the list of the one used to run a snapshot.

### run_snapshot(_**run_id, collectors**_)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Runs collectors for a snapshot.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_run_id_ (str): identifier of the snapshot.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_collectors_ (list\[str\]): list of collectors' name used for the analysis.

### make_diff(_**first_run, second_run, report_id = None**_)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Analyze the difference between two snapshots.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_first_run_ (str): run_id of the first run to compare.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_second_run_ (str): run_id of the second run to compare.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_report_id_ (str): identifies the report. (default: None; if None, then combines the first and second snapshot id's)

### export_report(_**report_id, method = BIN, db = None, buf_size = 64**_)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Export a report.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_report_id_ (str): identifier of the report.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_method_ (int): the method used to export the data (binary: 0, sqlite3 db: 1). (default = BIN = 0)\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_db_ (str): path to the database. (MUST be used ONLY if method is set to 1 (DB), default = None)\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_buf_size_ (int): buffer size in kB used while writing a rpt file.. (default = 64)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;True if the export succeeded, False otherwize.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Raises*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_ValueError_: unknown method provided.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_ValueError_: method is set to 1 (DB) but no path to the database provided.

### import_report(_**report_id, method = BIN, db = None, buf_size = 64**_):
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;import a report.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_report_id_ (str): identifier of the report.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_method_ (int): the method used to export the data (binary: 0, sqlite3 db: 1). (default = BIN = 0)\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_db_ (str): path to the database. (MUST be used ONLY if method is set to 1 (DB), default = None)\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_buf_size_ (int): buffer size in kB used while reading a rpt file. (default = 64)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;True if the loading was successful, False if it has already been loaded.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Raises*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_ValueError_: unknown method provided.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_ValueError_: method is set to 1 (DB) but no path to the database provided.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_FileNotFoundError_: incorrect path to the file (based on the run_id).\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_IOError_: unexpected bytes at the end of the file.