import gdb

import sys
import os
sys.path.insert(0, "/".join(os.path.realpath(__file__).split("/")[:-1]))
sys.path.insert(0, "./")

from delta import resolve_mapping


gdb.execute("break _start", to_string=True)
#gdb.execute("r")
#gdb.execute("record")
gdb.execute("set print frame-arguments none")
gdb.execute("set print address off")
gdb.execute("set print symbol-filename off")
gdb.execute("set print symbol off")

gdb.execute("catch syscall", to_string=True)
gdb.execute("r", to_string=True)
gdb.execute("c")
#gdb.execute("target record-full")
#gdb.execute("c", to_string=True)

'''
	-	write each syscall info 2 a file to easily read.
		
'''

new_breaks = []
while True:
	try:
#		address = gdb.execute("i r rip", to_string=True).split("\t")[0].split(" ")[-1]
		address = gdb.execute("x/-1i $pc", to_string=True).strip().split(" ")[0]
		print("Break on address == " + address)
		if(address not in new_breaks):
			new_breaks.append(address)
		gdb.execute("c", to_string=True)
	except Exception as e:
		break
#	gdb -q -x ./dynamic/helper_scripts/gdb_trace_syscalls.py /root/test/test_binaries/getgid

gdb.execute("info breakpoints")
gdb.execute("delete 2")
gdb.execute("r")
gdb.execute("set logging off")
for x in new_breaks:
	if("0x" in x):
		print("break *" + x)
		gdb.execute("break *" + x, to_string=True)
gdb.execute("c")

file = "log.txt"
content = open(file, "w")#.write()

while True:
	try:
		syscall_before_rax = [
			gdb.execute("i r rax", to_string=True),
			gdb.execute("i r rdx", to_string=True)
		]

		gdb.execute("stepi")
		sysall_after_rax = [
			gdb.execute("i r rax", to_string=True),
			gdb.execute("i r rdx", to_string=True)
		]

		content.write("before")
		content.write("\n")
		for i in syscall_before_rax:
			gdb_val = int(i.split(" ")[-1].split("\t")[0], 16)
			_, gdb_val, _, _ = resolve_mapping(gdb_val, debug=True)
			content.write(hex(gdb_val) + "\n")


		content.write("\n")
		content.write("after")
		content.write("\n")
		for j in sysall_after_rax:
			gdb_val = int(j.split(" ")[-1].split("\t")[0], 16)
			_, gdb_val, _, _ = resolve_mapping(gdb_val, debug=True)
			content.write(hex(gdb_val) + "\n")

		content.write("="*16)
		content.write("\n")

		gdb.execute("c")
	except Exception as e:
		print(e)
		break
print("happy")
gdb.execute("quit")



