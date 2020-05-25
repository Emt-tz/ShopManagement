
from tkinter import *
import tkinter as tk
from tkinter import messagebox
import sqlite3 as sq
import datetime as dt

conn = sq.connect('sales')

c = conn.cursor()

timenow = str(dt.datetime.today())

v = c.execute("SELECT * FROM 'openingstock' WHERE Timed=?",(timenow[0:10],)).fetchall()

dates = []

for i in range(0, len(v)):
	try:
		dates.append(v[0][i])
	except:
		pass

class Balance(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title(f'Mobile Money System {timenow[0:10]}')
		#Initiate connection to the database
#====================================================================================================================
		self.conn = sq.connect("sales")
		self.c = self.conn.cursor()
		#This variables will hold cash in values
#====================================================================================================================
		self.cashin1 = IntVar()
		self.cashin2 = IntVar()
		self.cashin3 = IntVar()
		self.cashin4 = IntVar()
#====================================================================================================================

		#This variables will hold cash out values
#====================================================================================================================
		self.cashin5 = IntVar()
		self.cashin6 = IntVar()
		self.cashin7 = IntVar()
		self.cashin8 = IntVar()

		self.total = IntVar()

		self.openingmainlabel = Label(text="Total",height=2)
		self.openingmainlabel.place(relx=0,rely=0.6)

		self.closingmainlabel = Label(text="Total",height=2)
		self.closingmainlabel.place(relx=0.5,rely=0.6)
#====================================================================================================================
		self.geometry("800x360+300+200")
		self.resizable(False,False)
		self.MainPage()
		#self.initiate()
#====================================================================================================================
	def initiate(self):
		#====================================================================================================================
		#Opening stock data
		v1 = self.c.execute("SELECT * FROM 'openingstock' ").fetchall()
		if timenow[0:10] in dates:
			try:
				self.cashin1.set(v1[0][1])
				self.cashin2.set(v1[0][2])
				self.cashin3.set(v1[0][3])
				self.cashin4.set(v1[0][4])
			except:
				pass

		#Closing stock data
		v2 = self.c.execute("SELECT * FROM 'closingstock' ").fetchall()
		if timenow[0:10] in dates:
			try:
				self.cashin5.set(v2[0][1])
				self.cashin6.set(v2[0][2])
				self.cashin7.set(v2[0][3])
				self.cashin8.set(v2[0][4])
			except:
				pass
		var = v2[0][5]-v1[0][5]
		self.total.set(format(var,","))
		self.openingmainlabel.config(text="")
		self.closingmainlabel.config(text="")

#====================================================================================================================
	def MainPage(self):
#====================================================================================================================
		self.initiate()

		self.loadbutton = Button(text="Load Data", command=self.initiate)
		self.loadbutton.place(relx=0, rely=0.9)

		self.nettotallabel = Label(text="Net Total",fg="red")
		self.nettotallabel.place(relx=0.69, rely=0.91)

		self.nettotal = Entry(bd=2,textvariable=self.total,fg="red",justify="right")
		self.nettotal.place(relx=0.79, rely=0.9)

		self.mainsystem = Button(text="Exit", command=self.exit)
		self.mainsystem.place(relx=0.5,rely=0.9)
#====================================================================================================================
		#Opening Stock 
		#Render all the main labels
		Label_dict = {
			0:"Mpesa",
			1:"Tigo Pesa",
			2:"Airtel Money",
			3:"Opening Cash"
		}

		colors = ["red","blue","tomato","green"]

		for k, j in Label_dict.items():
			entries = tk.Label(text=j,width=12,fg=colors[k],height=1,font="time 12 bold", justify="left",pady=6,padx=0)
			entries.grid()
		#Render all the main entries
		variable_dict = {
			0:self.cashin1,
			1:self.cashin2,
			2:self.cashin3,
			3:self.cashin4,
		}

		for k, j in variable_dict.items():
			entries = tk.Entry(textvariable=j,fg=colors[k],font="time 12 bold", justify="right")
			entries.grid(row=k,column=1)

		#separate opening stock with closing stock
		separation_frame1 = tk.Frame(bg="cadetblue",height=174,width=1)
		separation_frame1.place(relx=0.48)

		separation_frame2 = tk.Frame(bg="cadetblue",height=1,width=800)
		separation_frame2.place(relx=0,rely=0.48)

		#Required buttons
		add_button = Button(text="Add",height=1,width=5,bg="white",command=self.openstockbtn)
		add_button.place(rely=0.38,relx=0.365)
#====================================================================================================================

#====================================================================================================================
		#Closing stock zone
		#Render all the main labels
		Label_dict = {
			0:"Mpesa",
			1:"Tigo Pesa",
			2:"Airtel Money",
			3:"Closing Cash"
		}

		colors = ["red","blue","tomato","green"]

		for k, j in Label_dict.items():
			entries = tk.Label(text=j,width=12,fg=colors[k],height=1,font="time 12 bold", justify="left",pady=6,padx=0)
			entries.grid(row=k,column=2,padx=34)
		#Render all the main entries
		variable_dict = {
			0:self.cashin5,
			1:self.cashin6,
			2:self.cashin7,
			3:self.cashin8,
		}

		colors = ["red","blue","tomato","green"]

		for k, j in variable_dict.items():
			entries = tk.Entry(textvariable=j,fg=colors[k],font="time 12 bold", justify="right")
			entries.grid(row=k, column=3)
		#Required buttons
		add_button = Button(text="Add",height=1,width=5,bg="white",command=self.closingstockbtn)
		add_button.place(rely=0.38,relx=0.897)
#====================================================================================================================

	def openstockbtn(self):
		conn = sq.connect('sales')
		c = conn.cursor()

		cashin = self.cashin1.get()+self.cashin2.get()+self.cashin3.get()+self.cashin4.get()

		values = (timenow[0:10],self.cashin1.get(),
		self.cashin2.get(),
		self.cashin3.get(),
		self.cashin4.get(),cashin)

		if 0 in values:
			tk.messagebox.showinfo("Zero Values","Please input valid values")
		else:
			if str(timenow[0:10]) in dates:
				#tk.messagebox.askyesno("Reply","Do you want to overwrite")
				c.execute("DELETE FROM openingstock WHERE ROWID = (SELECT MAX(ROWID) FROM 'openingstock');")
				c.execute("INSERT INTO openingstock Values(?,?,?,?,?,?)",values)
				conn.commit()
				conn.close()
				self.openingmainlabel.config(text=f'Opening Stock =={format(cashin,",")}')
				self.cashin1.set("0")
				self.cashin2.set("0")
				self.cashin3.set("0")
				self.cashin4.set("0")
				
			else:
				c.execute("INSERT INTO openingstock Values(?,?,?,?,?,?)",values)
				conn.commit()
				conn.close()
				self.openingmainlabel.config(text=f'Opening Stock =={format(cashin,",")}')
				self.cashin1.set("0")
				self.cashin2.set("0")
				self.cashin3.set("0")
				self.cashin4.set("0")

	def closingstockbtn(self):
		conn = sq.connect('sales')
		c = conn.cursor()

		cashout = self.cashin5.get()+self.cashin6.get()+self.cashin7.get()+self.cashin8.get()

		values = (timenow[0:10],self.cashin5.get(),
		self.cashin6.get(),
		self.cashin7.get(),
		self.cashin8.get(),cashout)

		if 0 in values:
			tk.messagebox.showinfo("Zero Values","Please input valid values")
		else:
			if str(timenow[0:10]) in dates:
				c.execute("DELETE FROM closingstock WHERE ROWID = (SELECT MAX(ROWID) FROM 'closingstock');")
				c.execute("INSERT INTO closingstock Values(?,?,?,?,?,?)",values)
				conn.commit()
				conn.close()
				self.closingmainlabel.config(text=f'Closing Stock =={format(cashout,",")}')
				self.cashin5.set("0")
				self.cashin6.set("0")
				self.cashin7.set("0")
				self.cashin8.set("0")

			else:
				c.execute("INSERT INTO closingstock Values(?,?,?,?,?,?)",values)
				conn.commit()
				conn.close()
				self.closingmainlabel.config(text=f'Closing Stock =={format(cashout,",")}')
				self.cashin5.set("0")
				self.cashin6.set("0")
				self.cashin7.set("0")
				self.cashin8.set("0")

	def exit(self):
		from shop import ShopLogin
		Tk.destroy(self)
		return ShopLogin().mainloop()
	


if __name__ == '__main__':
	Balance().mainloop()


'''
Okay so we can manage our balance, our cash in , we can add payment options
as for example mpesa, tigo pesa, airtel money

nbc wakala, all the cash that goes in and out

hey new name emt stationery solution
'''
