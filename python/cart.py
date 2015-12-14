import datetime
from os import environ
from os.path import join, exists
import sqlite3
import operator
import json

import numpy as np

from inventory import Inventory

class Cart(object):

    def __init__(self):
        self.inv = Inventory()
        self._basket = {}

    def to_JSON(self):
        # JSON serializability
        del self.inv.c
        del self.inv.conn
        print (json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4))
        self.inv = Inventory()

    def basket(self, name):
        try:
            return self._basket[name.lower()]
        except KeyError:
            print 'Item not in basket.'
            return 0

    def add_item(self, name, qty):
        if self.inv.view_qty(name.lower()) >= qty:
            if name.lower() in self._basket:
                self._basket[name.lower()] += qty
            else:
                self._basket[name.lower()] = qty
            self.inv.update_qty(name, self.inv.view_qty(name.lower())-qty)
        else:
            print 'Inventory only has %s of this item' % self.inv.view_qty(name.lower())
            if name.lower() in self._basket:
                self._basket[name.lower()] += self.inv.view_qty(name.lower())
            else:
                self._basket[name.lower()] = self.inv.view_qty(name.lower())
            self.inv.update_qty(name, 0)

    def remove_item(self, name, qty):
        if name.lower() in self._basket:
            if self.basket(name.lower()) >= qty:
                self._basket[name.lower()] -= qty
                self.inv.update_qty(name, self.inv.view_qty(name.lower())+qty)
            else:
                self.inv.update_qty(name, self.inv.view_qty(name.lower())+self._basket[name.lower()])
                self._basket[name.lower()] = 0

    def edit_item(self, name, qty):
        if qty < 0:
            return
        diff = qty - self.basket(name.lower())
        if diff > 0:
            # Need to add items from inventory
            if self.inv.view_qty(name.lower()) >= diff:
                self._basket[name.lower()] = qty
                self.inv.update_qty(name, self.inv.view_qty(name.lower())-diff)
            else:
                print 'Only %s in inventory' % self.inv.view_qty(name.lower())
                self._basket[name.lower()] = self.inv.view_qty(name.lower())
                self.inv.update_qty(name, 0)
        elif diff < 0:
            # Remove items from cart
            self._basket[name.lower()] = qty
            self.inv.update_qty(name, self.inv.view_qty(name.lower())-diff)
        else:
            # Cart already has qty items
            pass

    def items_total(self):
        """Return total cost of all items in cart."""
        total = 0
        for item in self._basket:
            total += self._basket[item] * self.inv.c.execute('SELECT price FROM inventory WHERE item=?', (item,)).fetchone()[0]
        return total

    def list_items(self, sortby='item'):
        list = []
        for key in self._basket:
            list.append( (key, self._basket[key], self.inv.view_price(key)) )
        if sortby.lower() == 'item':
            self.sort_list_of_tuples(list,0)
        elif sortby.lower() == 'qty':
            self.sort_list_of_tuples(list,1)
        elif sortby.lower() == 'price':
            self.sort_list_of_tuples(list,2)
        else:
            print 'Cart can only be sorted by "item", "qty", or "price".'
            return
        for _tuple in list:
            yield _tuple

    def query_by_price(self, lowprice=0, highprice=None, sortby='item'):
        list = []
        if highprice is not None:
            for key in self._basket:
                this_price = self.inv.view_price(key)
                if this_price >= lowprice and this_price <= highprice:
                    list.append( (key, self._basket[key], self.inv.view_price(key)) )
        else:
            for key in self._basket:
                this_price = self.inv.view_price(key)
                if this_price >= lowprice:
                    list.append( (key, self._basket[key], self.inv.view_price(key)) )
        if sortby.lower() == 'item':
            self.sort_list_of_tuples(list,0)
        elif sortby.lower() == 'qty':
            self.sort_list_of_tuples(list,1)
        elif sortby.lower() == 'price':
            self.sort_list_of_tuples(list,2)
        else:
            print 'Cart can only be sorted by "item", "qty", or "price".'
            return
        for _tuple in list:
            yield _tuple

    def sort_list_of_tuples(self, list, index):
        return list.sort(key=lambda tup: tup[index])

    def query_by_name(self, name, lowprice=0, highprice=None, sortby='item'):
        list = []
        if highprice is not None:
            for key in self._basket:
                this_price = self.inv.view_price(key)
                if this_price >= lowprice and this_price <= highprice and key.startswith(name.lower()):
                    list.append( (key, self._basket[key], this_price) )
        else:
            for key in self._basket:
                this_price = self.inv.view_price(key)
                if this_price >= lowprice and key.startswith(name.lower()):
                    list.append( (key, self._basket[key], this_price) )
        if sortby.lower() == 'item':
            self.sort_list_of_tuples(list,0)
        elif sortby.lower() == 'qty':
            self.sort_list_of_tuples(list,1)
        elif sortby.lower() == 'price':
            self.sort_list_of_tuples(list,2)
        else:
            print 'Cart can only be sorted by "item", "qty", or "price".'
            return
        for _tuple in list:
            yield _tuple
            



