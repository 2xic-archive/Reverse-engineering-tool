#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject *error;

static PyObject *hello(PyObject *self, PyObject *args){
	printf("Hello from C \n");
	return PyLong_FromLong(1);
}

static PyMethodDef methods[] = {
	{"hello",  hello, METH_VARARGS,
	 "just a test"},
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


PyMODINIT_FUNC PyInit_triforce_db(void){
	return PyModule_Create(&module);
}

int main(int argc, char *argv[]){
	wchar_t *program = Py_DecodeLocale(argv[0], NULL);
	if (program == NULL) {
		fprintf(stderr, "Fatal error: cannot decode argv[0]\n");
		exit(1);
	}
	/* Add a built-in module, before Py_Initialize */
	PyImport_AppendInittab("triforce_db", PyInit_triforce_db);

	/* Pass argv[0] to the Python interpreter */
	Py_SetProgramName(program);

	/* Initialize the Python interpreter.  Required. */
	Py_Initialize();

	PyImport_ImportModule("triforce_db");

	PyMem_RawFree(program);
	return 0;
}




