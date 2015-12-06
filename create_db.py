"""
Script to create fake inventory database of 300 items of 
500 quantity each, and random gaussian distribution of prices
"""

import datetime
import sqlite3

import numpy as np

conn = sqlite3.connect('inventory.db')
c = conn.cursor()
c.execute('''CREATE TABLE inventory (item text, price real, qty integer, updated text)''')

prices = np.abs(np.random.normal(10., 4, 300))

records = []
for i, price in enumerate(prices):
    records.append(('item%s' % i, '%.02f' % price, 500, str(datetime.datetime.now())))

c.executemany('INSERT INTO inventory VALUES (?,?,?,?)', records)

conn.commit()
conn.close()
