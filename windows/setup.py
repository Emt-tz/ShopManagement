#nuitka setup options 

#flags to passthrough

options = [
	"--windows-disable-console",
	"--no-pyi-file",
	# "--include-module=tkinter",
	# "--include-module=matplotlib",
	# "--include-module=cryptography",
	# "--standalone",
	"--plugin-no-detection",
	"--show-progress",
	"--output-dir=stat",
	"--windows-icon=sc.ico",
]

import os

file = "Admin.py"
n = ["--run"]
os.system(f'nuitka {options[1]} {options[3]} {options[4]} {options[5]} {file} ')