import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet 
from pandas import read_csv
from tkinter import filedialog
import csv
import sqlite3

dailysales_table = """
CREATE TABLE "Daily Sales" (
	"Timed"	TEXT,
	"Product"	TEXT,
	"Quantity"	INTEGER,
	"Buying Price"	INTEGER,
	"Price"	NUMERIC
);"""

addproducts_table = """
CREATE TABLE "AddProducts" (
	"Name"	TEXT,
	"Buy_Price"	NUMERIC,
	"Sell_Price"	NUMERIC,
	"Quantity"	NUMERIC
);"""

login_table = """
CREATE TABLE "login" (
	"User"	TEXT,
	"Password"	TEXT
);"""

class InitializeDatabase:

	def createdb():
		dbname = 'sales'
		conn = sqlite3.connect(dbname)
		c = conn.cursor()
		c.execute(dailysales_table)
		c.execute(addproducts_table)
		c.execute(login_table)
		conn.commit()
		conn.close()

class PasswordEncrypter:

	def GenerateKey():
		password_provided = "Windows78!" # This is input in the form of a string
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
		return read_csv(file)

	def convertToExcel(file):
		x = ConvertCsvtoExcel.getCSV(file)
		export_file_path = filedialog.asksaveasfilename(defaultextension='.xlsx')
		x.to_excel(export_file_path, index=None, header=True)

