
# gdb -q -x gdb_helper.py

import gdb
gdb.execute('file /root/test/test_binaries/static_v2')

output = gdb.execute('break _start', to_string=True)

output = gdb.execute('display/i $pc', to_string=True)

output = gdb.execute('run', to_string=True)

debug_file = open("/root/test/test_binaries/gdb.log", "w")
for i in range(10000):
	output = gdb.execute('stepi', to_string=True)
	if(len(output) == 0):
		break
	debug_file.write(output.split("\n")[1].split(":")[0] + "\n")
#	debug_file.write(gdb.execute('info registers eflags', to_string=True))
	debug_file.write(gdb.execute('info registers esi', to_string=True))

debug_file.write("finish")
debug_file.close()

