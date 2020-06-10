from login import admin
from tkinter import *
import tkinter as tk
from tkinter import messagebox
import sys
import os
import time

class Admin(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title('Administrator')
		self.color = ['cadetblue','orange','yellowgreen','lightgrey']
		self.iconbitmap("sc.ico")
		self.mainframe = Frame(bg=self.color[0],width=600,height=600).place(relx=0,rely=0)
		self.drawframe = Frame(bg=self.color[1],width=540,height=5).place(relx=0.05,rely=0.1)
		self.bottomframe = Frame(bg=self.color[1],width=540,height=5).place(relx=0.05,rely=0.9)
		self.sideframe = Frame(bg=self.color[1],width=5,height=480).place(relx=0.05,rely=0.1)
		self.sideframe1 = Frame(bg=self.color[1],width=5,height=485).place(relx=0.945,rely=0.1)
		self.centerframe = Frame(bg=self.color[3],width=532,height=475).place(relx=0.058,rely=0.109)

		self.geometry("600x600+300+50")
		self.resizable(False,False)

		self.Mainmenu()

	def Mainmenu(self):
		heading = Label(self.mainframe,text="Welcome to Administration Page, Kindly Choose a Service".upper())
		heading.place(relx=0.15,rely=0.05)

		btns = Button(self.centerframe,text="Shop".upper(),height=5,width=22,command=self.shop,bg=self.color[0])
		btns.place(relx=0.55,rely=0.15)


		btns1 = Button(self.centerframe,text="Analysis".upper(),height=5,width=22,command=self.analyse,bg=self.color[0])
		btns1.place(relx=0.15,rely=0.15)

		btns2 = Button(self.centerframe,text="mobile money".upper(),height=5,width=22,command=self.mobile,bg=self.color[0])
		btns2.place(relx=0.15,rely=0.4)

		btns4 = Button(self.centerframe,text="Receipt".upper(),height=5,width=22,command=self.receipt,bg=self.color[0])
		btns4.place(relx=0.55,rely=0.4)

		btns3 = Button(self.centerframe,text="Product Manegement".upper(),height=5,width=22,command=self.prodmgmt,bg=self.color[0])
		btns3.place(relx=0.15,rely=0.65)

		btns5 = Button(self.centerframe,text="Exit".upper(),height=5,width=22,command=self.exit,bg=self.color[0])
		btns5.place(relx=0.55,rely=0.65)

if __name__=="__main__":
	try:
		from test2 import InitializeDatabase as dbinit
		dbinit.createdb()
	except:
		pass
	admin().mainloop()
	try:
		os.mkdir('csvf')
	except:
		pass
	