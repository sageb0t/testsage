r"""
Additive Abelian Groups

Additive abelian groups are just modules over `\ZZ`. Hence the classes in this
module derive from those in the module :mod:`sage.modules.fg_pid`. The only
major differences are in the way elements are printed.
"""

from sage.groups.group import AbelianGroup
from sage.modules.fg_pid.fgp_module import FGP_Module_class
from sage.modules.fg_pid.fgp_element import FGP_Element
from sage.rings.all import ZZ

def AdditiveAbelianGroup(invs, remember_generators = True):
    r"""
    Construct a finitely-generated additive abelian group.

    INPUTS:

    - ``invs`` (list of integers): the invariants. These should all be `\ge 0`.

    - ``remember_generators`` (boolean): whether or not to fix a set of
      generators (corresponding to the given invariants, which need not be in
      Smith form).

    OUTPUT:

    the abelian group `\bigoplus_i \ZZ / n_i \ZZ`, where `n_i` are the invariants.

    EXAMPLE::

        sage: AdditiveAbelianGroup([0, 2, 4])
        Additive abelian group isomorphic to Z/2 + Z/4 + Z

    An example of the ``remember_generators`` switch::

        sage: G = AdditiveAbelianGroup([0, 2, 3]); G
        Additive abelian group isomorphic to Z/6 + Z
        sage: G.gens()
        ((1, 0, 0), (0, 1, 0), (0, 0, 1))

        sage: H = AdditiveAbelianGroup([0, 2, 3], remember_generators = False); H
        Additive abelian group isomorphic to Z/6 + Z
        sage: H.gens()
        ((0, 1, 2), (1, 0, 0))

    .. note ::

        TODO: The output of the above tests is somewhat disturbing! I haven't
        yet come up with a good way of printing these things. Note that (0, -3,
        -3) is just (0, 1, 0) and (0, -2, -2) is just (0, 0, 1), but I can't
        think of a way of reducing modulo the relations that is canonical in
        all cases and still comes up with the "obviously right answer" here.
    """

    invs = [ZZ(x) for x in invs]
    if not all( [x >= 0 for x in invs] ): raise ValueError, "Invariants must be nonnegative"
    A, B = cover_and_relations_from_invariants(invs)
    if remember_generators:
        G = AdditiveAbelianGroup_fixed_gens(A, B, A.gens())
    else:
        G = AdditiveAbelianGroup_class(A, B)
    return G

def cover_and_relations_from_invariants(invs):
    r"""
    Utility function: given a list of integers, construct the obvious pair of
    free modules such that the quotient is naturally isomorphic to the
    corresponding product of cyclic modules.

    EXAMPLES::

        sage: from sage.groups.additive_abelian.additive_abelian_group import cover_and_relations_from_invariants as cr
        sage: cr([0,2,3])
        (Ambient free module of rank 3 over the principal ideal domain Integer Ring, Free module of degree 3 and rank 2 over Integer Ring
        Echelon basis matrix:
        [0 2 0]
        [0 0 3])
    """
    n = len(invs)
    A = ZZ**n
    B = A.span([A.gen(i) * invs[i] for i in xrange(n)])
    return (A, B)

# Note: It's important that the class inherits from FGP_Module_class first,
# since we want to inherit things like __hash__ from there rather than the
# hyper-generic implementation for abstract abelian groups.

class AdditiveAbelianGroup_class(FGP_Module_class, AbelianGroup):
    r"""
    An additive abelian group, implemented using the `\ZZ`-module machinery.
    """

    def __init__(self, cover, relations):
        r"""
        EXAMPLE::

            sage: G = AdditiveAbelianGroup([0]); G # indirect doctest
            Additive abelian group isomorphic to Z
            sage: G == loads(dumps(G))
            True
        """
        FGP_Module_class.__init__(self, cover, relations)

    def _repr_(self):
        r"""
        String representation of this group.

        EXAMPLES::

            sage: AdditiveAbelianGroup([0, 2, 3])._repr_()
            'Additive abelian group isomorphic to Z/6 + Z'
        """
        if self.V().rank() == 0:
            return "Trivial group"
        else:
            return "Additive abelian group isomorphic to %s" % self.short_name()

    def short_name(self):
        r"""
        Return a name for the isomorphism class of this group.

        EXAMPLE::

            sage: AdditiveAbelianGroup([0, 2,4]).short_name()
            'Z/2 + Z/4 + Z'
            sage: AdditiveAbelianGroup([0, 2, 3]).short_name()
            'Z/6 + Z'
        """
        invs = self.invariants()
        if not invs: return "Trivial group"
        s = ""
        for j in invs:
            if j == 0: s += "Z + "
            else: s += "Z/%s + " % j
        return s[:-3] # drop the final " + "

    def _subquotient_class(self):
        r"""
        Return the class of subquotients of this group.

        EXAMPLE::

            sage: AdditiveAbelianGroup([0])._subquotient_class()
            <class 'sage.groups.additive_abelian.additive_abelian_group.AdditiveAbelianGroup_class'>
        """
        return AdditiveAbelianGroup_class

    def _element_class(self):
        r"""
        Return the class of elements of this group.

        EXAMPLE::

            sage: AdditiveAbelianGroup([0])._element_class()
            <class 'sage.groups.additive_abelian.additive_abelian_group.AdditiveAbelianGroupElement'>
        """
        return AdditiveAbelianGroupElement

    def order(self):
        r"""
        Return the order of this group (an integer or infinity)

        EXAMPLES::

            sage: AdditiveAbelianGroup([2,4]).order()
            8
            sage: AdditiveAbelianGroup([0, 2,4]).order()
            +Infinity
            sage: AdditiveAbelianGroup([]).order()
            1
        """
        return self.cardinality()

    def exponent(self):
        r"""
        Return the exponent of this group (the smallest positive integer `N`
        such that `Nx = 0` for all `x` in the group). If there is no such
        integer, return 0.

        EXAMPLES::

            sage: AdditiveAbelianGroup([2,4]).exponent()
            4
            sage: AdditiveAbelianGroup([0, 2,4]).exponent()
            0
            sage: AdditiveAbelianGroup([]).exponent()
            1
        """
        if not self.invariants():
            return 1
        else:
            ann =  self.annihilator().gen()
            if ann:
                return ann
            return ZZ(0)

    def is_multiplicative(self):
        r"""
        Return False since this is an additive group.

        EXAMPLE::

            sage: AdditiveAbelianGroup([0]).is_multiplicative()
            False
        """
        return False

class AdditiveAbelianGroup_fixed_gens(AdditiveAbelianGroup_class):
    r"""
    A variant which fixes a set of generators, which need not be in Smith form
    (or indeed independent).
    """
    def __init__(self, cover, rels, gens):
        r"""
        Standard initialisation function

        EXAMPLE::

            sage: AdditiveAbelianGroup([3]) # indirect doctest
            Additive abelian group isomorphic to Z/3
        """
        AdditiveAbelianGroup_class.__init__(self, cover, rels)
        self._orig_gens = [self(x) for x in gens]

    def gens(self):
        r"""
        Return the specified generators for self (as a tuple). Compare
        ``self.smithform_gens()``.

        EXAMPLE::

            sage: G = AdditiveAbelianGroup([2,3])
            sage: G.gens()
            ((1, 0), (0, 1))
            sage: G.smith_form_gens()
            ((1, 2),)
        """
        return tuple(self._orig_gens)

class AdditiveAbelianGroupElement(FGP_Element):

    def _hermite_lift(self):
        r"""
        This gives a certain canonical lifting of elements of this group
        (represented as a quotient `G/H` of free abelian groups) to `G`, using
        the Hermite normal form of the matrix of relations.

        Mainly used by the ``_repr_`` method.

        EXAMPLES::

            sage: A = AdditiveAbelianGroup([2, 3])
            sage: v = 3000001 * A.0
            sage: v.lift()
            (3000001, 0)
            sage: v._hermite_lift()
            (1, 0)
        """
        y = self.lift()
        H = self.parent().W().basis_matrix()

        for i in xrange(H.nrows()):
            if i in H.pivot_rows():
                j = H.pivots()[i]
                N = H[i,j]
                a = (y[j] - (y[j] % N)) // N
                y = y - a*H.row(i)
        return y

    def _repr_(self):
        r"""
        String representation. This uses a canonical lifting of elements of
        this group (represented as a quotient `G/H` of free abelian groups) to
        `G`, using the Hermite normal form of the matrix of relations.

        EXAMPLE::

            sage: G = AdditiveAbelianGroup([2,3])
            sage: repr(G.gen(0)) # indirect doctest
            '(1, 0)'
            sage: a = 13*G.gen(0); repr(a) # indirect doctest
            '(1, 0)'
            sage: a._x
            (13, 0)
        """
        return repr(self._hermite_lift())
