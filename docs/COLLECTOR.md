# Collector
This file contains the Abstract classes from which any Collector or Collectible implemented in _Exposure Scout_ inherits.

---------------------------------------------------
## Index
* [Collector](#collector)
    - [AbstractMethodException](#abstractmethodexception)
    ---------------------------------------------------
    - [FormattingError](#formattingerror)
    ---------------------------------------------------
    - [RunningError](#runningerror)
    ---------------------------------------------------
    - [ACollectible](#acollectible)
        - [to_bytes](#to_bytes)
        - [export_report_db](#export_report_dbreport_id-run_id-status-db_cursor)
        ---------------------------------------------------
        - [from_bytes](#from_bytesdata)
    ---------------------------------------------------
    - [ACollector](#acollector)
        - [is_running](#is_running)
        - [help](#help)
        - [\_format](#_format)
        - [\_export](#_export)
        - [export_bin](#export_bin)
        - [\_export_sql](#_export_sqldb_cursor-run_id)
        - [export_db](#export_dbdb_cursor-run_id)
        - [import_bin](#import_bindata)
        - [import_db](#import_dbdb_cursor-run_id)
        - [start_running](#start_running)
        - [stop_running](#stop_running)
        - [run](#run)
        ---------------------------------------------------
        - [make_diff](#make_diffa-b-report)
        - [import_diff_from_report](#import_diff_from_reportdata-run_ids-report)
        - [import_diff_from_report_db](#import_diff_from_report_dbdb_cursor-run_ids-report)
        - [get_report_tree_structure](#get_report_tree_structure)
        - [create_report_tables](#create_report_tablesdb_cursor)

---------------------------------------------------

## AbstractMethodException()
Inherits from python built-in _Exception_.

---------------------------------------------------

## FormattingError()
Inherits from python built-in _Exception_.

---------------------------------------------------

## RunningError()
Inherits from python built-in _Exception_.

---------------------------------------------------

## ACollectible()
Abstract class from which every collectible element of a Collector should derive.\
_You should see it like a mix between an abstract class and an interface in Java._

*Attributes*:
- _element_name_ (str): name of the collectible.

### to_bytes()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Converts the collectible to a byte string used to store it. **MUST** always been rewritten for every new module.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;If it has not been implemented, raises [AbstractMethodException](#abstractmethodexception).

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A bytes stream.

### export_report_db(*__report_id, run_id, status, db_cursor__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Export a collectible data structure that is part of a diff report into the specified database.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_report_id_ (str): identifer of the report the element is linked to.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_run_id_ (str): identifier of the snapshot run the element comes from.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_status_ (int): value of the element's status in the diff report (created, deleted, modified, ...).\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_db_cursor_ ([Cursor](doc.python.org/3/library/sqlite3.html#sqlite3.Cursor)): sqlite3 cursor that points to the database.

### from_bytes(*__data__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**_STATIC_** Convert bytes into a Collectible. **MUST** always been rewritten for every new module.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_data_ (bytes): a bytes stream begining with the encoded data of the collectible.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A tupple containing:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. the collectible data structure recovered from the bytes stream;\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. the rest of the unread bytes that are not part of this collectible data structure.

---------------------------------------------------

## ACollector()
Abstract class from which every analysis/collector module should derive.\
_You should see it like a mix between an abstract class and an interface in Java._

*Attributes*:
- _name_ (str): name of the Collector module.
- _descr_ (str): description of what the module does and what it was created for.
- _snapshot_elemnt_id_ (byte): byte used to identify the collector in the binary file.

- _result_ (bytes): formated data collected by the collector so it can be exported. (default: None)
- _raw_result_ (dict{str : ACollectible}): data collected by the collector before to be formated for export. (default: None)
- _running_ (bool): flag repesenting whether the module is running or not. (default: None)

### is_running()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Allows to check if the module is runing or not.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;True if the module is running, False otherwize.

### help()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Get the description of the module.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The description of the module.

### \_format()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Private** method to format raw collected data of a run to exportable data. **MUST** always been rewritten for every new module.

### \_export()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Private** method to export the result after running the module. **SHOULD** not be rewritten for every new module.

### export_bin()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Public** method to export the result after running the module. It is mainly used by the [AnalysisManager](./AM.md#analysismanager) of the [core](./CORE.md#core) python project module.

### \_export_sql(*__db_cursor, run_id__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Private** method to export the result in a db after running the module. **MUST** be rewritten for every new module.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_db_cursor_ ([Cursor](doc.python.org/3/library/sqlite3.html#sqlite3.Cursor)): pointer to the database.\\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_run_id_ (str): run identifier being exported.

### export_db(*__db_cursor, run_id__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Public** method to export the result in a db after running the module. It is mainly used by the CollectorManager of the "core" python project module.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_db_cursor_ ([Cursor](doc.python.org/3/library/sqlite3.html#sqlite3.Cursor)): pointer to the database.\\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_run_id_ (str): run identifier being exported.

### import_bin(*__data__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Import method to recover data of a previous run. Those data can then be previewed.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_data_ (bytes): raw data with the first bytes representing this collector.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The rest of raw bytes unrelated to this collector.

### import_db(*__db_cursor, run_id__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Import method to recover data of a previous run stored in DB. Those data can then be previewed.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Note: must already been connected to the database.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_db_cursor_ ([Cursor](doc.python.org/3/library/sqlite3.html#sqlite3.Cursor)): pointer to the database.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_run_id_ (str): id used to store the collected data in the db of a specific run.

### \_start_running()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Private** method used when starting the collector. **SHOULD** not be rewritten for every new module.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;It can be rewritten to perform some task before the execution of the collector(e.g. setting a timer).

### \_stop_running()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Private** method used when collector finished running. **SHOULD** not be rewritten for every new module.

### \_run()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Private** Private method used to run the collector. **MUST** be rewritten for every new module since every module/collector works differently.

### make_diff(*__a, b, report__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**_Static_** method used to get the difference between two collectors of the same type. **MUST** be rewritten for every new module since every module/collecor works differently.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_run_id_a_ (str): run_id of the first collector.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_run_id_b_ (str): run_id of the second collector.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_a_ ([Collector](#acollector)): one of the collectors.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_b_ ([Collector](#acollector)): the other collector.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_report_ ([DiffReport](./REPORT.md#diffreportfirst_run_id-second_run_id)): the report where to add the differences.

### import_diff_from_report(*__data, run_ids, report__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**_Static_** method used to import the values of report that are related to a given collector. **MUST** be rewritten for every new module since every module/collecor works differently.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_data_ (bytes): A bytes stream containing the data to import.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_run_ids_ (list[str]): the ordered list of the snapshot ids from which come the report elements.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_report_ ([DiffReport](./REPORT.md#diffreportfirst_run_id-second_run_id)): datastructure in which to store the recovered data.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;True if the [DiffElements](./REPORT.md#diffelementrun_id-element-type) associated to the collector data have been successfully imported.

### import_diff_from_report_db(*__db_cursor, run_ids, report__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**_Static_** method used to import the values of report that are related to a given collector from a database. **MUST** be rewritten for every new module since every module/collecor works differently.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_db_cursor_ ([Cursor](doc.python.org/3/library/sqlite3.html#sqlite3.Cursor)): pointer to the database.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_run_ids_ (list[str]): the ordered list of the snapshot ids from which come the report elements.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_report_ ([DiffReport](./REPORT.md#diffreportfirst_run_id-second_run_id)): datastructure in which to store the recovered data.

### get_report_tree_structure()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**_Static_** method used to get the structure of the Collector used for the report. **MUST** be rewritten for every new module since every module/collecor works differently.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A python dict representing the data structure to use in the [DiffReport](./REPORT.md#diffreportfirst_run_id-second_run_id)

### create_report_tables(*__db_cursor__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**_Static_** method used to create the different tables used by this collector for report structure in the specified database.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Note: modifications are not committed here. MUST be rewritten for every new module since every module/collecor works differently.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_db_cursor_ ([Cursor](doc.python.org/3/library/sqlite3.html#sqlite3.Cursor)): sqlite3 cursor pointing to the database in which the tables must be created.