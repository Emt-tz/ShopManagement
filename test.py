# try:
# 	import tkinter as tk
# 	from tkinter import PhotoImage
# except:
# 	import Tkinter as tk



# class App(tk.Frame):
# 	def __init__(self,master=None,**kw):
		
# 		self.splash = Splash(root)
# 		tk.Frame.__init__(self,master=master,**kw)
# 		tk.Label(self,text="MainFrame").grid()
# 		self.after(3000,self.splash.destroy)

# class Splash(tk.Toplevel):
# 	def __init__(self,master=None,**kw):
# 		tk.Toplevel.__init__(self,master=master,**kw)
# 		self.geometry('300x168+500+300')
# 		photo = PhotoImage(file="laod.png")

# 		w = tk.Label(self,image=photo)
# 		w.photo = photo
# 		w.grid(row=0, column=4)

# 		self.overrideredirect(1)

# if __name__ == '__main__':
# 	root = tk.Tk()
# 	App(root).grid()

# 	root.eval('tk::PlaceWindow . center')
# 	root.mainloop()

# from tkinter import *
# root = Tk()
# root.title('Simple Plot - Version 1')
# root.geometry('500x350+500+200')

# canvas = Canvas(root, width=450, height=300, bg = 'white')
# canvas.pack()

# Button(root, text='Quit', command=root.quit).pack()
# canvas.create_line(100,250,400,250, width=2)
# canvas.create_line(100,250,100,50, width=2)

# for i in range(11):
# 	x = 100 + (i * 30)
# 	canvas.create_line(x,250,x,245, width=2)
# 	canvas.create_text(x,254, text='%d'% (10*i), anchor=N)

# for i in range(6):
# 	y = 250 - (i * 40)
# 	canvas.create_line(100,y,105,y, width=2)
# 	canvas.create_text(96,y, text='%5.1f'% (50.*i), anchor=E)

# for x,y in [(12, 56), (20, 94), (33, 98), (45, 120), (61, 180),
# (75, 160), (98, 223)]:
# 	x = 100 + 3*x
# 	y = 250 - (4*y)/5
# 	canvas.create_oval(x-6,y-6,x+6,y+6, width=1,
# outline='black', fill='SkyBlue2')
# root.mainloop()

values = ""
var2 = ""

if values or var2 == "":
	print("var")
else:
	print("va")
