import gdb
import sys
import os
sys.path.insert(0, "/".join(os.path.realpath(__file__).split("/")[:-1]))
sys.path.insert(0, "./")
from reproducer import *
from stack_string import *

# gdb -q -x ./dynamic/helper_scripts/gdb_reproducer.py /root/test/test_binaries/getgid
def break_point_handler():
	try:
		print( gdb.execute('i r rax', to_string=True))
		print( gdb.execute('i r r8', to_string=True))
		print( gdb.execute('i r eflags', to_string=True))
	except Exception as e:
		pass

def init_gdb(break_adress, hit_counts=None, on_break_point=break_point_handler):
	for address in break_adress:
		gdb.execute('break *{}'.format(hex(address)), to_string=True)


	gdb.execute('run', to_string=True)

	if(hit_counts != None):
		for i in range(hit_counts):
			gdb.execute("c")
		on_break_point()
	else:
		while True:
			try:
				on_break_point()
				response = gdb.execute("c", to_string=True)
			except Exception as e:
				break
	gdb.execute("display/i $pc")
	#gdb.execute('quit', to_string=True)

if __name__ == "__main__":
	init_gdb(load_break_points(), hit_counts=hit_counts)

