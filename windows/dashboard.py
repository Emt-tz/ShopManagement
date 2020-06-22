from tkinter import *
import tkinter as tk
from Admin import Admin
import sqlite3 as sq
from tkinter import messagebox

class Dashboard(tk.Tk):

	def __init__(self):
		super().__init__()
		self.title('Dashboard')
		self.color = ['cadetblue','orange','yellowgreen','lightgrey']
		self.iconbitmap("sc.ico")
		self.mainframe = Frame(bg=self.color[0],height=600,width=1000).place(relx=0.40,rely=0)
		self.leftframe = Frame(bg=self.color[3],height=600,width=400).place(relx=0,rely=0)
		self.conn = sq.connect('sales')
		self.c = self.conn.cursor()
		self.shopname = StringVar()
		self.shopnumber = StringVar()
		self.geometry('1050x360+150+60')
		self.resizable(False,False)
		self.mainpage()

	def mainpage(self):
		heading = Label(self.leftframe,text='Edit Name and Number'.upper(),width=30).place(relx=0.1,rely=0.1)

		shopnamelable = Label(self.leftframe,text='Shop Name',bg=self.color[3]).place(relx=0.05,rely=0.25)
		shopnameentry = Entry(self.leftframe,width=32,textvariable=self.shopname).place(relx=0.18,rely=0.25)

		shopno = Label(self.leftframe,text='Shop Number',bg=self.color[3]).place(relx=0.05,rely=0.35)
		shopnoentry = Entry(self.leftframe,width=32,textvariable=self.shopnumber).place(relx=0.18,rely=0.35)

		submitbtn = Button(self.leftframe, text='SUBMIT',bg=self.color[0],relief=RAISED,width=20,height=1,command=self.shopd).place(relx=0.13,rely=0.65)

		#users option
		heading2 = Label(self.mainframe,text='Edit Users'.upper(),width=30).place(relx=0.6,rely=0.1)

		currentuser = Text(self.mainframe,height=14,width=30,state='disabled').place(relx=0.42,rely=0.2)
		transferbutton = Button(self.mainframe,text='----------->').place(relx=0.67,rely=0.5)
		transferreduser = Text(self.mainframe,height=14,width=30,state='disabled').place(relx=0.75,rely=0.2)

		submitbtn = Button(self.mainframe, text='DEL',bg=self.color[0],relief=RAISED,width=20,height=1).place(relx=0.79,rely=0.9)

		#exit button
		exitbtn = Button(self.mainframe, text='EXIT',bg=self.color[0],relief=RAISED,width=20,height=1,command=self.exit).place(relx=0.49,rely=0.9)
	
	def shopd(self):
		name = self.shopname.get()
		number = self.shopnumber.get()

		if name or number == '':
			tk.messagebox.showinfo('empty','fill valid values')
		else:
			self.c.execute("DELETE FROM 'shopdetails'")
			self.c.execute("INSERT INTO 'shopdetails' Values (?,?) ",(name,number))
			self.conn.commit()

			print(name,number)

	def exit(self):
		Tk.destroy(self)
		return Admin().mainloop()

# if __name__ == '__main__':
# 	Dashboard().mainloop()	