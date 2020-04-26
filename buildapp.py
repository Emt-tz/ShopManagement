import os

app = "shop.py"
icon = "icon.ico"

command = f'pyinstaller --onefile -i "{icon}" {app}'

os.system(command)