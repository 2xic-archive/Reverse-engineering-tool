import gdb
import sys
import os
sys.path.insert(0, "/".join(os.path.realpath(__file__).split("/")[:-1]))
sys.path.insert(0, "./")
from stack_string import *
#gdb.execute('file /root/test/test_binaries/small_c_hello')
#gdb.execute('file /root/test/test_binaries/static_small')

# gdb -q -x ./dynamic/helper_scripts/gdb_reproducer.py /root/test/test_binaries/static_small


break_adress = 0x4541cf
hit_counts = None# 11

output = gdb.execute('break *{}'.format(hex(break_adress)), to_string=True)
output = gdb.execute('run', to_string=True)

registers = [
	"rax"
]


if(hit_counts != None):
	for i in range(hit_counts):
		gdb.execute("c")
		
	for register in registers:
		hex_2_string(gdb.execute('x ${}'.format(register.lower()), to_string=True))

hex_2_string("0xe1d")
exit(0)

while True:
	try:
		for register in registers:
			padding = 0
			while True:
				print( gdb.execute('i r {}'.format(register.lower(), padding), to_string=True))
				hex_2_string(gdb.execute('i r {}'.format(register.lower(), padding), to_string=True))
				if "0" in gdb.execute('i r {}'.format(register.lower(), padding), to_string=True).replace("0x", ""):
					break
				padding += 4

		gdb.execute("c", to_string=True)
	except Exception as e:
		print(e)
		break

gdb.execute('quit', to_string=True)
