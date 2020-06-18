from test2 import PasswordEncrypter as pencrypt
from password_strength import PasswordPolicy as pc
import tkinter as tk
from tkinter import *
from tkinter import ttk
import sqlite3

key = pencrypt.GenerateKey()

class admin(tk.Tk):
	#=================================================================================================================#
	def __init__(self):
		super().__init__()
		self.title("Emt Mgmt Login")
		self.iconbitmap("sc.ico")
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
		heading = tk.Label(text="Login to Continue",fg="blue",font="time 14 bold", bd=0,height=3, width=18, relief=None,)
		heading.grid(row=0, column=0, columnspan=3) 
		for i in range(1, 2):
			col = []
			for j in range(0, 1):
				col.append(tk.Label(textvariable=self.lb,fg="white",font="time 14 bold", height=2, width=14, relief=RAISED))
				self.lb.set("User Data")
				col[j].grid(row=i, column=j)
			self.labels.append(col)
		

		username = tk.Entry(textvariable=self.un, bd=2,font="time 14 bold",width=22)
		username.grid(row=2, column=0)

		password = tk.Entry(textvariable=self.pwd, bd=2,font="time 14 bold", show="*",width=22)
		password.grid(row=3, column=0)

		loginbtn = tk.Button(text="Login",font="time 14 bold", command=self.Authenticate)
		loginbtn.grid(row=4, column=0)

		authtext = tk.Label(textvariable=self.txt,fg="cadetblue",font="time 12", relief=RAISED)
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
			tk.messagebox.showinfo("Error Login","Please fill all Fields")
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
							self.success()
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
							self.success()
						except:
							print("Error")
						#ShopLogin().mainloop()
					else:
						tk.messagebox.showinfo("Check","Review your credentials")
	def success(self):
		Tk.destroy(self)
		from Admin import Admin
		return Admin().mainloop()

	def CallAdmin1(self):
		Tk.destroy(self)
		return Admin1().mainloop()

class Admin1(tk.Tk):
	#=================================================================================================================#
	def __init__(self):
		super().__init__()
		self.title("Emt Mgmt Login")
		self.iconbitmap("sc.ico")
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
		heading = tk.Label(text="New User SignUp",fg="blue",font="time 14 bold", bd=0,height=3, width=18, relief=None,)
		heading.grid(row=0, column=0, columnspan=3) 
		for i in range(1, 2):
			col = []
			for j in range(0, 1):
				col.append(tk.Label(textvariable=self.lb,fg="cadetblue",font="time 14 bold", height=2, width=14, relief=RAISED))
				self.lb.set("User Info")
				col[j].grid(row=i, column=j)
			self.labels.append(col)
		

		username = tk.Entry(textvariable=self.unnew, bd=2,font="time 14 bold",width=22)
		username.grid(row=2, column=0)

		password = tk.Entry(textvariable=self.pwdnew, bd=2,font="time 14 bold", show="*",width=22)
		password.grid(row=3, column=0)

		passwordconfirm = tk.Entry(textvariable=self.pwdnewchk, bd=2,font="time 14 bold", show="*",width=22)
		passwordconfirm.grid(row=4, column=0)

		createuserbtn = tk.Button(text="CreateUser",font="time 14 bold", command=self.AddUser)
		createuserbtn.grid(row=5, column=0)

		loginbtn = tk.Button(text="Back to Login",font="time 14 bold", command=self.backtologin)
		loginbtn.grid(row=6, column=0)

		passwordconfirm.bind('<Return>',self.AddUser)

	def backtologin(self):
		Tk.destroy(self)
		admin().mainloop()

	def AddUser(self, event=None):
		conn = sqlite3.connect('sales')
		c = conn.cursor()

		cred = c.execute("SELECT * FROM 'login'").fetchall()

		users = []

		policy = pc.from_names(length=8,uppercase=1,numbers=1,special=1,nonletters=1)

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
					admin().mainloop()
				else:
					tk.messagebox.showinfo("Check Passwords","Ensure all Fields are Filled and If Passwords Match")
		elif self.unnew.get()== "" or self.pwdnew.get()=="" or self.pwdnewchk.get()=="":
			tk.messagebox.showinfo("Empty Fields","Please ensure all fields are filled")
		else:
			tk.messagebox.showinfo("Password Validation","Password length must be 8\nmust contain atleast 1 number\nletter,non-letter and special symbol")

# if __name__=="__main__":
# 	admin().mainloop()
