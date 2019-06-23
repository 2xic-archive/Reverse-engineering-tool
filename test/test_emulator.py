



'''
	bootstraping the emulator just to test
'''

import sys
import os
import sys
# Add the ptdraft folder path to the sys.path list

path = "/".join(os.path.realpath(__file__).split("/")[:-2]) + "/"
print(path)
sys.path.append(path)
sys.path.append("../")


from common.model  import *
from elf.elf_parser import *


working_model = model(elf(path + "/test_binaries/static_small"), None)
working_model.dynamic.unicorn_debugger.max_instructions = 10
working_model.dynamic.unicorn_debugger.test = True
working_model.dynamic.run()
