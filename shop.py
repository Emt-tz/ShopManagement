#This will be the main GUI, our Stationery Management System

#Functions
"""
1. Add or remove products based on quantity
2. Specify products buying and selling price so as to determine profit
3. Print out Graphs showing business performance(Daily, Weekly and Monthly)
4. Print receipt of daily, weekly and monthly sales based on dates
5. Print out overall sales daily, weekly or monthly based on dates
6. Adjust Products buying and selling price
7. Add discounts to some products if exists
8. Alert when products fall below certain amount of stock
9. Disply Word of God daily, Optional
10. Display the total Profit or Loss made overall since start of business
11. Notify when no Transactions
12. A Place to insert all the expenses 
13. Ability to add more Functionality as time Goes

"""

"""
Application Algorithm, we stick with simple as possible
1. The front face will have three columns and upper row
			Upper Row (Date)
	Column1     Column2     Column3 Column4   Column5 
	Products    quantity    Price    discount Expenses
at row can be added if many products are sold 

2. There will be two modes, single customer mode if receipt is required and 
overall mode is receipt is not required
Customer mode will only print out the receipt to the customer but the sales will automatically be added to overall mode

3. Products are pre written in a listdown box or combo box
4. At the bottom there is a calculate total button 
5. When program is exited information is stored in the database automatically so if exit and open it will return to where it was 
at the last time.
6. At the top Menu we have option to display Graph based on date with a range of starting at 1 week and above
The graph can be saved as a image
7. There will be an option at the top to add a new product which will have three columns

	ProductName BuyingPrice SellingPrice
8.  Other Functionalities will be added later on    

"""

"""
1. Login and choose between add product radio box and sales radio box and a log out button

2. Day one try to build the four columns
"""
import tkinter as tk
from tkinter import *
from tkinter import ttk
import time
import concurrent.futures
import sqlite3
import datetime as dt
import sys
from time import strftime
from prod import ProductManagement as pm

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
			if un == k and pwd ==v:
				try:
					Tk.destroy(self)
					ShopLogin().mainloop()
				except:
					tk.messagebox.showinfo("Error","Please Check Credentials")
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

		authtext = tk.Label(textvariable=self.txt,fg="cadetblue",font="time 12", relief=RAISED)
		self.txt.set("Add New Credentials")
		authtext.grid(row=6, column=0)

	def AddUser(self):
		conn = sqlite3.connect('sales')
		c = conn.cursor()

		if self.pwdnew.get() == self.pwdnewchk.get():

			c.execute("INSERT INTO 'login' VALUES (?,?) ", (self.unnew.get(),self.pwdnew.get()))
			conn.commit()

			tk.messagebox.showinfo("Succes", "User Added Successfully Press ok to Login")
			Tk.destroy(self)
			Admin().mainloop()
		else:
			tk.messagebox.showinfo("Check Passwords","Passwords Dont Match Please Check")
		


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

		self.sale_date_entry = StringVar()

		self.salesframe = Frame(bg="white", width=400, height=900, pady=3).place(x=1034,y=410)
		self.daily = tk.Text(self.salesframe,width=40, height=20, font="time 10",relief=RAISED)
		self.daily.place(x=1037, y=412)
		self.nl = "\t\t\t\t\t"
		self.daily.insert(END,f'Product\t\tQuantity\t\tTotal\n')
		self.daily.insert(END, f'{45*"_"}')
		# self.daily.insert(END, f'\t\t\t\t\t{self.nl.join(20*"|")}\n')

		self.lb = StringVar()
		self.lbtotal = StringVar()

		self.geometry('1350x1080+10+0')
		self.resizable(False, True)

		
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

		columnframe = Frame(bg="cadetblue", width=1920, height=360, pady=3).place(x=0,y=50)

		buttonframe = Frame(bg="lightgrey", width=1030, height=300, pady=3).place(x=2, y=413)
		#Label to Warn user to not conflict with database
		warning = Label(columnframe, bg="cadetblue",fg="green", text="*To Check Product Price Put Quantity 0 and Press Total", font="time 11").place(x=400,y=380)
	
		Product = tk.Label(columnframe, text="Product".upper(),bg="white",font="time 11 bold", height=2, width=34, relief=RAISED)
		Product.grid(row=1, column=0)

		Quantity = tk.Label(columnframe, text="Quantity".upper(),bg="white",font="time 11 bold", height=2, width=34, relief=RAISED)
		Quantity.grid(row=1, column=1)

		Discount = tk.Label(columnframe, text="Sell Price".upper(),bg="white",font="time 11 bold", height=2, width=34, relief=RAISED)
		Discount.grid(row=1, column=2)

		Price = tk.Label(columnframe, text="Price".upper(),bg="white",font="time 11 bold", height=2, width=34, relief=RAISED)
		Price.grid(row=1, column=3)

		
		
		# lbl = Label(font = ('calibri', 40, 'bold'), 
		# 	background = 'purple', 
		# 	foreground = 'white',width=300).place(y=0,x=600) 
		# lbl.config(clock)
		# #lbl.after(1000, time)  
	#=================================================================================================================#
	#============================Combobox,Entry Defined Here==========================================================#
		#Deal with the combobox here start at row=2
		box1 = ttk.Combobox(columnframe, textvariable=self.box1,values=self.ShopItems(),font="time 12")
		box1.grid(row=2, column=0)
		box2 = ttk.Combobox(columnframe, textvariable=self.box2,values=self.ShopItems(),font="time 12")
		box2.grid(row=3, column=0)
		box3 = ttk.Combobox(columnframe, textvariable=self.box3,values=self.ShopItems(),font="time 12")
		box3.grid(row=4, column=0)
		box4 = ttk.Combobox(columnframe, textvariable=self.box4,values=self.ShopItems(),font="time 12")
		box4.grid(row=5, column=0)
		box5 = ttk.Combobox(columnframe, textvariable=self.box5,values=self.ShopItems(),font="time 12")
		box5.grid(row=6, column=0)
		box6 = ttk.Combobox(columnframe, textvariable=self.box6,values=self.ShopItems(),font="time 12")
		box6.grid(row=7, column=0)
		box7 = ttk.Combobox(columnframe,textvariable=self.box7, values=self.ShopItems(),font="time 12")
		box7.grid(row=8, column=0)
		box8 = ttk.Combobox(columnframe, textvariable=self.box8,values=self.ShopItems(),font="time 12")
		box8.grid(row=9, column=0)
		box9 = ttk.Combobox(columnframe, textvariable=self.box9,values=self.ShopItems(),font="time 12")
		box9.grid(row=10, column=0)
		box10 = ttk.Combobox(columnframe, textvariable=self.box10,values=self.ShopItems(),font="time 12")
		box10.grid(row=11, column=0)
		box11 = ttk.Combobox(columnframe, textvariable=self.box11,values=self.ShopItems(),font="time 12")
		box11.grid(row=12, column=0)
		box12 = ttk.Combobox(columnframe, textvariable=self.box12,values=self.ShopItems(),font="time 12")
		box12.grid(row=13, column=0)
		#============================================================================================================

		#============================================================================================================
		#Quantity Entry Boxes
		entryq1 = tk.Entry(columnframe,bg="white",textvariable=self.entryq1,font="time 10")
		entryq1.grid(row=2, column=1)
		entryq2 = tk.Entry(columnframe,bg="white",textvariable=self.entryq2,font="time 10")
		entryq2.grid(row=3, column=1)
		entryq3 = tk.Entry(columnframe,bg="white",textvariable=self.entryq3,font="time 10")
		entryq3.grid(row=4, column=1)
		entryq4 = tk.Entry(columnframe,bg="white",textvariable=self.entryq4,font="time 10")
		entryq4.grid(row=5, column=1)
		entryq5 = tk.Entry(columnframe,bg="white",textvariable=self.entryq5,font="time 10")
		entryq5.grid(row=6, column=1)
		entryq6 = tk.Entry(columnframe,bg="white",textvariable=self.entryq6,font="time 10")
		entryq6.grid(row=7, column=1)
		entryq7 = tk.Entry(columnframe,bg="white",textvariable=self.entryq7,font="time 10")
		entryq7.grid(row=8, column=1)
		entryq8 = tk.Entry(columnframe,bg="white",textvariable=self.entryq8,font="time 10")
		entryq8.grid(row=9, column=1)
		entryq9 = tk.Entry(columnframe,bg="white",textvariable=self.entryq9,font="time 10")
		entryq9.grid(row=10, column=1)
		entryq10 = tk.Entry(columnframe,bg="white",textvariable=self.entryq10,font="time 10")
		entryq10.grid(row=11, column=1)
		entryq11 = tk.Entry(columnframe,bg="white",textvariable=self.entryq11,font="time 10")
		entryq11.grid(row=12, column=1)
		entryq12 = tk.Entry(columnframe,bg="white",textvariable=self.entryq12,font="time 10")
		entryq12.grid(row=13, column=1)

		#bind all q entries with the enter key
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
		entryq11.bind("<Return>",self.todayssales)
		entryq12.bind("<Return>",self.todayssales)
		#============================================================================================================

		#============================================================================================================
		#Sell Price Entries D[i].
		entryD1 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD1,font="time 10")
		entryD1.grid(row=2, column=2)
		entryD2 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD2,font="time 10")
		entryD2.grid(row=3, column=2)
		entryD3 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD3,font="time 10")
		entryD3.grid(row=4, column=2)
		entryD4 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD4,font="time 10")
		entryD4.grid(row=5, column=2)
		entryD5 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD5,font="time 10")
		entryD5.grid(row=6, column=2)
		entryD6 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD6,font="time 10")
		entryD6.grid(row=7, column=2)
		entryD7 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD7,font="time 10")
		entryD7.grid(row=8, column=2)
		entryD8 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD8,font="time 10")
		entryD8.grid(row=9, column=2)
		entryD9 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD9,font="time 10")
		entryD9.grid(row=10, column=2)
		entryD10 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD10,font="time 10")
		entryD10.grid(row=11, column=2)
		entryD11 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD11,font="time 10")
		entryD11.grid(row=12, column=2)
		entryD12 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD12,font="time 10")
		entryD12.grid(row=13, column=2)
		#============================================================================================================

		#============================================================================================================
		#Total Price Entries
		entryP1 = tk.Entry(columnframe,bg="white",textvariable=self.entryP1,font="time 10", state='disabled')
		entryP1.grid(row=2, column=3)
		entryP2 = tk.Entry(columnframe,bg="white",textvariable=self.entryP2,font="time 10", state='disabled')
		entryP2.grid(row=3, column=3)
		entryP3 = tk.Entry(columnframe,bg="white",textvariable=self.entryP3,font="time 10", state='disabled')
		entryP3.grid(row=4, column=3)
		entryP4 = tk.Entry(columnframe,bg="white",textvariable=self.entryP4,font="time 10", state='disabled')
		entryP4.grid(row=5, column=3)
		entryP5 = tk.Entry(columnframe,bg="white",textvariable=self.entryP5,font="time 10", state='disabled')
		entryP5.grid(row=6, column=3)
		entryP6 = tk.Entry(columnframe,bg="white",textvariable=self.entryP6,font="time 10", state='disabled')
		entryP6.grid(row=7, column=3)
		entryP7 = tk.Entry(columnframe,bg="white",textvariable=self.entryP7,font="time 10", state='disabled')
		entryP7.grid(row=8, column=3)
		entryP8 = tk.Entry(columnframe,bg="white",textvariable=self.entryP8,font="time 10", state='disabled')
		entryP8.grid(row=9, column=3)
		entryP9 = tk.Entry(columnframe,bg="white",textvariable=self.entryP9,font="time 10", state='disabled')
		entryP9.grid(row=10, column=3)
		entryP10 = tk.Entry(columnframe,bg="white",textvariable=self.entryP10,font="time 10", state='disabled')
		entryP10.grid(row=11, column=3)
		entryP11 = tk.Entry(columnframe,bg="white",textvariable=self.entryP11,font="time 10", state='disabled')
		entryP11.grid(row=12, column=3)
		entryP12 = tk.Entry(bg="white",textvariable=self.entryP12,font="time 10", state='disabled')
		entryP12.grid(row=13, column=3)
		
		#============================================================================================================

		#============================================================================================================
		# GrandTotal Button
		grandtotal = tk.Button(buttonframe,text="Total".upper()
			,bg="cadetblue",fg="white",font="time 10",
			bd=0,height=2, width=12, 
			relief=None,command=self.todayssales)
		grandtotal.place(x=60, y=650)


		

		# Exit Button
		logout = tk.Button(buttonframe,text="Exit".upper()
			,bg="cadetblue",fg="white",font="time 10",
			bd=0,height=2, width=12, 
			relief=None,command=sys.exit)
		logout.place(x=262, y=650)


		#Product Management Button
		prodmgmts = Button(buttonframe,font="time 10",text="Product Management".upper(),bg="cadetblue",fg="white",command=self.prodmgmt,bd=0,height=2, width=20).place(x=480, y=650)

		# self.Salesbtn = Button(buttonframe,font="time 10",text="Undo Sale".upper(),bg="cadetblue",fg="white",command=self.todayssales,bd=0,height=2, width=16, state=DISABLED)
		# self.Salesbtn.place(x=1160, y=650)

		#Entry Box So as to view Database Sales by Date
		SalesDateEntry = Entry(buttonframe,bg="white",textvariable=self.sale_date_entry,font="time 10")
		SalesDateEntry.place(x=200, y=500)

		SalesDateEntry_Button = Button(buttonframe,font="time 10",text="Get Sales".upper(),bg="cadetblue",fg="white",command=self.Get_Sales_By_Date,bd=0,height=1, width=20)
		SalesDateEntry_Button.place(x=400, y=495)

		SalesDateEntry_Label = Label(buttonframe,text="Enter Date -f dd/mm/yy i.e 24/4/2020 or 24.4.2020")
		SalesDateEntry_Label.place(x=160, y=530)

		SalesDateEntry.bind("<Return>",self.Get_Sales_By_Date)

	#=================================================================================================================#
		
	def Get_Sales_By_Date(self, event=None):
	#=================================================================================================================#
		#initiate Database Connection and Find Values with Date Entered
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
			#loop through the dictionary and get q and price
			for k,v in dtsales.items():
				newv = str(v).replace("(","")
				newv = newv.replace(")", "")

				q,p = newv.split(",")
				finall = p
				self.daily.insert(END, f'{k.upper()}\t\t{q}\t\t{p}\n')
				final.append(finall)

			self.daily.insert(END, f'\t\t\t\t\t\t\t\t__________________\n')
			#loop through the list and and calculate total
			totalsales = 0
			for i in range(0, len(final)):
				if len(final[i]) == 1:
					totalsales = final[0]
				else:
					totalsales = totalsales + int(final[i])
					
			self.daily.insert(END, f'\t\t\t\t\t\t\t\t\t{format(totalsales,",")}\n')
			self.daily.insert(END, f'\t\t\t__________________\n')
		except IndexError:
			tk.messagebox.showinfo("No Sales", f'No Sales Record Found for Date={valuestime}, try replacing 0 on the Month')

		
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
		f5 = self.box5.get()
		f6 = self.box6.get()
		f7 = self.box7.get()
		f8 = self.box8.get()
		f9 = self.box9.get()
		f10 = self.box10.get()
		f11 = self.box11.get()
		f12 = self.box12.get()
		#============================================================================================================
		#This logic performs the desired calculations.
		#First Row
		#=========================================================================
		for k,v in stprice.items():
			if f1 == k:
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
		#=========================================================================
		for k,v in stprice.items():
			if f5 == k:
				self.entryD5.set(v)
				x = self.entryD5.get()
				y = self.entryq5.get()
				e =  y * x
				self.entryP5.set(e)
				
		#==========================================================================
		#=========================================================================
		for k,v in stprice.items():
			if f6 == k:
				self.entryD6.set(v)
				x = self.entryD6.get()
				y = self.entryq6.get()
				e =  y * x
				self.entryP6.set(e)
				
		#==========================================================================
		#=========================================================================
		for k,v in stprice.items():
			if f7 == k:
				self.entryD7.set(v)
				x = self.entryD7.get()
				y = self.entryq7.get()
				e =  y * x
				self.entryP7.set(e)
				
		#==========================================================================
		#=========================================================================
		for k,v in stprice.items():
			if f8 == k:
				self.entryD8.set(v)
				x = self.entryD8.get()
				y = self.entryq8.get()
				e =  y * x
				self.entryP8.set(e)
				
		#==========================================================================
		#=========================================================================
		for k,v in stprice.items():
			if f9 == k:
				self.entryD9.set(v)
				x = self.entryD9.get()
				y = self.entryq9.get()
				e =  y * x
				self.entryP9.set(e)
				
		#==========================================================================
		#=========================================================================
		for k,v in stprice.items():
			if f10 == k:
				self.entryD10.set(v)
				x = self.entryD10.get()
				y = self.entryq10.get()
				e =  y * x
				self.entryP10.set(e)
				
		#==========================================================================
		#=========================================================================
		for k,v in stprice.items():
			if f11 == k:
				self.entryD11.set(v)
				x = self.entryD11.get()
				y = self.entryq11.get()
				e =  y * x
				self.entryP11.set(e)
				
		#==========================================================================
		#=========================================================================
		for k,v in stprice.items():
			if f12 == k:
				self.entryD12.set(v)
				x = self.entryD12.get()
				y = self.entryq12.get()
				e =  y * x
				self.entryP12.set(e)
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
		values11 = (valuestime,self.box11.get(), self.entryq11.get(), self.entryD11.get(), self.entryP11.get())
		values12 = (valuestime,self.box12.get(), self.entryq12.get(), self.entryD12.get(), self.entryP12.get())     
		
	#=================================================================================================================#


	#==================================Calculating Total Values and inserting to db===================================#
		grandfinal = (self.entryP1.get() +self.entryP2.get() +self.entryP3.get()
		 +self.entryP4.get() +self.entryP4.get() +self.entryP5.get() +self.entryP6.get()
		  +self.entryP7.get() +self.entryP8.get() +self.entryP9.get() +self.entryP10.get()
		   +self.entryP11.get() +self.entryP12.get())


		#self.lbtotal.set(f'Jumla={grandfinal}')


		values = (values1,values2,values3,values4
		,values5,values6,values7,values8,
			values9,values10,values11,values12)

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

	#=================================Call Today Sales Function=======================================================#
		#self.Salesbtn.config(state=NORMAL)

		#return self.todayssales()
	#=========================================Drawing Canvas Graph====================================================#
		# canvas = Canvas(self.salesframe, width=465, height=290, bg = 'white')
		# canvas.place(x=330, y=412)

		# canvas.create_line(100,250,400,250, width=2)
		# canvas.create_line(100,250,100,50, width=2)

		# for i in range(6):
		#   y = 250 - (i * 40)
		#   canvas.create_line(100,y,105,y, width=2)
		#   canvas.create_text(96,y, text='%5.1f'% (50.*i), anchor=E)

		# for x,y in [(12, 56), (20, 94), (33, 98), (45, 120), (61, 180),
		# (75, 160), (98, 223)]:
		#   x = 100 + 3*x
		#   y = 250 - (4*y)/5
		#   canvas.create_oval(x-6,y-6,x+6,y+6, width=1,
		# outline='black', fill='SkyBlue2')
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
		#loop through the dictionary and get q and price
		for k,v in dtsales.items():
			newv = str(v).replace("(","")
			newv = newv.replace(")", "")

			q,p = newv.split(",")
			finall = p
			self.daily.insert(END, f'{k.upper()}\t\t{q}\t\t{p}\n')
			final.append(finall)

		self.daily.insert(END, f'\t\t\t\t\t\t\t\t__________________\n')
		#loop through the list and and calculate total
		totalsales = 0
		for i in range(0, len(final)):
			if len(final[i]) == 1:
				totalsales = final[0]
			else:
				totalsales = totalsales + int(final[i])
				
		self.daily.insert(END, f'\t\t\t\t\t\t\t\t\t{format(totalsales,",")}\n')
		self.daily.insert(END, f'\t\t\t__________________\n')
		
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
	# def UndoSale(self):
	# #====================================When Wrong Sale Entered======================================================#


if __name__ == '__main__':
	Admin().mainloop()



