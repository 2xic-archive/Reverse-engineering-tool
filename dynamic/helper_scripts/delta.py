'''
	used to debug unicorn against gdb
'''
import sys
sys.path.insert(0, "../../")
from common.printer import *
from elf.utils import get_symbol_name as elf_get_symbol_name

def split_safe(input_list, index):
	if(index < len(input_list)):
		return input_list[index]
	return None

def unicorn_report(refrence, op_count, last_address):
	if(refrence == None):
		bold_print("unicorn not available to give a report")
	else:
		state = refrence.address_instruction_lookup[last_address][0]
		bold_print("Latest instruction : %s" % ("".join(state[0])))
		for i in state[1]:
			if("flags" in i.lower()):
				continue
			bold_print("Where %s was last changed : 0x%x" % (i, refrence.get_latest_register_write(i, op_count)))


'''
	usually you want to be able to have gdb and unicorn follow the exact
	same path. However, because of things like different memory addresses this is not
	necessarily the case. 
'''
def check_for_new_consensus(gdb, unicorn, i, j):
	new_i = i
	new_j = j
	for index_unicorn, m in enumerate(unicorn[new_i:]):
		found_agreement = False
		for index_gdb, n in enumerate(gdb[new_j:]):
			if(("=>" in n) and m == n.strip().split(" ")[1]):
			#	print("next agreement is at {}".format(m))
				found_agreement = True
				new_j += index_gdb
				break
		if(found_agreement):
			new_i += index_unicorn
#			print(((unicorn[new_i].strip(), gdb[new_j].strip().split(" ")[1] )))
			return (new_i, new_j)

	return (None, None)


#	not perfect, but usally you want to higher up in memory.
def linear_loop(gdb_val, unicorn_val):
	bold_print("stuck in linear loop? (blame %s )" % ("gdb" if(gdb_val < unicorn_val) else "unicorn"))
	print("")

#def latest_change(register_name):
#	state = refrence.address_instruction_lookup[last_address][0]
#	bold_print("Latest instruction with consensus : %s" % ("".join(state[0])))


def run_check(unicorn_refrence=None):
	print("\n")
	unicorn = open("/root/test/test_binaries/unicorn.log").read().split("\n")
	gdb = open("/root/test/test_binaries/gdb.log").read().split("\n")

	i = 0
	j = 0

	disagreement_count = 0
	last_agrement = None

	#can_catch_up = False
	trace_register = False

	op_count = 0

	last_register_state = None

	hit_count = {

	}

	while i < len(unicorn) and j < len(gdb) and 0 < len(unicorn[i]):
		if(unicorn[i].strip() == (split_safe(gdb[j].strip().split(" "), 1)) or (unicorn[i].strip() ==  gdb[j].strip().split("\t")[0].split(" ")[-1])):
			if("=>" in gdb[j]):
				last_agrement = unicorn[i].strip()

				hit_count[last_agrement] = hit_count.get(last_agrement, 0) + 1

				op_count += 1
		else:
			if("=>" in gdb[j]):
				if(unicorn[i].strip() != gdb[j]):
					unicorn_val = int(unicorn[i].strip(), 16)
					gdb_val = int(gdb[j].strip().split(" ")[1].strip(), 16)
					old_i, old_j = i, j

					bold_print("Error in function %s" % (elf_get_symbol_name(unicorn_refrence.target, int(int(last_agrement, 16)))))
					bold_print("Last agreement {} (hit {})".format(last_agrement, hit_count[last_agrement]))
					bold_print("Unicorn : %s, GDB : %s" % (unicorn[i].strip(), gdb[j].strip().split(" ")[1]))
					
					target = "unicorn" if(unicorn_val < gdb_val) else "gdb"

					simulate_variable = None

					if(target == "gdb"):
						simulate_variable = j
						while simulate_variable < len(gdb) and unicorn[i] != split_safe(gdb[simulate_variable].strip().split(" "), 1):
							simulate_variable += 1
					else:
						simulate_variable = i
						while simulate_variable < len(unicorn) and unicorn[simulate_variable] != gdb[j].strip().split(" ")[1]:
							simulate_variable += 1

					if (not (simulate_variable < len(gdb) and target == "gdb")) or (not (simulate_variable < len(unicorn) and target == "unicorn")):
						bold_print("Could not resolve linearly... {}".format(target))

						new_i, new_j = check_for_new_consensus(gdb, unicorn, i, j)
						if(new_i == None):
							bold_print("Could not catch up ... {}".format(target))
							exit(0)
						else:
							bold_print("Could catch up non linear!!! Next agreement {} <3 ({})".format(unicorn[new_i], elf_get_symbol_name(unicorn_refrence.target, int(int(unicorn[new_i], 16))) ))
							bold_print("Unicorn had to take %i steps" % (new_i - i))
							bold_print("Gdb had to take %i steps" % (new_j - j))
							i = new_i
							j = new_j

					elif(target == "gdb"):
						linear_loop(gdb_val, unicorn_val)
						j = simulate_variable
					elif(target == "unicorn"):
						linear_loop(gdb_val, unicorn_val)
						i = simulate_variable
						
					if(i == old_i and j == old_j):
						bold_print("Could not resolve...")
						exit(0)
						break

					disagreement_count += 1
					print("")
					'''
					command = input("continue ? \n")
					if(command == "cc"):
						last_register_state = [unicorn_val, gdb_val]
					elif(command[:2] == "0x"):
						if(0 < len(command)):
							unicorn_refrence.boot()
							unicorn_refrence.unicorn_debugger.add_breakpoint(int(command, 16))
							unicorn_refrence.run()
					'''
					continue

			elif(trace_register):
				unicorn_val, gdb_val =	unicorn[i], gdb[j].strip().split("\t")[0].split(" ")[-1]
				if not (last_register_state == None):
					if(unicorn_val == last_register_state[0] and gdb_val == last_register_state[1]):
						i += 1
						j += 1
						continue
				'''
					tracking register like eflags make it easy to find bugs.
				'''
				bold_print("Mismatch register value....")
				print("From address : 0x%x" % int(unicorn[i - 3], 16))
				print("unicorn %s, gdb %s " % (unicorn_val, gdb_val))
				print(gdb[j])

				unicorn_report(unicorn_refrence, op_count, unicorn[i - 3])

				command = input("continue ? \n")
				if(command == "cc"):
					last_register_state = [unicorn_val, gdb_val]
				elif(command[:2] == "0x"):
					if(0 < len(command)):
						unicorn_refrence.boot()
						unicorn_refrence.unicorn_debugger.add_breakpoint(int(command, 16))
						unicorn_refrence.run()

		i += 1
		j += 1

	if(i < len(gdb)):
		bold_print("EARLY EXIT, did something bad happen with unicorn? [unicorn i, vs gbd j : %i vs %i" % (i, len(gdb)))
		bold_print("Size unicron %i, size gdb %i" % (len(unicorn), len(gdb)))
		print("Last instruction {}".format(unicorn[i-1]))
		print("Last instruction {}".format(unicorn[i-2]))
		print("Last instruction {}".format(unicorn[i-3]))

	bold_print("Disagreement with gdb == %i" % (disagreement_count))
	print("This can be error with handling of instruction or the simple fact that unicorn can have placed something more accesible than gdb.")
	print("For instance, enviorment variables are stored more clossely with unicorn")

if __name__ == "__main__":
	run_check()

