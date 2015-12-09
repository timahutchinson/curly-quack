===========
curly-quack
===========

Qvantel task
------------

Contains scripts and modules for my Qvantel task - build a backend application
and API for a product catalog and shopping basket for a website.  It's written
in Python. The only package dependency outside the standard library is NumPy.
It's supposed to be a mock website backend, so I've tried to write it in a way
that would easily plug into a Django web interface (i.e., the classes here could
easily become models, and each method called by a view).

Set-up
------

The environmental variable QVANTEL_DIR needs to be set to point to the top directory
of the repo (i.e., the directory this file is in).
Then, a test database needs to be created by running the create_db.py script.

Classes
-------

There are two classes - an Inventory class (in inventory.py) to interface with the inventory database,
and a Cart class (in cart.py) to act as a shopping cart to interface with the Inventory class.
Methods within these classes are documunted in the code.

Testing
-------
There is a file for unit testing (unit_test.py), which contains unit tests for most methods
of the two above classes.  It is run as a script.