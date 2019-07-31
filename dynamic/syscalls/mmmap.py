


def mmap_type(proc_id):
	PROT_READ = 0x1 # page can be read */
	PROT_WRITE = 0x2 # page can be written */
	PROT_EXEC = 0x4 # page can be executed */
	PROT_SEM = 0x8 # page may be used for atomic ops */
	PROT_NONE = 0x0 # page can not be accessed */
	PROT_GROWSDOWN = 0x01000000 # mprotect flag: extend change to start of growsdown vma */
	PROT_GROWSUP = 0x02000000 # mprotect flag: extend change to end of growsup vma */

	if(proc_id == PROT_READ):
		return "PROT_READ"
	elif(proc_id == PROT_WRITE):
		return "PROT_WRITE"
	elif(proc_id == PROT_EXEC):
		return "PROT_EXEC"
	elif(proc_id == PROT_SEM):
		return "PROT_SEM"
	elif(proc_id == PROT_NONE):
		return "PROT_NONE"
	elif(proc_id == PROT_GROWSDOWN):
		return "PROT_GROWSDOWN"
	elif(proc_id == PROT_GROWSUP):
		return "PROT_GROWSUP"
	return None

def find_memory_adress(user_data, size):
	location = user_data.round_memory(user_data.last_mmap_address)
	user_data.emulator.mem_map(location, user_data.round_memory(size))

	user_data.last_mmap_address += user_data.round_memory(size)
	return location

def check_flags(flag):
	flags = {
			"MAP_FILE"      :   0,
			"MAP_SHARED"    :   1,
			"MAP_PRIVATE"   :   2,
			"MAP_TYPE"      :   0xf,
			"MAP_FIXED"     :   0x10,
			"MAP_ANONYMOUS" :   0x20,
		}
	enabled_flags = []
	for key, value in flags.items():
		if(flag & value != 0):
			enabled_flags.append(key)
	return enabled_flags




