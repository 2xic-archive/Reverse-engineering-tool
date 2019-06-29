


import sys
from common.web import *
from common.terminal import *

if __name__ == "__main__":
	use_web = True
	test = True

	if(test):
#		target = model(elf("/root/test/test_binaries/static_small"), None)
		target = model(elf("/root/test/test_binaries/small_c_hello"), None)
		target.run_emulator(force=True, thread=False)
		exit(0)

	if(1 < len(sys.argv)):
		if(use_web):
			go_online(sys.argv[1])
		else:
			go_text(sys.argv[1])
	else:
		print("script.py binary")