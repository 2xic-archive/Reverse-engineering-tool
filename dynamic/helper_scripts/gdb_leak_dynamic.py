import gdb
import sys
import os

PATH = (os.path.dirname(os.path.abspath(__file__)) + "/")
sys.path.insert(0, PATH + "../")
sys.path.insert(0, PATH + "../../")

from dynamic_linker import *
from elf.utils import get_symbol_name as elf_get_symbol_name
from elf.elf_parser import * 

libc_offset = 0x7ffff7a3a000
ld_offset = 0x7ffff7dd9000

libc = elf("/lib/x86_64-linux-gnu/libc.so.6")
program = elf("/root/test/test_binaries/getgid")
print(program.program_header_start)

'''
	
'''

exit(0)

gdb.execute("display/i $pc")
#output = gdb.execute('break _start', to_string=True)
#output = gdb.execute('run', to_string=True)
'''
for section_key, section_info in libc.sections_with_name.items():
	if(section_info["type"] == 0x4):
		for key, item in parse_relocation(libc, section_key, debug=True).items():
			if not ("unamed" in key):
				continue
			output = gdb.execute('x {}'.format(libc_offset + item[0]), to_string=True)
			print("Reading from {}".format(libc_offset + item[0]))
			print("Address {}, added {}".format(item[0], item[1]))
			print(output)
			break
#		break
'''
'''
leak_info = [
	(ld_offset, 0x224a00),
	(ld_offset, 0x1860)
]
for x, y in leak_info:
	print(gdb.execute('x {}'.format(x + y)))
'''
#gdb.execute("break *{}".format(libc_offset + 0x20400))

#ENTRY_OFFSET = 	gdb.execute("break *{}".format(ld_offset + 0xc20))
gdb.execute("break *{}".format(ld_offset + 0x2490))

#gdb.execute("r")
#gdb.execute("break *{}".format(ld_offset + 0xc64))
gdb.execute("r")

'''
for i in range(5000):
	gdb.execute("stepi", to_string=False)
gdb.execute("info proc mappings")
'''


'''
gdb.execute("i r")
gdb.execute("info frame")
gdb.execute("info proc mappings")
gdb.execute("break *{}".format(ld_offset + 0xc64))
gdb.execute("r")
gdb.execute("i r")
gdb.execute("info frame")
gdb.execute("info proc mappings")
gdb.execute("stepi")
'''
#	gdb.execute("break *{}".format(libc_offset + 0x20400))
#	gdb.execute("r")

#gdb.execute('quit', to_string=True)


#	gdb -q -x ./dynamic/helper_scripts/gdb_leak_dynamic.py ./test_binaries/getgid







