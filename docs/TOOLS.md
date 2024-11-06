# tools
It provides useful tools such as computing the md5 hash of a file or implements functions to use logical _xor_ and _and_ on python lists.

---------------------------------------------------

## Index
* [tools](#tools)
    - [xor_list](#xor_lista-b)
    - [and_list](#and_lista-b)
    - [get_file_hash](#get_file_hashfilename-buf_size--65536)
    ---------------------------------------------------
    - [ResultThread](#resultthreadargs-kwargs)

---------------------------------------------------

## xor_list(_**a, b**_)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Make the disjunction (by their names) between 2 lists.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_a_ (list): the first list to compare with.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_b_ (list): the second list to compare with.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A tupple with the elements of the first list and the ones of the second.

## and_list(_**a, b**_)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Make the junction (by their names) between 2 list of collectors.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_a_ (list): the first list to compare with.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_b_ (list): the second list to compare with.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A list of the selements that appears on both the provided lists.

## get_file_hash(_**filename, buf_size = 65536**_)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Get the MD5 hash of a file.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_filename_ (str): path to the file to get its hash.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_buf_size_ (int): buffer size. Helps reading big files. (default: 64kb = 65536b)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A byte string representing the MD5 hash of the given file.

---------------------------------------------------

## ResultThread(*__\*args, \*\*kwargs__*)
Inherits from [threading.Thread](https://docs.python.org/3/library/threading.html#threading.Thread) class and only features the result handling of the target function it ran via the _result_ attribute.