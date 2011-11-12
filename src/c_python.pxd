# -*- Mode: Python -*-  Not really, but close enough

# Expose as much of the Python C API as we need here

cdef extern from "stdlib.h":
    ctypedef int size_t

cdef extern from "Python.h":
    ctypedef int Py_intptr_t
    void*  PyMem_Malloc(size_t)
    void*  PyMem_Realloc(void *p, size_t n)
    void   PyMem_Free(void *p)
    char*  PyString_AsString(object string)
    object PyString_FromString(char *v)
    object PyString_InternFromString(char *v)
    int    PyErr_CheckSignals()
    object PyFloat_FromDouble(double v)
    void   Py_XINCREF(object o)
    void   Py_XDECREF(object o)
    void   Py_CLEAR(object o) # use instead of decref
    void*  PyCObject_AsVoidPtr(object o)
    object PyObject_GetAttrString(object o, char *v)

    ctypedef struct PyListObject:
        void *ob_item
    
    void * PyList_GET_ITEM(PyListObject *o, int i)
    int    PyList_GET_SIZE(PyListObject *o)

    int    PySequence_Check(object o)
    object PySequence_GetItem(object o, int i)
    int    PySequence_Length(object o)
