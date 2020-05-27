#This gui is for single customer mode

#Functionalities
	#Enter transaction for a single customer and as well as print out the receipt

#what is needed, 
	#customer name
	#item
	#quantity
	#total price
	#date of purchase and exact purchase time
	#shop name and address

#the products choosen should imediately be synced to the database

from tkinter import *
import tkinter as tk
from tkinter import ttk
import sqlite3 as sq
import datetime as dt

import subprocess as s
from tkinter import messagebox

curtime = dt.datetime.now()

time = str(curtime)

number = "0693677033"
curtime = f'\nDate:\t\t   {time[0:10]}\nTime:\t\t   {time[11:19]}\nPhone:\t\t   {number}\n'

class Customer(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title("Emt Customer Mode")
		self.colors = ['cadetblue','white','lightgrey']

		self.name = StringVar()
		self.product = StringVar()
		self.quantity = IntVar()
		self.displayreceipt = StringVar()

		self.total = 0 
		self.price = 0 

		self.date = dt.datetime.now()

		self.font = "time 10 bold"
		self.geometry('600x600+400+50')
		self.resizable(False,False)
		self.Mainui()


	def Mainui(self):
	#=========================Frames==============================================================
		topframe = Frame(bg=self.colors[0],width=600,height=600)
		topframe.place(relx=0,rely=0)

		leftframe = Frame(bg=self.colors[2],width=300,height=550)
		leftframe.place(relx=0.03,rely=0.05)

		rightframe = Frame(bg=self.colors[1],width=280,height=550)
		rightframe.place(relx=0.52,rely=0.05)
	#=======================Labels and Entries=====================================================

		customerlabel = Label(leftframe,text="Name")
		customerlabel.place(relx=0.05,rely=0.105)

		customername = Entry(leftframe,width=21,bd=2,font=self.font,textvariable=self.name)
		customername.place(relx=0.3,rely=0.1)

		productlabel = Label(leftframe,text="Product")
		productlabel.place(relx=0.05,rely=0.205)

		def products():
			conn = sq.connect('sales')
			c = conn.cursor()
			stitems = c.execute("SELECT * FROM AddProducts").fetchall() 
			items = []
			for row in stitems:
				for i in range(0, len(row)):
					x = row[0]
				items.append(x.upper())
				
			return sorted(items)
		productcombo = ttk.Combobox(leftframe,width=23,textvariable=self.product,values=products())
		productcombo.place(relx=0.3,rely=0.205)

		quantitylabel = Label(leftframe,text="Quantity")
		quantitylabel.place(relx=0.05,rely=0.305)

		quantityentry = Entry(leftframe,width=21,bd=2,font=self.font,textvariable=self.quantity)
		quantityentry.place(relx=0.3,rely=0.3)
	#=======================Text Display==========================================================
		displayreceipt = Text(rightframe,width=32,height=31,bd=8)
		displayreceipt.place(relx=0,rely=0)
	#=======================Buttons===============================================================
		def logic():
			conn = sq.connect('sales')
			c = conn.cursor()

			displayreceipt.insert(END,f'\n\n\n--------------------------------')
			displayreceipt.insert(END,f'\nTotal:\t\t\t{self.total}')
			displayreceipt.insert(END,f'\n--------------------------------\n')

			newtime = f'{self.date.day}/{self.date.month}/{self.date.year}'

			PrintButton.config(state="normal")

		def add():
			#add each sale to Daily Sales table
			conn = sq.connect('sales')
			c = conn.cursor()

			stitems = c.execute("SELECT * FROM AddProducts").fetchall()

			stprice = {}

			for stitem in stitems:
			            #print(stitem)
			            j = [j for j in range(0, len(stitem))]
			            i = [i for i in range(0, len(stitem))]
			            
			            stprice.update({stitem[j[0]]:stitem[i[2]]})
			
			for k,v in stprice.items():
				if self.product.get() == k:
					self.price = v
					x = self.price
					y = self.quantity.get()
					self.total = x * y

			newtime = f'{self.date.day}/{self.date.month}/{self.date.year}'
			#print(newtime)
			values1 = (newtime,self.product.get(),self.quantity.get(),self.price,self.total)

			values = (values1)
			#===================Database delete all empty values==========================
			var = "0"
			c.executemany("DELETE FROM 'Daily Sales' WHERE Quantity=?", var)
			conn.commit()

			c.executemany("DELETE FROM 'Daily Sales' WHERE Price=?", var)
			conn.commit()

			c.execute("INSERT INTO 'Daily Sales' VALUES (?,?,?,?,?)", values)
			conn.commit()

			c.execute("INSERT INTO 'Temp Sales' VALUES (?,?,?,?,?)", values)
			conn.commit()

			#v = c.execute("SELECT * FROM 'Daily Sales' WHERE ROWID = (SELECT MAX(ROWID) FROM 'Daily Sales');").fetchall()

			v = c.execute("SELECT * FROM 'Temp Sales' WHERE Timed=?", (str(newtime),)).fetchall()
			
			displayreceipt.delete(1.0,END)
			displayreceipt.insert(END,
				f'    Emt Stationery Receipt\n--------------------------------\n{curtime}\n--------------------------------\n')
			x = f'--------------------------------\n'
			message = f'From:\t{self.name.get().upper()}\n{x}Products\t\tQty\tTotal\n'
			displayreceipt.insert(END,message)
			displayreceipt.insert(END,f'--------------------------------\n')

			transactions = {}
			
			for row in v:
				#print(row[0])
				i = [i for i in range(0, len(row))]
				j = [j for j in range(0, len(row))]

				x = row[i[1]]
				x2 = row[j[2]]
				x3 = row[j[4]]

				if x in transactions:
					transactions.update({x:(x2,x3)})
				else:
					transactions.update({x:(x2,x3)})
			
			final = []

			for k,v in transactions.items():
				newv = str(v).replace("(","")
				newv = newv.replace(")", "")

				q,p = newv.split(",")
				finall = p.replace(" ","")
				final.append(int(finall))

				values = f'{k}\t\t{q}\t{p}\n'

				displayreceipt.insert(END,values)
			self.total = sum(final)

		def printf():

			conn = sq.connect('sales')
			c = conn.cursor()
			
			newtime = f'{self.date.day}/{self.date.month}/{self.date.year}'
			
			total = displayreceipt.get('1.0',tk.END)

			print(str(total))

			# lpr = s.Popen("/usr/bin/lpr",stdin=s.PIPE)

			# x = tk.messagebox.askyesno("Print Receipt","Do you wish to print the receipt?")
			# if x == False:
			# 	pass
		
			# if x == True:
			# 	lpr.stdin.write(total.encode())
			# 	stdout, stderr = lpr.communicate(input=total.encode())
			c.execute("DELETE FROM 'Temp Sales' WHERE Timed=?", (str(newtime),))
			conn.commit()


		AddButton = Button(leftframe,text="Add",bg=self.colors[0],command=add)
		AddButton.place(relx=0.05,rely=0.905)

		TotalButton = Button(leftframe,text="Total",bg=self.colors[0],command=logic)
		TotalButton.place(relx=0.35,rely=0.905)

		PrintButton = Button(leftframe,text="Print",bg=self.colors[0],command=printf,state="disabled")
		PrintButton.place(relx=0.65,rely=0.905)

if __name__ == '__main__':
	Customer().mainloop()