

# Triforce

#   Notes
Mostly tested on some CTF binaries, I'm sure you can make the program do weird things if you try it on something different. The program is still under construction.

#	features
-	flat view (see all the sections with code)
-	code grapth (click in a section, view the branches of the block)
-	hex view (click an instruction see where it is in the binary)

#	work in progress / ideas
-	unicorn support
	-	see what each instruction has done to the memory and other registers
		-	basically like gdb break on every instruction
	-	rewind, go to the previous state just by moving the arrow keys(like QIRA)...
-	binary patching
	-	I have coded parts of this already, however it needs a better interface
-	visualizing a binary
	-	see the entropy
	-	regions with text/data etc

#   what is the plan?
static and dynamic reverse engineering, one package.
<img src="README/idea.png"  width="500px" />

(from http://www.keystone-engine.org/docs/BHUSA2016-keystone.pdf )

# setup
-	install capstone from the next branch
		https://github.com/aquynh/capstone/tree/next
- install keystone
		https://github.com/keystone-engine/keystone
    >  pip3 install -r requirements.txt