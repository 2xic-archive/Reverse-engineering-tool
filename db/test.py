import triforce_db

triforce_db.add_register("r1")
triforce_db.add_register("r2")
triforce_db.add_register("r3")

triforce_db.add_register_hit("0x1", "r1", 30)
triforce_db.add_register_hit("0x1", "r2", 50)
triforce_db.add_register_hit("0x1", "r3", 50)


triforce_db.add_register_hit("0x1", "r1", 40)
triforce_db.add_register_hit("0x1", "r2", 60)
triforce_db.add_register_hit("0x1", "r3",  0)


results  = triforce_db.get_register_hit("0x1", "r1", 0)
print("r1 have had thesse values at adress 0x1 (round 0)")
print(results)
assert([30, 40] == results)


results  = triforce_db.get_register_hit("0x1", "r2", 0)
print("r2 have had thesse values at adress 0x1 (round 0)")
print(results)
assert([50, 60] == results)

triforce_db.add_new_execution()

triforce_db.add_register_hit("0x1", "r1", 40)
triforce_db.add_register_hit("0x1", "r2", 60)
triforce_db.add_register_hit("0x1", "r3",  0)

results  = triforce_db.get_register_hit("0x1", "r2", 1)
print("r2 have had thesse values at adress 0x1 (round 1)")
print(results)
assert([60] == results)




