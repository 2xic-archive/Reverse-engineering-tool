

CC=gcc

vector: vector_array.c
	@echo "making vector"
	$(CC) -g -Wall -D DEBUG -o test_bin/vector vector_array.c

hash: hash_table.c
	@echo "making hash_table"
	$(CC) -g -Wall -std=c11 -Wall -ggdb3 -D DEBUG -o test_bin/hash_table hash_table.c

test: hash_table.c
	@echo "making tests"
	$(CC) -g -Wall -std=c11 -Wall -ggdb3 -D DEBUG -o test_bin/hash_table hash_table.c
	./test_bin/hash_table
	python3 setup.py install
	python3 test.py

test_leak_hash:
	make hash
	valgrind --leak-check=full \
			--show-leak-kinds=all \
			--track-origins=yes \
			--verbose \
			--log-file=valgrind-out.txt \
			./test_bin/hash_table 
test_leak_script:
	PYTHONMALLOC=debug valgrind --tool=memcheck --suppressions=valgrind-python.supp \
		python3 -tt test.py -u bsddb,network

all:
	make vector
	make hash