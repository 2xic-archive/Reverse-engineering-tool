# DB

Need a database for all the registers and access patterns, extending python with c is something I wanted to try. 

The database is bascially a key value storage, what the cool kids call a hash table. Using some clever techniques to not have to store all the memory for each state. The register design will be changed in the future to use the memory design, saves a lot of memory this way(or maybe I will add as an option, O(1) access with O(n) memory or O(log(n)) access with a lot less memory usage (only new memory cell for each edit))!

# Regarding Valgrind
There might be some memory leaks lurking somewhere. Haven't gotten [valgrind working for python](https://github.com/python/cpython/blob/master/Misc/README.valgrind) yet. Valgrind will say there are problems even when passed an empty script, so I can't actually run the test script to debug.

# What do we want to store?
-	Register values
	-	at different points in time/at different runs
		-	you should be able to see the difference between all the registers at diffrent runs
		- 	A dynamic array can point to each run, and each run can be stored as a hashtable.
			(want that o(1) lookup when checking for a specific addresses)

		-	this is basically what the current db has to offer.

-	Memory layout ? 
	-	Unicorn report changes to memory layout
		-	Look up a value at a state with a binary search. 
