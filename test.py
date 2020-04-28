#1 rim of paper is sold at 8000 Tsh
# so one paper is bought at 8000/500 = 16tsh
# 1 copy costs 100
# so profit for one copy = (100-16) = 84
# so profit for n copies = n * 84


def profit(bp,qt,sp,nqt):
	try:
		priceforone = bp/qt
		profit = sp - priceforone
		value = sp*nqt
	except ZeroDivisionError:
		"Check rows with zerob"
	return nqt*profit

import sqlite3

conn = sqlite3.connect('sales')
c = conn.cursor()


x = c.execute("SELECT * FROM 'AddProducts'").fetchall()

for i in range(0, len(x)):
	productname = x[i][0]
	bp = x[i][1]
	sp = x[i][2]
	qt = x[i][3]
	#print(productname,bp,sp,qt)
	print(productname,profit(bp,qt,sp,1))

