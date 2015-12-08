import datetime
from os import environ
from os.path import join, exists
import sqlite3
import operator

import numpy as np

from inventory import Inventory

class Cart(object):

    def __init__(self):
        self.inv = Inventory()
        self._basket = {}

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
            list.sort(key=lambda tup: tup[0])
        elif sortby.lower() == 'qty':
            list.sort(key=lambda tup: tup[1])
        elif sortby.lower() == 'price':
            list.sort(key=lambda tup: tup[2])
        else:
            print 'Cart can only be sorted by "item", "qty", or "price".'
            return
        for _tuple in list:
            yield _tuple




