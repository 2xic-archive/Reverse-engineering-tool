#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdio.h>

#ifdef DEBUG
	#include "vector_array.h"
	#include "vector_array.c"
	
	void test_bad_hash_function(void);

	int main(int argc, char *argv[]){
		test_bad_hash_function();
	}
#endif


#define TABLE_SIZE 1024

struct hashtable_item_pointer{
	char *key;
	int type;
	struct vector_stucture_pointer *value;
};

struct hash_table_structure {
	char *keyword;
	void **items;
	struct vector_stucture *keys;
	int max_capacity;
	int size;
};


#ifdef DEBUG
	//	use bad hash function to get collisions!
	int hash_function(const char* str){
		return 4;
	}
#else
	int hash_function(const char* str){
		unsigned long hash = 5381;
		int c;
		while ((c = *str++)){
			hash = ((hash << 5) + hash) + c;
		}
		//	256 should be safe for registers
		//	should be higher for the address space
		return hash % 256;
	}
#endif


struct hash_table_structure *init_table(char *keyword){
	struct hash_table_structure *hash_table = malloc(sizeof(struct hash_table_structure));
	hash_table->max_capacity = TABLE_SIZE;

	hash_table->items = malloc(sizeof(void *) * hash_table->max_capacity);
	memset(hash_table->items, 0, sizeof(void *) * hash_table->max_capacity);

	hash_table->size = 0;
	hash_table->keyword = keyword;
	
	return hash_table;
}

void *add_hash_table_value(struct hash_table_structure *hash_table, char *keyword, void *value, int type){
	int index = hash_function(keyword);

	if(hash_table->max_capacity < index){
		printf("neeed to resize\n");
		exit(0);
	}

	struct vector_stucture_pointer *value_vector = NULL;
	if(hash_table->items[index] == NULL){

		struct hashtable_item_pointer *hash_table_entry = malloc(sizeof(struct hashtable_item_pointer));
		hash_table_entry->key = "base";
		hash_table_entry->value =  init_vector_pointer("collisions");
		hash_table_entry->type = type;
		hash_table->items[index] = hash_table_entry;

		hash_table_entry->value->type = 0;

		if(type == VALUE_INT){
			value_vector = vector_add_pointer(hash_table_entry->value, init_vector_pointer(keyword));
			vector_add_pointer(value_vector, value);
		}else if(type == VALUE_VECTOR){
			hash_table_entry->value->type = 2;
			value_vector = vector_add_pointer(hash_table_entry->value, init_vector_pointer(keyword));
			vector_add_pointer(value_vector, init_vector_pointer(value));
		}
	}else{
		struct hashtable_item_pointer *address = hash_table->items[index];
		struct vector_stucture_pointer *vector_table = address->value;

		struct vector_stucture_pointer *found_entry = NULL;

		for(int i = 0; i < vector_table->size; i++){
			struct vector_stucture_pointer *entry = vector_get_pointer(vector_table, i);
			if(strcmp(entry->keyword, keyword) == 0){
				found_entry = entry;
				break;
			}
		}
		if(found_entry == NULL){
			if(type == VALUE_INT){
				value_vector = vector_add_pointer(address->value, init_vector_pointer(keyword));
				vector_add_pointer(value_vector, value);
			}else if(type == VALUE_VECTOR){
				value_vector = vector_add_pointer(address->value, init_vector_pointer(keyword));
				vector_add_pointer(value_vector, init_vector_pointer(value));
			}
		}else{
			value_vector = found_entry;
			if(type == VALUE_INT){
				vector_add_pointer(found_entry, value);				
			}else if(type == VALUE_VECTOR){
				vector_add_pointer(found_entry, init_vector_pointer(value));
			}		
		}
	}
	hash_table->size += 1;
	return value_vector;
}


void *get_hash_table_value(struct hash_table_structure *hash_table, char*keyword){
	int index = hash_function(keyword);

	if(hash_table->max_capacity < index){
		return NULL;
	}

	if(hash_table->items[index] != NULL){
		struct hashtable_item_pointer *address = hash_table->items[index];
		struct vector_stucture_pointer *vector_table = address->value;

		struct vector_stucture_pointer *found_key = NULL;
	
		for(int i = 0; i < vector_table->size; i++){
			struct vector_stucture_pointer *vec = vector_get_pointer(address->value, i);
			if(strcmp(vec->keyword, keyword) == 0){
				found_key = vec;
				break;
			}
		}
		return found_key;
	}
	return NULL;
}


int free_table(struct hash_table_structure *hash_table){
	for(int i = 0; i < hash_table->max_capacity; i++){
		if(hash_table->items[i] != NULL){
			struct hashtable_item_pointer *address = hash_table->items[i];	
			struct vector_stucture_pointer *vector_table = address->value;

			for(int collision_index = 0; collision_index < vector_table->size; collision_index++){
				struct vector_stucture_pointer *collisions = vector_get_pointer(vector_table, collision_index);	
				if(vector_table->type == 2){
					for(int element_index = 0; element_index < collisions->size; element_index++){
						struct vector_stucture_pointer *values = vector_get_pointer(collisions, element_index);
						free_vector_pointer(values);
					}
				}
				free_vector_pointer(collisions);
			}
			free_vector_pointer(vector_table);
			free(address);
		}
	}
	free(hash_table->items);
	free(hash_table);
	return 0;
}



void test_bad_hash_function(void){
	struct hash_table_structure *address_table = init_table("address");	

	struct vector_stucture_pointer *value_list;
	struct vector_stucture_pointer *actual_value;

	struct vector_stucture_pointer *found_value_list;

	int a = 40;
	int b = 90;

	value_list = add_hash_table_value(address_table, "0x1", NULL, VALUE_VECTOR);
	actual_value = vector_get_pointer(value_list, 0);

	vector_add_pointer(actual_value, &a);

	found_value_list = get_hash_table_value(address_table, "0x1");			
	actual_value = vector_get_pointer(found_value_list, 0);

	assert(strcmp(found_value_list->keyword, "0x1") == 0);

	int *value = vector_get_pointer(actual_value, 0);
	assert(*value == 40);

	value_list = add_hash_table_value(address_table, "0x2", NULL, VALUE_VECTOR);
	actual_value = vector_get_pointer(value_list, 0);

	vector_add_pointer(actual_value, &b);

	found_value_list = get_hash_table_value(address_table, "0x2");			

	assert(found_value_list != NULL);
	assert(strcmp(found_value_list->keyword, "0x2") == 0);

	actual_value = vector_get_pointer(found_value_list, 0);

	value = vector_get_pointer(actual_value, 0);
	assert(*value == 90);

	free_table(address_table);

}




