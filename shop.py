#created 10/04/2020
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkcalendar import DateEntry
import time,os
import sqlite3
import datetime as dt
import sys
from prod import ProductManagement as pm
from test2 import PasswordEncrypter as pencrypt
from test2 import ConvertCsvtoExcel as cexcel
import csv
from test2 import InitializeDatabase as dbinit
from test2 import Profit as profit

key = pencrypt.GenerateKey()

class Admin(tk.Tk):
	#=================================================================================================================#
	def __init__(self):
		super().__init__()
		self.title("Emt Mgmt Login")
		self.turn = True
		self.labels = []
		self.txt = StringVar()
		self.lb = StringVar()
		self.un = StringVar()
		self.pwd = StringVar()
		self.unnew = StringVar()
		self.pwdnew = StringVar()
		self.pwdnewchk = StringVar()
		self.geometry('250x300+500+300')
		self.resizable(False, False)
		self.Interface()
	#=================================================================================================================#

	def Interface(self):
	#=================================================================================================================#
		heading = tk.Label(text="Login to Continue",fg="blue",font="time 13 bold", bd=0,height=3, width=18, relief=None,)
		heading.grid(row=0, column=0, columnspan=3) 
		for i in range(1, 2):
			col = []
			for j in range(0, 1):
				col.append(tk.Label(textvariable=self.lb,fg="white",font="time 13 bold", height=2, width=14, relief=RAISED))
				self.lb.set("User Data")
				col[j].grid(row=i, column=j)
			self.labels.append(col)
		

		username = tk.Entry(textvariable=self.un, bd=2,font="time 13 bold")
		username.grid(row=2, column=0)

		password = tk.Entry(textvariable=self.pwd, bd=2,font="time 13 bold", show="*")
		password.grid(row=3, column=0)

		loginbtn = tk.Button(text="Login",font="time 13 bold", command=self.Authenticate)
		loginbtn.grid(row=4, column=0)

		authtext = tk.Label(textvariable=self.txt,fg="cadetblue",font="time 12", relief=RAISED)
		self.txt.set("Credential Check")
		authtext.grid(row=5, column=0)

		newuserbtn = tk.Button(text="Add User",font="time 13 bold", command=self.CallAdmin1)
		newuserbtn.grid(row=6, column=0)

		self.bind('<Return>',self.Authenticate)
	#=================================================================================================================#

	def Authenticate(self, event=None):
		un = self.un.get()
		pwd = self.pwd.get()

		#===========================Connect to the Database and Authenticate=========================================#
		conn = sqlite3.connect('sales')
		c = conn.cursor()

		try:
			cred = c.execute("SELECT * FROM 'login'").fetchall()

			#loop through the database and check for user if exists

			#user one is when [0][0] and pass [0][1]
			#user two is when [1][0] and pass[1][1]
			userdict = {}
			for i in range(0, len(cred)):
				user = cred[1-i][0]
				password = cred[1-i][1]

				userdict.update({user:password})

			for k,v in userdict.items():
				v = pencrypt.Decrypt(v, key)
				if un == k and pwd == v.decode():
					try:
						Tk.destroy(self)
						ShopLogin().mainloop()
					except:
						pass
					#ShopLogin().mainloop()
		except:
			try:
				dbinit.createdb()
			except:
				pass

			cred = c.execute("SELECT * FROM 'login'").fetchall()
			#loop through the database and check for user if exists

			#user one is when [0][0] and pass [0][1]
			#user two is when [1][0] and pass[1][1]
			userdict = {}
			for i in range(0, len(cred)):
				user = cred[1-i][0]
				password = cred[1-i][1]

				userdict.update({user:password})

			for k,v in userdict.items():
				v = pencrypt.Decrypt(v, key)
				if un == k and pwd == v.decode():
					try:
						Tk.destroy(self)
						ShopLogin().mainloop()
					except:
						pass
					#ShopLogin().mainloop()

	def CallAdmin1(self):
		Tk.destroy(self)
		return Admin1().mainloop()

class Admin1(tk.Tk):
	#=================================================================================================================#
	def __init__(self):
		super().__init__()
		self.title("Emt Mgmt Login")
		self.turn = True
		self.labels = []
		self.txt = StringVar()
		self.lb = StringVar()
		self.un = StringVar()
		self.pwd = StringVar()
		self.unnew = StringVar()
		self.pwdnew = StringVar()
		self.pwdnewchk = StringVar()
		self.geometry('250x300+500+300')
		self.resizable(False, False)
		self.CreateUser()

	def CreateUser(self):
		heading = tk.Label(text="New User SignUp",fg="blue",font="time 13 bold", bd=0,height=3, width=18, relief=None,)
		heading.grid(row=0, column=0, columnspan=3) 
		for i in range(1, 2):
			col = []
			for j in range(0, 1):
				col.append(tk.Label(textvariable=self.lb,fg="cadetblue",font="time 13 bold", height=2, width=14, relief=RAISED))
				self.lb.set("User Info")
				col[j].grid(row=i, column=j)
			self.labels.append(col)
		

		username = tk.Entry(textvariable=self.unnew, bd=2,font="time 13 bold")
		username.grid(row=2, column=0)

		password = tk.Entry(textvariable=self.pwdnew, bd=2,font="time 13 bold", show="*")
		password.grid(row=3, column=0)

		passwordconfirm = tk.Entry(textvariable=self.pwdnewchk, bd=2,font="time 13 bold", show="*")
		passwordconfirm.grid(row=4, column=0)

		createuserbtn = tk.Button(text="CreateUser",font="time 13 bold", command=self.AddUser)
		createuserbtn.grid(row=5, column=0)

		passwordconfirm.bind('<Return>',self.AddUser)

		authtext = tk.Label(textvariable=self.txt,fg="cadetblue",font="time 12", relief=RAISED)
		self.txt.set("Add New Credentials")
		authtext.grid(row=6, column=0)

	def AddUser(self, event=None):
		conn = sqlite3.connect('sales')
		c = conn.cursor()
		try:
			if self.pwdnew.get() == self.pwdnewchk.get() and (self.pwdnew.get() != ""):
				c.execute("INSERT INTO 'login' VALUES (?,?) ", (self.unnew.get(),pencrypt.Encrypt(self.pwdnew.get(),key)))
				conn.commit()

				tk.messagebox.showinfo("Succes", "User Added Successfully Press ok to Login")
				Tk.destroy(self)
				Admin().mainloop()
			else:
				tk.messagebox.showinfo("Check Passwords","Ensure all Fields are Filled and If Passwords Match")
		except:
			try:
				dbinit.createdb()
			except:
				pass

			if self.pwdnew.get() == self.pwdnewchk.get() and (self.pwdnew.get() !=""):
				c.execute("INSERT INTO 'login' VALUES (?,?) ", (self.unnew.get(),pencrypt.Encrypt(self.pwdnew.get(),key)))
				conn.commit()

				tk.messagebox.showinfo("Succes", "User Added Successfully Press ok to Login")
				Tk.destroy(self)
				Admin().mainloop()
			else:
				tk.messagebox.showinfo("Check Passwords","Ensure all Fields are Filled and If Passwords Match")
		
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
		self.box10 = StringVar()
		self.box11 = StringVar()
		self.box12 = StringVar()

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
		self.entryq11 = IntVar()
		self.entryq12 = IntVar()

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
		self.entryD11 = IntVar()
		self.entryD12 = IntVar()

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
		self.entryP11 = IntVar()
		self.entryP12 = IntVar()

		self.entrytv = IntVar()
		self.entrypv = IntVar()



		self.sale_date_entry = StringVar()

		self.salesframe = Frame(bg="white", width=400, height=900, pady=3).place(x=1034,y=410)

		self.daily = tk.Text(self.salesframe,width=40, height=20, font="time 10",relief=RAISED)
		self.daily.place(x=1037, y=412)

		self.daily.insert(END,f'Product\t\tQuantity\t\tTotal\n')
		self.daily.insert(END, f'{45*"_"}')

		self.entryt = Entry(bg="white",textvariable=self.entrytv, font="time 10", state='normal',justify='right',bd=5,width=39)
		self.entryt.place(x=1035, y=642)

		self.entryp = Entry(bg="white",textvariable=self.entrypv, font="time 10", state='normal',justify='right',bd=5,width=39)
		self.entryp.place(x=1035, y=672)

		self.lb = StringVar()
		self.lbtotal = StringVar()

		self.geometry('1350x1080+10+0')
		self.resizable(True, True)

		self.todayssales()
		self.Sales()
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

	def Sales(self):
		#Top Header Arrangement
	#===========================All Frames to Control The Main GUI are Placed Here ========================================#
		headingframe = Frame(bg="lightgrey",width=1920, height=200).place(x=0,y=0)

		Shop_title = Label(headingframe,text="Welcome to Emt Shop Management System".upper(),bg="lightgrey",fg="green",font="time 14", bd=0,height=2,relief=None)
		Shop_title.place(y=0, x=500)

		heading1 = tk.Label(headingframe,text="",bg="lightgrey",fg="blue",font="time 10", bd=0,pady=3,height=3, width=20, relief=None,)
		heading1.grid(row=0, column=0)

		buttonframe = Frame(bg="lightgrey", width=1030, height=300, pady=3).place(x=2, y=413)

		maincanvas = Canvas(self,width=1920,height=360,bg="cadetblue")
		maincanvas.place(x=0,y=50)
		#Entry Box So as to view Database Sales by Date
		# self.SalesDateEntry = DateEntry(foreground="white",background='green',date_pattern="dd/m/yyyy",textvariable=self.sale_date_entry,font="time 10")
		# self.SalesDateEntry.place(x=200, y=420)

		self.SalesDateEntry = Entry(foreground="white",background='white',textvariable=self.sale_date_entry,font="time 10")
		self.SalesDateEntry.place(x=200, y=420)

		SalesDateEntry_Button = Button(buttonframe,font="time 10",text="Get Sales".upper(),bg="cadetblue",fg="white",command=self.Get_Sales_By_Date,bd=0,height=1, width=20)
		SalesDateEntry_Button.place(x=400, y=420)

		self.SalesDateEntry.bind("<Return>",self.Get_Sales_By_Date)

		#Label to Warn user to not conflict with database
		warning = Label(bg="cadetblue",fg="green", text="*To Check Product Price Put Quantity 0 and Press Total", font="time 11").place(x=400,y=380)
	
		Product = tk.Label(text="Product".upper(),bg="white",font="time 11 bold", height=2, width=34, relief=RAISED)
		Product.grid(row=1, column=0)

		Quantity = tk.Label(text="Quantity".upper(),bg="white",font="time 11 bold", height=2, width=34, relief=RAISED)
		Quantity.grid(row=1, column=1)

		Discount = tk.Label(text="Sell Price".upper(),bg="white",font="time 11 bold", height=2, width=34, relief=RAISED)
		Discount.grid(row=1, column=2)

		Price = tk.Label(text="Price".upper(),bg="white",font="time 11 bold", height=2, width=34, relief=RAISED)
		Price.grid(row=1, column=3)

				# GrandTotal Button
		grandtotal = tk.Button(buttonframe,text="Total".upper()
			,bg="cadetblue",fg="white",font="time 10",
			bd=0,height=1, width=12, 
			relief=None,command=self.todayssales)
		grandtotal.place(x=60, y=672)

		undobtn = Button(buttonframe,font="time 10",text="UNDO SALE".upper(),bg="cadetblue",fg="white",command=self.UndoLastSale,bd=0,height=1, width=20)
		undobtn.place(x=180, y=672)
		
		#Product Management Button
		prodmgmts = Button(buttonframe,font="time 10",text="Product Management".upper(),bg="cadetblue",fg="white",command=self.prodmgmt,bd=0,height=1, width=20)
		prodmgmts.place(x=360, y=672)

		exportsales = Button(buttonframe,font="time 10",text="Export".upper(),bg="cadetblue",fg="white",command=self.exporttocsv,bd=0,height=1, width=20)
		exportsales.place(x=545, y=672)

		# Exit Button
		logout = tk.Button(buttonframe,text="Exit".upper()
			,bg="cadetblue",fg="white",font="time 10",
			bd=0,height=1, width=12, 
			relief=None,command=self.logout)
		logout.place(x=900, y=672)
	#=================================================================================================================#
	#============================Combobox,Entry Defined Here==========================================================#
	# 	#Deal with the combobox here start at row=2
		box1 = ttk.Combobox(textvariable=self.box1,values=self.ShopItems(),font="time 12")
		box2 = ttk.Combobox(textvariable=self.box2,values=self.ShopItems(),font="time 12")
		box3 = ttk.Combobox(textvariable=self.box3,values=self.ShopItems(),font="time 12")
		box4 = ttk.Combobox(textvariable=self.box4,values=self.ShopItems(),font="time 12")

		maincanvas.create_window(170,58,window=box1)
		maincanvas.create_window(170,78,window=box2)
		maincanvas.create_window(170,98,window=box3)
		maincanvas.create_window(170,118,window=box4)
	
	# #============================================================================================================

	# #============================Quantity Entry Defined Here========================================================
	# 	#Quantity Entry Boxes
		entryq1 = tk.Entry(bg="white",textvariable=self.entryq1,font="time 10")
		entryq2 = tk.Entry(bg="white",textvariable=self.entryq2,font="time 10")
		entryq3 = tk.Entry(bg="white",textvariable=self.entryq3,font="time 10")
		entryq4 = tk.Entry(bg="white",textvariable=self.entryq4,font="time 10")

		maincanvas.create_window(530,58,window=entryq1)
		maincanvas.create_window(530,78,window=entryq2)
		maincanvas.create_window(530,98,window=entryq3)
		maincanvas.create_window(530,118,window=entryq4)


	# 	#bind all q entries with the enter key
		entryq1.bind("<Return>",self.todayssales)
		entryq2.bind("<Return>",self.todayssales)
		entryq3.bind("<Return>",self.todayssales)
		entryq4.bind("<Return>",self.todayssales)

	#============================================================================================================

	#============================Price Entry Defined Here============================================================
		#Sell Price Entries D[i].
		entryD1 = tk.Entry(bg="white",state=
			'disabled',textvariable=self.entryD1,font="time 10")
		entryD1.grid(row=2, column=2)
		entryD2 = tk.Entry(bg="white",state=
			'disabled',textvariable=self.entryD2,font="time 10")
		entryD3 = tk.Entry(bg="white",state=
			'disabled',textvariable=self.entryD3,font="time 10")
		entryD4 = tk.Entry(bg="white",state=
			'disabled',textvariable=self.entryD4,font="time 10")
	

		maincanvas.create_window(850,58,window=entryD1)
		maincanvas.create_window(850,78,window=entryD2)
		maincanvas.create_window(850,98,window=entryD3)
		maincanvas.create_window(850,118,window=entryD4)
	
	#============================================================================================================

	#============================Total Price Entry Defined Here=======================================================
		#Total Price Entries
		entryP1 = tk.Entry(bg="white",textvariable=self.entryP1,font="time 10", state='disabled')
		entryP2 = tk.Entry(bg="white",textvariable=self.entryP2,font="time 10", state='disabled')
		entryP3 = tk.Entry(bg="white",textvariable=self.entryP3,font="time 10", state='disabled')
		entryP4 = tk.Entry(bg="white",textvariable=self.entryP4,font="time 10", state='disabled')

		maincanvas.create_window(1180,58,window=entryP1)
		maincanvas.create_window(1180,78,window=entryP2)
		maincanvas.create_window(1180,98,window=entryP3)
		maincanvas.create_window(1180,118,window=entryP4)

	#=================================================================================================================#
	def exporttocsv(self):
		#---------------------Get Database by date--------------------------------------------#
		tk.messagebox.showinfo("Export as Excel", "Export Daily Sales in Excel Format, Select Date to Export")
		valuestime = self.sale_date_entry.get()

		if valuestime == "":
			valuestime = f'{self.date.day}/{self.date.month}/{self.date.year}'

		if "." in valuestime:
			valuestime = valuestime.replace(".","/")

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
		#loop through the dictionary and get q and price
		try:
			filename = 'csvf/Sales.csv'

			with open(filename, 'w', newline='') as file:
				w = csv.writer(file)
				w.writerow(["Date","Product","Quantity","Price"])
				for k,v in dtsales.items():
					newv = str(v).replace("(","")
					newv = newv.replace(")", "")
					q,p = newv.split(",")
					finall = p
					final.append(finall)
					w.writerow([valuestime,k.upper(),q,p.replace(" ","")])
					
			#create the csvfile
			
				#loop through the list and and calculate total
				totalsales = 0
				for i in range(0, len(final)):
					if len(final[i]) == 1:
						totalsales = final[0]
					else:
						totalsales = totalsales + int(final[i])
				w.writerow(["","","",""])
				w.writerow(["Jumla","","",totalsales])
		except:
			os.mkdir('csvf')

			filename = 'csvf/Sales.csv'
			
			with open(filename, 'w', newline='') as file:
				w = csv.writer(file)
				w.writerow(["Date","Product","Quantity","Price"])
				for k,v in dtsales.items():
					newv = str(v).replace("(","")
					newv = newv.replace(")", "")
					q,p = newv.split(",")
					finall = p
					final.append(finall)
					w.writerow([valuestime,k.upper(),q,p.replace(" ","")])
					
			#create the csvfile
			
				#loop through the list and and calculate total
				totalsales = 0
				for i in range(0, len(final)):
					if len(final[i]) == 1:
						totalsales = final[0]
					else:
						totalsales = totalsales + int(final[i])
				w.writerow(["","","",""])
				w.writerow(["Jumla","","",totalsales])
			#now we convert the csv to excel
		return cexcel.convertToExcel(filename)

	#=================================================================================================================#
	
	def Get_Sales_By_Date(self, event=None):
	#=================================================================================================================#
		#initiate Database Connection and Find Values with Date Entered
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

		self.stsales = self.c.execute("SELECT * FROM 'Daily Sales' WHERE Timed=?", (str(valuestime),)).fetchall()

		try:
			
			valuestime = str(self.stsales[0][0])
	
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
				finall = p
				self.daily.insert(END, f'{k.upper()}\t\t    {q}\t\t{p}\n')
				final.append(finall)

				x = self.c.execute("SELECT * FROM 'AddProducts'").fetchall()

				
				for i in range(0, len(x)):
					productname = x[i][0]
					if productname == k:
						prof = (profit.profit(int(x[i][1]),int(x[i][3]),int(x[i][2]),int(q)))
						profitn.append(prof)

			#self.daily.insert(END, f'\t\t\t\t\t\t\t\t__________________\n')
			#loop through the list and and calculate total
			totalsales = 0
			profitnew = 0
			for i in range(0, len(final)):
				if len(final[i]) == 1:
					totalsales = final[0]
					profitnew = profitn[0]
				else:
					totalsales = totalsales + int(final[i])
					profitnew = profitnew+int(profitn[i])
					
			self.entrytv.set(format(totalsales,","))
			self.entrypv.set(format(profitnew,","))
		except IndexError:
			tk.messagebox.showinfo("No Sales", f'No Sales Record Found for Date={valuestime}')
			self.entrytv.set(format(0,","))
			self.entrypv.set(format(0,","))

		
	#=================================================================================================================#
	def changelabel(self, event=None):
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
		#============================================================================================================
		#This logic performs the desired calculations.
		#First Row
		#=========================================================================
		for k,v in stprice.items():
			if f1 == k :
				self.entryD1.set(v)
				x = self.entryD1.get()
				y = self.entryq1.get()
				e =  y * x
				self.entryP1.set(e)
				
		#==========================================================================
		#=========================================================================
		for k,v in stprice.items():
			if f2 == k:
				self.entryD2.set(v)
				x = self.entryD2.get()
				y = self.entryq2.get()
				e =  y * x
				self.entryP2.set(e)
				
		#==========================================================================
		#=========================================================================
		for k,v in stprice.items():
			if f3 == k:
				self.entryD3.set(v)
				x = self.entryD3.get()
				y = self.entryq3.get()
				e =  y * x
				self.entryP3.set(e)
				
		#==========================================================================
		#=========================================================================
		for k,v in stprice.items():
			if f4 == k:
				self.entryD4.set(v)
				x = self.entryD4.get()
				y = self.entryq4.get()
				e =  y * x
				self.entryP4.set(e)
				
		#==========================================================================
		

		#==================================Perfom Desired Mathematics q,d,p========================================
		valuestime = f'{self.date.day}/{self.date.month}/{self.date.year}'

		values1 = (valuestime,self.box1.get(), self.entryq1.get(), self.entryD1.get(), self.entryP1.get())
		values2 = (valuestime,self.box2.get(), self.entryq2.get(), self.entryD2.get(), self.entryP2.get())
		values3 = (valuestime,self.box3.get(), self.entryq3.get(), self.entryD3.get(), self.entryP3.get())
		values4 = (valuestime,self.box4.get(), self.entryq4.get(), self.entryD4.get(), self.entryP4.get())
	#=================================================================================================================#


	#==================================Calculating Total Values and inserting to db===================================#
		grandfinal = (self.entryP1.get() +self.entryP2.get() +self.entryP3.get()
		 +self.entryP4.get() +self.entryP4.get())

		values = (values1,values2,values3,values4)

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
		self.entryq11.set("0")
		self.entryq12.set("0")

	#=================================================================================================================#
	def todayssales(self, event=None):
	#=================================================================================================================#
		#self.Salesbtn.config(state=DISABLED)
		self.changelabel()
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
			finall = p
			self.daily.insert(END, f'{k.upper()}\t\t    {q}\t\t{p}\n')
			final.append(finall)

			x = self.c.execute("SELECT * FROM 'AddProducts'").fetchall()
			for i in range(0, len(x)):
				productname = x[i][0]
				if productname == k:
					prof = (profit.profit(int(x[i][1]),int(x[i][3]),int(x[i][2]),int(q)))
					profitn.append(prof)

		#self.daily.insert(END, f'\t\t\t\t\t\t\t\t__________________\n')
		#loop through the list and and calculate total
		totalsales = 0
		profitnew = 0
		for i in range(0, len(final)):
			if len(final[i]) == 1:
				totalsales = final[0]
				profitnew = profitn[0]
			else:
				totalsales = totalsales + int(final[i])
				profitnew = profitnew+int(profitn[i])
				
		self.entrytv.set(format(totalsales,","))
		self.entrypv.set(format(profitnew,","))
		
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
		return Admin().mainloop()
	#=================================================================================================================#
	def prodmgmt(self):
		Tk.destroy(self)
		return pm().mainloop()

	#=================================================================================================================#

if __name__ == '__main__':
	Admin().mainloop()



