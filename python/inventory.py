import datetime
from os import environ
from os.path import join, exists
import sqlite3

import numpy as np

class Inventory(object):
    
    def __init__(self):
        self.open_db()
        self.count_records()

    def open_db(self):
        if exists( join(environ['QVANTEL_DIR'], 'inventory.db') ):
            self.conn = sqlite3.connect( join(environ['QVANTEL_DIR'], 'inventory.db') )
            self.c = self.conn.cursor()
            print 'Database succesfully opened.'
        else:
            print 'Database doesn\'t exist. Use create_db.py to create it.'

    def count_records(self):
        self.nrecords = 0
        for row in self.c.execute('SELECT * FROM inventory'):
            self.nrecords += 1

    def close(self):
        self.conn.commit()
        self.conn.close()

    def add_item(self, name, price, count):
        record = ('%s' % name, '{0:.2f}'.format(price), int(count), str(datetime.datetime.now()))
        self.c.execute('INSERT INTO inventory VALUES (?,?,?,?)', record)
        self.conn.commit()

    def remove_item(self, name):
        name = ('%s' % name,)
        self.c.execute('DELETE FROM inventory WHERE item=?', name)
        self.conn.commit()

    def update_qty(self, name, newqty):
        record = (newqty, name)
        self.c.execute('UPDATE inventory SET qty = ? WHERE item=?', record)
        self.conn.commit()

    def update_price(self, name, newprice):
        record = ('{0:.2f}'.format(newprice), name)
        self.c.execute('UPDATE inventory SET price = ? WHERE item=?', record)
        self.conn.commit()

    def query_sort(self, sort_field='name', direction='ascending'):
        self.sort_field = sort_field
        self.direction = direction
        self.offset = 100
        if self.direction.lower() == 'ascending':
            if self.sort_field.lower() == 'name':
                return self.c.execute('SELECT * FROM inventory ORDER BY item ASC LIMIT 100')
            elif self.sort_field.lower() == 'price':
                return self.c.execute('SELECT * FROM inventory ORDER BY price ASC LIMIT 100')
            elif self.sort_field.lower() == 'qty':
                return self.c.execute('SELECT * FROM inventory ORDER BY qty ASC LIMIT 100')
            elif self.sort_field.lower() == 'updated':
                return self.c.execute('SELECT * FROM inventory ORDER BY updated ASC LIMIT 100')
            else:
                print 'Sortable fields are "name", "price", "qty", and "updated".'
        elif self.direction.lower() == 'descending':
            if self.sort_field.lower() == 'name':
                return self.c.execute('SELECT * FROM inventory ORDER BY item DESC LIMIT 100')
            elif self.sort_field.lower() == 'price':
                return self.c.execute('SELECT * FROM inventory ORDER BY price DESC LIMIT 100')
            elif self.sort_field.lower() == 'qty':
                return self.c.execute('SELECT * FROM inventory ORDER BY qty DESC LIMIT 100')
            elif self.sort_field.lower() == 'updated':
                return self.c.execute('SELECT * FROM inventory ORDER BY updated DESC LIMIT 100')
            else:
                print 'Sortable fields are "name", "price", "qty", and "updated".'
        else:
            print 'Sorts can be ascending or descending.'

    def next_page(self):
        if self.offset >= 100:
            if (self.offset+100) <= self.nrecords:
                self.offset += 100
                if self.direction.lower() == 'ascending':
                    if self.sort_field.lower() == 'name':
                        return self.c.execute('SELECT * FROM inventory ORDER BY item ASC LIMIT 100 OFFSET ?', (self.offset-100,))
                    elif self.sort_field.lower() == 'price':
                        return self.c.execute('SELECT * FROM inventory ORDER BY price ASC LIMIT 100 OFFSET ?', (self.offset-100,))
                    elif self.sort_field.lower() == 'qty':
                        return self.c.execute('SELECT * FROM inventory ORDER BY qty ASC LIMIT 100 OFFSET ?', (self.offset-100,))
                    elif self.sort_field.lower() == 'updated':
                        return self.c.execute('SELECT * FROM inventory ORDER BY updated ASC LIMIT 100 OFFSET ?', (self.offset-100,))
                elif self.direction.lower() == 'descending':
                    if self.sort_field.lower() == 'name':
                        return self.c.execute('SELECT * FROM inventory ORDER BY item DESC LIMIT 100 OFFSET ?', (self.offset-100,))
                    elif self.sort_field.lower() == 'price':
                        return self.c.execute('SELECT * FROM inventory ORDER BY price DESC LIMIT 100 OFFSET ?', (self.offset-100,))
                    elif self.sort_field.lower() == 'qty':
                        return self.c.execute('SELECT * FROM inventory ORDER BY qty DESC LIMIT 100 OFFSET ?', (self.offset-100,))
                    elif self.sort_field.lower() == 'updated':
                        return self.c.execute('SELECT * FROM inventory ORDER BY updated DESC LIMIT 100 OFFSET ?', (self.offset-100,))
            else:
                print 'Already on last page.'
                return []
        else:
            self.query_sort()

    def prev_page(self):
        if self.offset > 100:
            self.offset -= 100
            if self.direction.lower() == 'ascending':
                if self.sort_field.lower() == 'name':
                    return self.c.execute('SELECT * FROM inventory ORDER BY item ASC LIMIT 100 OFFSET ?', (self.offset-100,))
                elif self.sort_field.lower() == 'price':
                    return self.c.execute('SELECT * FROM inventory ORDER BY price ASC LIMIT 100 OFFSET ?', (self.offset-100,))
                elif self.sort_field.lower() == 'qty':
                    return self.c.execute('SELECT * FROM inventory ORDER BY qty ASC LIMIT 100 OFFSET ?', (self.offset-100,))
                elif self.sort_field.lower() == 'updated':
                    return self.c.execute('SELECT * FROM inventory ORDER BY updated ASC LIMIT 100 OFFSET ?', (self.offset-100,))
            elif self.direction.lower() == 'descending':
                if self.sort_field.lower() == 'name':
                    return self.c.execute('SELECT * FROM inventory ORDER BY item DESC LIMIT 100 OFFSET ?', (self.offset-100,))
                elif self.sort_field.lower() == 'price':
                    return self.c.execute('SELECT * FROM inventory ORDER BY price DESC LIMIT 100 OFFSET ?', (self.offset-100,))
                elif self.sort_field.lower() == 'qty':
                    return self.c.execute('SELECT * FROM inventory ORDER BY qty DESC LIMIT 100 OFFSET ?', (self.offset-100,))
                elif self.sort_field.lower() == 'updated':
                    return self.c.execute('SELECT * FROM inventory ORDER BY updated DESC LIMIT 100 OFFSET ?', (self.offset-100,))
        else:
            print 'Already on first page.'
            return []

    def query_by_price(self, low=0, high=None):
        if high is not None:
            return self.c.execute('SELECT * FROM inventory WHERE price >= ? AND price <= ? ORDER BY price', (low, high))
        else:
            return self.c.execute('SELECT * FROM inventory WHERE price >= ? ORDER BY price', (low,))
