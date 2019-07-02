
#include <stdio.h> 
#include <stdlib.h> 
#include <assert.h>


struct memory{
	unsigned long long *value;
	int *op_count;
	unsigned long long *adress_execution;
};

#define MEMORY_VALUE 0
#define MEMORY_EXECUTION 1

#define DEBUG_MEMORY 0

/*
	since all memory cells are added in the correct order, we can use some binary search magic 
	to find the latest memory cell coresponding to a state.

		-	you can lookup a state by getting all memory hits at address and then reading off the cell 
			op_count!
		-	and even find out where that memory was changed by looking at the adress_execution

*/

int get_op_count(struct memory*cell){
	return *cell->op_count;
}

unsigned long long *get_cell_address(struct memory *cell){
	return cell->adress_execution;
}

unsigned long long *get_cell_value(struct memory *cell){
	return cell->value;
}

unsigned long long get_cell_direct_value(struct memory *cell){
	return *cell->value;
}

unsigned long long *latest_cell_value(struct vector_stucture_pointer *array){
	struct memory * cell = vector_get_pointer(array, array->size - 1);
	return cell->value;
}

unsigned long long *get_cell_type_value(struct memory *cell, int type){
	if(type == MEMORY_VALUE){
		return get_cell_value(cell);
	}else if(type == MEMORY_EXECUTION){
		return get_cell_address(cell);
	}else{
		return NULL;
	}
}

unsigned long long *get_closest(struct memory *cell_1, struct memory *cell_2, int target, int type){
	int op_count_1 = get_op_count(cell_1);
	int op_count_2 = get_op_count(cell_2);

	int delta1 = (target - op_count_1);
	int delta2 = (op_count_2 - target);

	if (delta2 <= delta1 || (get_op_count(cell_1) <= target && target < get_op_count(cell_2))){
		if(DEBUG_MEMORY){
			printf("Selected with op_count 1: %i\n", get_op_count(cell_1));
		}
		return get_cell_type_value(cell_1, type); 
	}else{
		if(DEBUG_MEMORY){
			printf("Selected with op_count 2: %i\n", get_op_count(cell_2));
		}
		return get_cell_type_value(cell_2, type); 
	}
} 

void pretty_print(struct vector_stucture_pointer *array){
	for(int i = 0; i < array->size; i++){
		struct memory *cell = vector_get_pointer(array, i);
		printf("0x%llx == %llu [%i]\n",  *get_cell_address(cell), get_cell_direct_value(cell), *cell->op_count);
	}
}

unsigned long long *find_closest(struct vector_stucture_pointer *array, int target, int type) { 
	// O(1) !!!!
	if(DEBUG_MEMORY){
		printf("Target op_count == %i\n", target);
	}

	int size = array->size;

	int array_min = get_op_count(vector_get_pointer(array, 0));

	if (target < array_min){
		return NULL;
	}

	if (target == array_min){
		return get_cell_type_value(vector_get_pointer(array, 0), type);
	}
	
	int array_max = get_op_count(vector_get_pointer(array, size-1));
	if(array_max <= target){
		return get_cell_type_value(vector_get_pointer(array, size-1), type);
	}

	int low = 0, high = size, mid = 0; 
	while (low < high) { 
		//	overflow is bad!
		mid = low + (high - low ) / 2; 
		
		int array_mid = get_op_count(vector_get_pointer(array, mid));
		if (array_mid == target) {
			return get_cell_type_value(vector_get_pointer(array, mid), type);
		}

		if (target < array_mid) { 
			if(0 < mid && get_op_count(vector_get_pointer(array, mid - 1)) < target) {
				return get_closest(	vector_get_pointer(array, mid - 1), 
									vector_get_pointer(array, mid), 
									target,
									type); 
			}
			high = mid; 
		}else {
			if(mid < (size - 1) && target < get_op_count(vector_get_pointer(array, mid + 1))) {
				return get_closest(	vector_get_pointer(array, mid ), 
									vector_get_pointer(array, mid+1), 
									target,
									type); 
			}
			low = mid + 1;
		}
	}
	return get_cell_type_value(vector_get_pointer(array, mid), type);
}