#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "vector_array.h"

#include "hash_table.c"
#include "vector_array.c"
#include "structmember.h"


int get_register_index_object(struct hash_table_structure *real_register_table, char *regsiter){
	int *index = vector_get_pointer(get_hash_table_value(real_register_table, regsiter), 0);
	return *index;	
}

unsigned long long *int_deepcopy(unsigned long long input){
	unsigned long long*copy = malloc(sizeof(unsigned long long));
	*copy = input;	
	return copy;	
}


static PyMethodDef methods[] = {
/*	{"add_new_execution",  add_new_execution, METH_NOARGS,
	 "start with a fresh table"},
	 {"add_register", (PyCFunction)add_register_track, METH_VARARGS,
	  "add a register to track"},
	{"add_register_hit",  (PyCFunction)add_register_hit_python, METH_VARARGS,
	 "add a register hit value"},
	 {"get_register_hit",  (PyCFunction)get_register_hit_python, METH_VARARGS,
	 "get the register values at a certain execution"},*/
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
	struct vector_stucture_pointer *syscall_trace; // will add this soon.
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

static int *init_object(db_object *self, PyObject *Py_UNUSED(ignored)){
	self->execution_time = init_vector_pointer("execution track");
	self->syscall_trace = init_vector_pointer("syscall track");
	self->register_table = init_table("registers");	
	
	struct hash_table_structure *hash_table = init_table("execution");
	vector_add_pointer(self->execution_time, hash_table);   
	return 0;   
}

static PyObject *add_new_execution(db_object *self, PyObject *args){
	struct hash_table_structure *hash_table = init_table("execution");
	vector_add_pointer(self->execution_time, hash_table);    

	struct vector_stucture_pointer *syscall_list = init_vector_pointer("syscalls");
	vector_add_pointer(self->syscall_trace, syscall_list);    
	
	return PyLong_FromLong(self->execution_time->size - 1);
}

static PyObject *add_register_object(db_object *self, PyObject *args, PyObject *kwargs) {
	char *register_;  // register is a keyword
	static char *kwlist[] = {"register", NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s", kwlist, &register_)){
		return NULL;
	}

	if(self->register_table != NULL){
		add_hash_table_value(self->register_table, register_, int_deepcopy(self->register_count), VALUE_INT);
		vector_get_pointer(get_hash_table_value(self->register_table, register_), 0);		
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
	char *register_; // register is a keyword

	unsigned long long value; 

	static char *kwlist[] = {"adress", "register", "value" , NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ssk", kwlist, &address, &register_, &value)){
		return NULL;
	}


	//	deepcopy that value
	struct hash_table_structure *execution_table = vector_get_pointer(self->execution_time, self->execution_time->size - 1);
	struct vector_stucture_pointer *address_vector = add_hash_table_value(execution_table, 
																address, NULL, VALUE_VECTOR);	
	struct vector_stucture_pointer *register_value = vector_get_pointer(address_vector, 0);
	
	if(!((register_value->size % self->register_table->size) == get_register_index_object(self->register_table, register_))){
		PyErr_SetString(PyExc_TypeError, "Need to call add_register_hit in the same order as add_register");
		return NULL;
	}
	
	vector_add_pointer(register_value, int_deepcopy(value));
	self->values_added++;	
	return PyLong_FromLong(0);
}


static PyObject *get_register_hit_object(db_object *self, PyObject *args, PyObject *kwargs) {
	char *address;
	char *register_; // register is a keyword
	int execution_count; 

	static char *kwlist[] = {"address", "register", "execution_number", NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ssi", kwlist, &address, &register_, &execution_count)){
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
		int register_index = get_register_index_object(self->register_table,register_);

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
//	init();

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
	/*
	if (Py_AtExit(clean)) {
		return NULL;
	}*/
	return m;
}

