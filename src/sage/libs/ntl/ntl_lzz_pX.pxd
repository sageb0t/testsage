from sage.libs.ntl.ntl_lzz_pX_decl cimport *, zz_pX_c, zz_pX_Modulus_c
from sage.libs.ntl.ntl_lzz_p_decl cimport *, zz_p_c

from sage.libs.ntl.ntl_lzz_pContext cimport ntl_zz_pContext_class

#cdef extern from "ntl_wrap.h":
#    struct zz_pX

cdef class ntl_zz_pX:
    cdef zz_pX_c x
    cdef ntl_zz_pContext_class c
    cdef ntl_zz_pX _new(self)
