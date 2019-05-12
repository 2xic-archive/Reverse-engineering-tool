#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "vector_array.h"

#include "hash_table.c"
#include "vector_array.c"


struct vector_stucture_pointer *execution_time;
int current_execution = 0;

struct hash_table_structure *register_table = NULL;
int register_count = 0;

int init(void){
	execution_time = init_vector_pointer("execution track");
	register_table = init_table("registers");	
	
	struct hash_table_structure *hash_table = init_table("execution");
	vector_add_pointer(execution_time, hash_table);  
	return 0;  	
}

static PyObject *add_new_execution(PyObject *self, PyObject *args){
	struct hash_table_structure *hash_table = init_table("execution");
	vector_add_pointer(execution_time, hash_table);    
	return PyLong_FromLong(execution_time->size - 1);
}

int get_register_index(char *regsiter){
	int *lega = vector_get_pointer(get_hash_table_value(register_table, regsiter), 0);
	return *lega;	
}

long *int_deepcopy(long input){
	long *copy = malloc(sizeof(long));
	*copy = input;	
	return copy;	
}

PyObject *add_register_track(PyObject *self, PyObject *args, PyObject *kwargs) {
	char *register_;  // register is a keyword
	static char *kwlist[] = {"register", NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s", kwlist, &register_)){
		return NULL;
	}

	if(register_table != NULL){
		add_hash_table_value(register_table, register_, int_deepcopy(register_count), VALUE_INT);
		vector_get_pointer(get_hash_table_value(register_table, register_), 0);		
	}else{
		PyErr_SetString(PyExc_TypeError, "Something is wrong. Register table is NULL");
		return NULL;
	}
	register_count += 1;
	return PyLong_FromLong(19);
}


PyObject *get_register_hit_python(PyObject *self, PyObject *args, PyObject *kwargs) {
	char *address;
	char *register_; // register is a keyword
	int execution_count; 

	static char *kwlist[] = {"address", "register", "execution_number", NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ssi", kwlist, &address, &register_, &execution_count)){
		return NULL;
	}

	if(execution_count < execution_time->size){
		struct hash_table_structure *execution_table = vector_get_pointer(execution_time, execution_count);
		struct vector_stucture_pointer *vector_address = get_hash_table_value(execution_table, address);			
		struct vector_stucture_pointer *register_value = vector_get_pointer(vector_address, 0);

		int register_index = get_register_index(register_);

		//	return results as a list
		PyObject* results = PyList_New(0);

		//	all values are stored in linear form, jump through all the items.
		for(int i = register_index; i < register_value->size; i+=(register_table->size)){
			int *value =  vector_get_pointer(register_value, i);		
			PyList_Append(results, PyLong_FromLong(*value));
		}
		return results;
	}else{
		PyErr_SetString(PyExc_TypeError, "execution_number is not valid");
		return NULL;
	}
}


PyObject *add_register_hit_python(PyObject *self, PyObject *args, PyObject *kwargs) {
	char *address;
	char *register_; // register is a keyword

	long value; 

	static char *kwlist[] = {"adress", "register", "value" , NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ssl", kwlist, &address, &register_, &value)){
		return NULL;
	}

	//	deepcopy that value
	struct hash_table_structure *execution_table = vector_get_pointer(execution_time, execution_time->size - 1);
	struct vector_stucture_pointer *address_vector = add_hash_table_value(execution_table, 
																address, NULL, VALUE_VECTOR);	

	struct vector_stucture_pointer *register_value = vector_get_pointer(address_vector, 0);
	if(!((register_value->size % register_table->size) == get_register_index(register_))){
		PyErr_SetString(PyExc_TypeError, "Need to call add_register_hit in the same order as add_register");
	}
	vector_add_pointer(register_value, int_deepcopy(value));
	return PyLong_FromLong(0);
}

static PyMethodDef methods[] = {
	{"add_new_execution",  add_new_execution, METH_NOARGS,
	 "start with a fresh table"},
	 {"add_register", (PyCFunction)add_register_track, METH_VARARGS,
	  "add a register to track"},
	{"add_register_hit",  (PyCFunction)add_register_hit_python, METH_VARARGS,
	 "add a register hit value"},
	 {"get_register_hit",  (PyCFunction)get_register_hit_python, METH_VARARGS,
	 "get the register values at a certain execution"},
	{NULL, NULL, 0, NULL}        /* Sentinel */
};


static void clean(void) {
	//	clean the memory
	for(int i = 0; i < execution_time->size; i++){
		struct hash_table_structure *table = vector_get_pointer(execution_time, i);
		free_table(table);
	}
	free_table(register_table);
}

static struct PyModuleDef module = {
	PyModuleDef_HEAD_INIT,
	"triforce_db",   /* name of module */
	NULL, /* module documentation, may be NULL */
	-1, /* size of per-interpreter state of the module,
		or -1 if the module keeps state in global variables. */
	methods
};


PyMODINIT_FUNC PyInit_triforce_db(void){
	init();
	if (Py_AtExit(clean)) {
		return NULL;
	}
	return PyModule_Create(&module);
}

