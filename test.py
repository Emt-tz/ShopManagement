
import subprocess

lpr =  subprocess.Popen("/usr/bin/lpr", stdin=subprocess.PIPE)


name = "emt"




printing = '''

    \t\t\tEmmanuel Hezekia Mtera

    \t\t\tProduct Quantity

    \t\t\tCopy    40

    \t\t\tchalk   45

    \t\t\tTotal   8500

  '''

#lpr.stdin.write(printing.encode())

print(lpr)