from cx_Freeze import setup, Executable

import os
import sys
from distutils.sysconfig import get_python_lib

PYTHON_INSTALL_DIR = os.path.dirname(sys.executable)
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

pkg = os.path.join(get_python_lib(),'mpl_toolkits')
pkg2 = "C:\\Users\\MR LAPTOP\\AppData\\Local\\Programs\\Python\\Python38\\Lib\\tkinter"

include_files = ['sc.ico',pkg,pkg2]
packages = ["datetime","time","sqlite3","pandas","babel","matplotlib","tkinter"]
options = {'build_exe' : {'packages':packages, 'include_files':include_files}}

# GUI applications require a different base on Windows (the default is for a console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"
    #base = None


executables = [Executable("Admin.py", base=base,icon='sc.ico',
                          shortcutName="Stationery",
            shortcutDir="DesktopFolder")]

setup(name="Shop",options=options,version="1",description="A simple Shop Management System, contact 0693677033",executables=executables)


