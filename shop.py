#created 10/04/2020
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.font import Font
import time,os
import sqlite3
import datetime as dt
import sys
from test2 import ConvertCsvtoExcel as cexcel
import csv
from test2 import Profit as profit
from tkcalendar import DateEntry


class ShopLogin(tk.Tk):
	#=================================================================================================================#
	def __init__(self):
		super().__init__()
		self.title("Emt Management System")
		self.labels = []
		self.turn = True
		self.count = 0
		self.txt = []
		self.date = dt.datetime.now()
		self.textinput = []
		self.height = 1

		self.conn = sqlite3.connect('sales')
		self.c = self.conn.cursor()

		self.stitems = self.c.execute("SELECT * FROM AddProducts").fetchall() 

		self.box1 =  StringVar()
		self.box2 =  StringVar()
		self.box3 =  StringVar()
		self.box4 =  StringVar()
		self.box5 =  StringVar()
		self.box6 =  StringVar()
		self.box7 =  StringVar()
		self.box8 =  StringVar()
		self.box9 =  StringVar()
		self.box10 =  StringVar()
	

		self.entryq1 = IntVar()
		self.entryq2 = IntVar()
		self.entryq3 = IntVar()
		self.entryq4 = IntVar()
		self.entryq5 = IntVar()
		self.entryq6 = IntVar()
		self.entryq7 = IntVar()
		self.entryq8 = IntVar()
		self.entryq9 = IntVar()
		self.entryq10 = IntVar()

		self.entryD1 = IntVar()
		self.entryD2 = IntVar()
		self.entryD3 = IntVar()
		self.entryD4 = IntVar()
		self.entryD5 = IntVar()
		self.entryD6 = IntVar()
		self.entryD7 = IntVar()
		self.entryD8 = IntVar()
		self.entryD9 = IntVar()
		self.entryD10 = IntVar()

		self.entryP1 = IntVar()
		self.entryP2 = IntVar()
		self.entryP3 = IntVar()
		self.entryP4 = IntVar()
		self.entryP5 = IntVar()
		self.entryP6 = IntVar()
		self.entryP7 = IntVar()
		self.entryP8 = IntVar()
		self.entryP9 = IntVar()
		self.entryP10 = IntVar()

		self.debtnameentry = StringVar()
		self.debtcashentry = IntVar()

		self.majinacombo = StringVar()

		self.entrytv = IntVar()
		self.entrypv = IntVar()

		self.font = Font(family="Times New Roman bold", size=10)


		self.WIDTH, self.HEIGHT = 1095, 690

		self.btny = 672
		self.btnx = 0
		#label height and width
		self.labelheight = 1
		self.labelwidth = 33
		#entries y and x values
		self.entry1y = 58
		self.entry2y = 78
		self.entry3y = 98
		self.entry4y = 118
		self.entry5y = 138
		self.entry6y = 158
		self.entry7y = 178
		self.entry8y = 198
		self.entry9y = 218
		self.entry10y = 238
		#combobox x value
		self.entrybx = 190
		#quantity x values
		self.entryqx = 550
		#sell price x values
		self.entrydx = 930
		#price x values
		self.entrypx = 1180
		#profit entry and total sales
		self.xvalue = 1040
		self.yvalue = 300
		self.total1y = 642
		self.profit1y = 672
		#buttons frame width and height
		self.buttonsframewidth = 1040
		self.buttonsframeheight = 800
		#getsales entry and button
		self.entrydatey = 420
		self.entrydatex = 50
		self.entrydatebuttonx = 220

		self.sale_date_entry = StringVar()

		self.salesframe = Frame(bg="lightgrey", width=40, height=900, pady=3).place(x=self.xvalue-300,y=self.yvalue)

		self.daily = tk.Text(self.salesframe,width=40, height=20, font=self.font,relief=RAISED)
		self.daily.place(x=self.xvalue-270, y=self.yvalue-20)

		self.entryt = Entry(bg="white",textvariable=self.entrytv, font=self.font, state='normal',justify='right',bd=5,width=39)
		self.entryt.place(x=self.xvalue-270, y=self.total1y-20)

		self.entryp = Entry(bg="white",textvariable=self.entrypv, font=self.font, state='normal',justify='right',bd=5,width=39)
		self.entryp.place(x=self.xvalue-270, y=self.profit1y-20)

		self.lb = StringVar()
		self.lbtotal = StringVar()

		self.geometry(f'{self.WIDTH}x{self.HEIGHT}+150+0')

		self.resizable(False, False)
		
		self.Sales()    
		#self.todayssales()
	#=================================================================================================================#

	def ShopItems(self):
	#=================================================================================================================#
		#This Function Just Returns all products input by user and combobox displays them
		stitems = self.stitems
		
		items = []

		for row in stitems:
			for i in range(0, len(row)):
				x = row[0]
			items.append(x.upper())
			
		return sorted(items)
	#=================================================================================================================#
	def madeninames(self,event=None):
		conn= sqlite3.connect('sales')
		c = conn.cursor()

		names = c.execute("SELECT * FROM madeni").fetchall()

		majina = []

		for row in names:
			for i in range(0, len(row)):
				x = row[0]
			majina.append(x)

		return sorted(majina)
	#=================================================================================================================#
	def updatecomboboxlist(self):
		liste = self.madeninames()
		self.debtview12['values'] = liste
	#=================================================================================================================#

	def Sales(self):
		#Top Header Arrangement
	#===========================All Frames to Control The Main GUI are Placed Here ========================================#
		headingframe = Frame(bg="lightgrey",width=1920, height=200).place(x=0,y=0)

		Shop_title = Label(headingframe,text="Welcome to Emt Shop Management System".upper(),bg="lightgrey",fg="green",font="time 14", bd=0,height=2,relief=None)
		Shop_title.place(y=0, x=280)

		heading1 = tk.Label(headingframe,text="",bg="lightgrey",fg="blue",font=self.font, bd=0,pady=3,height=3, width=20, relief=None,)
		heading1.grid(row=0, column=0)

		buttonframe = Frame(bg="lightgrey", width=self.buttonsframewidth-282, height=self.buttonsframeheight, pady=3).place(x=1, y=210)

		maincanvas = Canvas(self,width=1920,height=231,bg="cadetblue")
		maincanvas.place(x=0,y=50)
		#Label to Warn user to not conflict with database   
		Product = tk.Label(text="Product".upper(),bg="white",font="time 12 bold", height=self.labelheight, width=self.labelwidth, relief=RAISED)
		Product.grid(row=1, column=0)

		Quantity = tk.Label(text="Quantity".upper(),bg="white",font="time 12 bold", height=self.labelheight, width=self.labelwidth, relief=RAISED)
		Quantity.grid(row=1, column=1)

		Discount = tk.Label(text="Sell Price".upper(),bg="white",font="time 12 bold", height=self.labelheight, width=self.labelwidth, relief=RAISED)
		Discount.grid(row=1, column=2)

		# Price = tk.Label(text="Price".upper(),bg="white",font="time 11 bold", height=self.labelheight, width=self.labelwidth, relief=RAISED)
		# Price.grid(row=1, column=3)

			#============================Combobox,Entry Defined Here==========================================================#
	#   #Deal with the combobox here start at row=2
		box1 = ttk.Combobox(textvariable=self.box1,values=self.ShopItems(),font="time 12")
		box2 = ttk.Combobox(textvariable=self.box2,values=self.ShopItems(),font="time 12")
		box3 = ttk.Combobox(textvariable=self.box3,values=self.ShopItems(),font="time 12")
		box4 = ttk.Combobox(textvariable=self.box4,values=self.ShopItems(),font="time 12")
		box5 = ttk.Combobox(textvariable=self.box5,values=self.ShopItems(),font="time 12")
		box6 = ttk.Combobox(textvariable=self.box6,values=self.ShopItems(),font="time 12")
		box7 = ttk.Combobox(textvariable=self.box7,values=self.ShopItems(),font="time 12")
		box8 = ttk.Combobox(textvariable=self.box8,values=self.ShopItems(),font="time 12")
		box9 = ttk.Combobox(textvariable=self.box9,values=self.ShopItems(),font="time 12")
		box10 = ttk.Combobox(textvariable=self.box10,values=self.ShopItems(),font="time 12")

		maincanvas.create_window(self.entrybx,self.entry1y-18,window=box1)
		maincanvas.create_window(self.entrybx,self.entry2y-18,window=box2)
		maincanvas.create_window(self.entrybx,self.entry3y-18,window=box3)
		maincanvas.create_window(self.entrybx,self.entry4y-18,window=box4)
		maincanvas.create_window(self.entrybx,self.entry5y-18,window=box5)
		maincanvas.create_window(self.entrybx,self.entry6y-18,window=box6)
		maincanvas.create_window(self.entrybx,self.entry7y-18,window=box7)
		maincanvas.create_window(self.entrybx,self.entry8y-18,window=box8)
		maincanvas.create_window(self.entrybx,self.entry9y-18,window=box9)
		maincanvas.create_window(self.entrybx,self.entry10y-18,window=box10)
	
	# #============================================================================================================

	# #============================Quantity Entry Defined Here========================================================
	#   #Quantity Entry Boxes
		entryq1 = tk.Entry(bg="white",textvariable=self.entryq1,font=self.font)
		entryq2 = tk.Entry(bg="white",textvariable=self.entryq2,font=self.font)
		entryq3 = tk.Entry(bg="white",textvariable=self.entryq3,font=self.font)
		entryq4 = tk.Entry(bg="white",textvariable=self.entryq4,font=self.font)
		entryq5 = tk.Entry(bg="white",textvariable=self.entryq5,font=self.font)
		entryq6 = tk.Entry(bg="white",textvariable=self.entryq6,font=self.font)
		entryq7 = tk.Entry(bg="white",textvariable=self.entryq7,font=self.font)
		entryq8 = tk.Entry(bg="white",textvariable=self.entryq8,font=self.font)
		entryq9 = tk.Entry(bg="white",textvariable=self.entryq9,font=self.font)
		entryq10 = tk.Entry(bg="white",textvariable=self.entryq10,font=self.font)

		maincanvas.create_window(self.entryqx,self.entry1y-18,window=entryq1)
		maincanvas.create_window(self.entryqx,self.entry2y-18,window=entryq2)
		maincanvas.create_window(self.entryqx,self.entry3y-18,window=entryq3)
		maincanvas.create_window(self.entryqx,self.entry4y-18,window=entryq4)
		maincanvas.create_window(self.entryqx,self.entry5y-18,window=entryq5)
		maincanvas.create_window(self.entryqx,self.entry6y-18,window=entryq6)
		maincanvas.create_window(self.entryqx,self.entry7y-18,window=entryq7)
		maincanvas.create_window(self.entryqx,self.entry8y-18,window=entryq8)
		maincanvas.create_window(self.entryqx,self.entry9y-18,window=entryq9)
		maincanvas.create_window(self.entryqx,self.entry10y-18,window=entryq10)



	#   #bind all q entries with the enter key
		entryq1.bind("<Return>",self.todayssales)
		entryq2.bind("<Return>",self.todayssales)
		entryq3.bind("<Return>",self.todayssales)
		entryq4.bind("<Return>",self.todayssales)
		entryq5.bind("<Return>",self.todayssales)
		entryq6.bind("<Return>",self.todayssales)
		entryq7.bind("<Return>",self.todayssales)
		entryq8.bind("<Return>",self.todayssales)
		entryq9.bind("<Return>",self.todayssales)
		entryq10.bind("<Return>",self.todayssales)

	#============================================================================================================

	#============================Price Entry Defined Here============================================================
		#Sell Price Entries D[i].
		entryD1 = tk.Entry(bg="white",textvariable=self.entryD1,font=self.font,state="disabled")
		entryD2 = tk.Entry(bg="white",textvariable=self.entryD2,font=self.font,state="disabled")
		entryD3 = tk.Entry(bg="white",textvariable=self.entryD3,font=self.font,state="disabled")
		entryD4 = tk.Entry(bg="white",textvariable=self.entryD4,font=self.font,state="disabled")
		entryD5 = tk.Entry(bg="white",textvariable=self.entryD5,font=self.font,state="disabled")
		entryD6 = tk.Entry(bg="white",textvariable=self.entryD6,font=self.font,state="disabled")
		entryD7 = tk.Entry(bg="white",textvariable=self.entryD7,font=self.font,state="disabled")
		entryD8 = tk.Entry(bg="white",textvariable=self.entryD8,font=self.font,state="disabled")
		entryD9 = tk.Entry(bg="white",textvariable=self.entryD9,font=self.font,state="disabled")
		entryD10 = tk.Entry(bg="white",textvariable=self.entryD10,font=self.font,state="disabled")

		maincanvas.create_window(self.entrydx,self.entry1y-18,window=entryD1)
		maincanvas.create_window(self.entrydx,self.entry2y-18,window=entryD2)
		maincanvas.create_window(self.entrydx,self.entry3y-18,window=entryD3)
		maincanvas.create_window(self.entrydx,self.entry4y-18,window=entryD4)
		maincanvas.create_window(self.entrydx,self.entry5y-18,window=entryD5)
		maincanvas.create_window(self.entrydx,self.entry6y-18,window=entryD6)
		maincanvas.create_window(self.entrydx,self.entry7y-18,window=entryD7)
		maincanvas.create_window(self.entrydx,self.entry8y-18,window=entryD8)
		maincanvas.create_window(self.entrydx,self.entry9y-18,window=entryD9)
		maincanvas.create_window(self.entrydx,self.entry10y-18,window=entryD10)
	#===================================================================================================================================
	#===================================================================================================================================
		# GrandTotal Button
		grandtotal = tk.Button(buttonframe,text="Total".upper()
			,bg="cadetblue",fg="white",font=self.font,
			bd=0,height=1, width=12, 
			relief=None,command=self.todayssales)
		grandtotal.place(x=20, y=self.btny-93)

		undobtn = Button(buttonframe,font=self.font,text="UNDO SALE".upper(),bg="cadetblue",fg="white",command=self.UndoLastSale,bd=0,height=1, width=20)
		undobtn.place(x=140, y=self.btny-93)
		# Exit Button
		logout = tk.Button(buttonframe,text="Exit".upper()
			,bg="cadetblue",fg="white",font=self.font,
			bd=0,height=1, width=12, 
			relief=None,command=self.logout)
		logout.place(x=320, y=self.btny-93)
	#=================================================================================================================#
				#We need name, item, debt
		debtcanvas = Canvas(self,width=238,height=370,bg="lightgrey")
		debtcanvas.place(x=490,y=301)

		madenilabel = Label(fg="cadetblue",text="Debt and Expenses")
		debtcanvas.create_window(108, 10, window=madenilabel)

		self.debtnameentry12 = Entry(bg="white",textvariable=self.debtnameentry,font=self.font,width=26)
		self.debtnameentry.set("")
		debtcanvas.create_window(108,45,window=self.debtnameentry12)


		self.debtcashentry12 = Entry(bg="white",textvariable=self.debtcashentry,font=self.font,width=26)
		debtcanvas.create_window(108,75,window=self.debtcashentry12)


		self.debtview12 = ttk.Combobox(textvariable=self.majinacombo,postcommand=self.updatecomboboxlist,font="time 12")
		debtcanvas.create_window(108, 200,window=self.debtview12)

		self.submitbutton = Button(font=self.font,text="Add".upper(),bg="cadetblue",fg="white",command=self.submittodb,bd=0,height=1, width=6)
		self.submitbutton.place(x=560, y=self.entrydatey+10)

	
		self.removebutton = Button(font=self.font,text="Del".upper(),bg="cadetblue",fg="white",command=self.removedb,bd=0,height=1, width=6)
		self.removebutton.place(x=560, y=self.entrydatey+120)

		self.disablebutton = Button(font=self.font,text="Debts".upper(),bg="cadetblue",fg="white",command=self.DebtFunction,bd=0,height=1, width=15,state="normal")
		self.disablebutton.place(x=530, y=self.entrydatey+160)

		self.debtnameentry12.config(state="disabled")
		self.debtcashentry12.config(state="disabled")
		self.debtview12.config(state="disabled")
		self.submitbutton.config(state="disabled")
		self.removebutton.config(state="disabled")

		self.debtcashentry12.bind("<Return>",self.submittodb)
		self.daily.delete(1.0, END)

	#=================================================================================================================#
	def DebtFunction(self):
		self.daily.delete(1.0, END)
		self.daily.insert(END,f'Name\t\t\t\tTotal\n')
		self.daily.insert(END, f'{45*"_"}')

		self.debtnameentry12.config(state="normal")
		self.debtcashentry12.config(state="normal")
		self.debtview12.config(state="normal")
		self.submitbutton.config(state="normal")
		self.removebutton.config(state="normal")
		self.disablebutton.config(state="normal")
		self.debtnameentry.set("")

		madeni = self.c.execute("SELECT * FROM 'madeni'").fetchall()

		totaldebt = []

		for row in sorted(madeni):
			self.daily.insert(END,f'{row[0]}\t\t\t\t{row[1]}\n')
			values = row[1]
			totaldebt.append(values)

		self.entrytv.set(format(sum(totaldebt),","))
		self.entrypv.set(0)

		#==============================================Exporting by date range===============================================================
		self.today = Button(font=self.font,text="Sales".upper(),bg="cadetblue",fg="white",command=self.Get_Sales_By_Date,bd=0,height=1, width=15)
		self.today.place(x=self.entrydatex+150, y=self.entrydatey-45)

		self.SalesDateEntry = DateEntry(foreground="white",background='cadetblue',date_pattern="dd/m/yyyy",textvariable=self.sale_date_entry,font=self.font)
		self.SalesDateEntry.place(x=self.entrydatex, y=self.entrydatey-40)

		self.after(1,self.updatecomboboxlist(),END)

	def submittodb(self, event=None):
		jina = self.debtnameentry.get()
		kiasi = self.debtcashentry.get()

		query = (jina.upper(),kiasi)

		self.c.execute("INSERT INTO 'madeni' Values (?,?)", query)
		self.conn.commit()

	

		self.debtnameentry.set("")
		self.debtcashentry.set("")

		self.after(1, self.DebtFunction(),END)

	def removedb(self):
		
		jina = self.majinacombo.get()

		query = (jina.upper())

		self.c.execute("DELETE FROM 'madeni' WHERE jina=?", (jina,))
		self.conn.commit()

		self.debtnameentry.set("")
		self.debtcashentry.set("")
		self.majinacombo.set("")

		self.after(1, self.DebtFunction(),END)
	#=================================================================================================================#
	
	def Get_Sales_By_Date(self, event=None):
	# #=================================================================================================================#
		#self.after(1, self.SalesDateEntry.delete,0,END)
		self.daily.delete(1.0, END)

		self.daily.insert(END,"Product\t\tQuantity\t\tTotal\n")
		self.daily.insert(END, f'{45*"_"}')

		valuestime = self.sale_date_entry.get()
		
		if "." in valuestime:
			valuestime = valuestime.replace(".","/")

		var = "0"
		self.c.executemany("DELETE FROM 'Daily Sales' WHERE Quantity=?", var)
		self.conn.commit()

		stsales = self.c.execute("SELECT * FROM 'Daily Sales' WHERE Timed=?", (str(valuestime),)).fetchall()
		try:
			
			valuestime = str(stsales[0][0])
	
			dtsales = {}    

			#loop through the database values and append to dictionary
			for row in stsales:

				i = [i for i in range(0, len(row))]
				j = [j for j in range(0, len(row))]

				x = row[i[1]]
				x2 = row[j[2]]
				x3 = row[j[4]]

				if x in dtsales:
					y = str(dtsales[x])
					z = str(y).replace("(","")
					zn = z.replace(")", "")
					f = zn.replace(" ","")
					p,n = f.split(",")
					#print(p)
					dtsales.update({x:(x2+int(p),x3+int(n))})
				else:
					dtsales.update({x:(x2,x3)})
			final = []
			profitn = []
			#loop through the dictionary and get q and price
			for k,v in dtsales.items():
				newv = str(v).replace("(","")
				newv = newv.replace(")", "")

				q,p = newv.split(",")
				finall = p.replace(" ","")
				self.daily.insert(END, f'{k.upper()}\t\t    {q}\t\t{p}\n')
				final.append(int(finall))

				x = self.c.execute("SELECT * FROM 'AddProducts'").fetchall()

				
				for i in range(0, len(x)):
					productname = x[i][0]
					if productname == k:
						prof = (profit.profit(int(x[i][1]),int(x[i][3]),int(x[i][2]),int(q)))
						profitn.append(int(prof))
			
			self.entrytv.set(format(sum(final),","))
			self.entrypv.set(format(sum(profitn),","))
		except IndexError:
			tk.messagebox.showinfo("No Sales", f'No Sales Record Found for Date={valuestime}')
			self.entrytv.set(format(0,","))
			self.entrypv.set(format(0,","))

		
	#=================================================================================================================#
	def gettotalsales(self, event=None):
	#========================================Update Dictionarys=========================================================#
		stitems = self.stitems
		stprice = {}
		#============================================================================================================
		#This Dictionary Takes The Price of list items
		for stitem in stitems:
			#print(stitem)
			j = [j for j in range(0, len(stitem))]
			i = [i for i in range(0, len(stitem))]
			
			stprice.update({stitem[j[0]]:stitem[i[2]]})
		
		#============================================================================================================
		
		
	#=================================================================================================================#
		#Get combo box texts
		f1 = self.box1.get()
		f2 = self.box2.get()
		f3 = self.box3.get()
		f4 = self.box4.get()
		f5 = self.box5.get()
		f6 = self.box6.get()
		f7 = self.box7.get()
		f8 = self.box8.get()
		f9 = self.box9.get()
		f10 = self.box10.get()

		#============================================================================================================
		#This logic performs the desired calculations.
		#First Row
		#=========================================================================
		for k,v in stprice.items():
			if f1 == k :
				if self.entryD1.get() != 0:
					x = self.entryD1.get()
					y = self.entryq1.get()
					e =  y * x
					self.entryP1.set(e)
				else:
					self.entryD1.set(v)
					x = self.entryD1.get()
					y = self.entryq1.get()
					e =  y * x
					self.entryP1.set(e)
				
				
		#==========================================================================
		#=========================================================================
		for k,v in stprice.items():
			if f2 == k:
				if self.entryD2.get() != 0:
					x = self.entryD2.get()
					y = self.entryq2.get()
					e =  y * x
					self.entryP2.set(e)
				else:
					self.entryD2.set(v)
					x = self.entryD2.get()
					y = self.entryq2.get()
					e =  y * x
					self.entryP2.set(e)
				
		#==========================================================================
		#=========================================================================
		for k,v in stprice.items():
			if f3 == k:
				if self.entryD3.get() != 0:
					x = self.entryD3.get()
					y = self.entryq3.get()
					e =  y * x
					self.entryP3.set(e)
				else:
					self.entryD3.set(v)
					x = self.entryD3.get()
					y = self.entryq3.get()
					e =  y * x
					self.entryP3.set(e)
				
		#==========================================================================
		#=========================================================================
		for k,v in stprice.items():
			if f4 == k:
				if self.entryD4.get() != 0:
					x = self.entryD4.get()
					y = self.entryq4.get()
					e =  y * x
					self.entryP4.set(e)
				else:
					self.entryD4.set(v)
					x = self.entryD4.get()
					y = self.entryq4.get()
					e =  y * x
					self.entryP4.set(e)
				
		#==========================================================================
		#=========================================================================
		for k,v in stprice.items():
			if f5 == k :
				if self.entryD5.get() != 0:
					x = self.entryD5.get()
					y = self.entryq5.get()
					e =  y * x
					self.entryP5.set(e)
				else:
					self.entryD5.set(v)
					x = self.entryD5.get()
					y = self.entryq5.get()
					e =  y * x
					self.entryP5.set(e)
				
				
		#==========================================================================
		#=========================================================================
		for k,v in stprice.items():
			if f6 == k:
				if self.entryD6.get() != 0:
					x = self.entryD6.get()
					y = self.entryq6.get()
					e =  y * x
					self.entryP6.set(e)
				else:
					self.entryD6.set(v)
					x = self.entryD6.get()
					y = self.entryq6.get()
					e =  y * x
					self.entryP6.set(e)
				
		#==========================================================================
		#=========================================================================
		for k,v in stprice.items():
			if f7 == k:
				if self.entryD7.get() != 0:
					x = self.entryD7.get()
					y = self.entryq7.get()
					e =  y * x
					self.entryP7.set(e)
				else:
					self.entryD7.set(v)
					x = self.entryD7.get()
					y = self.entryq7.get()
					e =  y * x
					self.entryP7.set(e)
				
		#==========================================================================
		#=========================================================================
		for k,v in stprice.items():
			if f8 == k:
				if self.entryD8.get() != 0:
					x = self.entryD8.get()
					y = self.entryq8.get()
					e =  y * x
					self.entryP8.set(e)
				else:
					self.entryD8.set(v)
					x = self.entryD8.get()
					y = self.entryq8.get()
					e =  y * x
					self.entryP8.set(e)
				
		#==========================================================================
		#=========================================================================
		for k,v in stprice.items():
			if f9== k:
				if self.entryD9.get() != 0:
					x = self.entryD9.get()
					y = self.entryq9.get()
					e =  y * x
					self.entryP9.set(e)
				else:
					self.entryD9.set(v)
					x = self.entryD9.get()
					y = self.entryq9.get()
					e =  y * x
					self.entryP9.set(e)
				
		#==========================================================================
		#=========================================================================
		for k,v in stprice.items():
			if f10 == k:
				if self.entryD10.get() != 0:
					x = self.entryD10.get()
					y = self.entryq10.get()
					e =  y * x
					self.entryP10.set(e)
				else:
					self.entryD10.set(v)
					x = self.entryD10.get()
					y = self.entryq10.get()
					e =  y * x
					self.entryP10.set(e)
				
		#==========================================================================
		

		#==================================Perfom Desired Mathematics q,d,p========================================
		valuestime = f'{self.date.day}/{self.date.month}/{self.date.year}'

		values1 = (valuestime,self.box1.get(), self.entryq1.get(), self.entryD1.get(), self.entryP1.get())
		values2 = (valuestime,self.box2.get(), self.entryq2.get(), self.entryD2.get(), self.entryP2.get())
		values3 = (valuestime,self.box3.get(), self.entryq3.get(), self.entryD3.get(), self.entryP3.get())
		values4 = (valuestime,self.box4.get(), self.entryq4.get(), self.entryD4.get(), self.entryP4.get())
		values5 = (valuestime,self.box5.get(), self.entryq5.get(), self.entryD5.get(), self.entryP5.get())
		values6 = (valuestime,self.box6.get(), self.entryq6.get(), self.entryD6.get(), self.entryP6.get())
		values7 = (valuestime,self.box7.get(), self.entryq7.get(), self.entryD7.get(), self.entryP7.get())
		values8 = (valuestime,self.box8.get(), self.entryq8.get(), self.entryD8.get(), self.entryP8.get())
		values9 = (valuestime,self.box9.get(), self.entryq9.get(), self.entryD9.get(), self.entryP9.get())
		values10 = (valuestime,self.box10.get(), self.entryq10.get(), self.entryD10.get(), self.entryP10.get())
	#=================================================================================================================#


	#==================================Calculating Total Values and inserting to db===================================#
		grandfinal = (self.entryP1.get() +self.entryP2.get() +self.entryP3.get()
		 +self.entryP4.get() +self.entryP4.get()+self.entryP5.get() +self.entryP6.get() +self.entryP7.get()
		 +self.entryP8.get() +self.entryP9.get()+self.entryP10.get())

		values = (values1,values2,values3,values4,values5,values6,values7,values8,values9,values10)

		self.c.executemany("INSERT INTO 'Daily Sales' VALUES (?,?,?,?,?)", values)
		self.conn.commit()
	#==================================After Executing Values Set Quantites to Zero===================================#
		self.entryq1.set("0")
		self.entryq2.set("0")
		self.entryq3.set("0")
		self.entryq4.set("0")
		self.entryq5.set("0")
		self.entryq6.set("0")
		self.entryq7.set("0")
		self.entryq8.set("0")
		self.entryq9.set("0")
		self.entryq10.set("0")

		self.entryD1.set("0")
		self.entryD2.set("0")
		self.entryD3.set("0")
		self.entryD4.set("0")
		self.entryD5.set("0")
		self.entryD6.set("0")
		self.entryD7.set("0")
		self.entryD8.set("0")
		self.entryD9.set("0")
		self.entryD10.set("0")

		self.entryP1.set("0")
		self.entryP2.set("0")
		self.entryP3.set("0")
		self.entryP4.set("0")
		self.entryP5.set("0")
		self.entryP6.set("0")
		self.entryP7.set("0")
		self.entryP8.set("0")
		self.entryP9.set("0")
		self.entryP10.set("0")
	#=================================================================================================================#
	def todayssales(self, event=None):
	#=================================================================================================================#
		#self.Salesbtn.config(state=DISABLED)
		self.gettotalsales()

		self.debtnameentry12.config(state="disabled")
		self.debtcashentry12.config(state="disabled")
		self.debtview12.config(state="disabled")
		self.submitbutton.config(state="disabled")
		self.removebutton.config(state="disabled")
		self.debtnameentry.set("Jina")

		self.daily.delete(1.0, END)

		self.daily.insert(END,"Product\t\tQuantity\t\tTotal\n")

		valuestime = f'{self.date.day}/{self.date.month}/{self.date.year}' 
		#self.daily.insert(END,f'{valuestime}')
		self.daily.insert(END, f'{45*"_"}')

		#===================Database delete all empty values==========================
		var = "0"
		self.c.executemany("DELETE FROM 'Daily Sales' WHERE Quantity=?", var)
		self.conn.commit()

		self.c.executemany("DELETE FROM 'Daily Sales' WHERE Price=?", var)
		self.conn.commit()
		#===================Database delete all empty values==========================

		self.stsales = self.c.execute("SELECT * FROM 'Daily Sales' WHERE Timed=?", (str(valuestime),)).fetchall()

		dtsales = {}    

		#loop through the database values and append to dictionary
		for row in self.stsales:

			i = [i for i in range(0, len(row))]
			j = [j for j in range(0, len(row))]

			x = row[i[1]]
			x2 = row[j[2]]
			x3 = row[j[4]]

			if x in dtsales:
				y = str(dtsales[x])
				z = str(y).replace("(","")
				zn = z.replace(")", "")
				f = zn.replace(" ","")
				p,n = f.split(",")
				#print(p)
				dtsales.update({x:(x2+int(p),x3+int(n))})
			else:
				dtsales.update({x:(x2,x3)})
		final = []
		profitn = []
		#loop through the dictionary and get q and price
		for k,v in dtsales.items():
			newv = str(v).replace("(","")
			newv = newv.replace(")", "")

			q,p = newv.split(",")
			finall = p.replace(" ","")
			self.daily.insert(END, f'{k.upper()}\t\t    {q}\t\t{p}\n')
			final.append(int(finall))

			x = self.c.execute("SELECT * FROM 'AddProducts'").fetchall()
			for i in range(0, len(x)):
				productname = x[i][0]
				if productname == k:
					prof = (profit.profit(int(x[i][1]),int(x[i][3]),int(x[i][2]),int(q)))
					profitn.append(int(prof))
	
		self.entrytv.set(format(sum(final),","))
		self.entrypv.set(format(sum(profitn),","))

		# try:
		# 	self.clicktoload.config(text="*Click Debts to Get Export Sales Functions".upper())
		# 	self.fromdateEntry.config(state="disabled")
		# 	self.todateEntry.config(state="disabled")
		# 	self.exportsales.config(state="disabled")
		# except:
		# 	pass
		
	#=================================================================================================================#
	def UndoLastSale(self):
		self.c.execute("DELETE FROM 'Daily Sales' WHERE ROWID = (SELECT MAX(ROWID) FROM 'Daily Sales');")
		self.conn.commit()
		self.todayssales()
	#=================================================================================================================#
	#=================================================================================================================#
	def stockleft(self):
		pass
	#=================================================================================================================#
	def logout(self):
	#=================================================================================================================#
		self.conn.commit()
		self.conn.close()
		Tk.destroy(self)
		from Admin import Admin
		return Admin().mainloop()
	#=================================================================================================================#
	

if __name__ == '__main__':
	ShopLogin().mainloop()



