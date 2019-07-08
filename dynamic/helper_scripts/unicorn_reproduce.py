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

file = "/root/test/test_binaries/small_c_hello"
target = model(elf(file), None)

def call_back(emulator_object):
	global target
	location = emulator_object.reg_read(eval("UC_X86_REG_RAX"))
	print(hex(location))

	location = emulator_object.reg_read(eval("UC_X86_REG_R8"))
	print(hex(location))

	location = emulator_object.reg_read(eval("UC_X86_REG_EFLAGS"))
	print(target.dynamic.unicorn_debugger.readable_eflags(location))
	
def init_unicorn(file, break_adress, hit_counts=None, on_break_point=call_back):
	global target

	for address in break_adress:
		target.dynamic.unicorn_debugger.add_breakpoint(address, on_break_point)

	target.run_emulator(force=True, thread=False)


#	python3 ./dynamic/helper_scripts/unicorn_reproduce.py
if __name__ == "__main__":
	init_unicorn(file, break_adress,hit_counts=hit_counts, on_break_point=call_back)
