#created 10/04/2020
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkcalendar import DateEntry
import time,os
import sqlite3
import datetime as dt
import sys,os
from prod import ProductManagement as pm
from test2 import PasswordEncrypter as pencrypt
from test2 import ConvertCsvtoExcel as cexcel
from test2 import MonthlySales as mnsales
import csv
from test2 import InitializeDatabase as dbinit
from test2 import Profit as profit
from password_strength import PasswordPolicy as pc

#======define our password rules======================
policy = pc.from_names(length=8,uppercase=1,numbers=1,special=1,nonletters=1)

key = pencrypt.GenerateKey()

try:
	os.mkdir("csvf")
except:
	pass

class Admin(tk.Tk):
	#=================================================================================================================#
	def __init__(self):
		super().__init__()
		self.title("Emt Mgmt Login")
		#self.iconbitmap("sc.ico")
		self.turn = True
		self.labels = []
		self.txt = StringVar()
		self.lb = StringVar()
		self.un = StringVar()
		self.pwd = StringVar()
		self.unnew = StringVar()
		self.pwdnew = StringVar()
		self.pwdnewchk = StringVar()
		self.geometry('246x300+500+300')
		#self.resizable(False, False)
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
		

		username = tk.Entry(textvariable=self.un, bd=2,font="time 16 bold")
		username.grid(row=2, column=0)

		password = tk.Entry(textvariable=self.pwd, bd=2,font="time 16 bold", show="*")
		password.grid(row=3, column=0)

		loginbtn = tk.Button(text="Login",font="time 14 bold", command=self.Authenticate)
		loginbtn.grid(row=4, column=0)

		authtext = tk.Label(textvariable=self.txt,fg="cadetblue",font="time 14", relief=RAISED)
		self.txt.set("Credential Check")
		authtext.grid(row=5, column=0)

		newuserbtn = tk.Button(text="Add User",font="time 14 bold", command=self.CallAdmin1)
		newuserbtn.grid(row=6, column=0)

		self.bind('<Return>',self.Authenticate)
	#=================================================================================================================#

	def Authenticate(self, event=None):
		un = self.un.get()
		pwd = self.pwd.get()

		#===========================Connect to the Database and Authenticate=========================================#
		conn = sqlite3.connect('sales')
		c = conn.cursor()

		if un == "" or pwd == "":
			tk.messagebox.showinfo("Error Login","Please fill all values")
		else:
			try:
				cred = c.execute("SELECT * FROM 'login'").fetchall()

				#loop through the database and check for user if exists

				#user one is when [0][0] and pass [0][1]
				#user two is when [1][0] and pass[1][1]
				userdict = {}
				for i in range(0, len(cred)):
					user = cred[i][0]
					password = cred[i][1]

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
					else:
						tk.messagebox.showinfo("Error","Invalid Credentials")
					break
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
					else:
						tk.messagebox.showinfo("Check","Review your credentials")

	def CallAdmin1(self):
		Tk.destroy(self)
		return Admin1().mainloop()

class Admin1(tk.Tk):
	#=================================================================================================================#
	def __init__(self):
		super().__init__()
		self.title("Emt Mgmt Login")
		#self.iconbitmap("sc.ico")
		self.turn = True
		self.labels = []
		self.txt = StringVar()
		self.lb = StringVar()
		self.un = StringVar()
		self.pwd = StringVar()
		self.unnew = StringVar()
		self.pwdnew = StringVar()
		self.pwdnewchk = StringVar()
		self.geometry('246x300+500+300')
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
		

		username = tk.Entry(textvariable=self.unnew, bd=2,font="time 16 bold")
		username.grid(row=2, column=0)

		password = tk.Entry(textvariable=self.pwdnew, bd=2,font="time 16 bold", show="*")
		password.grid(row=3, column=0)

		passwordconfirm = tk.Entry(textvariable=self.pwdnewchk, bd=2,font="time 16 bold", show="*")
		passwordconfirm.grid(row=4, column=0)

		createuserbtn = tk.Button(text="CreateUser",font="time 14 bold", command=self.AddUser)
		createuserbtn.grid(row=5, column=0)

		loginbtn = tk.Button(text="Back to Login",font="time 14 bold", command=self.backtologin)
		loginbtn.grid(row=7, column=0)

		passwordconfirm.bind('<Return>',self.AddUser)

		authtext = tk.Label(textvariable=self.txt,fg="cadetblue",font="time 14", relief=RAISED)
		self.txt.set("Add New Credentials")
		authtext.grid(row=6, column=0)

	def backtologin(self):
		Tk.destroy(self)
		Admin().mainloop()

	def AddUser(self, event=None):
		conn = sqlite3.connect('sales')
		c = conn.cursor()

		cred = c.execute("SELECT * FROM 'login'").fetchall()

		users = []

		for i in range(0, len(cred)):
			users.append(cred[i][0])
		#before trying anything validate the password here
		if policy.test(self.pwdnew.get()) == []:      
			try:
				if self.pwdnew.get() == self.pwdnewchk.get() and (self.pwdnew.get() != ""):
					#Check if user exists in the database
					if self.unnew.get() in users:
						tk.messagebox.showinfo("User name exists",f"User {self.unnew.get()} in database")
					else:
						c.execute("INSERT INTO 'login' VALUES (?,?) ", (self.unnew.get(),pencrypt.Encrypt(self.pwdnew.get(),key)))
						conn.commit()

						tk.messagebox.showinfo("Success", f'User {self.unnew.get()} is added')
						self.unnew.set("")
						self.pwdnew.set("")
						self.pwdnewchk.set("")
						
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

					tk.messagebox.showinfo("Success", "User Added Successfully Press ok to Login")
					Tk.destroy(self)
					Admin().mainloop()
				else:
					tk.messagebox.showinfo("Check Passwords","Ensure all Fields are Filled and If Passwords Match")
		elif self.unnew.get()== "" or self.pwdnew.get()=="" or self.pwdnewchk.get()=="":
			tk.messagebox.showinfo("Empty Fields","Please ensure all fields are filled")
		else:
			tk.messagebox.showinfo("Password Validation","Password length must be 8,must contain atleast 1 number,letter,non-letter and special symbol")
			
class ShopLogin(tk.Tk):
	#=================================================================================================================#
	def __init__(self):
		super().__init__()
		self.title("Emt Management System")
		self.iconbitmap("sc.ico")
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

		self.fromdateentry = StringVar()
		self.todateentry = StringVar()

		self.debtnameentry = StringVar()
		self.debtcashentry = IntVar()

		self.majinacombo = StringVar()

		self.yearlyentry = IntVar()

		self.entrytv = IntVar()
		self.entrypv = IntVar()


		self.WIDTH, self.HEIGHT = self.winfo_screenwidth(), self.winfo_screenheight()
##		elif (self.WIDTH == 1366 and self.HEIGHT == 768) or (self.WIDTH ==1360 and self.HEIGHT==768):
##		#==============Screen of 1280 x 720 ========================
		#buttons y place values
		self.btny = 672
		self.btnx = 0
		#label height and width
		self.labelheight = 2
		self.labelwidth = 34
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
		self.entrybx = 170
		#quantity x values
		self.entryqx = 530
		#sell price x values
		self.entrydx = 850
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
##		else:
##			#==============Screen of 1280 x 720 ========================
##			#buttons y place values
##			self.btny = 672
##			self.btnx = 0
##			#label height and width
##			self.labelheight = 2
##			self.labelwidth = 34
##			#entries y and x values
##			self.entry1y = 58
##			self.entry2y = 78
##			self.entry3y = 98
##			self.entry4y = 118
##			self.entry5y = 138
##			self.entry6y = 158
##			self.entry7y = 178
##			self.entry8y = 198
##			self.entry9y = 218
##			self.entry10y = 238
##			#combobox x value
##			self.entrybx = 170
##			#quantity x values
##			self.entryqx = 530
##			#sell price x values
##			self.entrydx = 850
##			#price x values
##			self.entrypx = 1180
##			#profit entry and total sales
##			self.xvalue = 1040
##			self.yvalue = 300
##			self.total1y = 642
##			self.profit1y = 672
##			#buttons frame width and height
##			self.buttonsframewidth = 1040
##			self.buttonsframeheight = 800
##			#getsales entry and button
##			self.entrydatey = 420
##			self.entrydatex = 50
##			self.entrydatebuttonx = 220

		self.sale_date_entry = StringVar()

		self.salesframe = Frame(bg="white", width=400, height=900, pady=3).place(x=self.xvalue,y=self.yvalue)

		self.daily = tk.Text(self.salesframe,width=46, height=800, font="time 11",relief=RAISED)
		self.daily.place(x=self.xvalue, y=self.yvalue)

		self.entryt = Entry(bg="white",textvariable=self.entrytv, font="time 11", state='normal',justify='right',bd=5,width=39)
		self.entryt.place(x=self.xvalue, y=self.total1y)

		self.entryp = Entry(bg="white",textvariable=self.entrypv, font="time 11", state='normal',justify='right',bd=5,width=39)
		self.entryp.place(x=self.xvalue, y=self.profit1y)

		self.lb = StringVar()
		self.lbtotal = StringVar()

		
		self.geometry(f'{self.WIDTH}x{self.HEIGHT}+0+0')
	

		self.resizable(False, True)

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
		Shop_title.place(y=0, x=450)

		heading1 = tk.Label(headingframe,text="",bg="lightgrey",fg="blue",font="time 10", bd=0,pady=3,height=3, width=20, relief=None,)
		heading1.grid(row=0, column=0)

		buttonframe = Frame(bg="lightgrey", width=self.buttonsframewidth-4, height=self.buttonsframeheight, pady=3).place(x=2, y=210)

		maincanvas = Canvas(self,width=1920,height=250,bg="cadetblue")
		maincanvas.place(x=0,y=50)
		#Label to Warn user to not conflict with database   
		Product = tk.Label(text="Product".upper(),bg="white",font="time 12 bold", height=self.labelheight, width=self.labelwidth, relief=RAISED)
		Product.grid(row=1, column=0)

		Quantity = tk.Label(text="Quantity".upper(),bg="white",font="time 12 bold", height=self.labelheight, width=self.labelwidth, relief=RAISED)
		Quantity.grid(row=1, column=1)

		Discount = tk.Label(text="Sell Price".upper(),bg="white",font="time 12 bold", height=self.labelheight, width=self.labelwidth, relief=RAISED)
		Discount.grid(row=1, column=2)

		Price = tk.Label(text="Price".upper(),bg="white",font="time 12 bold", height=self.labelheight, width=self.labelwidth, relief=RAISED)
		Price.grid(row=1, column=3)

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

		maincanvas.create_window(self.entrybx,self.entry1y,window=box1)
		maincanvas.create_window(self.entrybx,self.entry2y,window=box2)
		maincanvas.create_window(self.entrybx,self.entry3y,window=box3)
		maincanvas.create_window(self.entrybx,self.entry4y,window=box4)
		maincanvas.create_window(self.entrybx,self.entry5y,window=box5)
		maincanvas.create_window(self.entrybx,self.entry6y,window=box6)
		maincanvas.create_window(self.entrybx,self.entry7y,window=box7)
		maincanvas.create_window(self.entrybx,self.entry8y,window=box8)
		maincanvas.create_window(self.entrybx,self.entry9y,window=box9)
		maincanvas.create_window(self.entrybx,self.entry10y,window=box10)
	
	# #============================================================================================================

	# #============================Quantity Entry Defined Here========================================================
	#   #Quantity Entry Boxes
		entryq1 = tk.Entry(bg="white",textvariable=self.entryq1,font="time 12")
		entryq2 = tk.Entry(bg="white",textvariable=self.entryq2,font="time 12")
		entryq3 = tk.Entry(bg="white",textvariable=self.entryq3,font="time 12")
		entryq4 = tk.Entry(bg="white",textvariable=self.entryq4,font="time 12")
		entryq5 = tk.Entry(bg="white",textvariable=self.entryq5,font="time 12")
		entryq6 = tk.Entry(bg="white",textvariable=self.entryq6,font="time 12")
		entryq7 = tk.Entry(bg="white",textvariable=self.entryq7,font="time 12")
		entryq8 = tk.Entry(bg="white",textvariable=self.entryq8,font="time 12")
		entryq9 = tk.Entry(bg="white",textvariable=self.entryq9,font="time 12")
		entryq10 = tk.Entry(bg="white",textvariable=self.entryq10,font="time 12")

		maincanvas.create_window(self.entryqx,self.entry1y,window=entryq1)
		maincanvas.create_window(self.entryqx,self.entry2y,window=entryq2)
		maincanvas.create_window(self.entryqx,self.entry3y,window=entryq3)
		maincanvas.create_window(self.entryqx,self.entry4y,window=entryq4)
		maincanvas.create_window(self.entryqx,self.entry5y,window=entryq5)
		maincanvas.create_window(self.entryqx,self.entry6y,window=entryq6)
		maincanvas.create_window(self.entryqx,self.entry7y,window=entryq7)
		maincanvas.create_window(self.entryqx,self.entry8y,window=entryq8)
		maincanvas.create_window(self.entryqx,self.entry9y,window=entryq9)
		maincanvas.create_window(self.entryqx,self.entry10y,window=entryq10)



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
		entryD1 = tk.Entry(bg="white",textvariable=self.entryD1,state="disabled",font="time 12")
		entryD2 = tk.Entry(bg="white",textvariable=self.entryD2,state="disabled",font="time 12")
		entryD3 = tk.Entry(bg="white",textvariable=self.entryD3,state="disabled",font="time 12")
		entryD4 = tk.Entry(bg="white",textvariable=self.entryD4,state="disabled",font="time 12")
		entryD5 = tk.Entry(bg="white",textvariable=self.entryD5,state="disabled",font="time 12")
		entryD6 = tk.Entry(bg="white",textvariable=self.entryD6,state="disabled",font="time 12")
		entryD7 = tk.Entry(bg="white",textvariable=self.entryD7,state="disabled",font="time 12")
		entryD8 = tk.Entry(bg="white",textvariable=self.entryD8,state="disabled",font="time 12")
		entryD9 = tk.Entry(bg="white",textvariable=self.entryD9,state="disabled",font="time 12")
		entryD10 = tk.Entry(bg="white",textvariable=self.entryD10,state="disabled",font="time 12")

		maincanvas.create_window(self.entrydx,self.entry1y,window=entryD1)
		maincanvas.create_window(self.entrydx,self.entry2y,window=entryD2)
		maincanvas.create_window(self.entrydx,self.entry3y,window=entryD3)
		maincanvas.create_window(self.entrydx,self.entry4y,window=entryD4)
		maincanvas.create_window(self.entrydx,self.entry5y,window=entryD5)
		maincanvas.create_window(self.entrydx,self.entry6y,window=entryD6)
		maincanvas.create_window(self.entrydx,self.entry7y,window=entryD7)
		maincanvas.create_window(self.entrydx,self.entry8y,window=entryD8)
		maincanvas.create_window(self.entrydx,self.entry9y,window=entryD9)
		maincanvas.create_window(self.entrydx,self.entry10y,window=entryD10)
	
	#============================================================================================================

	#============================Total Price Entry Defined Here=======================================================
		#Total Price Entries
		entryP1 = tk.Entry(bg="white",textvariable=self.entryP1,state="disabled",font="time 12")
		entryP2 = tk.Entry(bg="white",textvariable=self.entryP2,state="disabled",font="time 12")
		entryP3 = tk.Entry(bg="white",textvariable=self.entryP3,state="disabled",font="time 12")
		entryP4 = tk.Entry(bg="white",textvariable=self.entryP4,state="disabled",font="time 12")
		entryP5 = tk.Entry(bg="white",textvariable=self.entryP5,state="disabled",font="time 12")
		entryP6 = tk.Entry(bg="white",textvariable=self.entryP6,state="disabled",font="time 12")
		entryP7 = tk.Entry(bg="white",textvariable=self.entryP7,state="disabled",font="time 12")
		entryP8 = tk.Entry(bg="white",textvariable=self.entryP8,state="disabled",font="time 12")
		entryP9 = tk.Entry(bg="white",textvariable=self.entryP9,state="disabled",font="time 12")
		entryP10 = tk.Entry(bg="white",textvariable=self.entryP10,state="disabled",font="time 12")

		maincanvas.create_window(self.entrypx,self.entry1y,window=entryP1)
		maincanvas.create_window(self.entrypx,self.entry2y,window=entryP2)
		maincanvas.create_window(self.entrypx,self.entry3y,window=entryP3)
		maincanvas.create_window(self.entrypx,self.entry4y,window=entryP4)
		maincanvas.create_window(self.entrypx,self.entry5y,window=entryP5)
		maincanvas.create_window(self.entrypx,self.entry6y,window=entryP6)
		maincanvas.create_window(self.entrypx,self.entry7y,window=entryP7)
		maincanvas.create_window(self.entrypx,self.entry8y,window=entryP8)
		maincanvas.create_window(self.entrypx,self.entry9y,window=entryP9)
		maincanvas.create_window(self.entrypx,self.entry10y,window=entryP10)

	#===================================================================================================================================
	#===================================================================================================================================
		# GrandTotal Button
		grandtotal = tk.Button(buttonframe,text="Total".upper()
			,bg="cadetblue",fg="white",font="time 10",
			bd=0,height=1, width=12, 
			relief=None,command=self.todayssales)
		grandtotal.place(x=20, y=self.btny)

		undobtn = Button(buttonframe,font="time 10",text="UNDO SALE".upper(),bg="cadetblue",fg="white",command=self.UndoLastSale,bd=0,height=1, width=20)
		undobtn.place(x=140, y=self.btny)
		
		#Product Management Button
		prodmgmts = Button(buttonframe,font="time 10",text="Product Management".upper(),bg="cadetblue",fg="white",command=self.prodmgmt,bd=0,height=1, width=20)
		prodmgmts.place(x=320, y=self.btny)

		# Exit Button
		logout = tk.Button(buttonframe,text="Exit".upper()
			,bg="cadetblue",fg="white",font="time 10",
			bd=0,height=1, width=12, 
			relief=None,command=self.logout)
		logout.place(x=660, y=self.btny)

		#debtbutton
		debtbutton = Button(buttonframe,font="time 10",text="Debts".upper(),bg="cadetblue",fg="white",command=self.DebtFunction,bd=0,height=1, width=15)
		debtbutton.place(x=845, y=self.btny)
	#=================================================================================================================#
				#We need name, item, debt
		debtcanvas = Canvas(self,highlightthickness=0,width=218,height=350,bg="lightgrey")
		debtcanvas.place(x=790,y=310)

		madenilabel = Label(fg="cadetblue",text="Debt and Expenses")
		debtcanvas.create_window(108, 10, window=madenilabel)

		self.debtnameentry12 = Entry(bg="white",textvariable=self.debtnameentry,font="time 11",width=26)
		self.debtnameentry.set("")
		debtcanvas.create_window(108,45,window=self.debtnameentry12)


		self.debtcashentry12 = Entry(bg="white",textvariable=self.debtcashentry,font="time 11",width=26)
		debtcanvas.create_window(108,75,window=self.debtcashentry12)


		self.debtview12 = ttk.Combobox(textvariable=self.majinacombo,postcommand=self.updatecomboboxlist,font="time 13")
		debtcanvas.create_window(108, 200,window=self.debtview12)

		self.submitbutton = Button(font="time 11",text="Add".upper(),bg="cadetblue",fg="white",command=self.submittodb,bd=0,height=1, width=6)
		self.submitbutton.place(x=860, y=self.entrydatey+10)

	
		self.removebutton = Button(font="time 11",text="Del".upper(),bg="cadetblue",fg="white",command=self.removedb,bd=0,height=1, width=6)
		self.removebutton.place(x=860, y=self.entrydatey+120)

		self.debtnameentry12.config(state="disabled")
		self.debtcashentry12.config(state="disabled")
		self.debtview12.config(state="disabled")
		self.submitbutton.config(state="disabled")
		self.removebutton.config(state="disabled")

		self.debtcashentry12.bind("<Return>",self.submittodb)

		self.clicktoload = Label(font="time 12", text="*Click Debts to Get Export Sales Functions".upper())
		self.clicktoload.place(x=self.entrydatex, y=self.entrydatey)

	#=================================================================================================================#
	def getsalesbymonth(self):
		return mnsales.salesbymonth(self.fromdateentry.get(),self.todateentry.get())

	def getsalesbyyear(self):
		return mnsales.GetYearlySales(self.yearlyentry.get())
	#=================================================================================================================#
	def DebtFunction(self):
		self.clicktoload.config(text="*Choose Start Date to End Date for Monthly\n*Enter Year only for Yearly Print".upper())

		self.daily.delete(1.0, END)
		self.daily.insert(END,f'Name\t\t\t\tTotal\n')
		self.daily.insert(END, f'{45*"_"}')

		self.debtnameentry12.config(state="normal")
		self.debtcashentry12.config(state="normal")
		self.debtview12.config(state="normal")
		self.submitbutton.config(state="normal")
		self.removebutton.config(state="normal")
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
		self.fromdateEntry = DateEntry(foreground="white",background='cadetblue',date_pattern="dd/m/yyyy",textvariable=self.fromdateentry,font="time 10")
		self.fromdateEntry.place(x=self.entrydatex, y=self.entrydatey+100)

		self.todateEntry = DateEntry(foreground="white",background='cadetblue',date_pattern="dd/m/yyyy",textvariable=self.todateentry,font="time 10")
		self.todateEntry.place(x=self.entrydatex+120, y=self.entrydatey+100)

		self.exportsales = Button(font="time 10",text="Monthly".upper(),bg="cadetblue",fg="white",command=self.getsalesbymonth,bd=0,height=1, width=15)
		self.exportsales.place(x=self.entrydatex+250, y=self.entrydatey+95)

		self.exportyearsales = Button(font="time 10",text="Yearly".upper(),bg="cadetblue",fg="white",command=self.getsalesbyyear,bd=0,height=1, width=15)
		self.exportyearsales.place(x=self.entrydatex+250, y=self.entrydatey+170)

		self.yearlysales = Entry(foreground="black",background='white',textvariable=self.yearlyentry,font="time 10",width=15)
		self.yearlysales.place(x=self.entrydatex, y=self.entrydatey+170)

		self.SalesDateEntry = DateEntry(foreground="white",background='cadetblue',date_pattern="dd/m/yyyy",textvariable=self.sale_date_entry,font=self.font)
		self.SalesDateEntry.place(x=self.entrydatex, y=self.entrydatey-40)

		self.today = Button(font=self.font,text="Sales".upper(),bg="cadetblue",fg="white",command=self.Get_Sales_By_Date,bd=0,height=1, width=15)
		self.today.place(x=self.entrydatex+250, y=self.entrydatey-40)

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

	def exporttocsv(self):
		#---------------------Get Database by date--------------------------------------------#
		tk.messagebox.showinfo("Export as Excel", "Export Daily Sales in Excel Format, Select Date to Export")

		valuestime1 = self.fromdateentry.get()
		valuestime2 = self.todateentry.get()
		
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
		return Admin().mainloop()
	#=================================================================================================================#
	def prodmgmt(self):
		Tk.destroy(self)
		return pm().mainloop()

	#=================================================================================================================#

if __name__ == '__main__':
	Admin().mainloop()



