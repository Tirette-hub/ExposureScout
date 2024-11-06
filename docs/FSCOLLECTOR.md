# FileSystemCollector
Implementation of the File System collector to gather files on the machine. This collector inherits from the abstract Collector class.
It also contains the data structures used for the different collectibles which inherit from the abstract Collectible class.

For every object, it describes how it can be exported or loaded and how it is being run.

---------------------------------------------------
## Index
* [FileSystemCollector](#filesystemcollector)
	- [DiffFile](#difffilefile)
	---------------------------------------------------
	- [File](#filepath-metadata-size-content_hash)
		- [get_filename](#get_filename)
		- [get_metadata](#get_metadata)
		- [is_dir](#is_dir)
		- [is_file](#is_file)
		- [make_diff](#make_diffcollector-run_id_a-run_id_b-a-b-report)
	---------------------------------------------------
	- [Directory](#directorypath-metadata)
	    - [get_content](#get_content)
	    - [append](#appendfile)
	    - [append_all](#append_allfile_list)
	    - [has](#hasfile)
	    - [contains](#containsfile_list)
	    - [contains_filename](#contains_filenamefilename)
	    - [contains_inode](#contains_inodeinode)
	    - [is_parent_of](#is_parent_offile)
	---------------------------------------------------
	- [LinFileSystemCollector](#linfilesystemcollector)
	    - [set_rule](#set_rulerule)
	    - [set_rules](#set_rulesrules)
	    - [get_content](#get_content)
	    - [walk_through](#walk_throughpath)
        ---------------------------------------------------
	    - [make_diff](#make_diffrun_id_a-run_id_b-a-b-report)
	    - [import_diff_from_report](#import_diff_from_reportdata-run_ids-report)
        - [import_diff_from_report_db](#import_diff_from_report_dbdb_cursor-run_ids-report)
        - [get_report_tree_structure](#get_report_tree_structure)
        - [create_report_tables](#create_report_tablesdb_cursor)

---------------------------------------------------

## DiffFile(*__file__*)
Datastructure used to store files in reports.\
Implements method inherited from [ACollectible](./COLLECTOR.md#acollectible). Please refer to it for its methods description.

*Arguments*:
- _file_ ([File](#filepath-metadata-size-content_hash)): file data structure to convert.

*Attributes*:
- _element_name_ (str): name used to identify this collectible.

- _path_ (str): path to the file.
- _mode_ (int): matadata.st_mode.
- _inode_ (int): metadata.st_ino.
- _uid_ (int): metadata.st_uid.
- _gid_ (int): metadata.st_gid.
- _size_ (int): file size.
- _metadata_hash_ (bytes): hash of the metadata.
- _content_hash_ (bytes): hash of the file's content.

---------------------------------------------------

## File(*__path, metadata, size, content_hash__*)
Datastructure used to represent a Linux/Unix File.

_Arguments_:
- _path_ (str): path to the file.
- _metadata_ ([os.stat_result](https://docs.python.org/3/library/os.html#os.stat_result)): matadata of the file.
- _content_hash_ (bytes): hash of the file's content.

_Attributes_:
- _element_name_ (str): name used to identify this collectible.

- _path_ (str): path to the file.
- _mode_ (int): matadata.st_mode.
- _inode_ (int): metadata.st_ino.
- _uid_ (int): metadata.st_uid.
- _gid_ (int): metadata.st_gid.
- _size_ (int): file size.
- _metadata_hash_ (bytes): hash of the metadata.
- _content_hash_ (bytes): hash of the file's content.

### get_filename()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Get the name of the file.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Returns_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The name of the file.

### get_metadata()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Get the metadata values (except size).

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Returns_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A tupples containing the file's mode, inode, uid and gid.

### is_dir()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Check if the file is a directory.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Returns_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;True if the file is a directory, False otherwize.

### is_file()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Check if the file is a regular file.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Returns_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;True if the file is a regular file, False otherwize.

### make_diff(*__collector, run_id_a, run_id_b, a, b, report__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Run a deep recursive diff.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Arguments_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_collector_ ([ACollector](./COLLECTOR.md#acollector)): the reference to the File System collector class definition.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_run_id_a_ (str): run_id of the first collector.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_run_id_b_ (str): run_id of the second collector.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_a_ ([File](#filepath-metadata-size-content_hash)): the first file or directory (optional).\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_b_ ([File](#filepath-metadata-size-content_hash)): the second file or directory (optional).\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_report_ ([DiffReport](./REPORT.md#diffreportfirst_run_id-second_run_id)): the report where to add the differences.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Raises_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_ValueError_: No file or directory provided.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_ValueError_: Two files or directories provided but their inode do not match.

---------------------------------------------------

## Directory(*__path, metadata__*)
Datastructure used to represent a Linux/Unix Directory.\
Since a directory is also a file in Linux/Unix, it fully inherits from the [File](#filepath-metadata-size-content_hash) data structures. However it does not require the content hash since the content are the files themselves.

_Arguments_:
- _path_ (str): path to the directory.
- _metadata_ ([os.stat_result](https://docs.python.org/3/library/os.html#os.stat_result)): matadata of the directory.

_Attributes_:
- _element_name_ (str): name used to identify this collectible.

- _path_ (str): path to the directory.
- _mode_ (int): matadata.st_mode.
- _inode_ (int): metadata.st_ino.
- _uid_ (int): metadata.st_uid.
- _gid_ (int): metadata.st_gid.
- _size_ (int): metadata.st_size.
- _metadata_hash_ (bytes): hash of the metadata.
- _content_hash_ (bytes): (set to None here: not used)
- _content_ ([File](#filepath-metadata-size-content_hash)): list of files and directories it contains.

### get_content()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Get the content of the directory.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Returns_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A list containing [Directories](#directorypath-metadata) and [Files](#filepath-metadata-size-content_hash).

### append(*__file__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Append a file or a directory to this directory.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Arguments_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;file (File](#filepath-metadata-size-content_hash)): [File](#filepath-metadata-size-content_hash) or [Directory](#directorypath-metadata) object to add in this directory.

### append_all(*__file_list__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Append a list of files and directories to this directory.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Arguments:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;file_list (list\[[File](#filepath-metadata-size-content_hash)\]): list of [File](#filepath-metadata-size-content_hash) or [Directory](#directorypath-metadata) object to add in this directory.

### has(*__file__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Verify if a file or a directory is in this directory.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Arguments_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;file ([File](#filepath-metadata-size-content_hash)): [File](#filepath-metadata-size-content_hash) or [Directory](#directorypath-metadata) object to check.

### contains(*__file_list__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Verify if a list of file or a directory is contained in this directory.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Arguments_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;file_list (list\[[File](#filepath-metadata-size-content_hash)\]): list of [File](#filepath-metadata-size-content_hash) or [Directory](#directorypath-metadata) object to check.

### contains_filename(*__filename__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Verify if the directory contains a file with the given name.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Arguments_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;filename (str): name to check.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Returns_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;True if the directory contains a file or a directory with the given name, False otherwise.

### contains_inode(*__inode__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;verify if the directory contains a file with the given inode.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Arguments_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;inode (int): inode to check.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Returns_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;True if the directory contains a file or a directory with the given inode, False otherwise.

### is_parent_of(*__file__*):
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Verify that this directory is a parent or an ancestor of a given file.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Returns_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;True if file is in the sub-tree

---------------------------------------------------

## LinFileSystemCollector()
Linux/Unix FileSystem collector.\
Inherits from [ACollector](./COLLECTOR.md#acollector).

_Attributes_:
- Inherits from [ACollector](./COLLECTOR.md#acollector)

### set_rule(*__rule__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Add directory to walk.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Arguments_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;rule (str): path to the directory to walk.

### set_rules(*__rules__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Add a list of directories to walk.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Arguments_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;rules (list[str]): list of path to the directories to walk.

### get_content()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Get the list of File System collector root files and directories it contains.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Returns_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A list of files or directories.

### walk_through(self, path)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Walk through a given path to collect all the data it contains. If the path points to a directory, it therefore also collects all the directories and files it contains (DFS on the File System of the machine). 

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Arguments_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;path (str): path to walk through.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Returns_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The [File](#filepath-metadata-size-content_hash) or [Directory](#directorypath-metadata) object collected that represent the one pointed by the given path on the machine File System.

### make_diff(*__run_id_a, run_id_b, a, b, report__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Static method used to get the difference between two "Linux/Unix File System" collectors.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Arguments_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_run_id_a_ (str): run_id of the first collector.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_run_id_b_ (str): run_id of the second collector.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_a_ ([LinFileSystemCollector](#linfilesystemcollector)): the first collectors.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_b_ ([LinFileSystemCollector](#linfilesystemcollector)): the second collector.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_report_ ([DiffReport](./REPORT.md#diffreportfirst_run_id-second_run_id)): the report where to add the differences.

### import_diff_from_report(*__run_ids, report__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Extract [LinFileSystemCollector](#linfilesystemcollector)'s diff elements from a report file.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Arguments:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_data_ (bytes): a bytes stream representing the elements associated to this collector in the report.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_run_ids_ (list[str]): the ordered list of the snapshot ids from which come the report elements.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_report_ ([DiffReport](./REPORT.md#diffreportfirst_run_id-second_run_id)): datastructure in which to store the recovered data.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Returns:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_True_ if the Diff Elements associated to [LinFileSystemCollector](#linfilesystemcollector) data have been successfully imported.

### import_diff_from_report_db(*__db_cursor, report_id, run_ids, report__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Extract [LinFileSystemCollector](#linfilesystemcollector)'s diff elements from a database.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Arguments_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_db_cursor_ ([Cursor](doc.python.org/3/library/sqlite3.html#sqlite3.Cursor)): pointer to the database.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_report_id_ (str): identifier of the report being imported.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_run_ids_ (list[str]): the ordered list of the snapshot ids from which come the report elements.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_report_ ([DiffReport](./REPORT.md#diffreportfirst_run_id-second_run_id)): datastructure in which to store the recovered data.

### get_report_tree_structure()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Get the structure of the Collector used for the report.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Returns_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A python dict with an empty list of Directories.

### create_report_tables(*__db_cursor__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Static method used to create the different tables used by this collector for report structure in the specified database.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Note: modifications are not committed here.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_Arguments_:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_db_cursor_ ([Cursor](doc.python.org/3/library/sqlite3.html#sqlite3.Cursor)): sqlite3 cursor pointing to the database in which the tables must be created.