#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "vector_array.h"

#include "memory.c"
#include "hash_table.c"
#include "vector_array.c"
#include "structmember.h"

int get_register_index_object(struct hash_table_structure *real_register_table, char *regsiter){
	int *index = vector_get_pointer(get_hash_table_value(real_register_table, regsiter), 0);
	return *index;	
}

unsigned long long *unsinged_deep_copy(unsigned long long input){
	unsigned long long*copy = malloc(sizeof(unsigned long long));
	*copy = input;	
	return copy;	
}

int *int_deepcopy(int input){
	int*copy = malloc(sizeof(int));
	*copy = input;	
	return copy;	
}

// we are a object now
static PyMethodDef methods[] = {
	{NULL, NULL, 0, NULL}        /* Sentinel */
};



static struct PyModuleDef module = {
	PyModuleDef_HEAD_INIT,
	"triforce_db",   /* name of module */
	NULL, /* module documentation, may be NULL */
	-1, /* size of per-interpreter state of the module,
		or -1 if the module keeps state in global variables. */
	methods
};


typedef struct {
	PyObject_HEAD
	struct vector_stucture_pointer *execution_time;
	struct vector_stucture_pointer *op_count;
	
	struct vector_stucture_pointer *syscall_trace;
	struct vector_stucture_pointer *memory_trace;
	struct hash_table_structure *register_table;

	int current_execution;
	int register_count;
	int values_added;
	int number;
} db_object;


static void clean_object(db_object *self) {
	//	clean the memory
	for(int i = 0; i < self->execution_time->size; i++){
		struct hash_table_structure *table = vector_get_pointer(self->execution_time, i);
		if(table != NULL){
			free_table(table);
		}

		struct vector_stucture_pointer *syscall_list = vector_get_pointer(self->syscall_trace, i);
		if(syscall_list != NULL){
			free_vector_pointer(syscall_list);
		}
	}
	free_table(self->register_table);
	free_vector_pointer(self->syscall_trace);
	free_vector_pointer(self->execution_time);
}


static PyObject *add_memory_trace(db_object *self, PyObject *args, PyObject *kwargs) {
	char *address;  // register is a keyword
	unsigned long value;
	unsigned long address_exectuion;
	int add_unique_only = 1;
	int increment_op = 1;
	static char *kwlist[] = {"address", "value", "address_exectuion", "increment_op", "add_unique_only", NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "sKK|ii", kwlist, &address, &value, &address_exectuion, &increment_op, &add_unique_only)){
		return NULL;
	}

	//	increment the op_count, that way we can easily rebuild the memory	
	int *current_op_count = vector_get_pointer(self->op_count, self->execution_time->size - 1);
	if(self->memory_trace != NULL){
		struct hash_table_structure *memory_table = vector_get_pointer(self->memory_trace, self->execution_time->size - 1);
		if(memory_table == NULL){
			printf("memory table is null...\n");
		}else{
			int add = 1;

			if(add_unique_only == 1){
				struct vector_stucture_pointer *memory_values = get_hash_table_value(memory_table, address);
				if(!(memory_values == NULL)){
					if(*latest_cell_value(memory_values) == value){
						add = 0;				
					}
				}
			}

			if(add == 1){
				struct memory *memory_cell = malloc(sizeof(struct memory));
				memory_cell->value = unsinged_deep_copy(value);
				memory_cell->op_count = int_deepcopy(*current_op_count);
				memory_cell->adress_execution = unsinged_deep_copy(address_exectuion);

				add_hash_table_value(memory_table, address, memory_cell, VALUE_MEMORY);	
				if(increment_op == 1){
					(*current_op_count)++;
				}
			}
		}
	}else{
		PyErr_SetString(PyExc_TypeError, "Something is wrong. Register table is NULL");
		return NULL;
	}
	return PyLong_FromLong(19);   
}

static PyObject *force_increment_op(db_object *self, PyObject *Py_UNUSED(ignored)){
	int *current_op_count = vector_get_pointer(self->op_count, self->execution_time->size - 1);
	(*current_op_count)++;
	Py_RETURN_NONE;
}

//	(in the future this will check all adress keys and then rebuild the entire memory at that given opcount state.)
static PyObject *rebuild_memory(db_object *self, PyObject *args, PyObject *kwargs) {
	char *address;  // register is a keyword
	int execution_count;
	int op_count;
	static char *kwlist[] = {"address", "execution_count", "op_count" , NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "sii", kwlist, &address, &execution_count, &op_count)){
		return NULL;
	}

	if(self->memory_trace != NULL){
		struct hash_table_structure *memory_table = vector_get_pointer(self->memory_trace, execution_count);
		if(memory_table == NULL){
			printf("memory_table is null....\n");
		}else{
			struct vector_stucture_pointer *memory_values = get_hash_table_value(memory_table, address);
			if(memory_values == NULL){
				PyErr_SetString(PyExc_TypeError, "Something is wrong. No memory cells.");
				return NULL;
			}


			//	the memory cell value at that given op_count state.
			unsigned long long *state_value = find_closest(memory_values, op_count, MEMORY_VALUE);
			if(state_value == NULL){
				Py_RETURN_NONE;
			}
			return PyLong_FromLong(*state_value);
		}
	}

	PyErr_SetString(PyExc_TypeError, "Something is wrong. Memory table is NULL");
	return NULL;
}

static PyObject *rebuild_memory_full(db_object *self, PyObject *args, PyObject *kwargs) {
	char *address;  // register is a keyword
	int execution_count;
	int op_count;
	int hit_count;
	static char *kwlist[] = {"address", "execution_count", "hit_count" , NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "sii", kwlist, &address, &execution_count, &hit_count)){
		return NULL;
	}

	if(self->memory_trace != NULL){
		struct hash_table_structure *memory_table = vector_get_pointer(self->memory_trace, execution_count);

		if(memory_table == NULL){
			PyErr_SetString(PyExc_TypeError, "Something is wrong. Memory table is NULL");
			return NULL;
		}

		struct vector_stucture_pointer *based_off_memory_state = get_hash_table_value(memory_table, address);
		if(based_off_memory_state == NULL){
			PyErr_SetString(PyExc_TypeError, "Did not find address, have it been added?");
			return NULL;
		}

		if(based_off_memory_state->size < hit_count || hit_count < 0){
			PyErr_SetString(PyExc_TypeError, "Hit count exceeds the actual hit count. (overflow)");
			return NULL;			
		}

		struct memory *target_cell_state = vector_get_pointer(based_off_memory_state, hit_count);
		if(target_cell_state == NULL){
			PyErr_SetString(PyExc_TypeError, "Something is wrong with the cell state.");
			return NULL;		
		}
		op_count = *target_cell_state->op_count;

		struct vector_stucture_pointer *keys = memory_table->keys;
		PyObject *results = PyDict_New();
		if(keys != NULL){
			for(int i = 0; i < keys->size; i++){
				
				struct vector_stucture_pointer *memory_values = get_hash_table_value(memory_table, vector_get_pointer(keys, i));
				if(memory_values == NULL){
					PyErr_SetString(PyExc_TypeError, "Something is wrong. No memory cells.");
					return NULL;
				}
				//	the memory cell value at that given op_count state.
				unsigned long long *state_value = find_closest(memory_values, op_count, MEMORY_VALUE);
				if(state_value == NULL){
					continue;
				}else{
//					printf("hit == %s, state value == %i\n", (char*)vector_get_pointer(keys, i), *state_value);
					PyDict_SetItem(results, PyUnicode_FromString(vector_get_pointer(keys, i)) , PyLong_FromLong(*state_value));
				}
			}
		}
		return results;
	}
	PyErr_SetString(PyExc_TypeError, "Something is wrong. Memory table is NULL");
	return NULL;
}

static PyObject *latest_memory_commit(db_object *self, PyObject *args, PyObject *kwargs) {
	char *address;  // register is a keyword
	int execution_count;
	int op_count;

	static char *kwlist[] = {"address", "execution_count", "op_count", NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "sii", kwlist, &address, &execution_count, &op_count)){
		return NULL;
	}

	if(self->memory_trace != NULL){
		struct hash_table_structure *memory_table = vector_get_pointer(self->memory_trace, execution_count);

		if(memory_table == NULL){
			PyErr_SetString(PyExc_TypeError, "Something is wrong. Memory table is NULL");
			return NULL;
		}

		struct vector_stucture_pointer *based_off_memory_state = get_hash_table_value(memory_table, address);
		if(based_off_memory_state == NULL){
			PyErr_SetString(PyExc_TypeError, "Did not find address, have it been added?");
			return NULL;
		}

		if(op_count == -1){
			int *current_op_count = vector_get_pointer(self->op_count, self->execution_time->size - 1);
			op_count = *current_op_count;
		}

//		unsigned long long *address_exectuion = latest_state_adress(based_off_memory_state);
		unsigned long long *address_exectuion = find_closest(based_off_memory_state, op_count, MEMORY_EXECUTION);
		if(address_exectuion == NULL){
			Py_RETURN_NONE;
		}else{
			return PyLong_FromLong(*address_exectuion);
		}
	}
	PyErr_SetString(PyExc_TypeError, "Something is wrong. Memory table is NULL");
	return NULL;
}


static PyObject *view_memory_commits(db_object *self, PyObject *args, PyObject *kwargs) {
	char *address;  // register is a keyword
	int execution_count;

	static char *kwlist[] = {"address", "execution_count", NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "si", kwlist, &address, &execution_count)){
		return NULL;
	}

	if(self->memory_trace != NULL){
		struct hash_table_structure *memory_table = vector_get_pointer(self->memory_trace, execution_count);

		if(memory_table == NULL){
			PyErr_SetString(PyExc_TypeError, "Something is wrong. Memory table is NULL");
			return NULL;
		}

		struct vector_stucture_pointer *based_off_memory_state = get_hash_table_value(memory_table, address);
		if(based_off_memory_state == NULL){
			PyErr_SetString(PyExc_TypeError, "Did not find address, have it been added?");
			return NULL;
		}
		pretty_print(based_off_memory_state);
		Py_RETURN_NONE;
	}
	PyErr_SetString(PyExc_TypeError, "Something is wrong. Memory table is NULL");
	return NULL;
}


static PyObject *get_memory_trace(db_object *self, PyObject *args, PyObject *kwargs) {
	char *address;  // register is a keyword
	int execution_count;
	static char *kwlist[] = {"address", "execution_count", NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "si", kwlist, &address, &execution_count)){
		return NULL;
	}


	if(self->memory_trace != NULL){
		struct hash_table_structure *memory_table = vector_get_pointer(self->memory_trace, execution_count);
		if(memory_table == NULL){
			printf("memory_table is null....\n");
		}else{
			PyObject* results = PyList_New(0);
			struct vector_stucture_pointer *memory_values = get_hash_table_value(memory_table, address);
			if(memory_values == NULL){
				return results;
			}
			for(int i = 0; i < memory_values->size; i++){
				struct memory *memory_cell = vector_get_pointer(memory_values, i);
				PyList_Append(results, PyLong_FromLong(*memory_cell->value));
			}
			return results;
		}
	}else{
		PyErr_SetString(PyExc_TypeError, "Something is wrong. Register table is NULL");
		return NULL;
	}
	return PyLong_FromLong(19);   
}


static int *init_object(db_object *self, PyObject *Py_UNUSED(ignored)){
	self->execution_time = init_vector_pointer("execution track");
	self->op_count = init_vector_pointer("op_count track");
	self->syscall_trace = init_vector_pointer("syscall track");
	self->memory_trace  = init_vector_pointer("memory track");
	self->register_table = init_table("registers");	

	struct hash_table_structure *hash_table = init_table("execution");
	vector_add_pointer(self->execution_time, hash_table);   

	vector_add_pointer(self->op_count, unsinged_deep_copy(0));

	struct hash_table_structure *memory_table = init_table("memory_table");
	vector_add_pointer(self->memory_trace, memory_table);   

	struct vector_stucture_pointer *syscall_list = init_vector_pointer("syscalls");
	vector_add_pointer(self->syscall_trace, syscall_list);    
	return 0;   
}

static PyObject *add_new_execution(db_object *self, PyObject *args){
	struct hash_table_structure *hash_table = init_table("execution");
	vector_add_pointer(self->execution_time, hash_table);    

	vector_add_pointer(self->op_count, unsinged_deep_copy(0));

	struct hash_table_structure *hash_table_memory = init_table("memory_table");
	vector_add_pointer(self->memory_trace, hash_table_memory);    

	struct vector_stucture_pointer *syscall_list = init_vector_pointer("syscalls");
	vector_add_pointer(self->syscall_trace, syscall_list);    
	
	return PyLong_FromLong(self->execution_time->size - 1);
}

static PyObject *add_register_object(db_object *self, PyObject *args, PyObject *kwargs) {
	char *register_name;  // register is a keyword
	static char *kwlist[] = {"register", NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s", kwlist, &register_name)){
		return NULL;
	}

	if(self->register_table != NULL){
		add_hash_table_value(self->register_table, register_name, unsinged_deep_copy(self->register_count), VALUE_INT);
//		vector_get_pointer(get_hash_table_value(self->register_table, register_name), 0);		
	}else{
		PyErr_SetString(PyExc_TypeError, "Something is wrong. Register table is NULL");
		return NULL;
	}
	self->register_count += 1;
	return PyLong_FromLong(19);   
}

static PyObject *get_register_count(db_object *self, PyObject *args) {
	return PyLong_FromLong(self->register_count);   
}

static PyObject *get_added_count(db_object *self, PyObject *args) {
	return PyLong_FromLong(self->values_added);   
}

static PyObject *add_register_hit_object(db_object *self, PyObject *args, PyObject *kwargs) {
	char *address;
	char *register_name; // register is a keyword

	unsigned long long value; 

	static char *kwlist[] = {"adress", "register", "value" , NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ssk", kwlist, &address, &register_name, &value)){
		return NULL;
	}


	//	deepcopy that value
	struct hash_table_structure *execution_table = vector_get_pointer(self->execution_time, self->execution_time->size - 1);
	struct vector_stucture_pointer *address_vector = add_hash_table_value(execution_table, 
																address, NULL, VALUE_VECTOR);	
	struct vector_stucture_pointer *register_value = vector_get_pointer(address_vector, 0);
	
	if(!((register_value->size % self->register_table->size) == get_register_index_object(self->register_table, register_name))){
		PyErr_SetString(PyExc_TypeError, "Need to call add_register_hit in the same order as add_register");
		return NULL;
	}
	
	vector_add_pointer(register_value, unsinged_deep_copy(value));
	self->values_added++;	
	return PyLong_FromLong(0);
}


static PyObject *get_register_hit_object(db_object *self, PyObject *args, PyObject *kwargs) {
	char *address;
	char *register_name; // register is a keyword
	int execution_count; 

	static char *kwlist[] = {"address", "register", "execution_number", NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ssi", kwlist, &address, &register_name, &execution_count)){
		return NULL;
	}

	if(execution_count < self->execution_time->size){
		struct hash_table_structure *execution_table = vector_get_pointer(self->execution_time, execution_count);


		struct vector_stucture_pointer *vector_address = get_hash_table_value(execution_table, address);			
		
		if(vector_address == NULL){
			PyObject* results = PyList_New(0);
			return results;
		//	PyErr_SetString(PyExc_TypeError, "did not find address");
		//	return NULL;			
		}

		struct vector_stucture_pointer *register_value = vector_get_pointer(vector_address, 0);
		int register_index = get_register_index_object(self->register_table,register_name);

		//	return results as a list
		PyObject* results = PyList_New(0);

		//	all values are stored in linear form, jump through all the items.
		for(int i = register_index; i < register_value->size; i+=(self->register_table->size)){
			int *value =  vector_get_pointer(register_value, i);		
			PyList_Append(results, PyLong_FromLong(*value));
		}
		return results;
	}else{
		PyErr_SetString(PyExc_TypeError, "execution_number is not valid");
		return NULL;
	}
}


/*

	strace

		seems like I can't call c with a list, so I will need to call in for each syscall
		argument.
			You can only pass a string or a number, string for name? or should I do a lookup for each name
			... maybe only index will be needed in the future.

*/

static PyObject *add_syscall_entry(db_object *self, PyObject *args, PyObject *kwargs) {
	struct vector_stucture_pointer *syscall = init_vector_pointer("singlesyscall");

	if(self->syscall_trace->size <= self->current_execution){
		PyErr_SetString(PyExc_TypeError, "Need to call add_new_execution or asking for not excecuted index");
		return NULL;
	}
	
	struct vector_stucture_pointer *execution_list = vector_get_pointer(self->syscall_trace, self->current_execution);
	vector_add_pointer(execution_list, syscall);

	return PyLong_FromLong(execution_list->size - 1);
}

static PyObject *add_syscall_argument_string(db_object *self, PyObject *args, PyObject *kwargs) {
	char *string_argument;
	int syscall_index; 

	static char *kwlist[] = {"string", "syscall_index", NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "si", kwlist, &string_argument, &syscall_index)){
		return NULL;
	}
	struct vector_stucture_pointer *execution_list = vector_get_pointer(self->syscall_trace, self->current_execution);

	struct vector_stucture_pointer *syscall_value = vector_get_pointer(execution_list, syscall_index);
	if(syscall_value == NULL){
		PyErr_SetString(PyExc_TypeError, "index is not valid");
		return NULL;
	}
	int size = 32;
	char *syscall_string_argument = (char*) malloc((size + 1)*sizeof(char));
	strncpy(syscall_string_argument, string_argument, size);

	vector_add_pointer(syscall_value, syscall_string_argument);

	return PyLong_FromLong(syscall_index);
}

static PyObject *get_syscall_from_index(db_object *self, PyObject *args, PyObject *kwargs) {
	int syscall_index; 

	static char *kwlist[] = {"syscall_index", NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "i", kwlist, &syscall_index)){
		return NULL;
	}

	struct vector_stucture_pointer *execution_list = vector_get_pointer(self->syscall_trace, self->current_execution);

	if(execution_list == NULL){
		PyErr_SetString(PyExc_TypeError, "bad execution_time");
		return NULL;
	}


	struct vector_stucture_pointer *syscall_value = vector_get_pointer(execution_list, syscall_index);

	if(syscall_value == NULL){
		PyErr_SetString(PyExc_TypeError, "bad syscall_index");
		return NULL;
	}

	PyObject* results = PyList_New(0);
	//	all values are stored in linear form, jump through all the items.
	for(int i = 0; i < syscall_value->size; i++){
		char *value =  vector_get_pointer(syscall_value, i);		
		PyList_Append(results, PyUnicode_FromString(value));
	}
	return results;
}

static PyObject *get_syscalls(db_object *self, PyObject *args, PyObject *kwargs) {
	struct vector_stucture_pointer *execution_list = vector_get_pointer(self->syscall_trace, self->current_execution);

	if(execution_list == NULL){
		PyErr_SetString(PyExc_TypeError, "bad execution_time");
		return NULL;
	}

	PyObject* results = PyList_New(0);

	for(int i = 0; i < execution_list->size; i++){
		PyObject* local_results = PyList_New(0);
		struct vector_stucture_pointer *syscall_value = vector_get_pointer(execution_list, i);

		for(int i = 0; i < syscall_value->size; i++){
			char *value =  vector_get_pointer(syscall_value, i);		
			PyList_Append(local_results, PyUnicode_FromString(value));
		}
		PyList_Append(results, local_results);
	}
	return results;
}

static PyMethodDef Custom_methods[] = {
	{"add_new_execution", (PyCFunction) add_new_execution, METH_NOARGS,	
		"add a execution to track"
	},
	{"get_added_count", (PyCFunction) get_added_count, METH_NOARGS,	
		"add a count of added entries"
	},
	{"get_register_count", (PyCFunction) get_register_count, METH_NOARGS,	
		"add a count of registers to track"
	},
	{"add_register", (PyCFunction) add_register_object, METH_VARARGS,	
		"add a register to track"
	},
	{"add_register_hit", (PyCFunction) add_register_hit_object, METH_VARARGS,
	 "add a register hit value"
	},
	{"get_register_hit", (PyCFunction) get_register_hit_object, METH_VARARGS,
	 "get the register values at a certain execution"
	},
	// strace database
	{"add_syscall_entry", (PyCFunction) add_syscall_entry, METH_NOARGS,	
		"add a new syscall entry"
	},
	{"syscall_argument_string", (PyCFunction) add_syscall_argument_string, METH_VARARGS,
		"add a argument string for syscall"
	},	
	{"get_syscall_from_index", (PyCFunction) get_syscall_from_index, METH_VARARGS,
		"get the syscall with arguments"
	},	
	{"get_syscalls", (PyCFunction) get_syscalls, METH_NOARGS,
		"get all syscalls"
	},	
	//	memory 
	{"add_memory_trace", (PyCFunction) add_memory_trace, METH_VARARGS,
		"want to keep add a memory value?"
	},		
	{"get_memory_trace", (PyCFunction) get_memory_trace, METH_VARARGS,
		"want to keep get a memory value?"
	},
	{"rebuild_memory", (PyCFunction) rebuild_memory, METH_VARARGS,
		"want to see the memory at a given state?"
	},
	{"rebuild_memory_full", (PyCFunction) rebuild_memory_full, METH_VARARGS,
		"want to see the full memory at a given state?"
	},
	{"latest_memory_commit", (PyCFunction) latest_memory_commit, METH_VARARGS,
		"what was the last instruction that comitted to a part of memory?"
	},
	{"view_memory_commits", (PyCFunction) view_memory_commits, METH_VARARGS,
		"easy to debug"
	},
	{"force_increment_op", (PyCFunction) force_increment_op, METH_NOARGS,
		"easy to debug"
	},
	{NULL}  /* Sentinel */
};


static PyMemberDef Custom_members[] = {
/*	{"number", T_INT, offsetof(db_object, number), 0,
	 "custom number"},*/
	{NULL} 
};

static PyTypeObject CustomType = {
	PyVarObject_HEAD_INIT(NULL, 0)
	.tp_name = "database object",
	.tp_doc = "None",
	.tp_basicsize = sizeof(db_object),
	.tp_itemsize = 0,
	.tp_flags = Py_TPFLAGS_DEFAULT,
	.tp_new = PyType_GenericNew,
	.tp_members = Custom_members,
	.tp_methods = Custom_methods,
	.tp_dealloc = (destructor) clean_object,
	.tp_init = (initproc) init_object,
};



PyMODINIT_FUNC PyInit_triforce_db(void){
	PyObject *m;
	if (PyType_Ready(&CustomType) < 0){
		return NULL;
	}

	m = PyModule_Create(&module);
	if(m == NULL){
		return NULL;
	}
	
	Py_INCREF(&CustomType);
	PyModule_AddObject(m, "db_init", (PyObject *) &CustomType);
	return m;
}


