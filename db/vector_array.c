
#include <stdio.h> 
#include <stdlib.h> 
#include <assert.h>

#define VECTOR_SIZE 12

typedef struct vector_stucture {
	void **items;
	int max_capacity;
	int size;
} vector_stucture;

void init_vector(vector_stucture *vector){
	vector->max_capacity = VECTOR_SIZE;
	vector->items = malloc(sizeof(void *) * vector->max_capacity);
	vector->size = 0;
}

int vector_add(vector_stucture *vector, void *item){
	assert(vector->items != NULL);
	if (vector->max_capacity == vector->size){
		return -1;
	}
	vector->items[vector->size++] = item;
	return vector->size - 1;
}

void *vector_get(vector_stucture *vector, int index){
	assert(vector->items != NULL);
	if ((0 <= index) && (index < vector->size)){
		return vector->items[index];
	}
	return NULL;
}

void free_vector(vector_stucture *vector){
	assert(vector->items != NULL);
    free(vector->items);
    vector->items = NULL;
}

int main() { 
	vector_stucture test_vector;
	init_vector(&test_vector);

	int index = vector_add(&test_vector, "Test");
	printf("Hello\n");
	printf("%s\n", vector_get(&test_vector, index));
	free_vector(&test_vector);
}

