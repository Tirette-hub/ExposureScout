# report
In this file, you can find the definition of a report and all the objects related to it. Basically, a report is represented as a python dictionnary containing a list of elements that was different from the two snapshots being compared for every collector they used.

*Data*:
- CREATED
- DELETED
- MODIFIED


---------------------------------------------------
## Index
* [report](#report)
    - [parse_snap_header](#parse_snap_headerdata)
    - [parse_rpt_header](#parse_rpt_headerdata)
    ---------------------------------------------------
    - [AlreadyExistsException](#alreadyexistsexception)
    ---------------------------------------------------
    - [UnknownValueException](#unknownvalueexception)
    ---------------------------------------------------
    - [DiffElement](#diffelementrun_id-element-type)
        - [get_collectible_name](#get_collectible_name)
        - [to_bytes](#to_bytesrun_id_bytes)
        - [from_bytes](#from_bytesrun_ids-element_class)
        - [export_db](#export_dbreport_id-db_cursor)
    ---------------------------------------------------
    - [DiffReport](#diffreportfirst_run_id-second_run_id)
        - [get_collectors_names](#get_collectors_names)
        - [add_diff_element](#add_diff_elementelement-collector_name)
        - [add_no_diff_element](#add_no_diff_elementcollector_name-type)
        - [add_no_diff_collector](#add_no_diff_collectorcollector_name)
        - [to_bytes](#to_bytes)
        - [read_collector_from_bytes](#read_collector_from_bytesdata-run_ids-collector)
        - [export_db](#export_dbreport_id-db)

---------------------------------------------------

## parse_snap_header(_**data**_):
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Parse the header of a snapshot binary file.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_data_ (bytes): header as bytes to parse.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A list of tupple containing the type of containers and their position in the file.

---------------------------------------------------

## parse_rpt_header(_**data**_):
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Parse the header of a report binary file.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_data_ (bytes): header as bytes to parse.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A tupple containing:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. an ordered list of the snapshot id's of the compared snapshots in the report;\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. a list of tupple containing the type of containers and their position in the file.

---------------------------------------------------

## AlreadyExistsException()
Inherits from python built-in _Exception_.

---------------------------------------------------

## UnknownValueException()
Inherits from python built-in _Exception_.

---------------------------------------------------

## DiffElement(_**run_id, element, type**_)
Representation of an element that differs during a comparison.\
It can either be a new element or an element that has changed between two snapshots.

*Arguments*:
- _run_id_ (str): identifier of the snapshot the element is associated to.
- _element_ (Object): the objects used by a collector to store what they collect. (e.g. [User](./USERSCOLLECTOR.md#useruid-name-groups) in [UsersCollector](./USERSCOLLECTOR.md#userscollector) to store users)
- _type_ (str): type of the element. (e.g. [User](./USERSCOLLECTOR.md#useruid-name-groups) in [UsersCollector](./USERSCOLLECTOR.md#userscollector) has the "user" type)

*Attributes*:
- _run_id_ (str): identifier of the snapshot the element is associated to.
- _element_ (Object): the objects used by a collector to store what they collect. (e.g. [User](./USERSCOLLECTOR.md#useruid-name-groups) in [UsersCollector](./USERSCOLLECTOR.md#userscollector) to store users)
- _type_ (str): type of the element. (e.g. [User](./USERSCOLLECTOR.md#useruid-name-groups) in [UsersCollector](./USERSCOLLECTOR.md#userscollector) has the "user" type)

### get_collectible_name()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Get the name of the collectible being stored.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The element_name of the stored collectible.

### to_bytes(_**run_id_bytes**_):
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Encode an element of the tree of differences.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_run_id_bytes_ (dict{str:bytes}): python dictionary mapping the run_id's used in the report to their respective byte identifier.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A bytes stream represdenting the element.

### from_bytes(_**run_ids, element_class**_):
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**_STATIC_** Decode an element of the tree of differences.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_data_ (bytes): a bytes stream representing a DiffElement.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_run_ids_ (list\[str\]): the snapshot id's used for the report.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_element_class_ ([Collectible](./COLLECTOR.md#acollectible)): reference to the class of the element.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A tupple containing:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. a bytes stream represdenting the element;\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. the rest of the unread bytes that are not part of this DiffElement datastructure.

### export_db(_**report_id, db_cursor**_)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Insert the element into the database.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_report_id_ (str): identifier of the report the element is linked to.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_db_cursor_ ([Cursor](doc.python.org/3/library/sqlite3.html#sqlite3.Cursor)): cursor pointing to the sqlite3 database.

---------------------------------------------------

## DiffReport(_**first_run_id, second_run_id**_)
Report of the differences between two snapshots.

*Arguments*:
- _first_run_id_ (str): identifier of the first snapshot to compare with.
- _second_run_id_ (str): identifier of the second snapshot to compare with.

*Attributes*:
- _first_run_id_ (str): identifier of the first snapshot to compare with.
- _second_run_id_ (str): identifier of the second snapshot to compare with.
- _diff_elements_ \(dict\{str : dict\{str : list\[[DiffElement](#diffelementrun_id-element-type)\]\}\}\): tree of differences.

### get_collectors_names()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Get a list of all the collectors' names in the tree of differences.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A list of collector's names.

### add_diff_element(_**element, collector_name**_)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Add an element to the tree of differences.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_element_ ([DiffElement](#diffelementrun_id-element-type)): the element to add in the tree.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_collector_name_ (str): the name of the collector that is compared.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Raises*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_[UnknownValueException](#unknownvalueexception)_: run id does not match between the snapshots beeing compared and the snapshot from which the element comes from.

### add_no_diff_element(_**collector_name, type**_)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Add the name of an element type of a collector for which there were no changes between the two snapshots.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(e.g. for [LinUsersCollector](./USERSCOLLECTOR.md#linuserscollector), there could be a new user without new group or sudoer)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_collector_name_ (str): the name of the collector that is compared.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_type_ (str): the name of the element type of the collector that is compared.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Raises*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_[AlreadyExistsException](#alreadyexistsexception)_: the element type already is in the report for the given collector name.

### add_no_diff_collector(_**collector_name**_)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Add the name of a collector that has not changed between the two snapshots.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_collector_name_ (str): the name of the collector that is compared.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Raises*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_[AlreadyExistsException](#alreadyexistsexception)_: the collecton name already is in the report.

### to_bytes()
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Encode the tree of differences.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A bytes stream representing\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. the header with preliminar informations over the collectors in the tree;\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. the tree of differences.

### read_collector_from_bytes(_**data, run_ids, collector**_)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Decode a bytes stream into a DiffReport for a single collector.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_data_ (bytes): the bytes stream that represent the DiffReport.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_run_ids_ (list\[str\]): ordered list of the snapshot id's compared in the report. (order is the same as in the report file)\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_collectors_ (list\[Class\]): ordered list of references to collectors classes used in the report. (order is the same as in the report file)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;True if the decoding was successful.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Raises*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_ValueError_: collectors do not match

### export_db(_**report_id, db**_):
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Export the report in the specified database.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_report_id_ (str): identifer of the report.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_db_ (str): path to the database.