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
        """Create inventory instance."""
        self.inv = Inventory()

    def tearDown(self):
        """Close database opened by self.inv."""
        self.inv.close()

    def test_add_record_to_database(self):
        nrecords = self.count_records()
        self.inv.add_item('test_item', 15.00, 200)
        self.assertEqual(self.count_records(), nrecords+1)

    def test_remove_record_from_database(self):
        nrecords = self.count_records()
        self.inv.remove_item('test_item')
        self.assertEqual(self.count_records(), nrecords-1)

    def test_query_sort(self):
        for field in ['name', 'price', 'qty', 'updated']:
            for direction in ['ascending', 'descending']:
                count = 0
                for row in self.inv.query_sort(field, direction):
                    count += 1
                self.assertEqual(count, 100)

    def test_count_records(self):
        self.assertEqual(self.count_records(), self.inv.nrecords)

    def test_next_page(self):
        pass

    def test_update_qty(self):
        self.inv.update_qty('item000', 250)
        self.inv.c.execute('SELECT qty FROM inventory WHERE item=?', ('item000',))
        self.assertEqual(self.inv.c.fetchone()[0], 250)
        self.inv.update_qty('item000', 500)

    def test_update_price(self):
        original_price = self.inv.c.execute('SELECT price FROM inventory WHERE item=?', ('item000',)).fetchone()[0]
        self.inv.update_price('item000', 10)
        self.inv.c.execute('SELECT price FROM inventory WHERE item=?', ('item000',))
        self.assertEqual(self.inv.c.fetchone()[0], 10)
        self.inv.update_price('item000', original_price)

    def test_query_by_price(self):
        original_price1 = self.inv.c.execute('SELECT price FROM inventory WHERE item=?', ('item050',)).fetchone()[0]
        original_price2 = self.inv.c.execute('SELECT price FROM inventory WHERE item=?', ('item150',)).fetchone()[0]
        self.inv.update_price('item050', 50)
        self.inv.update_price('item150', 70)
        # Check with low and high price range
        count = 0
        for row in self.inv.query_by_price(40,80):
            count += 1
        self.assertEqual(count, 2)
        # Check with only low price
        count = 0
        for row in self.inv.query_by_price(40):
            count += 1
        self.assertEqual(count, 2)
        # We also expect all records to be returned with no prices set
        count = 0
        for row in self.inv.query_by_price():
            count += 1
        self.assertEqual(count, self.count_records())

    def count_records(self):
        return self.inv.c.execute('SELECT Count(*) FROM inventory').fetchone()[0]


if __name__ == '__main__':
    unittest.main()
