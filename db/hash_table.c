#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdio.h>

#define TABLE_SIZE 4

/*
	only the structure foundation
		-	will code the rest later.
*/

typedef struct hashtable_item{
	int i;
} hashtable_item;

typedef struct hash_table_structure {
	void **items;
	int max_capacity;
	int size;
} hash_table_structure;

void table_item(hashtable_item *item){
	item->i = 10;
}

void init_table(hash_table_structure *hash_table){
	hash_table->max_capacity = TABLE_SIZE;
	hash_table->items = malloc(sizeof(void *) * hash_table->max_capacity);
	hash_table->size = 0;
}

int hash_function(){
	/*
		comming
	*/
	return 4;
}

void add_item(hash_table_structure *hash_table, hashtable_item *table_item){
	//assert(hashtable_item->items != NULL);
	int index = hash_function();
	hash_table->items[index] = table_item;
}

//	we do want key -> value
hashtable_item *get_item(hash_table_structure * hash_table, char *key){
	int index = hash_function();
	return hash_table->items[index];
}


int main(){
	hash_table_structure hash_table;
	init_table(&hash_table);

	hashtable_item item;
	table_item(&item);

	add_item(&hash_table, &item);

	hashtable_item *test = get_item(&hash_table, "");
	printf("%i\n", test->i);
}




