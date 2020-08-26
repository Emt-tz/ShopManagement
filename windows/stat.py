#this is the overall final product
#========================the main import area==============================================
from password_strength import PasswordPolicy as pc
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import sqlite3 as sq
import sys,time
import itertools as IT
import csv
from tkinter.font import Font
import datetime as dt
from tkcalendar import DateEntry
import base64,os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import subprocess as s
try:
	os.system('db.exe')
except:
	pass


#=====================================test2====================================================
def dicttable(dictn):

	root = tk.Tk()
	root.withdraw()
	matrix = zip(*[value if isinstance(value, list) else IT.repeat(value) for key,value in dictn.items()])
	v = (''.join(['{:10}'.format(key) for key in dictn.keys()]))
	for row in matrix:
		y = (''.join(['{:14}'.format(str(item)) for item in row]))
		tk.messagebox.showinfo('Running Low',f'The Following products are running low\n\n\n{v}\n{y}')
		break

from matplotlib import pyplot as plt
class graph:
	def plot(x, y,fromdate,todate,xpos,ypos,text):
		plt.xlabel("Products Sold".upper())
		plt.ylabel("Quantity Sold".upper())
		plt.title(f'Shop Sales from {fromdate} to {todate}')
		plt.xticks(rotation=90)
		x_pos = xpos
		y_pos = ypos
		plt.text(x_pos,y_pos,text,transform=plt.gca().transAxes)
		plt.gcf().subplots_adjust(bottom=0.3)
		plt.bar(x,y)
		plt.ylim(ymin=0)
		plt.show()


class MonthlySales:

	def GetYearlySales(year):
		if year == 0:
			messagebox.showinfo("Error","Please Enter a valid Year")
		else:
			conn = sq.connect('sales')
			c = conn.cursor()

			years = c.execute("SELECT * FROM 'Daily Sales'").fetchall()

			dt = []

			for row in years:
				date,mn,yr = str(row[0]).split("/")
				dt.append(f'{date}/{mn}/{yr}')

			query = f"SELECT * FROM 'Daily Sales' WHERE Timed in ({','.join(['?']*len(dt))})"

			stsales1 = c.execute(query,dt).fetchall()

			dtsales = {}

			for row in stsales1:
				date,mn,yr = str(row[0]).split("/")
				if yr == str(year):
					prod = row[1]
					quan = row[2]
					total = row[4]
					if prod in dtsales:
						y = str(dtsales[prod])
						z = str(y).replace("(","")
						zn = z.replace(")", "")
						f = zn.replace(" ","")
						p,n = f.split(",")
						#print(p)
						dtsales.update({prod:(quan+int(p),total+int(n))})
					else:
						dtsales.update({prod:(quan,total)})
			filename = 'csvf/Sales2.csv'

			final = []
			profitn = []

			with open(filename,'w',newline='') as file:
				w = csv.writer(file)
				w.writerow(["Date","Product","Quantity","Price"])
				for k,v in dtsales.items():
					newv = str(v).replace("(","")
					newv = newv.replace(")","")
					q,p = newv.split(",")
					finall = p.replace(" ","")
					final.append(finall)
					w.writerow(["",k.upper(),q,finall])
					x = c.execute("SELECT * FROM 'AddTemp'").fetchall()
					for i in range(0, len(x)):
						productname = x[i][0]
						if productname == k:
							prof = (Profit.profit(int(x[i][1]),int(x[i][3]),int(x[i][2]),int(q)))
							profitn.append(int(prof))

				#loop through the list and and calculate total
				totalsales = 0
				for i in range(0, len(final)):
					if len(final[i]) == 1:
						totalsales = final[0]
					else:
						totalsales = totalsales + int(final[i])
				w.writerow(["","","",""])
				w.writerow(["Jumla","","",totalsales])
				w.writerow(["Faida","","",sum(profitn)])

		return ConvertCsvtoExcel.convertToExcel(filename)

	def salesbymonth(fromdate, todate):
		conn = sq.connect('sales')
		c = conn.cursor()

		#this works if month is the same

		#predefine our dates at the top
		date,mn1,yer=fromdate.split("/")

		#what if month has changed???

		date2,mn2,yer2=todate.split("/")

		if mn1 != mn2:
			messagebox.showinfo("Monthly Support","Only 1 Month Export is Supported\ni.e 1/4/2020-30/4/2020 and not\n1/4/2020-1/5/2020")
		else:
			dt = []

			dtsales = {}

			for i in range(int(date),int(date2)+1):
				dt.append(f'{i}/{mn1}/{yer}')

			for i in range(0, len(dt)):
				stsales1 = c.execute("SELECT * FROM 'Daily Sales' WHERE Timed=?",(dt[i],)).fetchall()

				for row in stsales1:
					product = row[1]
					quantity = row[2]
					price = row[4]

					if product in dtsales:
						y = str(dtsales[product])
						z = str(y).replace("(","")
						zn = z.replace(")","")
						f = zn.replace(" ","")
						p,n = f.split(",")
						dtsales.update({product:(quantity+int(p),price+int(n))})
					else:
						dtsales.update({product:(quantity,price)})

			#writing to the csv so as to export to excel
			filename = 'csvf/Sales1.csv'

			final = []
			profitn = []

			with open(filename,'w',newline='') as file:
				w = csv.writer(file)
				w.writerow(["Date","Product","Quantity","Price"])
				for k,v in dtsales.items():
					newv = str(v).replace("(","")
					newv = newv.replace(")","")
					q,p = newv.split(",")
					finall = p.replace(" ","")
					final.append(finall)
					w.writerow(["",k.upper(),q,finall])

					x = c.execute("SELECT * FROM 'AddTemp'").fetchall()
					for i in range(0, len(x)):
						productname = x[i][0]
						if productname == k:
							prof = (Profit.profit(int(x[i][1]),int(x[i][3]),int(x[i][2]),int(q)))
							profitn.append(int(prof))

				#loop through the list and and calculate total
				totalsales = 0
				for i in range(0, len(final)):
					if len(final[i]) == 1:
						totalsales = final[0]
					else:
						totalsales = totalsales + int(final[i])
				w.writerow(["","","",""])
				w.writerow(["Jumla","","",totalsales])
				w.writerow(["Faida","","",sum(profitn)])
				
		return ConvertCsvtoExcel.convertToExcel(filename)

class Profit:

	def profit(bp,qt,sp,nqt):
		priceforone = bp/qt
		profit = sp - priceforone
		value = sp*nqt

		return nqt*profit

class PasswordEncrypter:

	def GenerateKey():
		password_provided = "password" # This is input in the form of a string
		password = password_provided.encode() # Convert to type bytes
		salt = b'salt_' # CHANGE THIS - recommend using a key from os.urandom(16), must be of type bytes
		kdf = PBKDF2HMAC(
		    algorithm=hashes.SHA256(),
		    length=32,
		    salt=salt,
		    iterations=100000,
		    backend=default_backend()
		)
		key = base64.urlsafe_b64encode(kdf.derive(password))
		return key

	def Encrypt(userpassword,key):
		msg = userpassword.encode()

		f = Fernet(key)

		encrypted = f.encrypt(msg)

		return encrypted


	def Decrypt(encryptedpassword,key):
		
		f = Fernet(key)
		decrypted = f.decrypt(encryptedpassword)

		return decrypted

class ConvertCsvtoExcel:

	def getCSV(file):
		from pandas import read_csv
		return read_csv(file)

	def convertToExcel(file):
		try:
			x = ConvertCsvtoExcel.getCSV(file)
			export_file_path = filedialog.asksaveasfilename(defaultextension='.xlsx')
			x.to_excel(export_file_path, index=None, header=True)
			messagebox.showinfo("Success",f'exported successfully')
		except:
			messagebox.showinfo("Speciy Directory","Please Specify Place To Save")
			
class Stock:

	def checkstock():
		conn = sq.connect('sales')
		c = conn.cursor()

		v = c.execute("SELECT * FROM AddProducts").fetchall()

		# try:
		prod = {}

		for row in v:
			if row[3] <= 5:
				prod.update({row[0]:row[3]})

		if len(prod) != 0:
			dicttable(prod)
		else:
			pass
		# except:
		# 	pass

#=====================================test2====================================================


#===========================Main Page which service is choosen=================================
class Admin(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title('Administrator')
		self.iconbitmap('sc.ico')
		self.color = ['cadetblue','orange','yellowgreen','lightgrey']
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
		heading.place(relx=0.16,rely=0.05)

		btns = Button(self.centerframe,font='time 9',text="Shop".upper(),height=5,width=22,command=self.shop,bg=self.color[0])
		btns.place(relx=0.55,rely=0.15)


		btns1 = Button(self.centerframe,font='time 9',text="Analysis".upper(),height=5,width=22,command=self.analyse,bg=self.color[0])
		btns1.place(relx=0.15,rely=0.15)

		btns2 = Button(self.centerframe,font='time 9',text="Dashboard".upper(),height=5,width=22,command=self.dash,bg=self.color[0])
		btns2.place(relx=0.15,rely=0.65)

		btns4 = Button(self.centerframe,font='time 9',text="Receipt".upper(),height=5,width=22,command=self.receipt,bg=self.color[0])
		btns4.place(relx=0.55,rely=0.4)

		btns3 = Button(self.centerframe,font='time 9',text="Product Manegement".upper(),height=5,width=22,command=self.prodmgmt,bg=self.color[0])
		btns3.place(relx=0.15,rely=0.4)

		btns5 = Button(self.centerframe,font='time 9',text="Exit".upper(),height=5,width=22,command=self.exit,bg=self.color[0])
		btns5.place(relx=0.55,rely=0.65)

		btns22 = Button(self.centerframe,font='time 9',text="Help".upper(),height=1,width=6,command=self.mobile,bg=self.color[3])
		btns22.place(relx=0.78,rely=0.84)

		heading = Label(self.mainframe,font='time 9 bold',fg='red',text="Please adjust clock for the data to be correct".upper())
		heading.place(relx=0.20,rely=0.85)

	#=================================================================================================================#
	def user(self):
		return Admin1().mainloop()
	#=================================================================================================================#
	def shop(self):
		Tk.destroy(self)
		return ShopLogin().mainloop()
	#=================================================================================================================#
	def receipt(self):
		Tk.destroy(self)
		return Customer().mainloop()
	#=================================================================================================================#
	def prodmgmt(self):
		Tk.destroy(self)
		return ProductManagement().mainloop()
	#=================================================================================================================#
	#=================================================================================================================#
	def dash(self):
		Tk.destroy(self)
		return Dashboard().mainloop()
	#=================================================================================================================#

	def exit(self):
		Tk.destroy(self)
		return sys.exit()
	#=================================================================================================================#
	def mobile(self):
		# from balance import Balance as mobilemoney
		# Tk.destroy(self)
		# return mobilemoney().mainloop()
		tk.messagebox.showinfo('Questions','For any system failure,questions,suggestions\n\nPlease call: 0693677033\n\nemail:peterkelvin16@gmail.com')
	#=================================================================================================================#
	def analyse(self):
		Tk.destroy(self)
		return Analysis().mainloop()
#===========================Main Page which service is choosen=================================



#===========================Main Page which calls the login=================================
class admin(tk.Tk):
	#=================================================================================================================#
	def __init__(self):
		super().__init__()
		self.title("Login")
		self.iconbitmap('sc.ico')
		self.turn = True
		self.labels = []
		self.txt = StringVar()
		self.lb = StringVar()
		self.un = StringVar()
		self.pwd = StringVar()
		self.unnew = StringVar()
		self.pwdnew = StringVar()
		self.pwdnewchk = StringVar()
		self.results = StringVar()
		self.mainframe = Frame(bg="cadetblue",height=300,width=250)
		self.mainframe.place(relx=0, rely=0)
		self.geometry('250x300+500+300')
		self.resizable(False, False)
		self.Interface()
	#=================================================================================================================#

	def Interface(self):
	#=================================================================================================================#
		heading = tk.Label(text="Login to Continue",bg="cadetblue",fg="white",font="time 12 bold", bd=0,height=3, width=18, relief=None,)
		heading.grid(row=0, column=0, columnspan=3) 
		for i in range(1, 2):
			col = []
			for j in range(0, 1):
				col.append(tk.Label(textvariable=self.lb,font="time 12",fg="cadetblue", height=2, width=14, relief=SUNKEN,borderwidth=0))
				self.lb.set("User Data")
				col[j].grid(row=i, column=j,pady=10)
			self.labels.append(col)
		

		username = tk.Entry(textvariable=self.un, bd=2,font="time 12 bold",width=25,borderwidth=0)
		username.grid(row=2, column=0,padx=11,pady=5)

		password = tk.Entry(textvariable=self.pwd, bd=2,font="time 12 bold", show="*",width=25,borderwidth=0)
		password.grid(row=3, column=0,padx=11)

		loginbtn = tk.Button(text="Login",bg="cadetblue",font="time 11",fg="white",command=self.Authenticate,borderwidth=1)
		loginbtn.grid(row=5, column=0,pady=4)

		newuserbtn = tk.Button(text="Add User",bg="cadetblue",font="time 11",fg="white",command=self.CallAdmin1,borderwidth=1)
		newuserbtn.grid(row=6, column=0,pady=4)

		results = tk.Label(text="",bg="cadetblue",font="time 10",fg="red",textvariable=self.results).grid(row=7,column=0)
		self.results.set("")
		self.bind('<Return>',self.Authenticate)
	#=================================================================================================================#

	def Authenticate(self, event=None):
		key = PasswordEncrypter.GenerateKey()
		un = self.un.get()
		pwd = self.pwd.get()
		#===========================Connect to the Database and Authenticate=========================================#
		conn = sq.connect('sales')
		c = conn.cursor()

		if un == "" or pwd == "":
			self.results.set("login error please fill all fields")
			self.after(1900, self.Interface)
		else:
			try:
				cred = c.execute("SELECT * FROM 'login'").fetchall()

				#loop through the database and check for user if exists

				#user one is when [0][0] and pass [0][1]
				#user two is when [1][0] and pass[1][1]
				userdict = {}
				for i in range(0, len(cred)):
					user = cred[i-1][0]
					password = cred[i-1][1]

					userdict.update({user:password})
				for k,v in userdict.items():
					v = PasswordEncrypter.Decrypt(v, key)
					if un == k and pwd == v.decode():
						try:
							self.success()
						except:
							pass
					elif un == k and pwd != v.decode():
						self.results.set("Please check your password")
						self.after(1900, self.Interface)
					else:
						self.results.set("Check you credentials")
						self.after(1900, self.Interface)
					#ShopLogin().mainloop()
					# else:
					# 	tk.messagebox.showinfo("Error","Invalid Credentials")
					# break
			except:
				try:
					os.system('db.exe')
				except:
					pass

				cred = c.execute("SELECT * FROM 'login'").fetchall()
				#loop through the database and check for user if exists

				#user one is when [0][0] and pass [0][1]
				#user two is when [1][0] and pass[1][1]
				userdict = {}
				for i in range(0, len(cred)):
					user = cred[i-1][0]
					password = cred[i-1][1]

					userdict.update({user:password})
				for k,v in userdict.items():
					v = PasswordEncrypter.Decrypt(v, key)
					if un == k and pwd == v.decode():
						try:
							self.success()
						except:
							pass
					elif un == k and pwd != v.decode():
						self.results.set("Please check your password")
						self.after(1900, self.Interface)
					else:
						self.results.set("Check you credentials")
						self.after(1900, self.Interface)

	def success(self):
		Tk.destroy(self)
		return Admin().mainloop()

	def CallAdmin1(self):
		Tk.destroy(self)
		return Admin1().mainloop()

class Admin1(tk.Tk):
	#=================================================================================================================#
	def __init__(self):
		super().__init__()
		self.title("Register")
		self.iconbitmap('sc.ico')
		self.turn = True
		self.labels = []
		self.txt = StringVar()
		self.lb = StringVar()
		self.un = StringVar()
		self.pwd = StringVar()
		self.unnew = StringVar()
		self.pwdnew = StringVar()
		self.pwdnewchk = StringVar()
		self.results = StringVar()
		self.mainframe = Frame(bg="cadetblue",height=350,width=250).place(relx=0,rely=0)
		self.geometry('250x300+500+300')
		self.resizable(False, False)
		self.CreateUser()

	def CreateUser(self):
		heading = tk.Label(bg="cadetblue",fg="white",text="New User SignUp",font="time 12 bold", bd=0,height=3, width=18, relief=None,)
		heading.grid(row=0, column=0, columnspan=3) 
		for i in range(1, 2):
			col = []
			for j in range(0, 1):
				col.append(tk.Label(textvariable=self.lb,fg="cadetblue",font="time 12", height=2, width=14, relief=SUNKEN,borderwidth=0))
				self.lb.set("User Info")
				col[j].grid(row=i, column=j,pady=5)
			self.labels.append(col)
		

		username = tk.Entry(textvariable=self.unnew, bd=2,font="time 12 bold",width=25,borderwidth=0)
		username.grid(row=2, column=0,padx=11,pady=5)

		password = tk.Entry(textvariable=self.pwdnew, bd=2,font="time 12 bold", show="*",width=25,borderwidth=0)
		password.grid(row=3, column=0,padx=5,pady=5)

		passwordconfirm = tk.Entry(textvariable=self.pwdnewchk, bd=2,font="time 12 bold", show="*",width=25,borderwidth=0)
		passwordconfirm.grid(row=4, column=0,padx=2,pady=5)

		createuserbtn = tk.Button(self.mainframe,text="CreateUser",font="time 10",bg="cadetblue",fg="white",command=self.AddUser,borderwidth=1)
		createuserbtn.grid(row=5, column=0,pady=5)

		loginbtn = tk.Button(text="Back to Login",font="time 10",bg="cadetblue",fg="white",command=self.backtologin,borderwidth=1)
		loginbtn.grid(row=6, column=0)


		results = tk.Label(text="",bg="cadetblue",font="time 9",fg="red",textvariable=self.results).grid(row=7, column=0)
		self.results.set("")

		passwordconfirm.bind('<Return>',self.AddUser)

	def backtologin(self):
		Tk.destroy(self)
		admin().mainloop()

	def AddUser(self, event=None):
		key = PasswordEncrypter.GenerateKey()

		conn = sq.connect('sales')
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
						self.results.set(f"User {self.unnew.get()} in database")
						self.after(1900, self.CreateUser)
					else:
						c.execute("INSERT INTO 'login' VALUES (?,?) ", (self.unnew.get(),PasswordEncrypter.Encrypt(self.pwdnew.get(),key)))
						conn.commit()

						self.results.set(f'User {self.unnew.get()} is added')
						self.unnew.set("")
						self.pwdnew.set("")
						self.pwdnewchk.set("")
						
				else:
					self.results.set("Ensure all Fields are Filled")
					self.after(1900, self.CreateUser)
			except:
				try:
					pass
				except:
					pass


				if self.pwdnew.get() == self.pwdnewchk.get() and (self.pwdnew.get() !=""):
					c.execute("INSERT INTO 'login' VALUES (?,?) ", (self.unnew.get(),PasswordEncrypter.Encrypt(self.pwdnew.get(),key)))
					conn.commit()

					self.results.set("User Added Successfully Press ok to Login")
					Tk.destroy(self)
					admin().mainloop()
				else:
					self.results.set("Ensure all Fields are Filled")
		elif self.unnew.get()== "" or self.pwdnew.get()=="" or self.pwdnewchk.get()=="":
			self.results.set("Please ensure all fields are filled")
			self.after(1900, self.CreateUser)
		else:
			self.results.set("Password length must be 8\nmust contain atleast 1 number\nletter,non-letter and special symbol")
			self.after(3000, self.CreateUser)

#===========================Main Page which calls the login=================================






#===========================Shop===============================================================
def getquantity(name):
		conn = sq.connect('sales')
		c = conn.cursor()
		data = (name,)
		c.execute("CREATE INDEX IF NOT EXISTS Idx5 ON AddProducts(Name)")
		v = c.execute("SELECT * FROM AddProducts WHERE Name=?",data)
		for row in v:
			z = row[3]
		x = z
		return x

def getprice(name):
	conn = sq.connect('sales')
	c = conn.cursor()
	data = (name,)
	c.execute("CREATE INDEX IF NOT EXISTS Idx5 ON AddProducts(Name)")
	v = c.execute("SELECT * FROM AddProducts WHERE Name=?",data)
	for row in v:
		z = row[2]
	x = z
	return x


class ShopLogin(tk.Tk):
	#=================================================================================================================#
	def __init__(self):
		super().__init__()
		self.title("Emt Management System")
		self.iconbitmap('sc.ico')
		self.labels = []
		self.turn = True
		self.count = 0
		self.txt = []
		self.date = dt.datetime.now()
		self.textinput = []
		self.height = 1

		self.conn = sq.connect('sales')
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

		self.font = "time 10"


		self.WIDTH, self.HEIGHT = 1095, 690

		self.btny = 672
		self.btnx = 0
		#label height and width
		self.labelheight = 1
		self.labelwidth = 45
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

		self.salesframe = Frame(bg="blue", width=40, height=900).place(x=self.xvalue-310,y=self.yvalue-20)

		self.daily = tk.Text(self.salesframe,width=40, height=20, font='time 11',relief=RAISED)
		self.daily.place(x=self.xvalue-270, y=self.yvalue-20)

		self.entryt = Entry(bg="white",textvariable=self.entrytv, font='time 11', state='normal',justify='right',bd=5,width=39)
		self.entryt.place(x=self.xvalue-270, y=self.total1y-20)

		self.entryp = Entry(bg="white",textvariable=self.entrypv, font='time 11', state='normal',justify='right',bd=5,width=39)
		self.entryp.place(x=self.xvalue-270, y=self.profit1y-20)

		self.lb = StringVar()
		self.lbtotal = StringVar()

		
		self.geometry(f'{self.WIDTH}x{self.HEIGHT}+150+0')

		self.resizable(False, False)

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
	def madeninames(self,event=None):
		conn= sq.connect('sales')
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

		Shop_title = Label(headingframe,text="Welcome to Emt Shop Management System".upper(),bg="lightgrey",fg="cadetblue",font="time 14", bd=0,height=2,relief=None)
		Shop_title.place(y=0, x=350)

		heading1 = tk.Label(headingframe,text="",bg="lightgrey",fg="blue",font=self.font, bd=0,pady=3,height=3, width=20, relief=None,)
		heading1.grid(row=0, column=0)

		buttonframe = Frame(bg="lightgrey", width=self.buttonsframewidth-270, height=self.buttonsframeheight, pady=3).place(x=1, y=210)

		maincanvas = Canvas(self,width=1920,height=231,bg="cadetblue")
		maincanvas.place(x=0,y=50)
		#Label to Warn user to not conflict with database   
		Product = tk.Label(text="Product".upper(),bg="white",font="time 10", height=self.labelheight, width=self.labelwidth-10, relief=RAISED)
		Product.grid(row=1, column=0,padx=50,pady=1)

		Quantity = tk.Label(text="Quantity".upper(),bg="white",font="time 10", height=self.labelheight, width=self.labelwidth-10, relief=RAISED)
		Quantity.grid(row=1, column=1,padx=20)

		Discount = tk.Label(text="Sell Price".upper(),bg="white",font="time 10", height=self.labelheight, width=self.labelwidth-10, relief=RAISED)
		Discount.grid(row=1, column=2,padx=80)

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

		#=======bind comboboxes to events======================#
		box1.bind("<<ComboboxSelected>>", self.modif1)
		box2.bind("<<ComboboxSelected>>", self.modif2)
		box3.bind("<<ComboboxSelected>>", self.modif3)
		box4.bind("<<ComboboxSelected>>", self.modif4)
		box5.bind("<<ComboboxSelected>>", self.modif5)
		box6.bind("<<ComboboxSelected>>", self.modif6)
		box7.bind("<<ComboboxSelected>>", self.modif7)
		box8.bind("<<ComboboxSelected>>", self.modif8)
		box9.bind("<<ComboboxSelected>>", self.modif9)
		box10.bind("<<ComboboxSelected>>", self.modif10)
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

		stockn = tk.Button(buttonframe,text="Stock Left".upper()
			,bg="cadetblue",fg="white",font=self.font,
			bd=0,height=1, width=12, 
			relief=None,command=Stock.checkstock)
		stockn.place(x=320, y=self.btny-140)
	#=================================================================================================================#
				#We need name, item, debt
		debtcanvas = Canvas(self,width=238,height=370,bg="lightgrey",highlightthickness=0)
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

		self.submitbutton = Button(font='time 11',text="Add".upper(),bg="cadetblue",fg="white",command=self.submittodb,bd=0,height=1, width=6)
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

		self.daily.insert(END,"Product\t\tQuantity\t\tTotal\n")
		self.daily.insert(END, f'{40*"_"}')

		self.debtnameentry12.config(state="disabled")
		self.debtcashentry12.config(state="disabled")
		self.debtview12.config(state="disabled")
		self.submitbutton.config(state="disabled")
		self.removebutton.config(state="disabled")
		self.debtnameentry.set("Jina")

	#=================================================================================================================#
	def DebtFunction(self):
		self.daily.delete(1.0, END)
		self.daily.insert(END,f'Name\t\t\t\tTotal\n')
		self.daily.insert(END, f'{40*"_"}')

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
		self.daily.insert(END, f'{40*"_"}')

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
			for row in self.stsales:
				x = row[1]
				x2 = row[2]
				x3 = row[4]
				if x in dtsales:
					p = dtsales.get(x)[0]
					n = dtsales.get(x)[1]
					dtsales.update({x:(x2+int(p),x3+int(n))})
				else:
					dtsales.update({x:(x2,x3)})
			final = []
			profitn = []
			#loop through the dictionary and get q and price
			for k,v in dtsales.items():
				q = dtsales.get(k)[0]
				p = dtsales.get(k)[1]

				self.daily.insert(END, f'{k.upper()}\t\t    {q}\t\t{p}\n')
				final.append(int(p))

				x = self.c.execute("SELECT * FROM 'AddProducts'").fetchall()

				for i in range(0, len(x)):
					productname = x[i][0]
					if productname == k:
						prof = (Profit.profit(int(x[i][1]),int(x[i][3]),int(x[i][2]),int(q)))
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
			if f5 == k :
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
			if f9== k:
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
		
		#==================================Perfom Desired Mathematics q,d,p========================================
		valuestime = f'{self.date.day}/{self.date.month}/{self.date.year}'

		values1 = (valuestime,f1, self.entryq1.get(), self.entryD1.get(), self.entryP1.get())
		values2 = (valuestime,f2, self.entryq2.get(), self.entryD2.get(), self.entryP2.get())
		values3 = (valuestime,f3, self.entryq3.get(), self.entryD3.get(), self.entryP3.get())
		values4 = (valuestime,f4, self.entryq4.get(), self.entryD4.get(), self.entryP4.get())
		values5 = (valuestime,f5, self.entryq5.get(), self.entryD5.get(), self.entryP5.get())
		values6 = (valuestime,f6, self.entryq6.get(), self.entryD6.get(), self.entryP6.get())
		values7 = (valuestime,f7, self.entryq7.get(), self.entryD7.get(), self.entryP7.get())
		values8 = (valuestime,f8, self.entryq8.get(), self.entryD8.get(), self.entryP8.get())
		values9 = (valuestime,f9, self.entryq9.get(), self.entryD9.get(), self.entryP9.get())
		values10 = (valuestime,f10, self.entryq10.get(), self.entryD10.get(), self.entryP10.get())
	#=================================================================================================================#


	#==================================Calculating Total Values and inserting to db===================================#
		grandfinal = (self.entryP1.get() +self.entryP2.get() +self.entryP3.get()
		 +self.entryP4.get() +self.entryP4.get()+self.entryP5.get() +self.entryP6.get() +self.entryP7.get()
		 +self.entryP8.get() +self.entryP9.get()+self.entryP10.get())

		self.box1.set("")
		self.box2.set("")
		self.box3.set("")
		self.box4.set("")
		self.box5.set("")
		self.box6.set("")
		self.box7.set("")
		self.box8.set("")
		self.box9.set("")
		self.box10.set("")

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

		values = (values1,values2,values3,values4,values5,values6,values7,values8,values9,values10)

		self.c.executemany("INSERT INTO 'Daily Sales' VALUES (?,?,?,?,?)", values)
		self.conn.commit()
	#=====================================================================#
		self.c.executemany("INSERT INTO 'Daily Temp' VALUES (?,?,?,?,?)", values)
		self.conn.commit()
	#=================================================================================================================#
	def todayssales(self, event=None):
		t = time.time()
	#=================================================================================================================#
		self.gettotalsales()

		valuestime = f'{self.date.day}/{self.date.month}/{self.date.year}' 
		
		self.daily.delete(1.0, END)

		self.daily.insert(END,"Product\t\tQuantity\t\tTotal\n")
		self.daily.insert(END, f'{40*"_"}')
		#===================Database delete all empty values==========================
		self.c.executemany("DELETE FROM 'Daily Sales' WHERE Quantity=?", '0')
		self.c.executemany("DELETE FROM 'Daily Temp' WHERE Quantity=? ",'0')
		self.conn.commit()
		#===================Database delete all empty values==========================
		self.stsales = self.c.execute("SELECT * FROM 'Daily Sales' WHERE Timed=?", (str(valuestime),)).fetchall()

		dtsales = {}    
		#loop through the database values and append to dictionary
		for row in self.stsales:
			if row[1] in dtsales:
				p = dtsales.get(row[1])[0]
				n = dtsales.get(row[1])[1]
				dtsales.update({row[1]:(row[2]+int(p),row[4]+int(n))})
			else:
				dtsales.update({row[1]:(row[2],row[4])})
		final = []
		profitn = []
		#loop through the dictionary and get q and price
		for k,v in dtsales.items():
			self.daily.insert(END, f'{k.upper()}\t\t    {dtsales.get(k)[0]}\t\t{dtsales.get(k)[1]}\n')
			final.append(int(dtsales.get(k)[1]))

			x = self.c.execute("SELECT * FROM 'AddTemp'").fetchall()
			for i in range(0, len(x)):
				productname = x[i][0]
				if productname == k:
					prof = (Profit.profit(int(x[i][1]),int(x[i][3]),int(x[i][2]),int(dtsales.get(k)[1])))
					profitn.append(int(prof))
	
		self.entrytv.set(format(sum(final),","))
		self.entrypv.set(format(sum(profitn),","))

		self.stock()
	
	#=================================================================================================================#
	def UndoLastSale(self):
		self.stock2()

	def fastupdate(self):
		last = self.c.execute("SELECT * FROM 'Daily Sales' WHERE ROWID = (SELECT MAX(ROWID) FROM 'Daily Sales');").fetchone()
		return last[1]

	def fastupdate1(self):
		last = self.c.execute("SELECT * FROM 'Daily Sales' WHERE ROWID = (SELECT MAX(ROWID) FROM 'Daily Sales');").fetchone()
		return last[2]

	def stock2(self):

		data = (int(getquantity(str(self.fastupdate()))) + int(self.fastupdate1()),str(self.fastupdate()))

		self.c.execute('UPDATE "main"."AddProducts" SET "Quantity"=? WHERE "Name"=?;',data)
		

		self.c.execute("DELETE FROM 'Daily Sales' WHERE ROWID = (SELECT MAX(ROWID) FROM 'Daily Sales');")

		self.c.execute("DELETE FROM 'Daily Temp' WHERE ROWID = (SELECT MAX(ROWID) FROM 'Daily Sales');")
		self.conn.commit()
		self.after(1,self.todayssales())
	#=================================================================================================================#
	#=================================================================================================================#
	def stock(self):
		#===================Database delete all empty values==========================
		v = self.c.execute("SELECT * FROM 'Daily Temp' WHERE ROWID = (SELECT MAX(ROWID) FROM 'Daily Temp');").fetchone()
		try:
			data = (int(getquantity(v[1])) - int(v[2]),v[1])
			self.c.execute('UPDATE "AddProducts" SET "Quantity"=? WHERE "Name"=?;',data)
			self.conn.commit()

			self.c.execute("DELETE FROM 'Daily Temp' WHERE ROWID = (SELECT MAX(ROWID) FROM 'Daily Temp');")
			self.conn.commit()

		except TypeError:
			pass

	#=================================================================================================================#
	def modif1(self,event=None):
		v = getprice(self.box1.get())
		self.entryD1.set(v)

	def modif2(self,event=None):
		v = getprice(self.box2.get())
		self.entryD2.set(v)

	def modif3(self,event=None):
		v = getprice(self.box3.get())
		self.entryD3.set(v)

	def modif4(self,event=None):
		v = getprice(self.box4.get())
		self.entryD4.set(v)

	def modif5(self,event=None):
		v = getprice(self.box5.get())
		self.entryD5.set(v)

	def modif6(self,event=None):
		v = getprice(self.box6.get())
		self.entryD6.set(v)

	def modif7(self,event=None):
		v = getprice(self.box7.get())
		self.entryD7.set(v)

	def modif8(self,event=None):
		v = getprice(self.box8.get())
		self.entryD8.set(v)

	def modif9(self,event=None):
		v = getprice(self.box9.get())
		self.entryD9.set(v)

	def modif10(self,event=None):
		v = getprice(self.box10.get())
		self.entryD10.set(v)

	def logout(self):
	#=================================================================================================================#
		self.conn.commit()
		self.conn.close()
		Tk.destroy(self)
		return Admin().mainloop()

	
	#=================================================================================================================#

#===========================Shop===============================================================






#===========================prod===============================================================
class ProductManagement(tk.Tk):
		
	def __init__(self):
		#=============================================================================================
		super().__init__()
		self.title("Product Management")
		self.iconbitmap('sc.ico')
		self.turn = True
		self.conn = sq.connect('sales')
		self.c = self.conn.cursor()
		self.btns = []
		self.font = "time 10"
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
		top_frame = Frame(bg='cadetblue', width=450, height=50, pady=3)
		center_frame = Frame(bg='grey', width=450, height=175, padx=3, pady=3)
		bottom_frame = Frame(bg='cadetblue', width=450, height=650, pady=10)
		#Layout the Main Containers
		top_frame.grid(row=0, sticky="ew")
		center_frame.grid(row=1, sticky="nsew")
		bottom_frame.grid(row=2,sticky="ew")
	
		#=============================================================================================
		# create the widgets for the top frame

		Heading = Label(top_frame, text="Welcome to Product Management".upper(), font=self.font).place(
			x=225, y=20,anchor="center")
		#=============================================================================================
		msg = Label(center_frame, font="time 12", text="*Click Button to Load Functionality").place(x=60,y=70)


		#=============================================================================================
		#Buttons Generator
		btn_dict = {2:"List Products  ", 0:"Add Products   ",3:"Modify Products", 1:"Delete Products"}

		btncommands = [self.AddProduct, self.DeleteProducts,self.ListProducts,self.ModifyProducts]


		for k, j in sorted(btn_dict.items()):
			btns = Button(bottom_frame,text=j, bg='white',relief=RAISED,width=13,height=1,padx=5,pady=5,font="time 10", command=btncommands[k], state=self.btnstate[k],borderwidth=0)
			btns.grid(padx=5)

			self.btns.append(btns)

		

		#=============================================================================================
	def AddProduct(self):
		#=============================================================================================
		#This Function is going to deal with Addition of Products
		#Text Variables
	
		#Main Layout:
		self.geometry('850x366+300+200')
		editframe = Frame(bg="cadetblue", width=450, height=366, pady=3).place(x=450,y=0)
		name = Label(editframe,text="Name", font=self.font).place(x=450,y=50)
		buy_price = Label(editframe,text="Buy_Price", font=self.font).place(x=450,y=100)
		sell_price = Label(editframe,text="Sell_Price", font=self.font).place(x=450,y=150)
		quantity = Label(editframe,text="Quantity", font=self.font).place(x=450,y=200)

		addbtn = Button(editframe, text="Add", font=self.font, command=self.addproduct,borderwidth=0).place(x=500,y=320)
		clearbtn = Button(editframe, text="Back",font=self.font, command=self.clearbtn,borderwidth=0).place(x=600, y=320)
		#Entries to get data
		name_entry = Entry(font=self.font,textvariable=self.namevar).place(x=590,y=50)
		buy_price_entry = Entry(font=self.font,textvariable=self.buypricevar).place(x=590, y=100)
		sell_price_entry = Entry(font=self.font,textvariable=self.sellpricevar).place(x=590, y=150)
		quantity_entry = Entry(font=self.font,textvariable=self.quantityvar).place(x=590, y=200)

		self.btns[1].config(state=tk.DISABLED)
		self.btns[2].config(state=tk.DISABLED)
		self.btns[3].config(state=tk.DISABLED)

		

		exitbtn = Button(editframe, font=self.font, command=self.maingui,text="Exit",borderwidth=0).place(x=700,y=320)
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

			except sq.ProgrammingError:
				tk.messagebox.showinfo("Error","Try Again")

		#self.c.executemany("INSERT INTO 'AddProducts' VALUES (?,?,?,?)", (values,))
		#=============================================================================================

	def ListProducts(self):
		self.geometry('900x366+300+200')
		#=============================================================================================
		self.btns[0].config(state=tk.DISABLED)
		self.btns[1].config(state=tk.DISABLED)
		self.btns[3].config(state=tk.DISABLED)

		editframe = Frame(bg="cadetblue", width=450, height=366, pady=3).place(x=450,y=0)

		products = self.c.execute("SELECT * FROM AddProducts ORDER BY Quantity DESC").fetchall()

		#Cerate 4 List Boxes to view the products 
		self.textlist1 = Listbox(editframe,font="time 8", height=21,width=21, fg="blue",yscrollcommand=self.yscroll2)
		self.textlist1.place(x=452)
		self.textlist1.insert(END, "  PRODUCTS")
		self.textlist1.insert(END,"--------------------------------")

		self.textlist2 = Listbox(editframe,font="time 8", height=21,width=16, fg="blue",yscrollcommand=self.yscroll2)
		self.textlist2.place(x=580)
		self.textlist2.insert(END, "BUYPRICE")
		self.textlist2.insert(END,"--------------------------------")

		self.textlist3 = Listbox(editframe,font="time 8", height=21,width=16, fg="blue")
		self.textlist3.place(x=680)
		self.textlist3.insert(END, "SELLPRICE")
		self.textlist3.insert(END,"--------------------------------")

		self.textlist4 = Listbox(editframe,font="time 8", height=21,width=16, fg="blue")
		self.textlist4.place(x=780)
		self.textlist4.insert(END, "QUANTITY")
		self.textlist4.insert(END,"--------------------------------")

		self.scrollbar = Scrollbar(self, orient='vertical')

		self.scrollbar.config(command=self.yview)
		self.scrollbar.place(x=880,height=319,width=24)
		

		for row in products:
			self.textlist1.insert(END, '{:10.16}'.format(row[0].upper()))
			self.textlist1.insert(END, "--------------------------------")
			self.textlist2.insert(END, f'  {row[1]}')
			self.textlist2.insert(END, "--------------------------------")
			self.textlist3.insert(END, f'  {row[2]}')
			self.textlist3.insert(END, "--------------------------------")
			self.textlist4.insert(END, f'  {row[3]}')
			self.textlist4.insert(END, "--------------------------------")

		
		clearbtn = Button(editframe, text="Back",font=self.font, command=self.clearbtn,borderwidth=0).place(x=600, y=320)
		exitbtn = Button(editframe, font=self.font, command=self.maingui, text="Exit",borderwidth=0).place(x=750,y=320)
				
		#=============================================================================================
	def DeleteProducts(self):
		self.geometry('850x366+300+200')
		self.btns[0].config(state=tk.DISABLED)
		self.btns[2].config(state=tk.DISABLED)
		self.btns[3].config(state=tk.DISABLED)

		editframe = Frame(bg="cadetblue", width=450, height=366, pady=3).place(x=450,y=0)

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

		delbtn = Button(editframe, text="Delete",font=self.font,command=self.delcombo,borderwidth=0).place(x=455, y=320)
		clearbtn = Button(editframe, text="Back",font=self.font, command=self.clearbtn,borderwidth=0).place(x=600, y=320)
		exitbtn = Button(editframe, font=self.font, command=self.maingui, text="Exit",borderwidth=0).place(x=750,y=320)
		#=============================================================================================
	
		#=============================================================================================
	def ModifyProducts(self):
		self.geometry('850x366+300+200')
		self.btns[0].config(state=tk.DISABLED)
		self.btns[1].config(state=tk.DISABLED)
		self.btns[2].config(state=tk.DISABLED)

		#Main UI

		editframe = Frame(bg="cadetblue", width=450, height=366, pady=3).place(x=450,y=0)

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

	
	
		updatebtn = Button(editframe, text="Update",font=self.font,command=self.checkcombo,borderwidth=0).place(x=455, y=320)
		clearbtn = Button(editframe, text="Back",font=self.font, command=self.clearbtn,borderwidth=0).place(x=600, y=320)
		exitbtn = Button(editframe, font=self.font, command=self.maingui, text="Exit",borderwidth=0).place(x=750,y=320)
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
#===========================prod===============================================================





#===========================receipt===============================================================
conn = sq.connect('sales')
c = conn.cursor()

def getquantity(name):
		data = (name,)
		c.execute("CREATE INDEX IF NOT EXISTS Idx5 ON AddProducts(Name)")
		v = c.execute("SELECT * FROM AddProducts WHERE Name=?",data)
		for row in v:
			z = row[3]
		x = z
		return x

def shopname():
	v = c.execute("SELECT * FROM 'shopdetails' ").fetchall()
	return v[0][0]

def shopno():
	v = c.execute("SELECT * FROM 'shopdetails' ").fetchall()
	return v[0][1]

class Customer(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title("Receipt Mode")
		self.iconbitmap('sc.ico')
		self.colors = ['cadetblue','white','lightgrey']

		self.name = StringVar()
		self.product = StringVar()
		self.quantity = IntVar()
		self.displayreceipt = StringVar()

		self.total = 0 
		self.price = 0 

		self.date = dt.datetime.now()

		self.font = "time 10"
		self.geometry('600x600+400+50')
		self.resizable(False,False)
		self.Mainui()

		self.curtime = dt.datetime.now()

		self.time = str(self.curtime)

		self.number = shopno()
		self.curtime = f'\nDate:\t\t\t{self.time[0:10]}\nTime:\t\t\t{self.time[11:19]}\nPhone:\t\t\t{self.number}\n'

		self.conn = sq.connect('sales')
		self.c = self.conn.cursor()


	def exit(self):
		Tk.destroy(self)
		return Admin().mainloop()


	def Mainui(self):
	#=========================Frames==============================================================
		topframe = Frame(bg=self.colors[0],width=600,height=600)
		topframe.place(relx=0,rely=0)

		leftframe = Frame(bg=self.colors[2],width=300,height=550)
		leftframe.place(relx=0.03,rely=0.05)

		rightframe = Frame(bg=self.colors[1],width=280,height=550)
		rightframe.place(relx=0.52,rely=0.05)
	#=======================Labels and Entries=====================================================

		customerlabel = Label(leftframe,text="Name")
		customerlabel.place(relx=0.05,rely=0.105)

		customername = Entry(leftframe,width=21,bd=2,font=self.font,textvariable=self.name)
		customername.place(relx=0.3,rely=0.1)

		productlabel = Label(leftframe,text="Product")
		productlabel.place(relx=0.05,rely=0.205)

		def products():
			conn = sq.connect('sales')
			c = conn.cursor()
			stitems = c.execute("SELECT * FROM AddProducts").fetchall() 
			items = []
			for row in stitems:
				for i in range(0, len(row)):
					x = row[0]
				items.append(x.upper())
				
			return sorted(items)
		productcombo = ttk.Combobox(leftframe,font=self.font,width=20,textvariable=self.product,values=products())
		productcombo.place(relx=0.3,rely=0.205)

		quantitylabel = Label(leftframe,text="Quantity")
		quantitylabel.place(relx=0.05,rely=0.305)

		quantityentry = Entry(leftframe,width=21,bd=2,font=self.font,textvariable=self.quantity)
		quantityentry.place(relx=0.3,rely=0.3)
	#=======================Text Display==========================================================
		displayreceipt = Text(rightframe,font="time 10 bold",width=38,height=35,bd=8)
		displayreceipt.place(relx=0,rely=0)
	#=======================Buttons===============================================================
		def logic():
			conn = sq.connect('sales')
			c = conn.cursor()

			displayreceipt.insert(END,f'\n\n\n{66*"-"}')
			displayreceipt.insert(END,f'\nTotal:\t\t\t        {self.total}')
			displayreceipt.insert(END,f'\n{66*"-"}\n')

			newtime = f'{self.date.day}/{self.date.month}/{self.date.year}'

			PrintButton.config(state="normal")

		def add():
			#add each sale to Daily Sales table
			conn = sq.connect('sales')
			c = conn.cursor()

			stitems = c.execute("SELECT * FROM AddProducts").fetchall()

			stprice = {}

			for stitem in stitems:
				    #print(stitem)
				    j = [j for j in range(0, len(stitem))]
				    i = [i for i in range(0, len(stitem))]
				    
				    stprice.update({stitem[j[0]]:stitem[i[2]]})
			
			for k,v in stprice.items():
				if self.product.get() == k:
					self.price = v
					x = self.price
					y = self.quantity.get()
					self.total = x * y

			newtime = f'{self.date.day}/{self.date.month}/{self.date.year}'
			#print(newtime)
			values1 = (newtime,self.product.get(),self.quantity.get(),self.price,self.total)

			self.values = (values1)
			#===================Database delete all empty values==========================
			var = "0"
			c.executemany("DELETE FROM 'Daily Sales' WHERE Quantity=?", var)
			conn.commit()

			c.executemany("DELETE FROM 'Daily Sales' WHERE Price=?", var)
			conn.commit()

			c.execute("INSERT INTO 'Temp Sales' VALUES (?,?,?,?,?)", self.values)
			conn.commit()

			#v = c.execute("SELECT * FROM 'Daily Sales' WHERE ROWID = (SELECT MAX(ROWID) FROM 'Daily Sales');").fetchall()

			v = c.execute("SELECT * FROM 'Temp Sales' WHERE Timed=?", (str(newtime),)).fetchall()
			
			displayreceipt.delete(1.0,END)
			displayreceipt.insert(END,
				f'\t{shopname()} Receipt\n{66*"-"}\n{self.curtime}\n{66*"-"}\n')
			x = f'{66*"-"}\n'
			message = f'From:\t{self.name.get().upper()}\n{x}Products\t\t    Qty\t    Total\n'
			displayreceipt.insert(END,message)
			displayreceipt.insert(END,f'{66*"-"}\n')

			transactions = {}
			
			for row in v:
				#print(row[0])
				i = [i for i in range(0, len(row))]
				j = [j for j in range(0, len(row))]

				x = row[i[1]]
				x2 = row[j[2]]
				x3 = row[j[4]]

				if x in transactions:
					transactions.update({x:(x2,x3)})
				else:
					transactions.update({x:(x2,x3)})
			
			final = []

			for k,v in transactions.items():
				newv = str(v).replace("(","")
				newv = newv.replace(")", "")

				q,p = newv.split(",")
				finall = p.replace(" ","")
				final.append(int(finall))
				k = '{:10.11}'.format(k)
				values = f'{k}\t\t    {q}\t    {p}\n'
				displayreceipt.insert(END,values)
			self.total = sum(final)

		def printf():
			file = open('me.txt','w')

			if sys.platform == "linux":
				conn = sq.connect('sales')
				c = conn.cursor()
				
				newtime = f'{self.date.day}/{self.date.month}/{self.date.year}'
				
				total = displayreceipt.get('1.0',tk.END)


				lpr = s.Popen("/usr/bin/lpr",stdin=s.PIPE)

				x = tk.messagebox.askyesno("Print Receipt","Do you wish to print the receipt?")
				if x == False:
					pass
			
				if x == True:
					#lpr.stdin.write(total.encode())
					c.execute("INSERT INTO 'Daily Sales' VALUES (?,?,?,?,?)", self.values)
					conn.commit()
					stdout, stderr = lpr.communicate(input=total.encode())
				self.after(1, self.stock)
			elif sys.platform == 'win32':
				# os.startfile("C:/Users/TestFile.txt", "print")
				conn = sq.connect('sales')
				c = conn.cursor()
				
				newtime = f'{self.date.day}/{self.date.month}/{self.date.year}'

				x = tk.messagebox.askyesno("Print Receipt","Do you wish to print the receipt?")
				if x == False:
					pass
				if x == True:
					#lpr.stdin.write(total.encode())
					c.execute("INSERT INTO 'Daily Sales' VALUES (?,?,?,?,?)", self.values)
					c.execute("INSERT INTO 'Daily Temp' VALUES (?,?,?,?,?)", self.values)
					conn.commit()
					file.write(displayreceipt.get('1.0',tk.END))
					file.close()
					os.startfile('me.txt','print')
				self.after(1, self.stock)
				#pass
			else:
				pass
				
			c.execute("DELETE FROM 'Temp Sales' WHERE Timed=?", (str(newtime),))
			conn.commit()


		AddButton = Button(leftframe,font=self.font,text="Add",bg=self.colors[0],command=add,width=6)
		AddButton.place(relx=0.05,rely=0.905)

		TotalButton = Button(leftframe,font=self.font,text="Total",bg=self.colors[0],command=logic,width=7)
		TotalButton.place(relx=0.32,rely=0.905)

		PrintButton = Button(leftframe,font=self.font,text="Print",bg=self.colors[0],command=printf,state="disabled",width=6)
		PrintButton.place(relx=0.62,rely=0.905)

		exitbutton = Button(leftframe,font=self.font,text="X",bg=self.colors[0],command=self.exit,state="normal",width=1)
		exitbutton.place(relx=0.86,rely=0.905)

	def stock(self):
		#===================Database delete all empty values==========================
		v = self.c.execute("SELECT * FROM 'Daily Temp' WHERE ROWID = (SELECT MAX(ROWID) FROM 'Daily Temp');").fetchone()
		
		try:
			oldquantity = getquantity(v[1])

			newquantity = int(oldquantity) - int(v[2])

			data = (newquantity,v[1])
			self.c.execute('UPDATE "AddProducts" SET "Quantity"=? WHERE "Name"=?;',data)
			self.conn.commit()

			self.c.execute("DELETE FROM 'Daily Temp' WHERE ROWID = (SELECT MAX(ROWID) FROM 'Daily Temp');")
			self.conn.commit()

		except TypeError:
			pass
#===========================receipt===============================================================





#===========================analysis===============================================================
class Analysis(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title('Analysis')
		self.color = ['cadetblue','orange','yellowgreen','lightgrey']
		self.iconbitmap('sc.ico')
		self.fromdateentry = StringVar()
		self.todateentry = StringVar()
		self.yearlyentry = IntVar()

			#getsales entry and button
		self.entrydatey = 420
		self.entrydatex = 50
		self.entrydatebuttonx = 220

		self.conn = sq.connect('sales')
		self.c = self.conn.cursor()

		self.font = "time 10"


		self.geometry("600x600+300+50")
		self.resizable(False,False)
		self.mainframe = Frame(bg=self.color[0],width=600,height=600).place(relx=0,rely=0)
		self.drawframe = Frame(bg=self.color[1],width=540,height=5).place(relx=0.05,rely=0.1)
		self.bottomframe = Frame(bg=self.color[1],width=540,height=5).place(relx=0.05,rely=0.9)
		self.sideframe = Frame(bg=self.color[1],width=5,height=480).place(relx=0.05,rely=0.1)
		self.sideframe1 = Frame(bg=self.color[1],width=5,height=485).place(relx=0.945,rely=0.1)
		self.centerframe = Frame(bg=self.color[3],width=532,height=475).place(relx=0.058,rely=0.109)
		
		self.Mainui()

	def Mainui(self):		
		self.label = Label(self.centerframe,text="Export your Sales by Month,Day and Year")
		self.label.place(relx=0.25,rely=0.7)

		self.btn = Button(self.centerframe,bg="cadetblue",text="export functions".upper(),height=1,command=self.Mainui)
		self.btn.place(relx=0.4,rely=0.14)

		exitbtn = Button(self.centerframe,font=self.font,bg='cadetblue',text="Exit",width=10,command=self.exit)
		exitbtn.place(relx=0.76,rely=0.8)

		self.btn.config(state='disabled')

		self.exportsales = Button(self.centerframe,font=self.font,text="Export".upper(),bg="cadetblue",fg="white",command=self.getsalesbymonth,bd=0,height=1, width=15)
		self.exportsales.place(x=self.entrydatex+320, y=self.entrydatey-255)

		self.exportyearsales = Button(self.centerframe,font=self.font,text="Yearly".upper(),bg="cadetblue",fg="white",command=self.getsalesbyyear,bd=0,height=1, width=15)
		self.exportyearsales.place(x=self.entrydatex+320, y=self.entrydatey-155)

		self.graphpreview = Button(self.centerframe,font=self.font,text="Graph Preview".upper(),bg="cadetblue",fg="white",command=self.plotting,bd=0,height=1, width=15)
		self.graphpreview.place(x=self.entrydatex+320, y=self.entrydatey-215)

		self.graphpreview1 = Button(self.centerframe,font=self.font,text="Graph Preview".upper(),bg="cadetblue",fg="white",command=self.GetYearlySales,bd=0,height=1, width=15)
		self.graphpreview1.place(x=self.entrydatex+320, y=self.entrydatey-115)

		self.yearlysales = Entry(self.centerframe,foreground="black",background='white',textvariable=self.yearlyentry,font=self.font,width=15)
		self.yearlysales.place(x=self.entrydatex+20, y=self.entrydatey-150)
		
		self.fromdateEntry = DateEntry(self.centerframe,foreground="white",background='cadetblue',date_pattern="dd/m/yyyy",textvariable=self.fromdateentry,font=self.font)
		self.fromdateEntry.place(x=self.entrydatex+20, y=self.entrydatey-250)

		self.todateEntry = DateEntry(self.centerframe,foreground="white",background='cadetblue',date_pattern="dd/m/yyyy",textvariable=self.todateentry,font=self.font)
		self.todateEntry.place(x=self.entrydatex+180, y=self.entrydatey-250)



	#=================================================================================================================#
	def getsalesbymonth(self):
		return MonthlySales.salesbymonth(self.fromdateentry.get(),self.todateentry.get())

	def getsalesbyyear(self):
		return MonthlySales.GetYearlySales(self.yearlyentry.get())
		#=================================================================================================================#
	#=================================================================================================================#
	def plotting(self):
		conn = sq.connect('sales')
		c = conn.cursor()

		#this works if month is the same
		#predefine our dates at the top
		date,mn1,yer=self.fromdateentry.get().split("/")

		#what if month has changed???

		date2,mn2,yer2=self.todateentry.get().split("/")

		x = []
		yr = []

		if mn1 != mn2:
			messagebox.showinfo("Monthly Support","Only 1 Month Preview is Supported\ni.e 1/4/2020-30/4/2020 and not\n1/4/2020-1/5/2020")
		else:
			dt = []

			dtsales = {}

			for i in range(int(date),int(date2)+1):
				dt.append(f'{i}/{mn1}/{yer}')

			for i in range(0, len(dt)):
				stsales1 = c.execute("SELECT * FROM 'Daily Sales' WHERE Timed=?",(dt[i],)).fetchall()

				for row in stsales1:
					product = row[1]
					quantity = row[2]
					price = row[4]

					if product in dtsales:
						y = str(dtsales[product])
						z = str(y).replace("(","")
						zn = z.replace(")","")
						f = zn.replace(" ","")
						p,n = f.split(",")
						dtsales.update({product:(quantity+int(p),price+int(n))})
					else:
						dtsales.update({product:(quantity,price)})
			profitn = []
			final = []
			t = []
			for k,v in sorted(dtsales.items(),key=lambda x: x[1]):
				newv = str(v).replace("(","")
				newv = newv.replace(")","")
				q,p = newv.split(",")
				finall = p.replace(" ","")
				final.append(finall)

				x2 = self.c.execute("SELECT * FROM 'AddProducts'").fetchall()
				for i in range(0, len(x2)):
					productname = x2[i][0]
					if productname == k:
						prof = (Profit.profit(int(x2[i][1]),int(x2[i][3]),int(x2[i][2]),int(q)))
						profitn.append(int(prof))
				x.append(k)
				yr.append(q)

				totalsales = 0
				for i in range(0, len(final)):
					if len(final[i]) == 1:
						totalsales = final[0]
					else:
						totalsales = totalsales + int(final[i])

			try:
				tt = totalsales
				graph.plot(x,yr,self.fromdateentry.get(),self.todateentry.get(),0.05,0.5,str(f'Total={format(tt,",")}\nProfit= {format(sum(profitn),",")}'))				
			except:	
				tt = 0	
				graph.plot(x,yr,self.fromdateentry.get(),self.todateentry.get(),0.05,0.5,str(f'Total={format(tt,",")}\nProfit= {format(sum(profitn),",")}'))

#=================================================================================================================#
	def GetYearlySales(self):
		year = self.yearlyentry.get()
		if year == 0:
			messagebox.showinfo("Error","Please Enter a valid Year")
		else:
			conn = sq.connect('sales')
			c = conn.cursor()

			years = c.execute("SELECT * FROM 'Daily Sales'").fetchall()

			dt = []
			for row in years:
				date,mn,yr = str(row[0]).split("/")
				dt.append(f'{date}/{mn}/{yr}')

			query = f"SELECT * FROM 'Daily Sales' WHERE Timed in ({','.join(['?']*len(dt))})"

			stsales1 = c.execute(query,dt).fetchall()

			dtsales = {}

			for row in stsales1:
				date,mn,yr = str(row[0]).split("/")
				if yr == str(year):
					prod = row[1]
					quan = row[2]
					total = row[4]
					if prod in dtsales:
						y = str(dtsales[prod])
						z = str(y).replace("(","")
						zn = z.replace(")", "")
						f = zn.replace(" ","")
						p,n = f.split(",")
						#print(p)
						dtsales.update({prod:(quan+int(p),total+int(n))})
					else:
						dtsales.update({prod:(quan,total)})
			filename = 'csvf/Sales2.csv'

			final = []

			x = []
			yr = []
			profitn = []
			final = []
			t = []
			for k,v in sorted(dtsales.items(),key=lambda x: x[1]):
				newv = str(v).replace("(","")
				newv = newv.replace(")","")
				q,p = newv.split(",")
				finall = p.replace(" ","")
				final.append(finall)

				x2 = self.c.execute("SELECT * FROM 'AddProducts'").fetchall()
				for i in range(0, len(x2)):
					productname = x2[i][0]
					if productname == k:
						prof = (Profit.profit(int(x2[i][1]),int(x2[i][3]),int(x2[i][2]),int(q)))
						profitn.append(int(prof))
				x.append(k)
				yr.append(q)

				totalsales = 0
				for i in range(0, len(final)):
					if len(final[i]) == 1:
						totalsales = final[0]
					else:
						totalsales = totalsales + int(final[i])

			try:
				tt = totalsales
				graph.plot(x,yr,dt[0],dt[-1],0.05,0.5,str(f'Total={format(tt,",")}\nProfit= {format(sum(profitn),",")}'))				
			except:	
				tt = 0	
				graph.plot(x,yr,dt[0],dt[-1],0.05,0.5,str(f'Total={format(tt,",")}\nProfit= {format(sum(profitn),",")}'))

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
			profitn = []
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

					x = self.c.execute("SELECT * FROM 'AddProducts'").fetchall()
					for i in range(0, len(x)):
						productname = x[i][0]
						if productname == k:
							prof = (Profit.profit(int(x[i][1]),int(x[i][3]),int(x[i][2]),int(q)))
							profitn.append(int(prof))
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
				w.writerow(["Faida","","",format(sum(profitn),",")])
			#now we convert the csv to excel
		return cexcel.convertToExcel(filename)
	def exit(self):
		Tk.destroy(self)
		return Admin().mainloop()

#===========================analysis===============================================================




#===========================dashboard===============================================================
class Dashboard(tk.Tk):

	def __init__(self):
		super().__init__()
		self.title('Dashboard')
		self.color = ['cadetblue','orange','yellowgreen','lightgrey']
		self.iconbitmap('sc.ico')
		self.mainframe = Frame(bg=self.color[0],height=600,width=1000).place(relx=0.40,rely=0)
		self.leftframe = Frame(bg=self.color[3],height=600,width=400).place(relx=0,rely=0)
		self.conn = sq.connect('sales')
		self.c = self.conn.cursor()
		self.shopname = StringVar()
		self.shopnumber = StringVar()
		self.geometry('350x200+400+300')
		self.resizable(False,False)
		self.mainpage()

	def mainpage(self):
		heading = Label(self.leftframe,font="time 11",text='Edit Name and Number'.upper(),width=30).place(relx=0.15,rely=0.1)

		shopnamelable = Label(self.leftframe,font="time 11",text='Shop Name',bg=self.color[3]).place(relx=0.05,rely=0.3)
		shopnameentry = Entry(self.leftframe,font="time 11",width=20,textvariable=self.shopname).place(relx=0.38,rely=0.3)

		shopno = Label(self.leftframe,font="time 11",text='Shop Number',bg=self.color[3]).place(relx=0.05,rely=0.5)
		shopnoentry = Entry(self.leftframe,font="time 11",width=20,textvariable=self.shopnumber).place(relx=0.38,rely=0.5)

		submitbtn = Button(self.leftframe,font="time 9",text='SUBMIT',bg=self.color[0],fg="white",width=10,height=1,command=self.shopd).place(relx=0.35,rely=0.70)

		#exit button
		exitbtn = Button(self.mainframe, text='EXIT',font="time 9",bg=self.color[0],fg="white",width=10,height=1,command=self.exit).place(relx=0.68,rely=0.70)
	
	def shopd(self):
		name = self.shopname.get()
		number = self.shopnumber.get()

		# if name or number == '':
		# 	tk.messagebox.showinfo('empty','fill valid values')
		# else:
		self.c.execute("DELETE FROM 'shopdetails'")
		self.c.execute("INSERT INTO 'shopdetails' Values (?,?) ",(name,number))
		self.conn.commit()
		self.conn.close()

		print(name,number)

	def exit(self):
		Tk.destroy(self)
		return Admin().mainloop()

#===========================dashboard===============================================================



#====================we now run the main app=======================================================
if __name__=="__main__":
	admin().mainloop()
