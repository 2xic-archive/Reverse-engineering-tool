import sys
import os
path = "/".join(os.path.realpath(__file__).split("/")[:-2]) + "/"
sys.path.append(path)
sys.path.append("../")

from elf.elf_parser import *
from elf.utils import *

path = "/".join(os.path.realpath(__file__).split("/")[:-2]) + "/"
sys.path.append(path)
sys.path.append("../")

def test_resolve():
	static = elf(path + "/test_binaries/static_small")

	assert(get_symbol_name(static, 0x4003b0) == "backtrace_and_maps")
	assert(get_symbol_name(static, 0x40eac0) == "malloc_init_state")
	assert(get_symbol_name(static, 0x4004fa) == "detach_arena.part.1")



