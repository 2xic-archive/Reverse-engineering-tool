import sys
import os

from elf.elf_parser import *

def test_headers():
	path = "/".join(os.path.realpath(__file__).split("/")[:-2]) + "/"
	sys.path.append(path)
	sys.path.append("../")

	static = elf("./test_binaries/static_small")

	assert(len(static.program_headers.items()) > 0)
	assert(len(static.section_headers.items()) > 0)