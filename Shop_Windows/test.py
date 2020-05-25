import sqlite3 as sq
import csv

def GetYearlySales(year):
	conn = sq.connect('sales')
	c = conn.cursor()

	years = c.execute("SELECT * FROM 'Daily Sales'").fetchall()

	dt = []

	for row in years:
		date,mn,yr = str(row[0]).split("/")
		dt.append(f'{date}/{mn}/{yr}')

	query = f"SELECT * FROM 'Daily Sales' WHERE Timed in ({','.join(['?']*len(dt))})"

	stsales1 = c.execute(query,dt).fetchall()

	dtsales = {}

	for row in stsales1:
		date,mn,yr = str(row[0]).split("/")
		if yr == str(year):
			prod = row[1]
			quan = row[2]
			total = row[4]
			if prod in dtsales:
				y = str(dtsales[prod])
				z = str(y).replace("(","")
				zn = z.replace(")", "")
				f = zn.replace(" ","")
				p,n = f.split(",")
				#print(p)
				dtsales.update({prod:(quan+int(p),total+int(n))})
			else:
				dtsales.update({prod:(quan,total)})
	filename = 'csvf/Sales2.csv'

	final = []

	with open(filename,'w',newline='') as file:
		w = csv.writer(file)
		w.writerow(["Date","Product","Quantity","Price"])
		for k,v in dtsales.items():
			newv = str(v).replace("(","")
			newv = newv.replace(")","")
			q,p = newv.split(",")
			finall = p.replace(" ","")
			final.append(finall)
			w.writerow(["",k.upper(),q,finall])

		#loop through the list and and calculate total
		totalsales = 0
		for i in range(0, len(final)):
			if len(final[i]) == 1:
				totalsales = final[0]
			else:
				totalsales = totalsales + int(final[i])
		w.writerow(["","","",""])
		w.writerow(["Jumla","","",totalsales])

	return ConvertCsvtoExcel.convertToExcel(filename)
