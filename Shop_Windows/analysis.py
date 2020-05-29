from tkinter import *
import tkinter as tk
from tkinter import messagebox
import sys
from tkcalendar import DateEntry
from tkinter.font import Font
import sqlite3
from test2 import MonthlySales as mnsales


class Analysis(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title('Analysis')
		self.color = ['cadetblue','orange','yellowgreen','lightgrey']

		self.mainframe = Frame(bg=self.color[0],width=600,height=600).place(relx=0,rely=0)
		self.drawframe = Frame(bg=self.color[1],width=540,height=5).place(relx=0.05,rely=0.1)
		self.bottomframe = Frame(bg=self.color[1],width=540,height=5).place(relx=0.05,rely=0.9)
		self.sideframe = Frame(bg=self.color[1],width=5,height=480).place(relx=0.05,rely=0.1)
		self.sideframe1 = Frame(bg=self.color[1],width=5,height=485).place(relx=0.945,rely=0.1)
		self.centerframe = Frame(bg=self.color[3],width=532,height=475).place(relx=0.058,rely=0.109)

		self.fromdateentry = StringVar()
		self.todateentry = StringVar()
		self.yearlyentry = IntVar()

			#getsales entry and button
		self.entrydatey = 420
		self.entrydatex = 50
		self.entrydatebuttonx = 220

		self.conn = sqlite3.connect('sales')
		self.c = self.conn.cursor()

		self.font = Font(family="Times New Roman bold", size=10)


		self.geometry("600x600+300+50")
		self.resizable(False,False)
		self.ExportAnalysis()

	def ExportAnalysis(self):
		self.btn = Button(self.centerframe,bg="cadetblue",text="click to open export functions".upper(),height=1,command=self.Mainui)
		self.btn.place(relx=0.28,rely=0.14)

	def Mainui(self):
		self.label = Label(self.centerframe,text="Export your Sales by Month,Day and Year")
		self.label.place(relx=0.25,rely=0.7)

		exitbtn = Button(self.centerframe,bg='cadetblue',text="Exit",command=self.exit)
		exitbtn.place(relx=0.78,rely=0.8)

		self.btn.config(state='disabled')

		self.exportsales = Button(self.centerframe,font=self.font,text="Export".upper(),bg="cadetblue",fg="white",command=self.getsalesbymonth,bd=0,height=1, width=15)
		self.exportsales.place(x=self.entrydatex+320, y=self.entrydatey-255)

		self.exportyearsales = Button(self.centerframe,font=self.font,text="Yearly".upper(),bg="cadetblue",fg="white",command=self.getsalesbyyear,bd=0,height=1, width=15)
		self.exportyearsales.place(x=self.entrydatex+320, y=self.entrydatey-155)

		self.yearlysales = Entry(self.centerframe,foreground="black",background='white',textvariable=self.yearlyentry,font=self.font,width=15)
		self.yearlysales.place(x=self.entrydatex+20, y=self.entrydatey-150)

		self.fromdateEntry = DateEntry(self.centerframe,foreground="white",background='cadetblue',date_pattern="dd/m/yyyy",textvariable=self.fromdateentry,font=self.font)
		self.fromdateEntry.place(x=self.entrydatex+20, y=self.entrydatey-250)

		self.todateEntry = DateEntry(self.centerframe,foreground="white",background='cadetblue',date_pattern="dd/m/yyyy",textvariable=self.todateentry,font=self.font)
		self.todateEntry.place(x=self.entrydatex+180, y=self.entrydatey-250)	

	#=================================================================================================================#
	def getsalesbymonth(self):
		return mnsales.salesbymonth(self.fromdateentry.get(),self.todateentry.get())

	def getsalesbyyear(self):
		return mnsales.GetYearlySales(self.yearlyentry.get())
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
	def exit(self):
		Tk.destroy(self)
		from Admin import Admin
		return Admin().mainloop()
		
# if __name__ == '__main__':
# 	Analysis().mainloop()