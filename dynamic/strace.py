


class strace(object):
	def __init__(self):
		pass

	def get_all_syscalls(self):
		for syscall in self.db.get_syscalls():
			name = syscall[0]
			args = ", ".join(syscall[1:])
			print('{}({})'.format(name, args))

	def add_syscall(self, name_with_arguments):
		new_syscall = self.db.add_syscall_entry()
		for syscall_entry_element in name_with_arguments:
			self.db.syscall_argument_string(str(syscall_entry_element), new_syscall)