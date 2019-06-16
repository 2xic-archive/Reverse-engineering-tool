import triforce_db


db_object = triforce_db.db_init()

db_object.add_register("r1")
db_object.add_register("r2")
db_object.add_register("r3")

db_object.add_register_hit("0x1", "r1", 30)
db_object.add_register_hit("0x1", "r2", 50)
db_object.add_register_hit("0x1", "r3", 50)

db_object.add_register_hit("0x1", "r1", 40)
db_object.add_register_hit("0x1", "r2", 60)
db_object.add_register_hit("0x1", "r3",  0)

#db_object.add_register_hit("0x400990", "rax",  0)

results  = db_object.get_register_hit("0x1", "r1", 0)
print("r1 have had thesse values at adress 0x1 (round 0)")
print(results)
assert([30, 40] == results)

results  = db_object.get_register_hit("0x1", "r2", 0)
print("r2 have had thesse values at adress 0x1 (round 0)")
print(results)
assert([50, 60] == results)


db_object.add_new_execution()

db_object.add_register_hit("0x1", "r1", 40)
db_object.add_register_hit("0x1", "r2", 60)
db_object.add_register_hit("0x1", "r3",  0)

results  = db_object.get_register_hit("0x1", "r2", 1)
print("r2 have had thesse values at adress 0x1 (round 1)")
print(results)
assert([60] == results)


new_syscall = db_object.add_syscall_entry()
print(new_syscall)

db_object.syscall_argument_string("test_syscall_3", new_syscall)
db_object.syscall_argument_string("test_syscall_4", new_syscall)

#print(db_object.get_syscall_from_index(new_syscall))
assert(db_object.get_syscall_from_index(new_syscall) == ["test_syscall_3", "test_syscall_4"])

new_syscall_2 = db_object.add_syscall_entry()

db_object.syscall_argument_string("test_syscall_1", new_syscall_2)
db_object.syscall_argument_string("test_syscall_2", new_syscall_2)

assert(db_object.get_syscall_from_index(new_syscall_2) == ["test_syscall_1", "test_syscall_2"])

assert(db_object.get_syscalls() == [['test_syscall_3', 'test_syscall_4'], ['test_syscall_1', 'test_syscall_2']])

