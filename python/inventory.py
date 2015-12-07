import numpy as np
import datetime
import os

class Inventory(object):
    
    def __init__(self):
        self.conn = sqlite3.connect( os.path.join(os.environ['QVANTEL_DIR'], 'inventory.db') )
        self.c = self.conn.cursor()

    def add_item(name, price, count):
        record = ('item%s' % i, '{0:.2f}'.format(price), int(count), str(datetime.datetime.now()))
        c.execute('INSERT INTO inventory VALUES (?,?,?,?)', record)
        conn.commit()
