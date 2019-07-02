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

db_object.add_memory_trace("0x4101", 1128, 0x0)
db_object.add_memory_trace("0x4101", 1256, 0x44)

assert(db_object.rebuild_memory("0x4101", 0, -1) == None)
assert(db_object.rebuild_memory("0x4101", 0, 0) == 1128)
assert(db_object.rebuild_memory("0x4101", 0, 1) == 1256)
assert((db_object.latest_memory_commit("0x4101", 0, 1) == 0x44))
assert(db_object.get_memory_trace("0x4101", 0) == [1128, 1256])

db_object.add_memory_trace("0x4101", 414141, 0x0)

assert(db_object.rebuild_memory("0x4101", 0, 0) == 1128)
assert(db_object.rebuild_memory("0x4101", 0, 1) == 1256)
assert(db_object.rebuild_memory("0x4101", 0, 2) == 414141)

db_object.add_memory_trace("0x4101", 0xbeef, 0x0)

assert(db_object.rebuild_memory("0x4101", 0, 0) == 1128)
assert(db_object.rebuild_memory("0x4101", 0, 1) == 1256)
assert(db_object.rebuild_memory("0x4101", 0, 2) == 414141)
assert(db_object.rebuild_memory("0x4101", 0, 3) == 0xbeef)

db_object.add_memory_trace("0x4104", 1, 0x0)
db_object.add_memory_trace("0x4104", 2, 0x0)
db_object.add_memory_trace("0x4105", 3, 0x0)
db_object.add_memory_trace("0x4105", 4, 0x0)
db_object.add_memory_trace("0x4104", 5, 0x0)


assert(db_object.rebuild_memory("0x4104", 0, 4) == 1)
assert(db_object.rebuild_memory("0x4104", 0, 5) == 2)
assert(db_object.rebuild_memory("0x4104", 0, 8) == 5)

assert(db_object.rebuild_memory("0x4105", 0, 6) == 3)
assert(db_object.rebuild_memory("0x4105", 0, 7) == 4)

# input is the hint of the state id!
target = {'0x4105': 3, '0x4104':2, '0x4101': 48879}
results = db_object.rebuild_memory_full("0x4105", 0, 0)

assert(len(target.keys()) == len(results.keys()))
assert(list(sorted(list(target.keys()))) == list(sorted(list(results.keys()))))
assert(list(sorted(list(target.values()))) == list(sorted(list(results.values()))))

#print(db_object.rebuild_memory_full("0x4105", 0, 0))


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

db_object.add_memory_trace("0x4100", 128, 0)
db_object.add_memory_trace("0x4100", 256, 0)

assert(db_object.get_memory_trace("0x4100", 1) == [128, 256])

db_object.add_memory_trace("0x4101", 1128, 0)
db_object.add_memory_trace("0x4101", 1256, 0)

assert(db_object.get_memory_trace("0x4101", 1) == [1128, 1256])

assert(db_object.get_memory_trace("0x41012", 1) == [])


db_object.add_memory_trace("0x4101", 1256, 0)


