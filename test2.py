import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet 



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



