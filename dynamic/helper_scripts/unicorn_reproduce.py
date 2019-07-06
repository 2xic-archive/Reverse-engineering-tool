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

break_adress = 0x4541b4
hit_counts = 11


file = "/root/test/test_binaries/static_small"

target = model(elf(file), None)

def call_back(emulator_object):
	location = emulator_object.reg_read(eval("UC_X86_REG_RDI"))
	pretty_print_bytes(emulator_object.mem_read(location, 8))


target.dynamic.unicorn_debugger.add_breakpoint(break_adress, call_back)

target.run_emulator(force=True, thread=False)

#	python3 ./dynamic/helper_scripts/unicorn_reproduce.py


'''
	okay so at 0x00000000004541b4
	mov rax, rdi

	rax will only get 0xe1d, I don't know why...
	rdi hold the value 0x7fffffffee1d

	unicorn and gdb both agree on the value that rdi points to....
	maybe bug with mov?
'''