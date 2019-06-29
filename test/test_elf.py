

import sys
import os
import sys
# Add the ptdraft folder path to the sys.path list

path = "/".join(os.path.realpath(__file__).split("/")[:-2]) + "/"
print(path)
sys.path.append(path)
sys.path.append("../")


from elf.elf_parser import *



static = elf("../test_binaries/small_c_hello")


for i in static.program_headers.items():
	print(i)