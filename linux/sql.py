import sqlite3 as sq
import datetime as dt 

conn = sq.connect('sales')
c = conn.cursor()

x = dt.datetime.now()

# print(x.date)
valuestime = f'{x.day}/{x.month}/{x.year}'
# value1 = ()

bp = 100
qn = 50
total = bp*qn
for i in range(0, 3000):
	values = (f'Copy{i}',bp+i,bp+(2+i),qn)

	var = c.executemany("INSERT INTO 'AddProducts' VALUES (?,?,?,?)", (values,))
conn.commit()



