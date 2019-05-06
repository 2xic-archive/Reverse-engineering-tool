





def readable_eflags(current_state):
	if(True):
		flags =	[
				[2,	0x0004,	"PF"],	 
				[4,	0x0010,	"AF"],	
				[6,	0x0040,	"ZF"],	
				[7,	0x0080,	"SF"],	
				[8,	0x0100,	"TF"],	
				[9,	0x0200,	"IF"],	
				[10,	0x0400,	"DF"],	
				[11,	0x0800,	"OF"]
			]
		enabled_string = ""

		for flag in flags:
			if( (current_state & flag[1]) >> flag[0]):
				enabled_string += flag[2] + " "
		return enabled_string



unicorn = open("/root/test/test_binaries/unicorn.txt").read().split("\n")
gdb = open("/root/test/test_binaries/gdb.log").read().split("\n")



for i in range(3000):
	if(unicorn[i].strip() == (gdb[i].strip().split(" ")[1]) or (unicorn[i].strip() == gdb[i].strip().split("\t")[0].split(" ")[-1] )):
#		print(((unicorn[i].strip(), gdb[i].strip().split(" ")[1] )))
		pass
	else:
		if("=>" in gdb[i]):
			print("")
			print("oh no...")
			print(( ( readable_eflags(int(unicorn[i - 1].strip().replace("0x", ""),16)) , readable_eflags(int(gdb[i - 1].strip().split("\t")[0].split(" ")[-1].replace("0x", ""),16 ))) ) )			
			print(( ( (int(unicorn[i - 1].strip().replace("0x", ""),16)) , (int(gdb[i - 1].strip().split("\t")[0].split(" ")[-1].replace("0x", ""),16 ))) ) )			

			print(((unicorn[i].strip(), gdb[i].strip().split(" ")[1] )))
			exit(0)
		else:
			print("unicorn | gdb")
			print(( ( readable_eflags(int(unicorn[i].strip().replace("0x", ""),16)) , readable_eflags(int(gdb[i].strip().split("\t")[0].split(" ")[-1].replace("0x", ""),16 ))) ) )			
#			exit(0)
print("all good?")
'''
	(gdb) info registers sil
	sil            0x1	1	


'''