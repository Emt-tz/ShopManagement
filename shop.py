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
from prod import ProductManagement as pm

global cmb
global stitems
global txtinput

#initiate connection to database

# conn = sqlite3.connect('sales')

# c = conn.cursor()


class Admin(tk.Tk):
	
	def __init__(self):
		super().__init__()
		self.title("Emt Stationery Login")
		self.turn = True
		self.labels = []
		self.txt = StringVar()
		self.lb = StringVar()
		self.un = StringVar()
		self.pwd = StringVar()
		self.geometry('250x250+500+300')
		self.resizable(False, False)
		self.Interface()

	def Interface(self):
		heading = tk.Label(text="Login to Continue",fg="blue",font="time 12 bold", bd=0,height=3, width=18, relief=None,)
		heading.grid(row=0, column=0, columnspan=3) 
		for i in range(1, 2):
			col = []
			for j in range(0, 1):
				col.append(tk.Label(textvariable=self.lb,fg="white",font="time 12 bold", height=2, width=14, relief=RAISED))
				self.lb.set("User Data")
				col[j].grid(row=i, column=j)
			self.labels.append(col)
		

		username = tk.Entry(textvariable=self.un, bd=2,font="time 14 bold")
		username.grid(row=2, column=0)

		password = tk.Entry(textvariable=self.pwd, bd=2,font="time 14 bold", show="*")
		password.grid(row=3, column=0)

		loginbtn = tk.Button(text="Login",font="time 12 bold", command=self.Authenticate)
		loginbtn.grid(row=4, column=0)

		

		authtext = tk.Label(textvariable=self.txt,fg="cadetblue",font="time 12 bold", relief=RAISED)
		self.txt.set("Credential Check")
		authtext.grid(row=6, column=0)

	def Authenticate(self):
		un = self.un.get()
		pwd = self.pwd.get()

		if un == 'admin' and pwd == 'admin':
			Tk.destroy(self)
			ShopLogin().mainloop()
		else:
			exit()

class ShopLogin(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title("Stationery Shop Management System")
		self.labels = []
		self.turn = True
		self.count = 0
		self.txt = []
		self.textinput = []
		self.conn = sqlite3.connect('sales')
		self.c = self.conn.cursor()

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

		self.lb = StringVar()
		self.lbtotal = StringVar()
		self.geometry('1920x1080')
		self.resizable(True, True)

		self.Sales()

	def ShopItems(self):
		#This Function Just Returns all products input by user and combobox displays them
		stitems = ['A3', 'A4', 'A5', 'BRILLIANT', 'COMPASS', 'COPY', 'COVER', 'FILE', 'GLUE MAJI', 'GLUE STICK', 'LAMINATION', 'MANILLA', 'PENI', 'PENSELI', 'PRINT', 'QUIRE 1', 'QUIRE 2', 'QUIRE 3', 'QUIRE 4', 'RIM', 'RUBBER', 'SCAN', 'TAPE', 'TYPING']

		return stitems

	def Sales(self):
		#Top Header Arrangement
		#============================================================================================================
		#Our main Heading Area
		headingframe = Frame(bg="green",width=1920, height=200,pady=3).place(x=0,y=0)
		heading1 = tk.Label(headingframe,text="Welcome",bg="green",fg="blue",font="time 12 bold", bd=0,pady=3,height=3, width=20, relief=None,)
		heading1.grid(row=0, column=1)

		#Handle all of the columns

		columnframe = Frame(bg="cadetblue", width=1920, height=360, pady=3).place(x=0,y=50)

		buttonframe = Frame(bg="yellow", width=1000, height=360, pady=3).place(x=0,y=410)

		salesframe = Frame(bg="white", width=1920/2, height=300, pady=3).place(x=1000, y=410)

		Product = tk.Label(columnframe, text="Product",bg="white",font="time 12 bold", height=2, width=34, relief=RAISED)
		Product.grid(row=1, column=0)

		Quantity = tk.Label(columnframe, text="Quantity",bg="white",font="time 12 bold", height=2, width=34, relief=RAISED)
		Quantity.grid(row=1, column=1)

		Discount = tk.Label(columnframe, text="Sell Price",bg="white",font="time 12 bold", height=2, width=34, relief=RAISED)
		Discount.grid(row=1, column=2)

		Price = tk.Label(columnframe, text="Price",bg="white",font="time 12 bold", height=2, width=34, relief=RAISED)
		Price.grid(row=1, column=3)
		#============================================================================================================


		#============================================================================================================
		#Deal with the combobox here start at row=2
		box1 = ttk.Combobox(columnframe, textvariable=self.box1,values=self.ShopItems(),font="Courier 14 bold")
		box1.grid(row=2, column=0)

		box2 = ttk.Combobox(columnframe, textvariable=self.box2,values=self.ShopItems(),font="Courier 14 bold")
		box2.grid(row=3, column=0)

		box3 = ttk.Combobox(columnframe, textvariable=self.box3,values=self.ShopItems(),font="Courier 14 bold")
		box3.grid(row=4, column=0)

		box4 = ttk.Combobox(columnframe, textvariable=self.box4,values=self.ShopItems(),font="Courier 14 bold")
		box4.grid(row=5, column=0)

		box5 = ttk.Combobox(columnframe, textvariable=self.box5,values=self.ShopItems(),font="Courier 14 bold")
		box5.grid(row=6, column=0)

		box6 = ttk.Combobox(columnframe, textvariable=self.box6,values=self.ShopItems(),font="Courier 14 bold")
		box6.grid(row=7, column=0)

		box7 = ttk.Combobox(columnframe,textvariable=self.box7, values=self.ShopItems(),font="Courier 14 bold")
		box7.grid(row=8, column=0)

		box8 = ttk.Combobox(columnframe, textvariable=self.box8,values=self.ShopItems(),font="Courier 14 bold")
		box8.grid(row=9, column=0)

		box9 = ttk.Combobox(columnframe, textvariable=self.box9,values=self.ShopItems(),font="Courier 14 bold")
		box9.grid(row=10, column=0)

		box10 = ttk.Combobox(columnframe, textvariable=self.box10,values=self.ShopItems(),font="Courier 14 bold")
		box10.grid(row=11, column=0)

		box11 = ttk.Combobox(columnframe, textvariable=self.box11,values=self.ShopItems(),font="Courier 14 bold")
		box11.grid(row=12, column=0)

		box12 = ttk.Combobox(columnframe, textvariable=self.box12,values=self.ShopItems(),font="Courier 14 bold")
		box12.grid(row=13, column=0)
		#============================================================================================================

		#============================================================================================================
		#Quantity Entry Boxes
		entryq1 = tk.Entry(columnframe,bg="white",textvariable=self.entryq1,font="time 12 bold")
		entryq1.grid(row=2, column=1)

		entryq2 = tk.Entry(columnframe,bg="white",textvariable=self.entryq2,font="time 12 bold")
		entryq2.grid(row=3, column=1)

		entryq3 = tk.Entry(columnframe,bg="white",textvariable=self.entryq3,font="time 12 bold")
		entryq3.grid(row=4, column=1)

		entryq4 = tk.Entry(columnframe,bg="white",textvariable=self.entryq4,font="time 12 bold")
		entryq4.grid(row=5, column=1)

		entryq5 = tk.Entry(columnframe,bg="white",textvariable=self.entryq5,font="time 12 bold")
		entryq5.grid(row=6, column=1)

		entryq6 = tk.Entry(columnframe,bg="white",textvariable=self.entryq6,font="time 12 bold")
		entryq6.grid(row=7, column=1)

		entryq7 = tk.Entry(columnframe,bg="white",textvariable=self.entryq7,font="time 12 bold")
		entryq7.grid(row=8, column=1)

		entryq8 = tk.Entry(columnframe,bg="white",textvariable=self.entryq8,font="time 12 bold")
		entryq8.grid(row=9, column=1)

		entryq9 = tk.Entry(columnframe,bg="white",textvariable=self.entryq9,font="time 12 bold")
		entryq9.grid(row=10, column=1)

		entryq10 = tk.Entry(columnframe,bg="white",textvariable=self.entryq10,font="time 12 bold")
		entryq10.grid(row=11, column=1)

		entryq11 = tk.Entry(columnframe,bg="white",textvariable=self.entryq11,font="time 12 bold")
		entryq11.grid(row=12, column=1)

		entryq12 = tk.Entry(columnframe,bg="white",textvariable=self.entryq12,font="time 12 bold")
		entryq12.grid(row=13, column=1)
		#============================================================================================================

		#============================================================================================================
		#Discount entries.
		entryD1 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD1,font="time 12 bold")
		entryD1.grid(row=2, column=2)

		entryD2 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD2,font="time 12 bold")
		entryD2.grid(row=3, column=2)

		entryD3 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD3,font="time 12 bold")
		entryD3.grid(row=4, column=2)

		entryD4 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD4,font="time 12 bold")
		entryD4.grid(row=5, column=2)

		entryD5 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD5,font="time 12 bold")
		entryD5.grid(row=6, column=2)

		entryD6 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD6,font="time 12 bold")
		entryD6.grid(row=7, column=2)

		entryD7 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD7,font="time 12 bold")
		entryD7.grid(row=8, column=2)

		entryD8 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD8,font="time 12 bold")
		entryD8.grid(row=9, column=2)

		entryD9 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD9,font="time 12 bold")
		entryD9.grid(row=10, column=2)

		entryD10 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD10,font="time 12 bold")
		entryD10.grid(row=11, column=2)

		entryD11 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD11,font="time 12 bold")
		entryD11.grid(row=12, column=2)

		entryD12 = tk.Entry(columnframe,bg="white",state=
			'disabled',textvariable=self.entryD12,font="time 12 bold")
		entryD12.grid(row=13, column=2)
		#============================================================================================================

		#============================================================================================================
		#Total Price Entries
		entryP1 = tk.Entry(columnframe,bg="white",textvariable=self.entryP1,font="time 12 bold", state='disabled')
		entryP1.grid(row=2, column=3)

		entryP2 = tk.Entry(columnframe,bg="white",textvariable=self.entryP2,font="time 12 bold", state='disabled')
		entryP2.grid(row=3, column=3)

		entryP3 = tk.Entry(columnframe,bg="white",textvariable=self.entryP3,font="time 12 bold", state='disabled')
		entryP3.grid(row=4, column=3)

		entryP4 = tk.Entry(columnframe,bg="white",textvariable=self.entryP4,font="time 12 bold", state='disabled')
		entryP4.grid(row=5, column=3)

		entryP5 = tk.Entry(columnframe,bg="white",textvariable=self.entryP5,font="time 12 bold", state='disabled')
		entryP5.grid(row=6, column=3)

		entryP6 = tk.Entry(columnframe,bg="white",textvariable=self.entryP6,font="time 12 bold", state='disabled')
		entryP6.grid(row=7, column=3)

		entryP7 = tk.Entry(columnframe,bg="white",textvariable=self.entryP7,font="time 12 bold", state='disabled')
		entryP7.grid(row=8, column=3)

		entryP8 = tk.Entry(columnframe,bg="white",textvariable=self.entryP8,font="time 12 bold", state='disabled')
		entryP8.grid(row=9, column=3)

		entryP9 = tk.Entry(columnframe,bg="white",textvariable=self.entryP9,font="time 12 bold", state='disabled')
		entryP9.grid(row=10, column=3)

		entryP10 = tk.Entry(columnframe,bg="white",textvariable=self.entryP10,font="time 12 bold", state='disabled')
		entryP10.grid(row=11, column=3)

		entryP11 = tk.Entry(columnframe,bg="white",textvariable=self.entryP11,font="time 12 bold", state='disabled')
		entryP11.grid(row=12, column=3)

		entryP12 = tk.Entry(bg="white",textvariable=self.entryP12,font="time 12 bold", state='disabled')
		entryP12.grid(row=13, column=3)
		
		#============================================================================================================

		#============================================================================================================
		#Label to Display total
		totallabel = tk.Label(columnframe,textvariable=self.lbtotal,
			fg=None,font="time 12 bold",bg="cadetblue",padx=12,pady=0, bd=0,height=3, 
			width=12, relief=None)
		self.lbtotal.set("Jumlisha")
		totallabel.place(x=1120, y=360)
		#Grandtotal Button
		grandtotal = tk.Button(buttonframe,text="Total"
			,bg="cadetblue",font="time 12 bold",
			padx=12,pady=0, bd=0,height=3, width=12, 
			relief=None,command=self.changelabel)
		grandtotal.place(x=840, y=650)

		#Clear Button
		logout = tk.Button(buttonframe,text="Exit"
			,bg="cadetblue",font="time 12 bold",
			padx=12,pady=0, bd=0,height=3, width=12, 
			relief=None,command=self.logout)
		logout.place(x=0, y=650)

		#product management Button
		prodmgmts = Button(columnframe,font="time 12 bold",text="Product Management",bg="cadetblue",command=self.prodmgmt,padx=12,pady=0, bd=0,height=3, width=16).place(x=840/2, y=650)

		#============================================================================================================
		

	def changelabel(self):
		#get combobox one test Check
		stitems = self.ShopItems()

		#============================================================================================================
		#This Dictionary Takes The Price of list items
		stprice = {
		stitems[0]:300,
		stitems[1]:200,
		stitems[2]:150,
		stitems[3]:1000,
		stitems[4]:2000,
		stitems[5]:100,
		stitems[6]:200,
		stitems[7]:1500,
		stitems[8]:1000,
		stitems[9]:1000,
		stitems[10]:1000,
		stitems[11]:200,
		stitems[12]:200,
		stitems[13]:300,
		stitems[14]:200,
		stitems[15]:1500,
		stitems[16]:2500,
		stitems[17]:3000,
		stitems[18]:3500,
		stitems[19]:12000,
		stitems[20]:500,
		stitems[21]:1000,
		stitems[22]:4000,
		stitems[23]:1000,
		}
		#============================================================================================================

		#============================================================================================================
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
		for i in range(0, 24):
			if f1 == stitems[i]:
				self.entryD1.set(stprice[stitems[i]])
				x = self.entryD1.get()
				y = self.entryq1.get()
				e =  y * x
				self.entryP1.set(e)
				
		#==========================================================================
		#=========================================================================
		for i in range(0, 24):
			if f2 == stitems[i]:
				self.entryD2.set(stprice[stitems[i]])
				x = self.entryD2.get()
				y = self.entryq2.get()
				e =  y * x
				self.entryP2.set(e)
				
		#==========================================================================
		#=========================================================================
		for i in range(0, 24):
			if f3 == stitems[i]:
				self.entryD3.set(stprice[stitems[i]])
				x = self.entryD3.get()
				y = self.entryq3.get()
				e =  y * x
				self.entryP3.set(e)
				
		#==========================================================================
		#=========================================================================
		for i in range(0, 24):
			if f4 == stitems[i]:
				self.entryD4.set(stprice[stitems[i]])
				x = self.entryD4.get()
				y = self.entryq4.get()
				e =  y * x
				self.entryP4.set(e)
				
		#==========================================================================
		#=========================================================================
		for i in range(0, 24):
			if f5 == stitems[i]:
				self.entryD5.set(stprice[stitems[i]])
				x = self.entryD5.get()
				y = self.entryq5.get()
				e =  y * x
				self.entryP5.set(e)
				
		#==========================================================================
		#=========================================================================
		for i in range(0, 24):
			if f6 == stitems[i]:
				self.entryD6.set(stprice[stitems[i]])
				x = self.entryD6.get()
				y = self.entryq6.get()
				e =  y * x
				self.entryP6.set(e)
				
		#==========================================================================
		#=========================================================================
		for i in range(0, 24):
			if f7 == stitems[i]:
				self.entryD7.set(stprice[stitems[i]])
				x = self.entryD7.get()
				y = self.entryq7.get()
				e =  y * x
				self.entryP7.set(e)
				
		#==========================================================================
		#=========================================================================
		for i in range(0, 24):
			if f8 == stitems[i]:
				self.entryD8.set(stprice[stitems[i]])
				x = self.entryD8.get()
				y = self.entryq8.get()
				e =  y * x
				self.entryP8.set(e)
				
		#==========================================================================
		#=========================================================================
		for i in range(0, 24):
			if f9 == stitems[i]:
				self.entryD9.set(stprice[stitems[i]])
				x = self.entryD9.get()
				y = self.entryq9.get()
				e =  y * x
				self.entryP9.set(e)
				
		#==========================================================================
		#=========================================================================
		for i in range(0, 24):
			if f10 == stitems[i]:
				self.entryD10.set(stprice[stitems[i]])
				x = self.entryD10.get()
				y = self.entryq10.get()
				e =  y * x
				self.entryP10.set(e)
				
		#==========================================================================
		#=========================================================================
		for i in range(0, 24):
			if f11 == stitems[i]:
				self.entryD11.set(stprice[stitems[i]])
				x = self.entryD11.get()
				y = self.entryq11.get()
				e =  y * x
				self.entryP11.set(e)
				
		#==========================================================================
		#=========================================================================
		for i in range(0, 24):
			if f12 == stitems[i]:
				self.entryD12.set(stprice[stitems[i]])
				x = self.entryD12.get()
				y = self.entryq12.get()
				e =  y * x
				self.entryP12.set(e)
		#==========================================================================

		#==========================================================================
		# #loading database values and setting them to respective entries
		# for row in self.c.execute("SELECT * FROM 'Daily Sales' ORDER BY Product"):
		# 	print(row)
		

		# values1 = [self.box1.get(), self.entryq1.get(), self.entryD1.get(), self.entryP1.get()]
		# #print(values)

		# values2 = [self.box2.get(), self.entryq2.get(), self.entryD2.get(), self.entryP2.get()]
		# #print(values)

		# values3 = [self.box3.get(), self.entryq3.get(), self.entryD3.get(), self.entryP3.get()]
		# #print(values)

		# values4 = [self.box4.get(), self.entryq4.get(), self.entryD4.get(), self.entryP4.get()]
		# #print(values)

		# values5 = [self.box5.get(), self.entryq5.get(), self.entryD5.get(), self.entryP5.get()]
		# #print(values)

		# values6 = [self.box6.get(), self.entryq6.get(), self.entryD6.get(), self.entryP6.get()]
		# #print(values)

		# values7 = [self.box7.get(), self.entryq7.get(), self.entryD7.get(), self.entryP7.get()]
		# #print(values)

		# values8 = [self.box8.get(), self.entryq8.get(), self.entryD8.get(), self.entryP8.get()]
		# #print(values)

		# values9 = [self.box9.get(), self.entryq9.get(), self.entryD9.get(), self.entryP9.get()]
		# #print(values)

		# values10 = [self.box10.get(), self.entryq10.get(), self.entryD10.get(), self.entryP10.get()]
		# #print(values)

		# values11 = [self.box11.get(), self.entryq11.get(), self.entryD11.get(), self.entryP11.get()]
		# #print(values)

		# values12 = [self.box12.get(), self.entryq12.get(), self.entryD12.get(), self.entryP12.get()]
		# #print(values)
		# values = (values1,values2,values3,values4,values5,values6,values7,values8,
		# 	values9,values10,values11,values12)

	
		#==========================================================================

		#==========================================================================
		valuestime = (time.asctime())

		values1 = (valuestime,self.box1.get(), self.entryq1.get(), self.entryD1.get(), self.entryP1.get())
		#print(values)

		values2 = (valuestime,self.box2.get(), self.entryq2.get(), self.entryD2.get(), self.entryP2.get())
		#print(values)

		values3 = (valuestime,self.box3.get(), self.entryq3.get(), self.entryD3.get(), self.entryP3.get())
		#print(values)

		values4 = (valuestime,self.box4.get(), self.entryq4.get(), self.entryD4.get(), self.entryP4.get())
		#print(values)

		values5 = (valuestime,self.box5.get(), self.entryq5.get(), self.entryD5.get(), self.entryP5.get())
		#print(values)

		values6 = (valuestime,self.box6.get(), self.entryq6.get(), self.entryD6.get(), self.entryP6.get())
		#print(values)

		values7 = (valuestime,self.box7.get(), self.entryq7.get(), self.entryD7.get(), self.entryP7.get())
		#print(values)

		values8 = (valuestime,self.box8.get(), self.entryq8.get(), self.entryD8.get(), self.entryP8.get())
		#print(values)

		values9 = (valuestime,self.box9.get(), self.entryq9.get(), self.entryD9.get(), self.entryP9.get())
		#print(values)

		values10 = (valuestime,self.box10.get(), self.entryq10.get(), self.entryD10.get(), self.entryP10.get())
		#print(values)

		values11 = (valuestime,self.box11.get(), self.entryq11.get(), self.entryD11.get(), self.entryP11.get())
		#print(values)

		values12 = (valuestime,self.box12.get(), self.entryq12.get(), self.entryD12.get(), self.entryP12.get())
		#print(values)
		
		
		#==========================================================================


		#==========================================================================
		grandfinal = (self.entryP1.get() +self.entryP2.get() +self.entryP3.get()
		 +self.entryP4.get() +self.entryP4.get() +self.entryP5.get() +self.entryP6.get()
		  +self.entryP7.get() +self.entryP8.get() +self.entryP9.get() +self.entryP10.get()
		   +self.entryP11.get() +self.entryP12.get())


		self.lbtotal.set(f'Jumla={grandfinal}')

		values = (values1,values2,values3,values4
		,values5,values6,values7,values8,
			values9,values10,values11,values12)

		# print(values)

		self.c.executemany("INSERT INTO 'Daily Sales' VALUES (?,?,?,?,?)", values)

	def logout(self):
		self.conn.commit()	
		self.conn.close()
		Tk.destroy(self)
		return Admin().mainloop()

	def prodmgmt(self):
		Tk.destroy(self)
		return pm().mainloop()

if __name__ == '__main__':
	
	ShopLogin().mainloop()



