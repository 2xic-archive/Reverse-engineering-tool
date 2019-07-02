'''
	used to debug unicorn against gdb
'''
import sys
sys.path.insert(0, "../../")
from common.printer import *

def split_safe(input_list, index):
	if(index < len(input_list)):
		return input_list[index]
	return None

def unicorn_report(refrence, op_count, last_address):
	if(refrence == None):
		bold_print("unicorn not avaible to give a report")
	else:
		state = refrence.address_instruction_lookup[last_address][0]
		bold_print("Latest instruction : %s" % ("".join(state[0])))
		for i in state[1]:
			bold_print("Where %s was last changed : 0x%x" % (i, refrence.get_latest_register_write(i, op_count)))


def run_check(unicorn_refrence=None):
	print("\n")
	unicorn = open("/root/test/test_binaries/unicorn.log").read().split("\n")
	gdb = open("/root/test/test_binaries/gdb.log").read().split("\n")

	i = 0
	j = 0

	disagreement_count = 0
	last_agrement = None

	can_catch_up = True
	trace_register = True

	op_count = 0

	while i < len(unicorn) and j < len(gdb):
		if(unicorn[i].strip() == (split_safe(gdb[j].strip().split(" "), 1)) or (unicorn[i].strip() ==  gdb[j].strip().split("\t")[0].split(" ")[-1] )):
			if("=>" in gdb[j]):
				last_agrement = unicorn[i].strip()
				op_count += 1
		else:
			if("=>" in gdb[j]):
				if(unicorn[i].strip() != gdb[j]):
					unicorn_val = int(unicorn[i].strip(), 16)
					gdb_val =  int(gdb[j].strip().split(" ")[1].strip(), 16)

					print("last agreement {}".format(last_agrement))
					print(((unicorn[i - 1].strip(), gdb[j - 1].strip().split(" ")[1])))
					print(((unicorn[i].strip(), gdb[j].strip().split(" ")[1])))
					old_i, old_j = i, j

					if(unicorn_val < gdb_val):
						if not can_catch_up:
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
						else:				
							while i < len(unicorn) and unicorn[i] != gdb[j].strip().split(" ")[1]:
								i += 1

							if not (i < len(unicorn)):
								bold_print("Could not resolve... unicorn")
								exit(0)
					else:
						if not can_catch_up:
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
						else:
							while j < len(gdb) and unicorn[i] != split_safe(gdb[j].strip().split(" "), 1):
								j += 1
							if not (j < len(gdb)):
								bold_print("Could not resolve... gdb")
								exit(0)

					if(i == old_i and j == old_j):
						bold_print("Could not resolve...")
						exit(0)
						break

					disagreement_count += 1
					#	not perfect, but usally you want to higher up in memory.
					bold_print("stuck in loop? (blame %s )" % ("gdb" if(gdb_val < unicorn_val) else "unicorn"))
					print("")
					continue

			elif(trace_register):
				bold_print("Mismatch register value....")
				print("From address : 0x%x" % int(unicorn[i - 3], 16))
				print(unicorn[i])
				print(gdb[j])

				unicorn_report(unicorn_refrence, op_count, unicorn[i - 3])
			#	print( gdb[j].strip().split("\t")[0].split(" ")[-1])
			#	input("continue ? ")
				print("exiting ....")
				exit(0)
		i += 1
		j += 1

	bold_print("Disagreement with gdb == %i" % (disagreement_count))
	print("This can be error with handling of instruction or the simple fact that unicorn can have placed something more accesible than gdb.")
	print("For instance, enviorment variables are stored more clossely with unicorn")

if __name__ == "__main__":
	run_check()

