# core
This is where the core functionalities of the application are implemented.

You can extend or modify it but keep in mind that any modification in those files may corrupt the application if not handled carefully.

---------------------------------------------------
## Index
* [core](#core)
	---------------------------------------------------
	- [Index](#index)
	---------------------------------------------------
	- [analysis_manager](./AM.md#analysis_manager)
	    - [AnalysisManager](./AM.md#analysismanager)
	        - [is_running](./AM.md#is_running)
	        - [get_running_snapshot](#get_running_snapshot)
	        - [save](./AM.md#saverun_id-method--bin-db--none-buf_size--64)
	        - [load](./AM.md#loadrun_id-method--bin-db--none-buf_size--64)
	        - [dump](./AM.md#dumprun_id)
	        - [dump_report](./AM.md#dump_reportreport_id)
	        - [pause_running](./AM.md#pause_running)
	        - [resume_running](./AM.md#resume_running)
	        - [quit_running](./AM.md#quit_running)
	        - [show_running_status](./AM.md#show_running_status)
	        - [run_snapshot](./AM.md#run_snapshotrun_id-collectors)
	        - [make_diff](./AM.md#make_difffirst_run-second_run-report_id--none)
	        - [export_report](./AM.md#export_reportreport_id-method--bin-db--none-buf_size--64)
	        - [import_report](./AM.md#import_reportreport_id-method--bin-db--none-buf_size--64)
	---------------------------------------------------
	- [report](./REPORT.md#report)
	    - [parse_snap_header](./REPORT.md#parse_snap_headerdata)
	    - [parse_rpt_header](./REPORT.md#parse_rpt_headerdata)
	    ---------------------------------------------------
	    - [AlreadyExistsException](./REPORT.md#alreadyexistsexception)
	    - [UnknownValueException](./REPORT.md#unknownvalueexception)
	    ---------------------------------------------------
	    - [DiffElement](./REPORT.md#diffelementrun_id-element-type)
	        - [get_collectible_name](./REPORT.md#get_collectible_name)
	        - [to_bytes](./REPORT.md#to_bytesrun_id_bytes)
	        - [from_bytes](./REPORT.md#from_bytesrun_ids-element_class)
	        - [export_db](./REPORT.md#export_dbreport_id-db_cursor)

	    - [DiffReport](./REPORT.md#diffreportfirst_run_id-second_run_id)
	        - [get_collectors_names](./REPORT.md#get_collectors_names)
	        - [add_diff_element](./REPORT.md#add_diff_elementelement-collector_name)
	        - [add_no_diff_element](./REPORT.md#add_no_diff_elementcollector_name-type)
	        - [add_no_diff_collector](./REPORT.md#add_no_diff_collectorcollector_name)
	        - [to_bytes](./REPORT.md#to_bytes)
	        - [read_collector_from_bytes](./REPORT.md#read_collector_from_bytesdata-run_ids-collector)
	        - [export_db](./REPORT.md#export_dbreport_id-db)
	---------------------------------------------------
	- [tools](./TOOLS.md#tools)
	    - [xor_list](./TOOLS.md#xor_lista-b)
	    - [and_list](./TOOLS.md#and_lista-b)
	    - [get_file_hash](./TOOLS.md#get_file_hashfilename-buf_size--65536)
	    ---------------------------------------------------
	    - [ResultThread](./TOOLS.md#resultthreadargs-kwargs)
	---------------------------------------------------
	- [octets](./OCTETS.md#octets)
	    - [VarInt](./OCTETS.md#varint)
	        - [to_bytes](./OCTETS.md#to_bytesvalue)
	        - [get_len](./OCTETS.md#get_lenb_array)
	        - [from_bytes](./OCTETS.md#from_bytesb_array)