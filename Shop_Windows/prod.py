#This will manage the products addition or removing
#Function inside here include
"""
1. Add Product(Name,Buy Price, Sell Price, Quantity)
2. Modify Product
3. Delete Product
"""

import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import sys
import sqlite3

#from shop import ShopLogin as sl

class ProductManagement(tk.Tk):
		
	def __init__(self):
		#=============================================================================================
		super().__init__()
		self.title("Product Management")
		self.iconbitmap("sc.ico")
		self.turn = True
		self.conn = sqlite3.connect('sales')
		self.c = self.conn.cursor()
		self.btns = []
		self.font = "Verdana 10 bold"
		self.bd = 20

		self.namevar = StringVar()
		self.buypricevar = IntVar()
		self.sellpricevar = IntVar()
		self.quantityvar = IntVar()

		self.namevar1 = StringVar()
		self.buypricevar1 = IntVar()
		self.sellpricevar1 = IntVar()
		self.quantityvar1 = IntVar()

		self.btncommands = []
		self.btnstate = [None,None,None,None]
		self.geometry('450x366+300+200')
		self.resizable(False, False)
		self.Load()

		#=============================================================================================

	def Load(self):
		#=============================================================================================
		#Create Main Containers
		top_frame = Frame(bg='yellowgreen', width=450, height=50, pady=3)
		center_frame = Frame(bg='grey', width=450, height=175, padx=3, pady=3)
		bottom_frame = Frame(bg='yellowgreen', width=450, height=100, pady=3)
		#Layout the Main Containers
		top_frame.grid(row=0, sticky="ew")
		center_frame.grid(row=1, sticky="nsew")
		bottom_frame.grid(row=2,sticky="ew")
	
		#=============================================================================================
		# create the widgets for the top frame

		Heading = Label(top_frame, text="Welcome to Product Management".upper(), font=self.font).place(
			x=225, y=20,anchor="center")
		#=============================================================================================
		msg = Label(center_frame, font="time 16", text="*Click Button to Load Functionality").place(x=15,y=70)


		#=============================================================================================
		#Buttons Generator
		btn_dict = {2:"List Products  ", 0:"Add Products   ",3:"Modify Products", 1:"Delete Products"}

		btncommands = [self.AddProduct, self.DeleteProducts,self.ListProducts,self.ModifyProducts]


		for k, j in sorted(btn_dict.items()):
			btns = Button(bottom_frame,text=j, width=12,height=1,pady=4,font=self.font, command=btncommands[k], state=self.btnstate[k])
			btns.grid()

			self.btns.append(btns)

		

		#=============================================================================================
	def AddProduct(self):
		#=============================================================================================
		#This Function is going to deal with Addition of Products
		#Text Variables
	
		#Main Layout:
		self.geometry('850x366+300+200')
		editframe = Frame(bg="yellowgreen", width=450, height=366, pady=3).place(x=450,y=0)
		name = Label(editframe,text="Name", font=self.font).place(x=450,y=50)
		buy_price = Label(editframe,text="Buy_Price", font=self.font).place(x=450,y=100)
		sell_price = Label(editframe,text="Sell_Price", font=self.font).place(x=450,y=150)
		quantity = Label(editframe,text="Quantity", font=self.font).place(x=450,y=200)

		addbtn = Button(editframe, text="Add", font=self.font, command=self.addproduct).place(x=500,y=320)
		clearbtn = Button(editframe, text="Back",font=self.font, command=self.clearbtn).place(x=600, y=320)
		#Entries to get data
		name_entry = Entry(font=self.font,textvariable=self.namevar).place(x=590,y=50)
		buy_price_entry = Entry(font=self.font,textvariable=self.buypricevar).place(x=590, y=100)
		sell_price_entry = Entry(font=self.font,textvariable=self.sellpricevar).place(x=590, y=150)
		quantity_entry = Entry(font=self.font,textvariable=self.quantityvar).place(x=590, y=200)

		self.btns[1].config(state=tk.DISABLED)
		self.btns[2].config(state=tk.DISABLED)
		self.btns[3].config(state=tk.DISABLED)

		

		exitbtn = Button(editframe, font=self.font, command=self.maingui,text="Exit").place(x=700,y=320)
		#=============================================================================================

		#=============================================================================================
	def addproduct(self):
		#tk.messagebox.showinfo("Empty Values", "Please Fill all Fields")

		values1 = self.namevar.get()
		values2 = self.buypricevar.get()
		values3 = self.sellpricevar.get()
		values4 = self.quantityvar.get()

		#check if empty value
		if values1 == "":
			tk.messagebox.showinfo("Empty Values", "Please Enter a Valid Value")
		else:
			values = (values1.upper(), values2, values3, values4)

			
			try:
				added = [self.namevar.get(), self.buypricevar.get(), self.sellpricevar.get(), self.quantityvar.get()]
				tk.messagebox.showinfo("Collected", f'added = {added}')

				self.c.executemany("INSERT INTO 'AddProducts' VALUES (?,?,?,?)", (values,))
				self.c.executemany("INSERT INTO 'AddTemp' VALUES (?,?,?,?)", (values,))

				self.namevar.set("")
				self.buypricevar.set("") 
				self.sellpricevar.set("")
				self.quantityvar.set("")

			except sqlite3.ProgrammingError:
				tk.messagebox.showinfo("Error","Try Again")

		#self.c.executemany("INSERT INTO 'AddProducts' VALUES (?,?,?,?)", (values,))
		#=============================================================================================

	def ListProducts(self):
		self.geometry('900x366+300+200')
		#=============================================================================================
		self.btns[0].config(state=tk.DISABLED)
		self.btns[1].config(state=tk.DISABLED)
		self.btns[3].config(state=tk.DISABLED)

		editframe = Frame(bg="white", width=450, height=366, pady=3).place(x=450,y=0)

		products = self.c.execute("SELECT * FROM AddProducts ORDER BY Quantity DESC").fetchall()

		#Cerate 4 List Boxes to view the products 
		self.textlist1 = Listbox(editframe,font="time 8", height=20,width=21, fg="blue",yscrollcommand=self.yscroll2)
		self.textlist1.place(x=452)
		self.textlist1.insert(END, "  PRODUCTS")
		self.textlist1.insert(END,"--------------------------------")

		self.textlist2 = Listbox(editframe,font="time 8", height=20,width=16, fg="blue",yscrollcommand=self.yscroll2)
		self.textlist2.place(x=580)
		self.textlist2.insert(END, "BUYPRICE")
		self.textlist2.insert(END,"--------------------------------")

		self.textlist3 = Listbox(editframe,font="time 8", height=20,width=16, fg="blue")
		self.textlist3.place(x=680)
		self.textlist3.insert(END, "SELLPRICE")
		self.textlist3.insert(END,"--------------------------------")

		self.textlist4 = Listbox(editframe,font="time 8", height=20,width=16, fg="blue")
		self.textlist4.place(x=780)
		self.textlist4.insert(END, "QUANTITY")
		self.textlist4.insert(END,"--------------------------------")

		self.scrollbar = Scrollbar(self, orient='vertical')

		self.scrollbar.config(command=self.yview)
		self.scrollbar.place(x=880,height=310)
		

		for row in products:
			self.textlist1.insert(END, '{:10.16}'.format(row[0].upper()))
			self.textlist1.insert(END, "--------------------------------")
			self.textlist2.insert(END, f'  {row[1]}')
			self.textlist2.insert(END, "--------------------------------")
			self.textlist3.insert(END, f'  {row[2]}')
			self.textlist3.insert(END, "--------------------------------")
			self.textlist4.insert(END, f'  {row[3]}')
			self.textlist4.insert(END, "--------------------------------")

		
		clearbtn = Button(editframe, text="Back",font="Verdana 10 bold", command=self.clearbtn).place(x=600, y=320)
		exitbtn = Button(editframe, font=self.font, command=self.maingui, text="Exit").place(x=750,y=320)
				
		#=============================================================================================
	def DeleteProducts(self):
		self.geometry('850x366+300+200')
		self.btns[0].config(state=tk.DISABLED)
		self.btns[2].config(state=tk.DISABLED)
		self.btns[3].config(state=tk.DISABLED)

		editframe = Frame(bg="white", width=450, height=366, pady=3).place(x=450,y=0)

		name = Label(editframe,text="Name", font=self.font).place(x=450,y=150)

		products = self.c.execute("SELECT * FROM AddProducts").fetchall()

		prod = []

		prod_dict = {}

		for row in products:
			ne = row[0]
			prod.append(ne)
			

		def combo():
			return [x for x in sorted(prod)]

		self.name_entry12 = ttk.Combobox(font=self.font,textvariable=self.namevar1,values=combo(), width=19,height=19)
		self.name_entry12.place(x=590,y=150)

		delbtn = Button(editframe, text="Delete",font="Verdana 10 bold",command=self.delcombo).place(x=455, y=320)
		clearbtn = Button(editframe, text="Back",font="Verdana 10 bold", command=self.clearbtn).place(x=600, y=320)
		exitbtn = Button(editframe, font=self.font, command=self.maingui, text="Exit").place(x=750,y=320)
		#=============================================================================================
	
		#=============================================================================================
	def ModifyProducts(self):
		self.geometry('850x366+300+200')
		self.btns[0].config(state=tk.DISABLED)
		self.btns[1].config(state=tk.DISABLED)
		self.btns[2].config(state=tk.DISABLED)

		#Main UI

		editframe = Frame(bg="yellowgreen", width=450, height=366, pady=3).place(x=450,y=0)

		name = Label(editframe,text="Name", font=self.font).place(x=450,y=50)
		buy_price = Label(editframe,text="Buy_Price", font=self.font).place(x=450,y=100)
		sell_price = Label(editframe,text="Sell_Price", font=self.font).place(x=450,y=150)
		quantity = Label(editframe,text="Quantity", font=self.font).place(x=450,y=200)

		#Entries to modify data

		products = self.c.execute("SELECT * FROM AddProducts").fetchall()

		prod = []

		prod_dict = {}

		for row in products:
			ne = row[0]
			prod.append(ne)
			

		def combo():
			return [x for x in sorted(prod)]
		#display previous stock quantity
		
		name_entry = ttk.Combobox(font=self.font,textvariable=self.namevar1,values=combo(),width=19,height=19)
		name_entry.place(x=590,y=50)
		buy_price_entry = Entry(font=self.font,textvariable=self.buypricevar1).place(x=590, y=100)
		sell_price_entry = Entry(font=self.font,textvariable=self.sellpricevar1).place(x=590, y=150)
		quantity_entry = Entry(font=self.font,textvariable=self.quantityvar1).place(x=590, y=200)

	
	
		updatebtn = Button(editframe, text="Update",font="Verdana 10 bold",command=self.checkcombo).place(x=455, y=320)
		clearbtn = Button(editframe, text="Back",font="Verdana 10 bold", command=self.clearbtn).place(x=600, y=320)
		exitbtn = Button(editframe, font=self.font, command=self.maingui, text="Exit").place(x=750,y=320)
		#=============================================================================================
		name_entry.bind("<<ComboboxSelected>>", self.modif)
		#=============================================================================================
	def modif(self,event=None):

			name = self.namevar1.get()
			v = self.c.execute("SELECT * FROM AddProducts WHERE Name=?",(name,)).fetchall()

			self.buypricevar1.set(v[0][1])
			self.sellpricevar1.set(v[0][2])
			self.quantityvar1.set(v[0][3])

	def checkcombo(self):

		x = self.namevar1.get()
		x2 = self.buypricevar1.get()
		x3 = self.sellpricevar1.get()
		x4 = self.quantityvar1.get()

		products = self.c.execute("SELECT * FROM AddProducts").fetchall()

		prod = []

		for row in products:
			ne = row[0]
			#print(ne)
			prod.append(ne)
		
		if x in prod:
			#print(x)
			values = (x, x2, x3, x4)
			self.c.execute("DELETE FROM AddProducts where Name=?", (x,))
			self.c.execute("INSERT INTO AddProducts VALUES (?,?,?,?)", values)

			self.conn.commit()

			self.c.execute("DELETE FROM AddTemp where Name=?", (x,))
			self.c.execute("INSERT INTO AddTemp VALUES (?,?,?,?)", values)

			self.conn.commit()
			tk.messagebox.showinfo("Success", f'Succesfully Updated {x.upper()}')
		else:
			tk.messagebox.showinfo("Not Present", "Selected Item is Not Found") 
		#=============================================================================================
	def delcombo(self):
		#=============================================================================================

		x = self.namevar1.get()

		products = self.c.execute("SELECT * FROM AddProducts").fetchall()

		prod = []

		for row in products:
			ne = row[0]
			#print(ne)
			prod.append(ne)
		
		if x in prod:
			self.c.execute("DELETE FROM AddProducts where Name=?", (x,))
			self.c.execute("DELETE FROM AddTemp where Name=?", (x,))
			self.conn.commit()
			tk.messagebox.showinfo("Success", f'Succesfully Deleted {x.upper()}')
		else:
			tk.messagebox.showinfo("Not Present", "Selected Item is Not Found") 
		self.after(1, self.DeleteProducts(),END)
		#=============================================================================================

	def clearbtn(self):
		self.geometry('450x366+300+200')
		self.conn.commit()  
		self.btns[0].config(state=tk.NORMAL)
		self.btns[1].config(state=tk.NORMAL)
		self.btns[2].config(state=tk.NORMAL)
		self.btns[3].config(state=tk.NORMAL)

	def maingui(self):
		self.conn.commit()  
		self.conn.close()
		Tk.destroy(self)
		from Admin import Admin
		return Admin().mainloop()

	def yscroll1(self, *args):
		if self.textlist2.yview() != self.textlist1.yview():
			self.textlist2.yview_moveto(args[0])
		self.scrollbar.set(*args)

	def yscroll2(self, *args):
		if self.textlist1.yview() != self.textlist2.yview():
			self.textlist1.yview_moveto(args[0])
		self.scrollbar.set(*args)

	def yscroll4(self, *args):
		if self.textlist2.yview() != self.textlist1.yview():
			self.textlist2.yview_moveto(args[0])
		self.scrollbar.set(*args)

	def yscroll3(self, *args):
		if self.textlist1.yview() != self.textlist2.yview():
			self.textlist1.yview_moveto(args[0])
		self.scrollbar.set(*args)

	def yview(self, *args):
		self.textlist1.yview(*args)
		self.textlist2.yview(*args)
		self.textlist3.yview(*args)
		self.textlist4.yview(*args)

# ProductManagement().mainloop()
