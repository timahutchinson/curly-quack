import unittest
import sqlite3
from os.path import join
from os import remove, environ

from inventory import Inventory

class DatabaseTest(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect( join(environ['QVANTEL_DIR'], 'inventory.db') )
        self.c = self.conn.cursor()

    def tearDown(self):
        self.conn.close()
    
    def test_db_contains_records(self):
        count = 0
        for row in self.c.execute('SELECT * FROM inventory'):
            count += 1
        self.assertNotEqual(count, 0)

    def test_entry_types(self):
        # Check if price is a float and has 2 digits after decimal
        for price in self.c.execute('SELECT price FROM inventory'):
            price = price[0]
            self.assertEqual(type(price), type(1.))
            self.assertEqual(len('{0:.2f}'.format(price).split('.')[1]), 2)
        # Check if qty is int
        for qty in self.c.execute('SELECT qty FROM inventory'):
            qty = qty[0]
            self.assertEqual(type(qty), type(1))

class InventoryTest(unittest.TestCase):
    
    def setUp(self):
        """Create test database"""
        self.conn = sqlite3.connect('test.db')
        self.c = self.conn.cursor()

    def tearDown(self):
        self.conn.close()
        remove('test.db')

    def test_add_record_to_database(self):
        nrecords = self.count_records()
        inv = Inventory()
        inv.add_item('test_item', 15.00, 200)
        self.assertEqual(self.count_records(), nrecords+1)

    def count_records(self):
        count = 0
        for row in self.c.execute('SELECT * FROM inventory'):
            count += 1
        return count


if __name__ == '__main__':
    unittest.main()
