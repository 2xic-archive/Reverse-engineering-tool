

# Triforce

<img src="README/current_state.png"  width="800px" />

#   Notes
Mostly tested on some CTF (elf)binaries, I'm sure you can make the program do weird things if you try it on something big and complicated. *This program is still under construction*.

#	Features
-	flat view (see all the sections with code)
-	code grapth (click in a section, view the branches of the block)
-	hex view (click an instruction see where it is in the binary)
-	(work in progress) dynamic view (click an instruction, see what the values have been when that instruction was executed)
-	when you click a jump instruction, it moves you to the target. The jump target was not interesting? Move back with the back arrow at the menu.
-	move around with arrow keys. Are you in graph view ? Use left and right arrow to select target block (if you are at a conditional block, if not press down). When you move between blocks a call stack will be made so you can easily move backwards.


# Design philosophy
What do you expect from a reverse engineering tool? You want quick insight into a program. How do you get insight? The best way is to get dynamic data with the aid of static information. The dynamic data show you where you have been, the static can help you get where you want to be. If the binary has been obfuscated the dynamic part will guide the static part. You want to be able to move around in the program flawlessly. This tool will have focus on speed, you want to do things like root cause analysis fast, this tool should work fast in environments like CTFs. 

#  Status with unicorn (dynamic side)
Currently I am running gdb and unicorn side by side on some static binaries, trying to get unicorn to run through the entire program flawlessly. Seems like special instructions like cpuid and xgetbv ~~and instructions that affect the eflags~~ give different results from gdb ... ~~Also as far as I know, implementing system specific system calls also has to be done~~ (written support for two syscalls, you can now run hello world). The debugger I wrote for unicorn does help (a lot) with root cause analysis, so I hope to see some meaningful progress soon. 

#  Do I think I can make a better tool than IDA? 
It's not about that. I started this project to hopefully see some changes in reverse engineering landscape. Things have been still there for a while and competition is needed to bring on changes with impact.

#	Work in progress / ideas
-	unicorn support
	-	see what each instruction has done to the memory and other registers
		-	basically like gdb break on every instruction
	-	rewind, go to the previous state just by moving the arrow keys(like QIRA)...
	-	dynamic code grapths?
-	**integrate dwarf data**
	-	you don't need a decompiler when you have dwarf!
-	make it easy to store comments and patches made to the binary. 
-	binary patching
	-	I have coded parts of this already, however it needs a better interface
-	visualizing a binary
	-	see the entropy
	-	regions with text/data etc
	-	not sure if I will integrate this into the main interface. I don't want things to get bloated


#   What is the plan?
static and dynamic reverse engineering, one package with a seamless interface. 
<img src="README/idea.png"  width="500px" />

(from http://www.keystone-engine.org/docs/BHUSA2016-keystone.pdf )

# setup
- install capstone from the next branch
		https://github.com/aquynh/capstone/tree/next
- install keystone
		https://github.com/keystone-engine/keystone
    >  pip3 install -r requirements.txt

# run
> python3 web.py ./test_binaries/fibonacci