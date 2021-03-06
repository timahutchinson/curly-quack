import unittest
import sqlite3
from os.path import join
from os import remove, environ

from inventory import Inventory
from cart import Cart

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
        for field in ['item', 'price', 'qty', 'updated']:
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

    def test_query_by_name(self):
        # Test should return same number of results regardless of sort
        count = 0
        for row in self.inv.query_by_name('item0', 0, 100, 'item'):
            count += 1
        self.assertEqual(count, 100)
        count = 0
        for row in self.inv.query_by_name('item0', 0, 100, 'price'):
            count += 1
        self.assertEqual(count, 100)
        count = 0
        for row in self.inv.query_by_name('item0', 0, 100):
            count += 1
        self.assertEqual(count, 100)
        count = 0
        for row in self.inv.query_by_name('item0'):
            count += 1
        self.assertEqual(count, 100)

    def test_get_qty(self):
        self.inv.update_qty('item100', 1000)
        self.assertEqual(self.inv.view_qty('item100'), 1000)
        self.inv.update_qty('item100', 1000)

    def count_records(self):
        return self.inv.c.execute('SELECT Count(*) FROM inventory').fetchone()[0]


class CartTest(unittest.TestCase):
    
    def setUp(self):
        self.cart = Cart()
        self.inv = Inventory()

    def tearDown(self):
        self.inv.close()

    def test_add_items_to_basket(self):
        # Test adding item, make sure it's in cart and inventory updates to reflect that
        old_qty= self.inv.view_qty('item050')
        self.cart.add_item('item050', 10)
        self.assertEqual(self.cart.basket('item050'), 10)
        self.assertEqual(self.inv.view_qty('item050'), old_qty-10)
        self.inv.update_qty('item050', 500)
        # Test adding more to cart than inventory contains
        self.cart._basket['item050'] = 0 # Temporary kluge 
        self.cart.add_item('item050', 600)
        self.assertEqual(self.cart.basket('item050'), 500)
        self.assertEqual(self.inv.view_qty('item050'), 0)
        self.inv.update_qty('item050', 500)

    def test_remove_items_from_basket(self):
        self.cart.add_item('item050', 10)
        self.cart.remove_item('item050',5)
        self.assertEqual(self.cart.basket('item050'), 5)
        self.assertEqual(self.inv.view_qty('item050'), 495)

    def test_edit_items(self):
        # Change to a quantity greater than you already have
        self.cart.edit_item('item050', 50)
        self.cart.edit_item('item050', 70)
        self.assertEqual(self.cart.basket('item050'), 70)
        self.assertEqual(self.inv.view_qty('item050'), 430)
        self.cart.remove_item('item050', 70)
        # Add more than are in inventory
        self.cart.edit_item('item050', 1000)
        self.assertEqual(self.inv.view_qty('item050'), 0)
        self.assertEqual(self.cart.basket('item050'), 500)
        self.cart.remove_item('item050', 500)
        # Change to a quantity less than what you already have
        self.cart.add_item('item050', 100)
        self.cart.edit_item('item050', 50)
        self.assertEqual(self.inv.view_qty('item050'), 450)
        self.assertEqual(self.cart.basket('item050'), 50)
        self.cart.remove_item('item050', 50)
        
    def test_items_total(self):
        self.cart.add_item('item100', 100)
        cost = 100 * self.inv.view_price('item100')
        self.assertEqual(self.cart.items_total(), cost)
        self.cart.remove_item('item100', 100)

    def test_list_items(self):
        self.cart.add_item('item100', 100)
        # Test listing sorted by item name
        for _tuple in self.cart.list_items('item'):
            self.assertEqual(_tuple, ('item100', 100, self.inv.view_price('item100')))
        # Test listing sorted by qty
        for _tuple in self.cart.list_items('price'):
            self.assertEqual(_tuple, ('item100', 100, self.inv.view_price('item100')))
        # Test listing sorted by price
            self.assertEqual(_tuple, ('item100', 100, self.inv.view_price('item100')))
        self.cart.remove_item('item100', 100)

if __name__ == '__main__':
    unittest.main()
