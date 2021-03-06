
#ifndef INTEGERMODULE_H
#define INTEGERMODULE_H

#include <Python.h>
#include <stdio.h>
#include <string.h>
#include <structmember.h>
#include <longintrepr.h>				/* for conversions */
#include <math.h>
#include <string.h>
#include <gmp.h>
#include "sha1.h"
#include "benchmarkmodule.h"
#include "base64.h"
/* used to initialize the RNG */
#include "openssl/objects.h"
#include "openssl/rand.h"
#include "openssl/bn.h"

/* integermath */
#define MAX_RUN 20
#define HASH_LEN 20
#define MSG_LEN 128

//#define DEBUG   1
//#define TRUE	1
//#define FALSE	0
#if DEBUG
#define debug(...)	printf("DEBUG: "__VA_ARGS__)
#else
#define debug(...)
#endif

#define ErrorMsg(msg) \
	PyErr_SetString(IntegerError, msg); \
	return NULL;

//#if PY_MAJOR_VERSION >= 3
//	#define _PyLong_Check(o1) PyLong_Check(o1)
//#else
//	#define _PyLong_Check(o1) PyLong_Check(o1) || PyInt_Check(o1)
//#endif


#if PY_MAJOR_VERSION >= 3

#define Check_Types(o1, o2, lhs, rhs, foundLHS, foundRHS, lhs_value, rhs_value)  \
	if(PyInteger_Check(o1)) { \
		lhs = (Integer *) o1; } \
	else if(PyLong_Check(o1)) { \
		lhs_value = PyLong_AsLong(o1); \
		foundLHS = TRUE;  } \
	else { ErrorMsg("invalid left operand type."); } \
							\
	if(PyInteger_Check(o2)) {  \
		rhs = (Integer *) o2; } \
	else if(PyLong_Check(o2)) {  \
		rhs_value = PyLong_AsLong(o2); \
		foundRHS = TRUE; }  \
	else { ErrorMsg("invalid right operand type."); }


#define Check_Types2(o1, o2, lhs, rhs, foundLHS, foundRHS)  \
	if(PyInteger_Check(o1)) { \
		lhs = (Integer *) o1; } \
	else if(PyLong_Check(o1)) { \
		foundLHS = TRUE;  } \
	else { ErrorMsg("invalid left operand type."); } \
							\
	if(PyInteger_Check(o2)) {  \
		rhs = (Integer *) o2; } \
	else if(PyLong_Check(o2)) {  \
		foundRHS = TRUE; }  \
	else { ErrorMsg("invalid right operand type."); }

#else
/* python 2.x series */
#define Check_Types(o1, o2, lhs, rhs, foundLHS, foundRHS, lhs_value, rhs_value)  \
	if(PyInteger_Check(o1)) { \
		lhs = (Integer *) o1; } \
	else if(PyLong_Check(o1) || PyInt_Check(o1)) { \
		lhs_value = PyLong_AsLong(PyNumber_Long(o1)); \
		foundLHS = TRUE;  } \
	else { ErrorMsg("invalid left operand type."); } \
							\
	if(PyInteger_Check(o2)) {  \
		rhs = (Integer *) o2; } \
	else if(PyLong_Check(o2) || PyInt_Check(o2)) {  \
		rhs_value = PyLong_AsLong(PyNumber_Long(o2)); \
		foundRHS = TRUE; }  \
	else { ErrorMsg("invalid right operand type."); }


#define Check_Types2(o1, o2, lhs, rhs, foundLHS, foundRHS)  \
	if(PyInteger_Check(o1)) { \
		lhs = (Integer *) o1; } \
	else if(PyLong_Check(o1) || PyInt_Check(o1)) { \
		o1 = PyNumber_Long(o1); \
		foundLHS = TRUE;  } \
	else { ErrorMsg("invalid left operand type."); } \
							\
	if(PyInteger_Check(o2)) {  \
		rhs = (Integer *) o2; } \
	else if(PyLong_Check(o2) || PyInt_Check(o2)) {  \
		o2 = PyNumber_Long(o2); \
		foundRHS = TRUE; }  \
	else { ErrorMsg("invalid right operand type."); }


#endif

/* Index numbers for different hash functions.  These are all implemented as SHA1(index || message).	*/
#define HASH_FUNCTION_STR_TO_Zr_CRH		0
#define HASH_FUNCTION_Zr_TO_G1_ROM		1
#define HASH_FUNCTION_KEM_DERIVE		2
#define RAND_MAX_BYTES					2048

// declare global gmp_randstate_t state object. Initialize based on /dev/random if linux
// then make available to all random functions
PyTypeObject IntegerType;
static PyObject *IntegerError;
static Benchmark *dBench;
#define PyInteger_Check(obj) PyObject_TypeCheck(obj, &IntegerType)
#define PyInteger_Init(obj1, obj2) obj1->initialized && obj2->initialized

typedef struct {
	PyObject_HEAD
	mpz_t m;
	mpz_t e;
//	gmp_randstate_t state;
//	int state_init;
	int initialized;
} Integer;

PyMethodDef Integer_methods[];
PyNumberMethods integer_number;

void	Integer_dealloc(Integer* self);
PyObject *Integer_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
int Integer_init(Integer *self, PyObject *args, PyObject *kwds);
PyObject *Integer_print(Integer *self);
Integer *createNewInteger(mpz_t m);
Integer *createNewIntegerNoMod(void);
void print_mpz(mpz_t x, int base);
void print_bn_dec(const BIGNUM *bn);

#endif
