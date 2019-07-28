
'''
	
'''
def get_symbol_name(elf, address):
	keys = list(elf.symbol_lookup.keys())

	if(len(keys) == 0):
		return None

	if(keys[0] == address):
		return elf.symbol_lookup[keys[0]]
	elif(keys[-1] == address):
		return elf.symbol_lookup[keys[0]]

	low = 0
	high = len(keys)
	mid = 0; 
	size = len(keys)

	def get_closest(x, y, target):
		delta1 = (target - x);
		delta2 = (y - target);

		if (delta2 <= delta1 or (x <= target and target < y)):
			return x
		else:
			return y

	while (low < high):
		#	overflow is bad!
		mid = low + (high - low ) // 2; 
		array_mid =	keys[mid]
		if (array_mid == address):
			return elf.symbol_lookup[keys[mid]]

		if (address < array_mid):
			if(0 < mid and keys[mid - 1] < address):
				return elf.symbol_lookup[get_closest(	keys[mid - 1], 
									keys[mid], 
									address)]
			high = mid; 
		else:
			if(mid < (size - 1) and address < keys[mid + 1]):
				return elf.symbol_lookup[get_closest(	keys[mid], 
									keys[mid+1], 
									address)]
			low = mid + 1;
	return elf.symbol_lookup[keys[mid]]
