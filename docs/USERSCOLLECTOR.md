# UsersCollector
Implementation of the users collector to gather users, groups and sudoers on the machine. This collector inherits from the abstract Collector class. It also contains the data structures used for the different collectibles which inherit from the abstract Collectible class.

For every object, it describes how it can be exported or loaded and how it is being run.

---------------------------------------------------
## Index
* [UsersCollector](#userscollector)
	- [parse_user_line](#parse_user_lineline)
	- [parse_group_line](#parse_group_lineline)
	---------------------------------------------------
	- [User](#useruid-name-groups)
	---------------------------------------------------
	- [Group](#groupgid-name)
	---------------------------------------------------
	- [Sudoer](#sudoeruid)
	---------------------------------------------------
	- [LinUsersCollector](#linuserscollector)
	    - [get_users](#get_users)
	    - [get_groups](#get_groups)
	    - [get_sudoers](#get_sudoers)
	    - [get_hashes](#get_hashes)
	    - [collect_users](#collect_users)
	    - [collect_groups](#collect_groups)
	    - [collect_sudoers](#collect_sudoers)
	    - [collect_passwd_hash](#collect_passwd_hash)
	    - [collect_group_hash](#collect_group_hash)
        ---------------------------------------------------
	    - [make_diff](#make_diffrun_id_a-run_id_b-a-b-report)
	    - [import_diff_from_report](#import_diff_from_reportdata-run_ids-report)
        - [import_diff_from_report_db](#import_diff_from_report_dbdb_cursor-run_ids-report)
        - [get_report_tree_structure](#get_report_tree_structure)
        - [create_report_tables](#create_report_tablesdb_cursor)

---------------------------------------------------

## parse_user_line(*__line__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Parse a line representing a user after running the collector bash script to extract data so it is easier to fill in the User data structure.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_line_ (str): the string line to parse.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A tupple with the uid, the user name, and the groups id it's in.

---------------------------------------------------

## parse_group_line(*__line__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Parse a line representing a group after running the collector bash script to extract data so it is easier to fill in the Group data structure.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_line_ (str): the string line to parse.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A tupple with the gid, the group name.

---------------------------------------------------

## User(*__uid, name, groups__*)
Datastructure used to represent a Linux/Unix User.\
Implements method inherited from [ACollectible](./COLLECTOR.md#acollectible). Please refer to it for its methods description.

*Arguments*:
- _uid_ (int): user id.
- _name_ (str): user's name.
- _groups_ (list[int]): list of groups' gid the user is in.

*Attributes*:

	element_name = "User"

- _element_name_ (str): name used to identify this collectible.

- _uid_ (int): user id.
- _name_ (str): user's name.
- _groups_ (list[int]): list of groups' gid the user is in.

---------------------------------------------------

## Group(*__gid, name__*)
Datastructure used to represent a Linux/Unix Group.\
Implements method inherited from [ACollectible](./COLLECTOR.md#acollectible). Please refer to it for its methods description.

*Arguments*:
- _gid_ (int): group id.
- _name_ (str): group's name.

*Attributes*:

	element_name = "Group"

- _element_name_ (str): name used to identify this collectible.

- _gid_ (int): group id.
- _name_ (str): group's name.

---------------------------------------------------

## Sudoer(*__uid__*)
Datastructure used to represent the sudoers.\
Implements method inherited from [ACollectible](./COLLECTOR.md#acollectible). Please refer to it for its methods description.

*Arguments*:
- _uid_ (int): sudoer's user id.

*Attributes*:

	element_name = "Sudoer"

- _element_name_ (str): name used to identify this collectible.

- _uid_ (int): sudoer's user id.

---------------------------------------------------

## LinUsersCollector()
Users, Groups and Sudoers collector.\
Implements method inherited from [ACollector](./COLLECTOR.md#acollector). Please refer to it for more methods.

*Attributes*: Inherits from [ACollector](./COLLECTOR.md#acollector).

	name = "Users Collector"
	descr = """
			For Linux/Unix platforms only.
			This module collects all the users and groups as well as sudoers available on this machine.
			"""
	snapshot_elemnt_id = b"\x00"

### get_users()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Get the list of collected users.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A list of [Users](#useruid-name-groups). (None if collector has not run yet)

### get_groups()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Get the list of collected groups.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A list of [Groups](#groupgid-name). (None if collector has not run yet)

### get_sudoers()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Get the list of collected sudoers.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A list of [Sudoers](#sudoeruid). (None if collector has not run yet)

### get_hashes()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Get the two collected hashes (passwd, group).

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A tupple with both hashes.

### collect_users()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Executes the bash script that will collect all the users.

### collect_groups()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Executes the bash script that will collect all the groups.

### collect_sudoers()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Executes the bash script that will collect the list of sudoers.

### collect_passwd_hash()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Computes the /etc/passwd file md5 hash.

### collect_group_hash()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Computes the /etc/group file md5 hash.

### make_diff(*__run_id_a, run_id_b, a, b, report__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_**Static**_ method used to get the difference between two "Linux/Unix users" collectors. **SHOULD** be used only if the two hashes have been checked and are different between both the collectors.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*: Inherits from [ACollector](./COLLECTOR.md#acollector).

### import_diff_from_report(*__data, run_ids, report__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_**Static**_: Extract LinUsersCollector's elements from a report file.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_data_ (bytes): a bytes stream representing the elements associated to this collector in the report.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_run_ids_ (list[str]): the ordered list of the snapshot ids from which come the report elements.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_report_ ([DiffReport](./REPORT.md#diffreportfirst_run_id-second_run_id)): datastructure in which to store the recovered data.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;True if the [DiffElements](./REPORT.md#diffelementrun_id-element-type) associated to LinUsersCollector data have been successfully imported.

### import_diff_from_report_db(*__db_cursor, report_id, run_ids, report__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_**Static**_: Extract LinUsersCollector's diff elements from a database.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_db_cursor_ ([Cursor](doc.python.org/3/library/sqlite3.html#sqlite3.Cursor)): pointer to the database.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_report_id_ (str): identifier of the report being imported.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_run_ids_ (list[str]): the ordered list of the snapshot ids from which come the report elements.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_report_ ([DiffReport](./REPORT.md#diffreportfirst_run_id-second_run_id)): datastructure in which to store the recovered data.

### get_report_tree_structure()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_**Static**_: Get the structure of the Collector used for the report.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A python dict with an empty list of users, an empty list of groups, and an empty list of sudoers.

### create_report_tables(*__db_cursor__*):
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_**Static**_ method used to create the different tables used by this collector for report structure in the specified database.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Note: modifications are not committed here.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_db_cursor_ ([Cursor](doc.python.org/3/library/sqlite3.html#sqlite3.Cursor)): sqlite3 cursor pointing to the database in which the tables must be created.