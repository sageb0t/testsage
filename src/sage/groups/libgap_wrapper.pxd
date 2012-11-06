from sage.structure.element cimport MultiplicativeGroupElement, MonoidElement
from sage.libs.gap.element cimport GapElement

cdef class ElementLibGAP(MultiplicativeGroupElement):
    cdef GapElement _libgap
    cpdef GapElement gap(self)
    cpdef MonoidElement _mul_(left, MonoidElement right)
    cpdef MultiplicativeGroupElement _div_(self, MultiplicativeGroupElement right)
