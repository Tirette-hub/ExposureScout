# modules
This is where the features of the application as well as the collectors are implemented.

The package itself provides a few important data such as a list of which collectors are available.

*Data*:
- _AVAILABLE_COLLECTORS_ ([CollectorList](#collectorlistcollectors))

---------------------------------------------------
## Index
* [modules](#modules)
	---------------------------------------------------
	- [Index](#index)
	---------------------------------------------------
	- [CollectorList](#collectorlistcollectors)
	    - [append](#appendcollector)
	    - [get_collector_by_name](#get_collector_by_namename)
	    - [get_collector_by_type](#get_collector_by_typetype)
	    ---------------------------------------------------
	    - [XOR](#xora-b)
	    - [AND](#anda-b)
	---------------------------------------------------
	- [Collector](./COLLECTOR.md#collector)
	    - [AbstractMethodException](./COLLECTOR.md#abstractmethodexception)
		---------------------------------------------------
	    - [FormattingError](./COLLECTOR.md#formattingerror)
		---------------------------------------------------
	    - [RunningError](./COLLECTOR.md#runningerror)
	    ---------------------------------------------------
	    - [ACollectible](./COLLECTOR.md#acollectible)
	        - [to_bytes](./COLLECTOR.md#to_bytes)
	        - [export_report_db](./COLLECTOR.md#export_report_dbreport_id-run_id-status-db_cursor)
	        ---------------------------------------------------
	        - [from_bytes](./COLLECTOR.md#from_bytesdata)
		---------------------------------------------------
	    - [ACollector](./COLLECTOR.md#acollector)
	        - [is_running](./COLLECTOR.md#is_running)
	        - [help](./COLLECTOR.md#help)
	        - [\_format](./COLLECTOR.md#_format)
	        - [\_export](./COLLECTOR.md#_export)
	        - [export_bin](./COLLECTOR.md#export_bin)
	        - [\_export_sql](./COLLECTOR.md#_export_sqldb_cursor-run_id)
	        - [export_db](./COLLECTOR.md#export_dbdb_cursor-run_id)
	        - [import_bin](./COLLECTOR.md#import_bindata)
	        - [import_db](./COLLECTOR.md#import_dbdb_cursor-run_id)
	        - [start_running](./COLLECTOR.md#start_running)
	        - [stop_running](./COLLECTOR.md#stop_running)
	        - [run](./COLLECTOR.md#run)
	        ---------------------------------------------------
	        - [make_diff](./COLLECTOR.md#make_diffa-b-report)
	        - [import_diff_from_report](./COLLECTOR.md#import_diff_from_reportdata-run_ids-report)
	        - [import_diff_from_report_db](./COLLECTOR.md#import_diff_from_report_dbdb_cursor-run_ids-report)
	        - [get_report_tree_structure](./COLLECTOR.md#get_report_tree_structure)
	        - [create_report_tables](./COLLECTOR.md#create_report_tablesdb_cursor)
	---------------------------------------------------
	- [UsersCollector](./USERSCOLLECTOR.md#userscollector)
		- [parse_user_line](./USERSCOLLECTOR.md#parse_user_lineline)
		- [parse_group_line](./USERSCOLLECTOR.md#parse_group_lineline)
		---------------------------------------------------
		- [User](./USERSCOLLECTOR.md#useruid-name-groups)
		---------------------------------------------------
		- [Group](./USERSCOLLECTOR.md#groupgid-name)
		---------------------------------------------------
		- [Sudoer](./USERSCOLLECTOR.md#sudoeruid)
		---------------------------------------------------
		- [LinUsersCollector](./USERSCOLLECTOR.md#linuserscollector)
		    - [get_users](./USERSCOLLECTOR.md#get_users)
		    - [get_groups](./USERSCOLLECTOR.md#get_groups)
		    - [get_sudoers](./USERSCOLLECTOR.md#get_sudoers)
		    - [get_hashes](./USERSCOLLECTOR.md#get_hashes)
		    - [collect_users](./USERSCOLLECTOR.md#collect_users)
		    - [collect_groups](./USERSCOLLECTOR.md#collect_groups)
		    - [collect_sudoers](./USERSCOLLECTOR.md#collect_sudoers)
		    - [collect_passwd_hash](./USERSCOLLECTOR.md#collect_passwd_hash)
		    - [collect_group_hash](./USERSCOLLECTOR.md#collect_group_hash)
	        ---------------------------------------------------
		    - [make_diff](./USERSCOLLECTOR.md#make_diffrun_id_a-run_id_b-a-b-report)
		    - [import_diff_from_report](./USERSCOLLECTOR.md#import_diff_from_reportdata-run_ids-report)
	        - [import_diff_from_report_db](./USERSCOLLECTOR.md#import_diff_from_report_dbdb_cursor-run_ids-report)
	        - [get_report_tree_structure](./USERSCOLLECTOR.md#get_report_tree_structure)
	        - [create_report_tables](./USERSCOLLECTOR.md#create_report_tablesdb_cursor)
	---------------------------------------------------
	- [FileSystemCollector](./FSCOLLECTOR.md#filesystemcollector)
		- [DiffFile](./FSCOLLECTOR.md#difffilefile)
		---------------------------------------------------
		- [File](./FSCOLLECTOR.md#filepath-metadata-size-content_hash)
			- [get_filename](./FSCOLLECTOR.md#get_filename)
			- [get_metadata](./FSCOLLECTOR.md#get_metadata)
			- [is_dir](./FSCOLLECTOR.md#is_dir)
			- [is_file](./FSCOLLECTOR.md#is_file)
			- [make_diff](./FSCOLLECTOR.md#make_diffcollector-run_id_a-run_id_b-a-b-report)
		---------------------------------------------------
		- [Directory](./FSCOLLECTOR.md#directorypath-metadata)
		    - [get_content](./FSCOLLECTOR.md#get_content)
		    - [append](./FSCOLLECTOR.md#appendfile)
		    - [append_all](./FSCOLLECTOR.md#append_allfile_list)
		    - [has](./FSCOLLECTOR.md#hasfile)
		    - [contains](./FSCOLLECTOR.md#containsfile_list)
		    - [contains_filename](./FSCOLLECTOR.md#contains_filenamefilename)
		    - [contains_inode](./FSCOLLECTOR.md#contains_inodeinode)
		    - [is_parent_of](./FSCOLLECTOR.md#is_parent_offile)
		---------------------------------------------------
		- [LinFileSystemCollector](./FSCOLLECTOR.md#linfilesystemcollector)
		    - [set_rule](./FSCOLLECTOR.md#set_rulerule)
		    - [set_rules](./FSCOLLECTOR.md#set_rulesrules)
		    - [get_content](./FSCOLLECTOR.md#get_content)
		    - [walk_through](./FSCOLLECTOR.md#walk_throughpath)
	        ---------------------------------------------------
		    - [make_diff](./FSCOLLECTOR.md#make_diffrun_id_a-run_id_b-a-b-report)
		    - [import_diff_from_report](./FSCOLLECTOR.md#import_diff_from_reportdata-run_ids-report)
	        - [import_diff_from_report_db](./FSCOLLECTOR.md#import_diff_from_report_dbdb_cursor-run_ids-report)
	        - [get_report_tree_structure](./FSCOLLECTOR.md#get_report_tree_structure)
	        - [create_report_tables](./FSCOLLECTOR.md#create_report_tablesdb_cursor)

---------------------------------------------------
## CollectorList(*__collectors = \[\]__*)
List object that must contain only collectors so we can easily perform operations with those collectors. It is subscriptible so you can use it as if it was a Python list.

*Arguments*:
- _collectors_ (list\[[Collector](#collector)\]): list of collectors.

*Attributes*:
- _collectors_ (list\[[Collector](#collector)\]): list of collectors.
- _names_ (list\[str\]): list of the names of the collectors list.
- _types_ (list\[bytes\]): list of the types of the collectors list.

### append(*__collector__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Append a collector to the list.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_collector_ ([Collector](#acollector)): the collector to append in the list.

### get_collector_by_name(*__name__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Get the collector by its name.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_name_ (str): name of the collector.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The Collector.

### get_collector_by_type(*__type__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Get the collector by its type.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_type_ (bytes): type of the collector.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The Collector.

### XOR(*__a, b__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**_STATIC_** Make the disjunction (by their names) between 2 list of collectors.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_a_ ([CollectorList](#collectorlistcollectors)): the first list to compare with.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_b_ ([CollectorList](#collectorlistcollectors)): the second list to compare with.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A list of the different collectors name.

### AND(*__a, b__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**_STATIC_** Make the junction (by their names) between 2 list of collectors.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_a_ ([CollectorList](#collectorlistcollectors)): the first list to compare with.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_b_ ([CollectorList](#collectorlistcollectors)): the second list to compare with.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A list of the same collectors name.