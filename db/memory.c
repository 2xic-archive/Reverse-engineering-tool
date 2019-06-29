

#include <stdio.h> 
#include <stdlib.h> 
#include <assert.h>


struct memory{
	int *value;
	int *op_count;
};



/*
	since all memory cells are added in the correct order, we can use some binary search magic 
	to find the latest memory cell coresponding to a state.

		-	you can lookup a state by getting all memory hits at address and then reading off the cell 
			op_count!

*/

int get_op_count(struct memory*cell){
	return *cell->op_count;
}

int *get_cell_value(struct memory *cell){
	return cell->value;
}

int get_cell_direct_value(struct memory *cell){
	return *cell->value;
}


int *get_closest(struct memory *cell_1, struct memory *cell_2, int target){
	int op_count_1 = get_op_count(cell_1);
	int op_count_2 = get_op_count(cell_2);

	int delta1 = (target - op_count_1);
	int delta2 = (op_count_2 - target);

	if (delta2 <= delta1){
		return get_cell_value(cell_1); 
	}else{
		return get_cell_value(cell_2); 
	}
} 


int *findClosest(struct vector_stucture_pointer *array, int target) { 
	// O(1) !!!!
	int n = array->size;

	int array_min = get_op_count(vector_get_pointer(array, 0));

	if (target < array_min){
		return NULL;
	}

	if (target == array_min){
		return get_cell_value(vector_get_pointer(array, 0));
	}
	
	int array_max = get_op_count(vector_get_pointer(array, n-1));
	if(array_max <= target){
		return get_cell_value(vector_get_pointer(array, n-1));
	}

	int low = 0, high = n, mid = 0; 
	while (low < high) { 
		//	overflow is bad!
		mid = low + (high - low ) / 2; 
		
		int array_mid = get_op_count(vector_get_pointer(array, mid));
		if (array_mid == target) {
			return get_cell_value(vector_get_pointer(array, mid));
		}

		if (target < array_mid) { 
			if(0 < mid && get_op_count(vector_get_pointer(array, mid - 1)) < target) {
				return get_closest(	vector_get_pointer(array, mid - 1), 
									vector_get_pointer(array, mid), 
									target); 
			}
			high = mid; 
		}else {
			if(mid < (n - 1) && target < get_op_count(vector_get_pointer(array, mid + 1))) {
				return get_closest(	vector_get_pointer(array, mid ), 
									vector_get_pointer(array, mid+1), 
									target); 
			}
			low = mid + 1;
		}
	}
	return get_cell_value(vector_get_pointer(array, mid));
}