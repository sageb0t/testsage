"""
Generic matrices
"""

###############################################################################
#   SAGE: System for Algebra and Geometry Experimentation
#       Copyright (C) 2006 William Stein <wstein@gmail.com>
#  Distributed under the terms of the GNU General Public License (GPL)
#  The full text of the GPL is available at:
#                  http://www.gnu.org/licenses/
###############################################################################

cimport sage.structure.element
import  sage.structure.element
cimport sage.structure.mutability

cdef class Matrix(sage.structure.element.ModuleElement):
    # Properties of any matrix  (plus _parent, inherited from base class)
    cdef Py_ssize_t _nrows
    cdef Py_ssize_t _ncols
    cdef object _cache
    cdef public object _base_ring
    cdef sage.structure.mutability.Mutability _mutability

    cdef int _will_use_strassen(self, Matrix right) except -1
    cdef int _strassen_default_cutoff(self, Matrix right) except -1

    cdef _mul_c_impl(self, Matrix right)
    cdef int _cmp_c_impl(self, Matrix right) except -2

    cdef richcmp(Matrix self, right, int op)

    # Pivots.
    cdef _set_pivots(self, X)

    # Cache
    cdef clear_cache(self)
    cdef fetch(self, key)
    cdef cache(self, key, x)

    # Mutability and bounds checking
    cdef check_bounds(self, Py_ssize_t i, Py_ssize_t j)
    cdef check_mutability(self)
    cdef check_bounds_and_mutability(self, Py_ssize_t i, Py_ssize_t j)

    # Unsafe entry access
    cdef set_unsafe(self, Py_ssize_t i, Py_ssize_t j, object x)
    cdef get_unsafe(self, Py_ssize_t i, Py_ssize_t j)

    # Pickling:
    cdef _pickle(self)
    cdef _unpickle(self, data, int version)

    # Strassen
    cdef subtract_strassen_product(result, A, B, int cutoff)

cdef class MatrixWindow:
    cdef Py_ssize_t _row, _col, _nrows, _ncols
    cdef Matrix _matrix
