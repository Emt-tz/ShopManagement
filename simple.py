
import sqlite3

def plot(x, y):
	from matplotlib import pyplot as plt
	plt.xlabel("Products")
	plt.ylabel("Quantity")
	plt.title("Shop Sales from 1/5/2020 to 20/5/2020")
	plt.xticks(rotation=90)
	plt.gcf().subplots_adjust(bottom=0.3)
	plt.plot(x,y)
	plt.ylim(ymin=0)
	mng = plt.get_current_fig_manager()
	mng.full_screen_toggle()
	return plt.show()

def plotmonthly():
	conn = sqlite3.connect('sales')
	c = conn.cursor()

	#this works if month is the same
	fromdate = "1/5/2020"
	todate = "30/5/2020"
	#predefine our dates at the top
	date,mn1,yer=fromdate.split("/")

	#what if month has changed???

	date2,mn2,yer2=todate.split("/")

	x = []
	yr = []

	if mn1 != mn2:
		messagebox.showinfo("Monthly Support","Only 1 Month Export is Supported\ni.e 1/4/2020-30/4/2020 and not\n1/4/2020-1/5/2020")
	else:
		dt = []

		dtsales = {}

		for i in range(int(date),int(date2)+1):
			dt.append(f'{i}/{mn1}/{yer}')

		for i in range(0, len(dt)):
			stsales1 = c.execute("SELECT * FROM 'Daily Sales' WHERE Timed=?",(dt[i],)).fetchall()

			for row in stsales1:
				product = row[1]
				quantity = row[2]
				price = row[4]

				if product in dtsales:
					y = str(dtsales[product])
					z = str(y).replace("(","")
					zn = z.replace(")","")
					f = zn.replace(" ","")
					p,n = f.split(",")
					dtsales.update({product:(quantity+int(p),price+int(n))})
				else:
					dtsales.update({product:(quantity,price)})
		for k,v in sorted(dtsales.items(),key=lambda x: x[1]):
			newv = str(v).replace("(","")
			newv = newv.replace(")","")
			q,p = newv.split(",")
			x.append(k)
			yr.append(q)
	print(x)
	print(yr)

	return plot(x,yr)

plotmonthly()