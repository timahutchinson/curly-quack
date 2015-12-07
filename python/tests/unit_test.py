import unittest
import sqlite3

class DatabaseTest(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect('../inventory.db')
        self.c = self.conn.cursor()

    def tearDown(self):
        self.conn.close()
    
    def test_db_contains_300_records(self):
        count = 0
        for row in self.c.execute('SELECT * FROM inventory'):
            count += 1
        self.assertEqual(count, 300)

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
    pass


if __name__ == '__main__':
    unittest.main()
