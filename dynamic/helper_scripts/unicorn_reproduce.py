import sys
sys.path.insert(0, "../../")
sys.path.insert(0, "../")
sys.path.insert(0, "./")

from common.printer import *
import os
import sys
from common.web import *
from common.terminal import *
import dynamic.helper_scripts.delta as delta_compatibility
from reproducer import *

file = "/root/test/test_binaries/getgid"
target = model(elf(file), None, auto_boot=False, disable_args=True)


def call_back(emulator_object):
	global target
#	location = emulator_object.reg_read(eval("UC_X86_REG_RAX"))
#	print(hex(location))

#	location = emulator_object.reg_read(eval("UC_X86_REG_R8"))
#	print(hex(location))

#	location = emulator_object.reg_read(eval("UC_X86_REG_EFLAGS"))
#	print(target.dynamic.unicorn_debugger.readable_eflags(location))

	target.dynamic.unicorn_debugger.handle_commands()

def init_unicorn(file, break_adress, hit_counts=None, on_break_point=call_back):
	global target
	print(break_adress)
	assert(len(break_adress) > 0)
	for address in break_adress:
		target.dynamic.unicorn_debugger.add_breakpoint(address, on_break_point)

	target.run_emulator(force=True, thread=False)


#	python3 ./dynamic/helper_scripts/unicorn_reproduce.py
if __name__ == "__main__":
	unicorn_mappings = (target.dynamic.look_up_library)#.values())
#	print(unicorn_mappings)
	init_unicorn(file, load_break_points(libc_offset=unicorn_mappings["libc.so.6"][0], 
										ld_offset=unicorn_mappings["ld-linux-x86-64.so.2"][0]), hit_counts=hit_counts, on_break_point=call_back)
