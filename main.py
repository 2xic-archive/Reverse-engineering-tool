


import sys
from common.web import *
from common.terminal import *

if __name__ == "__main__":
	use_web = True

	if(1 < len(sys.argv)):
		if(use_web):
			go_online(sys.argv[1])
		else:
			go_text(sys.argv[1])