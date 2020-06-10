from matplotlib import pyplot as plt
import base64
import os
try:
	from cryptography.hazmat.backends import default_backend
	from cryptography.hazmat.primitives import hashes
	from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
	from cryptography.fernet import Fernet
except:
	pass 
from pandas import read_csv
from tkinter import filedialog,messagebox
import csv
import sqlite3
from tkinter import messagebox
import tkinter as tk

dailysales_table = """
CREATE TABLE "Daily Sales" (
	"Timed"	TEXT,
	"Product"	TEXT,
	"Quantity"	INTEGER,
	"Buying Price"	INTEGER,
	"Price"	NUMERIC
);"""

addproducts_table = """
CREATE TABLE "AddProducts" (
	"Name"	TEXT,
	"Buy_Price"	NUMERIC,
	"Sell_Price"	NUMERIC,
	"Quantity"	NUMERIC
);"""

addproducts_temp = """
CREATE TABLE "AddTemp" (
	"Name"	TEXT,
	"Buy_Price"	NUMERIC,
	"Sell_Price"	NUMERIC,
	"Quantity"	NUMERIC
);"""

login_table = """
CREATE TABLE "login" (
	"User"	TEXT,
	"Password"	TEXT
);"""

madeni_table = """
CREATE TABLE "madeni" (
	"jina"	TEXT,
	"kiasi"	INTEGER
);
"""

closingstock_table = """
CREATE TABLE "closingstock" (
	"Timed"	INTEGER,
	"Mpesa"	INTEGER,
	"Tigo"	INTEGER,
	"Airtel"	INTEGER,
	"Closingcash"	INTEGER,
	"Total"	INTEGER
);
"""

openingstock_table = """
CREATE TABLE "openingstock" (
	"Timed"	INTEGER,
	"Mpesa"	INTEGER,
	"Tigo"	INTEGER,
	"Airtel"	INTEGER,
	"Opencash"	INTEGER,
	"Total"	INTEGER
);
"""

tempsales_table = """
CREATE TABLE "Temp Sales" (
	"Timed"	TEXT,
	"Product"	TEXT,
	"Quantity"	INTEGER,
	"Buying Price"	INTEGER,
	"Price"	NUMERIC
);
"""

daily_temp = """
CREATE TABLE "Daily Temp" (
	"Timed"	TEXT,
	"Product"	TEXT,
	"Quantity"	INTEGER,
	"Buying Price"	INTEGER,
	"Price"	NUMERIC
);
"""

class graph:
	def plot(x, y,fromdate,todate,xpos,ypos,text):
		plt.xlabel("Products Sold".upper())
		plt.ylabel("Quantity Sold".upper())
		plt.title(f'Shop Sales from {fromdate} to {todate}')
		plt.xticks(rotation=90)
		x_pos = xpos
		y_pos = ypos
		plt.text(x_pos,y_pos,text,transform=plt.gca().transAxes)
		plt.gcf().subplots_adjust(bottom=0.3)
		plt.bar(x,y)
		plt.ylim(ymin=0)
		plt.show()


class MonthlySales:

	def GetYearlySales(year):
		if year == 0:
			messagebox.showinfo("Error","Please Enter a valid Year")
		else:
			conn = sqlite3.connect('sales')
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
					x = c.execute("SELECT * FROM 'AddTemp'").fetchall()
					for i in range(0, len(x)):
						productname = x[i][0]
						if productname == k:
							prof = (Profit.profit(int(x[i][1]),int(x[i][3]),int(x[i][2]),int(q)))
							profitn.append(int(prof))

				#loop through the list and and calculate total
				totalsales = 0
				for i in range(0, len(final)):
					if len(final[i]) == 1:
						totalsales = final[0]
					else:
						totalsales = totalsales + int(final[i])
				w.writerow(["","","",""])
				w.writerow(["Jumla","","",totalsales])
				w.writerow(["Faida","","",sum(profitn)])

		return ConvertCsvtoExcel.convertToExcel(filename)

	def salesbymonth(fromdate, todate):
		conn = sqlite3.connect('sales')
		c = conn.cursor()

		#this works if month is the same

		#predefine our dates at the top
		date,mn1,yer=fromdate.split("/")

		#what if month has changed???

		date2,mn2,yer2=todate.split("/")

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

			#writing to the csv so as to export to excel
			filename = 'csvf/Sales1.csv'

			final = []
			profitn = []

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

					x = c.execute("SELECT * FROM 'AddTemp'").fetchall()
					for i in range(0, len(x)):
						productname = x[i][0]
						if productname == k:
							prof = (Profit.profit(int(x[i][1]),int(x[i][3]),int(x[i][2]),int(q)))
							profitn.append(int(prof))

				#loop through the list and and calculate total
				totalsales = 0
				for i in range(0, len(final)):
					if len(final[i]) == 1:
						totalsales = final[0]
					else:
						totalsales = totalsales + int(final[i])
				w.writerow(["","","",""])
				w.writerow(["Jumla","","",totalsales])
				w.writerow(["Faida","","",sum(profitn)])
				
		return ConvertCsvtoExcel.convertToExcel(filename)

class Profit:

	def profit(bp,qt,sp,nqt):
		priceforone = bp/qt
		profit = sp - priceforone
		value = sp*nqt

		return nqt*profit
class InitializeDatabase:

	def createdb():
		dbname = 'sales'
		conn = sqlite3.connect(dbname)
		c = conn.cursor()
		c.execute(dailysales_table)
		c.execute(addproducts_temp)
		c.execute(addproducts_table)
		c.execute(login_table)
		c.execute(madeni_table)
		c.execute(openingstock_table)
		c.execute(closingstock_table)
		c.execute(tempsales_table)
		c.execute(daily_temp)
		conn.commit()
		conn.close()

class PasswordEncrypter:

	def GenerateKey():
		password_provided = "Windows78!" # This is input in the form of a string
		password = password_provided.encode() # Convert to type bytes
		salt = b'salt_' # CHANGE THIS - recommend using a key from os.urandom(16), must be of type bytes
		kdf = PBKDF2HMAC(
		    algorithm=hashes.SHA256(),
		    length=32,
		    salt=salt,
		    iterations=100000,
		    backend=default_backend()
		)
		key = base64.urlsafe_b64encode(kdf.derive(password))
		return key

	def Encrypt(userpassword,key):

		msg = userpassword.encode()

		f = Fernet(key)

		encrypted = f.encrypt(msg)

		return encrypted


	def Decrypt(encryptedpassword,key):
		f = Fernet(key)
		decrypted = f.decrypt(encryptedpassword)

		return decrypted

class ConvertCsvtoExcel:

	def getCSV(file):
		return read_csv(file)

	def convertToExcel(file):
		try:
			x = ConvertCsvtoExcel.getCSV(file)
			export_file_path = filedialog.asksaveasfilename(defaultextension='.xlsx')
			x.to_excel(export_file_path, index=None, header=True)
			messagebox.showinfo("Success",f'exported successfully')
		except:
			messagebox.showinfo("Speciy Directory","Please Specify Place To Save")
			
class Stock:

	def checkstock():
		conn = sqlite3.connect('sales')
		c = conn.cursor()

		v = c.execute("SELECT * FROM AddProducts").fetchall()

		# try:
		prod = []

		for row in v:
			if row[3] <= 5:
				prod.append([row[0],row[3]])

		if len(prod) != 0:
			tk.messagebox.showinfo('Alert',f'Running out of Stock\n{prod}')
		else:
			pass
		# except:
		# 	pass
