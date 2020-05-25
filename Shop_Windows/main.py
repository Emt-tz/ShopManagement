# import sys # Imports are automatically detected (normally) in the script to freeze
# import os 
# import cx_Freeze

# base = None 

# os.environ["TCL_LIBRARY"] = "\\home\\anaconda3\\lib\\tcl8.6"
# os.environ["TK_LIBRARY"] = "\\home\\anaconda3\\lib\\tk8.6"

# if sys.platform=='win32':
#     base = "Win32GUI"


# executables = [cx_Freeze.Executable("shopcompile.py")]    

# cx_Freeze.setup(
#         name = "Emt-Mgmt",
#         options = {"build_exe":{"packages":["tkinter"],"include_files":["laod.png","sales"]}},
#         version="0.01",
#         executables=executables)
from cx_Freeze import setup, Executable

import os
import sys
PYTHON_INSTALL_DIR = os.path.dirname(sys.executable)
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

include_files = ["sc.ico"]
packages = ["tkinter","datetime","time","sqlite3","pandas","babel.numbers","Tkinter","tkinter.filedialog","openpyxl"]
options = {'build_exe' : {'packages':packages, 'include_files':include_files}}

# GUI applications require a different base on Windows (the default is for a console application).
base = None
if sys.platform == "win32":
   base = "Win32GUI"

executables = [Executable("shop.py", base=base,icon="sc.ico")]

setup(name="Shop",options=options,version="0.1",description="Emmanuel Mtera Shop Management System",executables=executables)
