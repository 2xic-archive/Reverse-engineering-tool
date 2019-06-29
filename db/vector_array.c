
#include <stdio.h> 
#include <stdlib.h> 
#include <assert.h>

struct vector_stucture *init_vector(void *key){
	struct vector_stucture *vector = malloc(sizeof(struct vector_stucture));
	vector->max_capacity = VECTOR_SIZE;
	vector->items = malloc(sizeof(int) * vector->max_capacity);
	vector->size = 0;
	vector->keyword = key;
	return vector;
}

struct vector_stucture_pointer *init_vector_pointer(void *key){
	struct vector_stucture_pointer *vector = malloc(sizeof(struct vector_stucture_pointer));
	vector->max_capacity = VECTOR_SIZE;
	vector->items = malloc(sizeof(void*) * vector->max_capacity);
	vector->size = 0;
	vector->malloc_keyword = 0; 
	vector->keyword = key;
	return vector;	
}

int vector_add(struct vector_stucture *vector, int item){
	if (vector->max_capacity == vector->size){
		vector->max_capacity *= 2;
		vector->items  = realloc(vector->items, (vector->max_capacity * sizeof(int)));
		vector->items[vector->size] = item;
		vector->size++;
	}else{
		vector->items[vector->size] = item;
		vector->size++;
	}
	return vector->size - 1;
}

void *vector_add_pointer(struct vector_stucture_pointer *vector, void*item){
	if (vector->max_capacity == vector->size){
		vector->max_capacity *= 2;
		vector->items  = realloc(vector->items, (vector->max_capacity * sizeof(void *)));
	}
	vector->items[vector->size++] = item;
	return vector->items[vector->size - 1];
}

void *vector_get_pointer(struct vector_stucture_pointer *vector, int index){
	assert(vector != NULL);
	assert(vector->items != NULL);
	if ((0 <= index) && (index < vector->size)){
		return vector->items[index];
	}
	return NULL;
}


int vector_get(struct vector_stucture *vector, int index){
	assert(vector->items != NULL);
	if ((0 <= index) && (index < vector->size)){
		return vector->items[index];
	}
	//	registers only store posetive numbersz
	return -1; 
}

void free_vector(struct vector_stucture *vector){
	assert(vector->items != NULL);
    free(vector->items);
    vector->items = NULL;
    free(vector);
    vector = NULL;
}

void free_vector_pointer(struct vector_stucture_pointer *vector){
	assert(vector->items != NULL);
    free(vector->items);
    vector->items = NULL;
    if(vector->malloc_keyword){
    	free(vector->keyword);
    	vector->keyword = NULL;
    }
    free(vector);
    vector = NULL;
}
