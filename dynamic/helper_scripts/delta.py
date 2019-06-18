'''
	used to debug unicorn against gdb
'''
import sys
sys.path.insert(0, "../../")

from common.printer import *

unicorn = open("/root/test/test_binaries/unicorn.log").read().split("\n")
gdb = open("/root/test/test_binaries/gdb.log").read().split("\n")

i = 0
j = 0

hit_count = {
	"unicorn":{

	},
	"gdb":{

	}
}

disagreement_count = 0
trace_register = False


while i < len(unicorn) and j < len(gdb):
	if("=>" in gdb[j]):
		results = hit_count["unicorn"].get(unicorn[i].strip(), 0)
	#	print(results)
		if(results == 0):
			hit_count["unicorn"][unicorn[i].strip()] = 1
			results = 1
		else:
			hit_count["unicorn"][unicorn[i].strip()] += 1
			results += 1
		#	unicorn[i].strip()

	if(unicorn[i].strip() == (gdb[j].strip().split(" ")[1]) or (unicorn[i].strip() == gdb[j].strip().split("\t")[0].split(" ")[-1] )):
#		if("=>" in gdb[j]):
#			print(((unicorn[i].strip(), gdb[j].strip().split(" ")[1] )))
		pass
	else:
		if("=>" in gdb[j]):
			if(unicorn[i].strip() != gdb[j]):
				#j += 3 * 2
				#while not "0x4142e0" in gdb[j]:
				#	j += 1
				unicorn_val = int(unicorn[i].strip(), 16)
				gdb_val =  int(gdb[j].strip().split(" ")[1].strip(), 16)

				print(((unicorn[i].strip(), gdb[j].strip().split(" ")[1] )))
				old_i, old_j = i, j
				if(unicorn_val < gdb_val):

				#	if(len(unicorn) < len(gdb)):
				
					for index_unicorn, m in enumerate(unicorn[i:]):
						found_agreement = False
						for index_gdb, n in enumerate(gdb[j:]):
							if(("=>" in n) and m == n.strip().split(" ")[1]):
								print("next agreement is at {}".format(m))
								found_agreement = True
								j += index_gdb
								break
						if(found_agreement):
							i += index_unicorn
							break
					print(((unicorn[i].strip(), gdb[j].strip().split(" ")[1] )))
				
#					while i < len(unicorn) and unicorn[i] != gdb[j].strip().split(" ")[1]:
#						i += 1

#					if not (i < len(unicorn)):
#						bold_print("Could not resolve... unicorn")
				else:
					found_agreement = False
					for index_unicorn, m in enumerate(unicorn[i:]):
						for index_gdb, n in enumerate(gdb[j:]):
							if(("=>" in n) and m == n.strip().split(" ")[1]):
								print("next agreement is at {}".format(m))
								found_agreement = True
								j += index_gdb
								break
						if(found_agreement):
							i += index_unicorn
							break
				if(i == old_i and j == old_j):
					bold_print("Could not resolve...")
					break

			#		while j < len(gdb) and unicorn[i] != gdb[j].strip().split(" ")[1]:
			#			j += 1
			#		if not (j < len(gdb)):
			#			bold_print("Could not resolve... gdb")

				disagreement_count += 1
				print("stuck in loop? (blame %s )" % ("gdb" if(gdb_val < unicorn_val) else "unicorn"))
				continue

		elif(trace_register):
			print("mismatch reg value....")
			print(unicorn[i])
			print(gdb[j])

	i += 1
	j += 1

bold_print("Disagreement with gdb == %i" % (disagreement_count))
print("This can be error with handling of instruction or the simple fact that unicorn can have placed something more accesible than gdb.")
print("For instance, enviorment variables are stored more clossely with unicorn")

