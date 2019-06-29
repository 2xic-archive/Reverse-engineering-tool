#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject *run_cpuid(PyObject *self, PyObject *args) {
	int function;
	int count;

	if (!PyArg_ParseTuple(args, "ii", &function, &count)){
		return NULL;
	}

	uint32_t vec[4];
	asm volatile("cpuid"
                 : "=a"(vec[0]), "=b"(vec[1]),
                   "=c"(vec[2]), "=d"(vec[3])
                 : "0"(function), "c"(count) : "cc");
	
	// resolve the rest on the python side.
	PyObject* results = PyList_New(0);
	for(int i = 0; i < 4; i++){
		uint32_t value = vec[i];		
		PyList_Append(results, PyLong_FromLong(value));
	}
	return results;
}


static PyMethodDef methods[] = {
	{"run_cpuid",  run_cpuid, METH_VARARGS,
	 "run cpuid from python"},
	{NULL, NULL, 0, NULL}        /* Sentinel */
};



static struct PyModuleDef module = {
	PyModuleDef_HEAD_INIT,
	"triforce_extender",   /* name of module */
	NULL, /* module documentation, may be NULL */
	-1, /* size of per-interpreter state of the module,
		or -1 if the module keeps state in global variables. */
	methods
};


PyMODINIT_FUNC PyInit_triforce_extender(void){
	PyObject *m;

	m = PyModule_Create(&module);
	if(m == NULL){
		return NULL;
	}	
	return m;
}

