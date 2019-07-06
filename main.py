

import os
import sys
from common.web import *
from common.terminal import *
import dynamic.helper_scripts.delta as delta_compatibility #import *

if __name__ == "__main__":
	use_web = True
	test = True

	if("--test" in sys.argv):
		'''
			run this tool vs gdb and cross check compatablity, 
			makes analyzing for bugs easier.
		'''
#		target = "/root/test/test_binaries/small_c_hello"
		target = "/root/test/test_binaries/static_small"

		last_run = ""
		if(os.path.isfile("/root/test/test_binaries/last_run.txt")):
			last_run = open("/root/test/test_binaries/last_run.txt", "r").read()
		if(last_run != target or "--gdb" in sys.argv):
			#	re run gdb and save output.
			os.system("gdb -q -x /root/test/dynamic/helper_scripts/gdb_helper.py {}".format(target))
			open("/root/test/test_binaries/last_run.txt", "w").write(target)

		target = model(elf(target), None)
		target.run_emulator(force=True, thread=False)

		delta_compatibility.run_check(target.dynamic)

	elif(1 < len(sys.argv)):
		if(use_web):
			go_online(sys.argv[1])
		else:
			go_text(sys.argv[1])
	else:
		print("script.py binary")