"""
Script to create fake inventory database of 300 items of 
500 quantity each, and random gaussian distribution of prices
"""

import datetime
import sqlite3
from os.path import join, exists
from os import environ, remove

import numpy as np

# Remove existing copy of database
if exists( join(environ['QVANTEL_DIR'], 'inventory.db') ):
    remove( join(environ['QVANTEL_DIR'],'inventory.db') )

conn = sqlite3.connect( join(environ['QVANTEL_DIR'], 'inventory.db') )
c = conn.cursor()
c.execute('''CREATE TABLE inventory (item text, price real, qty integer, updated text)''')

# Random prices drawn from gaussian distribution of mean 10 and sigma 4, not allowed to go negative
prices = np.abs(np.random.normal(10., 4, 300))

records = []
for i, price in enumerate(prices):
    records.append(('item%s' % '{0:3d}'.format(i), '{0:.2f}'.format(price), 500, str(datetime.datetime.now())))

c.executemany('INSERT INTO inventory VALUES (?,?,?,?)', records)

conn.commit()
conn.close()
