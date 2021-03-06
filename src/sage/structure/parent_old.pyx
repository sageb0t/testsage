r"""
Base class for old-style parent objects

CLASS HIERARCHY:

SageObject
    Parent
        ParentWithBase
            ParentWithGens

TESTS:

This came up in some subtle bug once.
::

    sage: gp(2) + gap(3)
    5
"""

###############################################################################
#   Sage: System for Algebra and Geometry Experimentation
#       Copyright (C) 2006 William Stein <wstein@gmail.com>
#  Distributed under the terms of the GNU General Public License (GPL)
#  The full text of the GPL is available at:
#                  http://www.gnu.org/licenses/
###############################################################################

cimport sage_object
import operator
from parent import Set_PythonType, Set_PythonType_class
from coerce import py_scalar_parent
from sage.structure.coerce_dict import MonoDict, TripleDict

include '../ext/python_object.pxi'
include '../ext/python_bool.pxi'
include '../ext/stdsage.pxi'

cdef inline check_old_coerce(Parent p):
    if p._element_constructor is not None:
        raise RuntimeError, "%s still using old coercion framework" % p

## def make_parent_v0(_class, _dict, has_coerce_map_from):
##     """
##     This should work for any Python class deriving from this, as long
##     as it doesn't implement some screwy __new__() method.
##     """
##     cdef Parent new_object
##     new_object = _class.__new__(_class)
##     if not _dict is None:
##         new_object.__dict__ = _dict
##     new_object._has_coerce_map_from = has_coerce_map_from
##     return new_object

cdef class Parent(parent.Parent):
    """
    Parents are the SAGE/mathematical analogues of container objects
    in computer science.

    TESTS::

        sage: V = VectorSpace(GF(2,'a'),2)
        sage: V.list()
        [(0, 0), (1, 0), (0, 1), (1, 1)]
        sage: MatrixSpace(GF(3), 1, 1).list()
        [[0], [1], [2]]
        sage: DirichletGroup(3).list()
        [Dirichlet character modulo 3 of conductor 1 mapping 2 |--> 1,
        Dirichlet character modulo 3 of conductor 3 mapping 2 |--> -1]
        sage: K = GF(7^6,'a')
        sage: K.list()[:10] # long time
        [0, 1, 2, 3, 4, 5, 6, a, a + 1, a + 2]
        sage: K.<a> = GF(4)
        sage: K.list()
        [0, a, a + 1, 1]
    """

    def __init__(self, coerce_from=[], actions=[], embeddings=[], category=None):
        # TODO: many classes don't call this at all, but __new__ crashes Sage
#        if len(coerce_from) > 0:
#            print type(self), coerce_from
        self.init_coerce(False)
        self._coerce_from_list = list(coerce_from)
        self._coerce_from_hash = MonoDict(23)
        self._action_list = list(actions)
        self._action_hash = TripleDict(23)

        cdef parent.Parent other
        for mor in embeddings:
            other = mor.domain()
            print "embedding", self, " --> ", other
            print mor
            other.init_coerce() # TODO remove when we can
            other._coerce_from_list.append(mor)

        self._set_element_constructor()

        # old
        self._has_coerce_map_from = MonoDict(23)
        if category is not None:
            self._init_category_(category)

    cdef int init_coerce(self, bint warn=False) except -1:
        parent.Parent.init_coerce(self, warn)

    #################################################################################
    # New Coercion support functionality
    #################################################################################

#    def coerce_map_from(self, S):
#        return self.coerce_map_from_c(S)

    cpdef coerce_map_from_c(self, S):
        """
        EXAMPLES:

        Check to make sure that we handle coerce maps from Python
        native types correctly::

            sage: QQ['q,t'].coerce_map_from(int)
            Composite map:
              From: Set of Python objects of type 'int'
              To:   Multivariate Polynomial Ring in q, t over Rational Field
              Defn:   Native morphism:
                      From: Set of Python objects of type 'int'
                      To:   Rational Field
                    then
                      Polynomial base injection morphism:
                      From: Rational Field
                      To:   Multivariate Polynomial Ring in q, t over Rational Field
        """
        check_old_coerce(self)
        if S is self:
            from sage.categories.homset import Hom
            return Hom(self, self).identity()
        elif S == self:
            # non-unique parents
            from sage.categories.homset import Hom
            from sage.categories.morphism import CallMorphism
            return CallMorphism(Hom(S, self))
        elif isinstance(S, Set_PythonType_class):
            return self.coerce_map_from_c(S._type)
        if self._coerce_from_hash is None: # this is because parent.__init__() does not always get called
            self.init_coerce()
        cdef object ret
        try:
            ret = PyObject_GetItem(self._coerce_from_hash,S)
            return ret
        except KeyError:
            pass

        if HAS_DICTIONARY(self):
            mor = self.coerce_map_from_impl(S)
        else:
            mor = self.coerce_map_from_c_impl(S)
        import sage.categories.morphism
        import sage.categories.map
        if mor is True:
            mor = sage.categories.morphism.CallMorphism(S, self)
        elif mor is False:
            mor = None
        elif mor is not None and not isinstance(mor, sage.categories.map.Map):
            raise TypeError, "coerce_map_from_impl must return a boolean, None, or an explicit Map"

        if mor is None and isinstance(S, type):
            #Convert Python types to native Sage types
            sage_type = py_scalar_parent(S)
            if sage_type is None:
                self._coerce_from_hash[S] = None
                return None
            mor = self.coerce_map_from_c(sage_type)
            if mor is not None:
                mor = mor * sage_type.coerce_map_from(S)

        if mor is not None:
            self._coerce_from_hash[S] = mor # TODO: if this is None, could it be non-None in the future?

        return mor

    def coerce_map_from_impl(self, S):
        check_old_coerce(self)
        return self.coerce_map_from_c_impl(S)

    cdef coerce_map_from_c_impl(self, S):
        check_old_coerce(self)
        import sage.categories.morphism
        from sage.categories.map import Map
        from sage.categories.homset import Hom
        cdef parent.Parent R
        for mor in self._coerce_from_list:
            if PY_TYPE_CHECK(mor, Map):
                R = mor.domain()
            else:
                R = mor
                mor = sage.categories.morphism.CallMorphism(Hom(R, self))
                i = self._coerce_from_list.index(R)
                self._coerce_from_list[i] = mor # cache in case we need it again
            if R is S:
                return mor
            else:
                connecting = R.coerce_map_from(S)
                if connecting is not None:
                    return mor * connecting

        # Piggyback off the old code for now
        # WARNING: when working on this, make sure circular dependencies aren't introduced!
        if self.has_coerce_map_from_c(S):
            if isinstance(S, type):
                S = Set_PythonType(S)
            return sage.categories.morphism.CallMorphism(Hom(S, self))
        else:
            return None

#    def get_action(self, S, op=operator.mul, self_on_left=True):
#        return self.get_action_c(S, op, self_on_left)

    cpdef get_action_c(self, S, op, bint self_on_left):
        check_old_coerce(self)
        try:
            if self._action_hash is None: # this is because parent.__init__() does not always get called
                self.init_coerce()
            return self._action_hash[S, op, self_on_left]
        except KeyError:
            pass
        if HAS_DICTIONARY(self):
            action = self.get_action_impl(S, op, self_on_left)
        else:
            action = self.get_action_c_impl(S, op, self_on_left)
        if action is not None:
            from sage.categories.action import Action
            if not isinstance(action, Action):
                raise TypeError, "get_action_impl must return None or an Action"
            self._action_hash[S, op, self_on_left] = action
        return action

    def get_action_impl(self, S, op, self_on_left):
        check_old_coerce(self)
        return self.get_action_c_impl(S, op, self_on_left)

    cdef get_action_c_impl(self, S, op, bint self_on_left):
        check_old_coerce(self)
        return self.discover_action(S, op, self_on_left)

    #################################################################################
    # Coercion support functionality
    #################################################################################

    def _coerce_(self, x):            # Call this from Python (do not override!)
        if self._element_constructor is not None:
            return self.coerce(x)
        check_old_coerce(self)
        return self._coerce_c(x)

    cpdef _coerce_c(self, x):          # DO NOT OVERRIDE THIS (call it)
        if self._element_constructor is not None:
            return self.coerce(x)
        check_old_coerce(self)
        try:
            P = x.parent()   # todo -- optimize
            if P is self:
                return x
        except AttributeError, msg:
            pass
        if HAS_DICTIONARY(self):
            return self._coerce_impl(x)
        else:
            return self._coerce_c_impl(x)

    cdef _coerce_c_impl(self, x):     # OVERRIDE THIS FOR CYTHON CLASSES
        """
        Canonically coerce x in assuming that the parent of x is not
        equal to self.
        """
        check_old_coerce(self)
        raise TypeError

    def _coerce_impl(self, x):        # OVERRIDE THIS FOR PYTHON CLASSES
        """
        Canonically coerce x in assuming that the parent of x is not
        equal to self.
        """
        check_old_coerce(self)
        return self._coerce_c_impl(x)

    def _coerce_try(self, x, v):
        """
        Given a list v of rings, try to coerce x canonically into each
        one in turn.  Return the __call__ coercion of the result into
        self of the first canonical coercion that succeeds.  Raise a
        TypeError if none of them succeed.

        INPUT:
             x -- Python object
             v -- parent object or list (iterator) of parent objects
        """
        check_old_coerce(self)
        if not isinstance(v, list):
            v = [v]

        for R in v:
            try:
                y = R._coerce_(x)
                return self(y)
            except (TypeError, AttributeError), msg:
                pass
        raise TypeError, "no canonical coercion of element into self"

    def _coerce_self(self, x):
        check_old_coerce(self)
        return self._coerce_self_c(x)

    cdef _coerce_self_c(self, x):
        """
        Try to canonically coerce x into self.
        Return result on success or raise TypeError on failure.
        """
        check_old_coerce(self)
        # todo -- optimize?
        try:
            P = x.parent()
            if P is self:
                return x
            elif P == self:
                return self(x)
        except AttributeError:
            pass
        raise TypeError, "no canonical coercion to self defined"

#    def has_coerce_map_from(self, S):
#        return self.has_coerce_map_from_c(S)

    cpdef has_coerce_map_from_c(self, S):
        """
        Return True if there is a natural map from S to self.
        Otherwise, return False.
        """
        check_old_coerce(self)
        if self == S:
            return True
        if self._has_coerce_map_from is None:
            self._has_coerce_map_from = MonoDict(23)
        else:
            try:
                return self._has_coerce_map_from[S]
            except KeyError:
                pass
        if HAS_DICTIONARY(self):
            x = self.has_coerce_map_from_impl(S)
        else:
            x = self.has_coerce_map_from_c_impl(S)
        self._has_coerce_map_from[S] = x
        return x

    def has_coerce_map_from_impl(self, S):
        check_old_coerce(self)
        return self.has_coerce_map_from_c_impl(S)

    cdef has_coerce_map_from_c_impl(self, S):
        check_old_coerce(self)
        if not PY_TYPE_CHECK(S, parent.Parent):
            return False
        try:
            self._coerce_c((<parent.Parent>S).an_element())
        except TypeError:
            return False
        except NotImplementedError, msg:
            raise NotImplementedError, "%s\nAlso, please make sure you have implemented has_coerce_map_from_impl or has_coerce_map_from_c_impl (or better _an_element_c_impl or _an_element_impl if possible) for %s"%(msg,self)
        return True

    def _an_element_impl(self):     # override this in Python
        check_old_coerce(self)
        return self._an_element_c_impl()

    cdef _an_element_c_impl(self):  # override this in Cython
        """
        Returns an element of self. Want it in sufficient generality
        that poorly-written functions won't work when they're not
        supposed to. This is cached so doesn't have to be super fast.
        """
        check_old_coerce(self)
        try:
            return self.gen(0)
        except StandardError:
            pass

        try:
            return self.gen()
        except StandardError:
            pass

        from sage.rings.infinity import infinity
        for x in ['_an_element_', 'pi', 1.2, 2, 1, 0, infinity]:
            try:
                return self(x)
            except (TypeError, NameError, NotImplementedError, AttributeError, ValueError):
                pass

        raise NotImplementedError, "please implement _an_element_c_impl or _an_element_impl for %s"%self

    def _an_element(self):        # do not override this (call from Python)
        check_old_coerce(self)
        return self._an_element_c()

    cpdef _an_element_c(self):     # do not override this (call from Cython)
        check_old_coerce(self)
        if not self.__an_element is None:
            return self.__an_element
        if HAS_DICTIONARY(self):
            self.__an_element = self._an_element_impl()
        else:
            self.__an_element = self._an_element_c_impl()
        return self.__an_element

    # This should eventually be inherited from the EnumeratedSets() category
    # This is just a convenient spot to cover the relevant cython parents,
    # without bothering the new parents
    list = parent.Parent._list_from_iterator_cached

    ################################################
    # Comparison of parent objects
    ################################################
    cdef _richcmp(left, right, int op):
        """
        Compare left and right.
        """
        check_old_coerce(left)
        cdef int r

        if not PY_TYPE_CHECK(right, parent.Parent) or not PY_TYPE_CHECK(left, parent.Parent):
            # One is not a parent -- use arbitrary ordering
            if (<PyObject*>left) < (<PyObject*>right):
                r = -1
            elif (<PyObject*>left) > (<PyObject*>right):
                r = 1
            else:
                r = 0

        else:
            # Both are parents -- but need *not* have the same type.
            if HAS_DICTIONARY(left):
                r = left.__cmp__(right)
            else:
                r = left._cmp_c_impl(right)

        if op == 0:  #<
            return PyBool_FromLong(r  < 0)
        elif op == 2: #==
            return PyBool_FromLong(r == 0)
        elif op == 4: #>
            return PyBool_FromLong(r  > 0)
        elif op == 1: #<=
            return PyBool_FromLong(r <= 0)
        elif op == 3: #!=
            return PyBool_FromLong(r != 0)
        elif op == 5: #>=
            return PyBool_FromLong(r >= 0)

##     ####################################################################
##     # For a derived Cython class, you **must** put the following in
##     # your subclasses, in order for it to take advantage of the
##     # above generic comparison code.  You must also define
##     # _cmp_c_impl for a Cython class.
##     #
##     # For a derived Python class, simply define __cmp__.
##     ####################################################################
##     def __richcmp__(left, right, int op):
##         return (<Parent>left)._richcmp(right, op)

##         # NOT NEEDED, since all attributes are public!
##     def __reduce__(self):
##         if HAS_DICTIONARY(self):
##             _dict = self.__dict__
##         else:
##             _dict = None
##         return (make_parent_v0, (self.__class__, _dict, self._has_coerce_map_from))

    cdef int _cmp_c_impl(left, parent.Parent right) except -2:
        check_old_coerce(left)
        pass
        # this would be nice to do, but we can't since
        # it leads to infinite recursions -- and is slow -- and this
        # stuff must be fast!
        #if right.has_coerce_map_from(left):
        #    if left.has_coerce_map_from(right):
        #        return 0
        #    else:
        #        return -1
        if (<PyObject*>left) < (<PyObject*>right):
            return -1
        elif (<PyObject*>left) > (<PyObject*>right):
            return 1
        return 0

##     def __cmp__(left, right):
##         return left._cmp_c_impl(right)   # default

    ############################################################################
    # Coercion Compatibility Layer
    ############################################################################

    cpdef _coerce_map_from_(self, S):
        if self._element_constructor is None:
            return self.coerce_map_from_c(S)
        else:
            return parent.Parent._coerce_map_from_(self, S)

    cpdef _get_action_(self, other, op, bint self_on_left):
        if self._element_constructor is None:
            return self.get_action_c(other, op, self_on_left)
        else:
            return parent.Parent._get_action_(self, other, op, self_on_left)

    def _an_element_(self):
        if self._element_constructor is None:
            return self._an_element_c()
        else:
            return parent.Parent._an_element_(self)

    cpdef _generic_convert_map(self, S):
        if self._element_constructor is None:
            if hasattr(self, '_element_constructor_'):
                assert callable(self._element_constructor_)
                self._element_constructor = self._element_constructor_
            else:
                from sage.categories.morphism import CallMorphism
                from sage.categories.homset import Hom
                if PY_TYPE_CHECK(S, type):
                    S = Set_PythonType(S)
                return CallMorphism(Hom(S, self))
        return parent.Parent._generic_convert_map(self, S)
