Dependencies
------------

  * Python 2.7
  * MySQL-python 1.2.5

To install Python dependencies, run: "pip install -r requirements.txt"


Usage
-----
    
python dbTableCopier.py table_name db1_ip db1_user db1_passwd db1_name db2_ip db2_user db2_passwd db2_name 

Example:
    python dbTableCopier.py titles localhost root '' employees localhost root '' employees_without_title

Tests
-----
To run unit test:
    python unitTest.py

There is an option to run full test which check row by row from two real databases tables.
Before You run it you should configure it. To do so change varables at the beginnig of fullTest.py.
    python fullTest.py
