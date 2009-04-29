"""
Symmetric Ideals of Infinite Polynomial Rings

This module provides an implementation of ideals of polynomial rings in a countably
infinite number of variables that are invariant under variable permuation.
Such ideals are called 'Symmetric Ideals' in the rest of this document.
Our implementation is based on the theory of M. Aschenbrenner and C. Hillar.

AUTHORS:

- Simon King <simon.king@uni-jena.de>

"""
#*****************************************************************************
#       Copyright (C) 2009 Simon King <king@mathematik.uni-jena.de>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************
from sage.rings.ideal import Ideal_generic
from sage.rings.integer import Integer
from sage.structure.sequence import Sequence
from sage.rings.integer_ring import ZZ
from sage.misc.cachefunc import cached_method
import sys

class SymmetricIdeal( Ideal_generic ):
    r"""
    Ideal in an Infinite Polynomial Ring, invariant under permutation of variable indices

    THEORY:

    An Infinite Polynomial Ring with finitely many generators `x_\ast, y_\ast, ...` over
    a field `F` is a free commutative `F`-algebra generated by infinitely many 'variables'
    `x_0, x_1, x_2,..., y_0, y_1, y_2,...`. We refer to the natural number `n` as the *index*
    of the variable `x_n`. See more detailed description at :mod:`~sage.rings.polynomial.infinite_polynomial_ring`

    Infinite Polynomial Rings are equipped with a permutation action by permuting positive
    variable indices, i.e., `x_n^P = x_{P(n)}, y_n^P=y_{P(n)}, ...` for any permutation `P`.
    Note that the variables `x_0, y_0, ...` of index zero are invariant under that action.

    A *Symmetric Ideal* is an ideal in an infinite polynomial ring `X` that is invariant under
    the permutation action. In other words, if `\mathfrak S_\infty` denotes the symmetric
    group of `1,2,...`, then a Symmetric Ideal is a right `X[\mathfrak S_\infty]`-submodule
    of `X`.

    It is known by work of Aschenbrenner and Hillar [AB2007]_ that an Infinite Polynomial
    Ring `X` with a single generator `x_\ast` is noetherian, in the sense
    that any Symmetric Ideal `I\subset X` is finitely generated modulo addition,
    multiplication by elements of `X`, and permutation of variable indices (hence, it is a
    finitely generated right `X[\mathfrak S_\infty]`-module).

    Moreover, if `X` is equipped with a lexicographic monomial ordering with `x_1 < x_2 < x_3 ...`
    then there is an algorithm of Buchberger type that computes a Groebner basis `G` for `I`
    that allows for computation of a unique normal form, that is zero precisely for the elements
    of `I` -- see [AB2008]_. See :meth:`.groebner_basis` for more details.

    Our implementation allows more than one generator and also provides degree
    lexicographic and degree reverse lexicographic monomial
    orderings -- we do, however, not guarantee termination of the Buchberger
    algorithm in these cases.

    .. [AB2007] M. Aschenbrenner, C. Hillar,
       Finite generation of symmetric ideals.
       Trans. Amer. Math. Soc. 359 (2007), no. 11, 5171--5192.

    .. [AB2008] M. Aschenbrenner, C. Hillar,
       `An Algorithm for Finding Symmetric Groebner Bases in Infinite Dimensional Rings. <http://de.arxiv.org/abs/0801.4439>`_

    EXAMPLES::

        sage: X.<x,y> = InfinitePolynomialRing(QQ)
        sage: I=X*(x[1]^2+y[2]^2,x[1]*x[2]*y[3]+x[1]*y[4])
        sage: I == loads(dumps(I))
        True
        sage: latex(I)
        \left(y_{2}^{2} + x_{1}^{2}, y_{4} x_{1} + y_{3} x_{2} x_{1}\right)\Bold{Q}[x_{\ast}, y_{\ast}][\mathfrak{S}_{\infty}]

    The default ordering is lexicographic. We now compute a Groebner basis::

        sage: J=I.groebner_basis()
        sage: J
        [x1^4 + x1^3, x2*x1^2 - x1^3, x2^2 - x1^2, y1*x1^3 + y1*x1^2, y1*x2 + y1*x1^2, y1^2 + x1^2, y2*x1 + y1*x1^2]

    Ideal membership in ``I`` can now be tested by commuting symmetric reduction modulo ``J``::

        sage: I.reduce(J)
        Symmetric Ideal (0, 0) of Infinite polynomial ring in x, y over Rational Field

    Note that the Groebner basis is not point-wise invariant under permutation. However, any element
    of ``J`` has symmetric reduction zero even after applying a permutation::

        sage: P=Permutation([1, 4, 3, 2])
        sage: J[2]
        x2^2 - x1^2
        sage: J[2]^P
        x4^2 - x1^2
        sage: J.__contains__(J[2]^P)
        False
        sage: [[(p^P).reduce(J) for p in J] for P in Permutations(4)]
        [[0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0]]

    Since ``I`` is not a Groebner basis, it is no surprise that it can not detect
    ideal membership::

        sage: [p.reduce(I) for p in J]
        [x1^4 + x1^3, x2*x1^2 - x1^3, x2^2 - x1^2, y1*x1^3 + y1*x1^2, y1*x2 + y1*x1^2, y1^2 + x1^2, y2*x1 + y1*x1^2]

    Note we give no guarantee that the computation of a symmetric Groebner basis will terminate in
    an order different from lexicographic.

    When multiplying Symmetric Ideals or raising them to some integer power,
    the permutation action is taken into account, so that the product is
    indeed the product of ideals in the mathematical sense.
    ::

        sage: I=X*(x[1])
        sage: I*I
        Symmetric Ideal (x1^2, x2*x1) of Infinite polynomial ring in x, y over Rational Field
        sage: I^3
        Symmetric Ideal (x1^3, x2*x1^2, x2^2*x1, x3*x2*x1) of Infinite polynomial ring in x, y over Rational Field
        sage: I*I == X*(x[1]^2)
        False

    """

    def __init__(self, ring, gens, coerce=True):
        """
        EXAMPLES::

            sage: X.<x,y> = InfinitePolynomialRing(QQ)
            sage: I=X*(x[1]^2+y[2]^2,x[1]*x[2]*y[3]+x[1]*y[4]) # indirect doctest
            sage: I
            Symmetric Ideal (y2^2 + x1^2, y4*x1 + y3*x2*x1) of Infinite polynomial ring in x, y over Rational Field
            sage: from sage.rings.polynomial.symmetric_ideal import SymmetricIdeal
            sage: J=SymmetricIdeal(X,[x[1]^2+y[2]^2,x[1]*x[2]*y[3]+x[1]*y[4]])
            sage: I==J
            True

        """
        Ideal_generic.__init__(self, ring, gens, coerce=coerce)

    def __repr__(self):
        """
        EXAMPLES::

            sage: X.<x,y> = InfinitePolynomialRing(QQ)
            sage: I=X*(x[1]^2+y[2]^2,x[1]*x[2]*y[3]+x[1]*y[4])
            sage: str(I) # indirect doctest
            'Symmetric Ideal (y2^2 + x1^2, y4*x1 + y3*x2*x1) of Infinite polynomial ring in x, y over Rational Field'

        """
        return "Symmetric Ideal %s of %s"%(self._repr_short(), self.ring())

    def _latex_(self):
        r"""
        EXAMPLES::

            sage: from sage.misc.latex import latex
            sage: X.<x,y> = InfinitePolynomialRing(QQ)
            sage: I=X*(x[1]*y[2])
            sage: latex(I)
            \left(y_{2} x_{1}\right)\Bold{Q}[x_{\ast}, y_{\ast}][\mathfrak{S}_{\infty}]

        """
        from sage.misc.latex import latex
        return '\\left(%s\\right)%s[\\mathfrak{S}_{\\infty}]'%(", ".join([latex(g) for g in self.gens()]), latex(self.ring()))

    def __mul__ (self, other):
        """
        Product of two symmetric ideals.

        Since the generators of a symmetric ideal are subject to a permutation action,
        they in fact stand for a set of polynomials. Hence, when multiplying two
        symmetric ideals, it does not suffice to simply multiply the respective
        generators.

        EXAMPLE::

            sage: X.<x> = InfinitePolynomialRing(QQ)
            sage: I=X*(x[1])
            sage: I*I         # indirect doctest
            Symmetric Ideal (x1^2, x2*x1) of Infinite polynomial ring in x over Rational Field

        """
        # determine maximal generator index
        PARENT = self.ring()
        if (not isinstance(other, self.__class__)) or self.ring()!=other.ring():
            if hasattr(other,'gens'):
                other = SymmetricIdeal(PARENT, other.gens(), coerce=True)
        other = other.symmetrisation()
        sN = max([X.max_index() for X in self.gens()]+[1])
        oN = max([X.max_index() for X in other.gens()]+[1])

        from sage.combinat.permutation import Permutation
        P = Permutation(range(2,sN+oN+1)+[1])
        oGen = list(other.gens())
        SymL = oGen
        for i in range(sN):
            oGen = [X.__pow__(P) for X in oGen]
            SymL = SymL + oGen
        # Now, SymL contains all necessary permutations of the second factor
        OUT = []
        for X in self.gens():
            OUT.extend([X*Y for Y in SymL])
        return SymmetricIdeal(PARENT, OUT, coerce=False).interreduction()

    def __pow__(self, n):
        """
        Raise self to some power.

        Since the generators of a symmetric ideal are subject to a permutation action,
        they in fact stand for a set of polynomials. Hence, when raising a symmetric
        ideals to some power, it does not suffice to simply raise the generators to
        the respective power.

        EXAMPLES::

            sage: X.<x> = InfinitePolynomialRing(QQ)
            sage: I=X*(x[1])
            sage: I^2     # indirect doctest
            Symmetric Ideal (x1^2, x2*x1) of Infinite polynomial ring in x over Rational Field

        """
        OUT = SymmetricIdeal(self.ring(),[1])
        for i in range(n):
            OUT = self*OUT
        return OUT

    def reduce(self, I, tailreduce=False):
        """
        Symmetric reduction of self by another Symmetric Ideal or list of Infinite Polynomials.

        INPUT:

        - ``I`` -- a Symmetric Ideal or a list of Infinite Polynomials
        - ``tailreduce`` (optional) -- if it is True, the non-leading terms will be
          reduced as well.

        Reducing an element `p` of an Infinite Polynomial Ring `X` by some other element `q`
        means the following:

        1. Let `M` and `N` be the leading terms of `p` and `q`.
        2. Test whether there is a permutation `P` that does not does not diminish the variable
           indices occoring in `N` and preserves their order, so that there is some term `T\in X`
           with `T N^P = M`. If there is no such permutation, return `p`
        3. Replace `p` by `p-T q^P` and continue with step 1.

        EXAMPLES::

            sage: X.<x,y> = InfinitePolynomialRing(QQ)
            sage: I = X*(y[1]^2*y[3]+y[1]*x[3])
            sage: I.reduce([y[2]^2*y[1]])
            Symmetric Ideal (y3*y1^2 + y1*x3) of Infinite polynomial ring in x, y over Rational Field

        The preceding is correct, since any permutation that turns ``y[2]^2*y[1]`` into
        a factor of ``y[1]^2*y[3]`` interchanges the variable indices 1 and 2 -- which is not
        allowed. However, reduction by ``y[1]^2*y[2]`` works, since one can change variable
        index 1 into 2 and 2 into 3::

            sage: I.reduce([y[1]^2*y[2]])
            Symmetric Ideal (y1*x3) of Infinite polynomial ring in x, y over Rational Field

        The next example shows that tail reduction is not done, unless it is explicitly adviced.
        The input can also be a symmetric ideal::

            sage: J = (x[2])*X
            sage: I.reduce(J)
            Symmetric Ideal (y3*y1^2 + y1*x3) of Infinite polynomial ring in x, y over Rational Field
            sage: I.reduce(J, tailreduce=True)
            Symmetric Ideal (y3*y1^2) of Infinite polynomial ring in x, y over Rational Field

        """
        from sage.rings.polynomial.symmetric_reduction import SymmetricReductionStrategy
        if hasattr(I,'gens'):
            I = I.gens()
        if (not I):
            return self
        I = list(I)
        S = SymmetricReductionStrategy(self.ring(),I, tailreduce)
        return SymmetricIdeal(self.ring(),[S.reduce(X) for X in self.gens()], coerce=False)

    def interreduction(self, tailreduce=True, sorted=False, report=None, RStrat=None):
        """
        Return symmetrically interreduced form of self

        INPUT:

        - ``tailreduce`` (optional) - If True, the interreduction is also performed on the non-leading
          monomials.
        - ``sorted`` (optional) - If True, it is assumed that the generators of self are already
          increasingly sorted.
        - ``report`` (optional) - If not None, some information on the progress of computation is printed
        - ``RStrat`` (optional) - A :class:`~sage.rings.polynomial.symmetric_reduction.SymmetricReductionStrategy`
          to which the polynomials resulting from the interreduction will be added. If ``RStrat`` already contains
          some polynomials, they will be used in the interreduction. The effect is
          to compute in a quotient ring.

        RETURN:
          A Symmetric Ideal J (sorted list of generators) coinciding with self as an ideal,
          so that any generator is symmetrically reduced w.r.t. the other generators. Note that
          the leading coefficients of the result are not necessarily 1.

        EXAMPLES::

            sage: X.<x> = InfinitePolynomialRing(QQ)
            sage: I=X*(x[1]+x[2],x[1]*x[2])
            sage: I.interreduction()
            Symmetric Ideal (-x1^2, x2 + x1) of Infinite polynomial ring in x over Rational Field

        Here, we show the ``report`` option::

            sage: I.interreduction(report=True)
            Symmetric interreduction
            [1/2]  >
            [2/2] : >
            [1/2]  >
            [2/2] T[1] >
            >
            Symmetric Ideal (-x1^2, x2 + x1) of Infinite polynomial ring in x over Rational Field

        ``[m/n]`` indicates that polynomial number ``m`` is considered and the
        total number of polynomials under consideration is ``n``.
        '-> 0' is printed if a zero reduction occured. The rest of the
        report is as described in :meth:`sage.rings.polynomial.symmetric_reduction.SymmetricReductionStrategy.reduce`.

        Last, we demonstrate the use of the optional parameter ``RStrat``::

            sage: from sage.rings.polynomial.symmetric_reduction import SymmetricReductionStrategy
            sage: R = SymmetricReductionStrategy(X)
            sage: R
            Symmetric Reduction Strategy in Infinite polynomial ring in x over Rational Field
            sage: I.interreduction(RStrat=R)
            Symmetric Ideal (-x1^2, x2 + x1) of Infinite polynomial ring in x over Rational Field
            sage: R
            Symmetric Reduction Strategy in Infinite polynomial ring in x over Rational Field, modulo
                x1^2,
                x2 + x1
            sage: R = SymmetricReductionStrategy(X,[x[1]^2])
            sage: I.interreduction(RStrat=R)
            Symmetric Ideal (x2 + x1) of Infinite polynomial ring in x over Rational Field

        """
        DONE = []
        j = 0
        TODO = []
        PARENT = self.ring()
        for P in self.gens():
            if P._p!=0:
                if P.lm()._p == P.lc(): # self generates all of self.ring()
                    if RStrat is not None:
                        RStrat.add_generator(PARENT(1))
                    return SymmetricIdeal(self.ring(),[self.ring()(1)], coerce=False)
                TODO.append(P)
        if not sorted:
            TODO = list(set(TODO))
            TODO.sort()
        if hasattr(PARENT,'_P'):
            CommonR = PARENT._P
        else:
            VarList = set([])
            for P in TODO:
                if P._p!=0:
                    if P.lm()._p == P.lc(): # self generates all of PARENT
                        if RStrat is not None:
                            RStrat.add_generator(PARENT(1))
                        return SymmetricIdeal(PARENT,[PARENT(1)], coerce=False)
                    VarList = VarList.union(P._p.parent().variable_names())
            VarList = list(VarList)
            if not VarList:
                return SymmetricIdeal(PARENT,[0])
            VarList.sort(cmp=PARENT.varname_cmp, reverse=True)
            from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
            CommonR = PolynomialRing(self.base_ring(), VarList, order=self.ring()._order)

        ## Now, the symmetric interreduction starts
        if not (report is None):
            print 'Symmetric interreduction'
        from sage.rings.polynomial.symmetric_reduction import SymmetricReductionStrategy
        if RStrat is None:
            RStrat = SymmetricReductionStrategy(self.ring(),tailreduce=tailreduce)
        GroundState = RStrat.gens()
        while (1):
            RStrat.setgens(GroundState)
            DONE = []
            for i in range(len(TODO)):
                if (not (report is None)):
                    print '[%d/%d] '%(i+1,len(TODO)),
                    sys.stdout.flush()
                p = RStrat.reduce(TODO[i], report=report)
                if p._p != 0:
                    if p.lm()._p == p.lc(): # self generates all of self.ring()
                        return SymmetricIdeal(self.ring(),[self.ring()(1)], coerce=False)
                    RStrat.add_generator(p, good_input=True)
                    DONE.append(p)
                else:
                    if not (report is None):
                        print "-> 0"
            DONE.sort()
            if DONE == TODO:
                break
            else:
                TODO = DONE
        return SymmetricIdeal(self.ring(),DONE, coerce=False)

    def interreduced_basis(self):
        """
        A fully symmetrically reduced generating set (type :class:`~sage.structure.sequence.Sequence`) of self.

        This does essentially the same as :meth:`interreduction` with the option 'tailreduce', but
        it returns a :class:`~sage.structure.sequence.Sequence` rather than a :class:`~sage.rings.polynomial.symmetric_ideal.SymmetricIdeal`.

        EXAMPLES::

            sage: X.<x> = InfinitePolynomialRing(QQ)
            sage: I=X*(x[1]+x[2],x[1]*x[2])
            sage: I.interreduced_basis()
            [-x1^2, x2 + x1]

        """
        return Sequence(self.interreduction(tailreduce=True).gens(), self.ring(), check=False)

    def symmetrisation (self, N=None, tailreduce=False, report=None, use_full_group=False):
        """
        Apply permutations to the generators of self and interreduce

        INPUT:

        - N (optional) -- apply permutations in Sym(N). Default is the maximal
          variable index occuring in the generators of ``self.interreduction().squeezed()``.
        - tailreduce (optional) -- If True, perform tail reductions
        - report (optional) -- If not None, report on the progress of computations
        - use_full_group (optional) -- If True, apply *all* elements of Sym(N) to the generators
          of self (this is what [AB2008]_ originally suggests). The default is to apply all
          elementary transpositions to the generators of ``self.squeezed()``, interreduce, and
          repeat until the result stabilises, which is often much faster than applying all of Sym(N),
          and we are convinced that both methods yield the same result.

        OUTPUT:
            A symetrically interreduced symmetric ideal with respect to which any
            Sym(N)-translate of a generator of self is symmetrically reducible,
            where by default N is the maximal variable index that occurs in the
            generators of ``self.interreduction().squeezed()``.

        NOTE:
            If ``I`` is a symmetric ideal whose generators are monomials,
            then ``I.symmetrisation()`` is its reduced Groebner basis.
            It should be noted that without symmetrisation, monomial
            generators, in general, do not form a Groebner basis.

        EXAMPLES::

            sage: X.<x> = InfinitePolynomialRing(QQ)
            sage: I = X*(x[1]+x[2], x[1]*x[2])
            sage: I.symmetrisation()
            Symmetric Ideal (-x1^2, x2 + x1) of Infinite polynomial ring in x over Rational Field
            sage: I.symmetrisation(N=3)
            Symmetric Ideal (-2*x1) of Infinite polynomial ring in x over Rational Field
            sage: I.symmetrisation(N=3, use_full_group=True)
            Symmetric Ideal (-2*x1) of Infinite polynomial ring in x over Rational Field

        """
        newOUT = self.interreduction(tailreduce=tailreduce, report=report).squeezed()
        R = self.ring()
        OUT = R*()
        if N is None:
            N = max([Y.max_index() for Y in newOUT.gens()]+[1])
        else:
            N = Integer(N)
        if hasattr(R,'_max') and R._max<N:
            R.gen()[N]
        if report!=None:
            print "Symmetrise %d polynomials at level %d"%(len(newOUT.gens()),N)
        if use_full_group:
            from sage.combinat.permutation import Permutations
            NewGens = []
            Gens = self.gens()
            for P in Permutations(N):
                NewGens.extend([p**P for p in Gens])
            return (NewGens * R).interreduction(tailreduce=tailreduce,report=report)
        from sage.combinat.permutation import Permutation
        from sage.rings.polynomial.symmetric_reduction import SymmetricReductionStrategy
        RStrat = SymmetricReductionStrategy(self.ring(),OUT.gens(),tailreduce=tailreduce)
        while (OUT!=newOUT):
            OUT = newOUT
            PermutedGens = list(OUT.gens())
            if not (report is None):
                print "Apply permutations"
            for i in range(1,N):
                for j in range(i+1,N+1):
                    P = Permutation(((i,j)))
                    for X in OUT.gens():
                        p = RStrat.reduce(X**P,report=report)
                        if p._p !=0:
                            PermutedGens.append(p)
                            RStrat.add_generator(p,good_input=True)
            newOUT = (PermutedGens * R).interreduction(tailreduce=tailreduce,report=report)
        return OUT

    def symmetric_basis(self):
        """
        A symmetrised generating set (type :class:`~sage.structure.sequence.Sequence`) of self.

        This does essentially the same as :meth:`symmetrisation` with the option 'tailreduce', and
        it returns a :class:`~sage.structure.sequence.Sequence` rather than a :class:`~sage.rings.polynomial.symmetric_ideal.SymmetricIdeal`.

        EXAMPLES::

            sage: X.<x> = InfinitePolynomialRing(QQ)
            sage: I = X*(x[1]+x[2], x[1]*x[2])
            sage: I.symmetric_basis()
            [x1^2, x2 + x1]

        """
        return Sequence(self.symmetrisation(tailreduce=True).normalisation().gens(), self.ring(), check=False)

    def normalisation(self):
        """
        Return an ideal that coincides with self, so that all generators have leading coefficient 1.

        Possibly occuring zeroes are removed from the generator list.

        EXAMPLES::

            sage: X.<x> = InfinitePolynomialRing(QQ)
            sage: I = X*(1/2*x[1]+2/3*x[2], 0, 4/5*x[1]*x[2])
            sage: I.normalisation()
            Symmetric Ideal (x2 + 3/4*x1, x2*x1) of Infinite polynomial ring in x over Rational Field

        """
        return SymmetricIdeal(self.ring(), [X/X.lc() for X in self.gens() if X._p!=0])

    def squeezed(self):
        """
        Reduce the variable indices occuring in self

        OUTPUT:
            A Symmetric Ideal whose generators are the result of applying
            :meth:`~sage.rings.polynomial.infinite_polynomial_element.InfinitePolynomial_sparse.squeezed`
            to the generators of self.

        NOTE:
            The output describes the same Symmetric Ideal as self.

        EXAMPLES::

            sage: X.<x,y> = InfinitePolynomialRing(QQ,implementation='sparse')
            sage: I = X*(x[1000]*y[100],x[50]*y[1000])
            sage: I.squeezed()
            Symmetric Ideal (y1*x2, y2*x1) of Infinite polynomial ring in x, y over Rational Field

        """
        return SymmetricIdeal(self.ring(), [X.squeezed() for X in self.gens()])

    @cached_method
    def groebner_basis(self, tailreduce=False, reduced=True, algorithm=None, report=None, use_full_group=False):
        """
        Return a symmetric Groebner basis (type :class:`~sage.structure.sequence.Sequence`) of self.

        INPUT:

        - ``tailreduce`` (optional, default False) - if True, use tail reduction
          in intermediate computations
        - ``reduced`` (optional, default True) - return the reduced normalised Groebner basis
        - ``algorithm`` (optional) - determine the algorithm (see below for available algorithms)
        - ``report`` (optional) - print information on the progress of computation.
        - ``use_full_group`` (optional, default False) - if True then proceed as originally suggested
          by [AB2008]_. Our default method should be faster, see :meth:`.symmetrisation` for more details.

        The computation of symmetric Groebner bases also involves the computation of *classical*
        Groebner bases, i.e., of Groebner bases for ideals in polynomial rings with finitely
        many variables. For these computations, Sage provides the following
        ALGORITHMS:

        ''
            autoselect (default)

        'singular:groebner'
            Singular's ``groebner`` command

        'singular:std'
            Singular's ``std`` command

        'singular:stdhilb'
            Singular's ``stdhib`` command

        'singular:stdfglm'
            Singular's ``stdfglm`` command

        'singular:slimgb'
            Singular's ``slimgb`` command

        'libsingular:std'
            libSingular's ``std`` command

        'libsingular:slimgb'
            libSingular's ``slimgb`` command

        'toy:buchberger'
            Sage's toy/educational buchberger without strategy

        'toy:buchberger2'
            Sage's toy/educational buchberger with strategy

        'toy:d_basis'
            Sage's toy/educational d_basis algorithm

        'macaulay2:gb'
            Macaulay2's ``gb`` command (if available)

        'magma:GroebnerBasis'
            Magma's ``Groebnerbasis`` command (if available)

        If only a system is given - e.g. 'magma' - the default algorithm is
        chosen for that system.

        .. note::

           The Singular and libSingular versions of the respective
           algorithms are identical, but the former calls an external
           Singular process while the later calls a C function, i.e. the
           calling overhead is smaller.

        EXAMPLES::

            sage: X.<x,y> = InfinitePolynomialRing(QQ)
            sage: I1 = X*(x[1]+x[2],x[1]*x[2])
            sage: I1.groebner_basis()
            [x1]
            sage: I2 = X*(y[1]^2*y[3]+y[1]*x[3])
            sage: I2.groebner_basis()
            [y1*x2^2 - y1*x2*x1, y2*x2*x1 - y2*x1^2, y2*y1*x2 - y2*y1*x1, y2*y1^2 + y1*x2, y2^2*y1 + y2*x1]

        When using the algorithm originally suggested by Aschenbrenner and Hillar, the
        result is the same, but the computation takes much longer::

            sage: I2.groebner_basis(use_full_group=True)
            [y1*x2^2 - y1*x2*x1, y2*x2*x1 - y2*x1^2, y2*y1*x2 - y2*y1*x1, y2*y1^2 + y1*x2, y2^2*y1 + y2*x1]

        Last, we demonstrate how the report on the progress of computations looks like::

            sage: I1.groebner_basis(report=True, reduced=True)
            Symmetric interreduction
            [1/2]  >
            [2/2] : >
            [1/2]  >
            [2/2]  >
            Symmetrise 2 polynomials at level 2
            Apply permutations
            >
            >
            Symmetric interreduction
            [1/3]  >
            [2/3]  >
            [3/3] : >
            -> 0
            [1/2]  >
            [2/2]  >
            Symmetrisation done
            Classical Groebner basis
            -> 2 generators
            Symmetric interreduction
            [1/2]  >
            [2/2]  >
            Symmetrise 2 polynomials at level 3
            Apply permutations
            >
            >
            :>
            ::>
            :>
            ::>
            Symmetric interreduction
            [1/4]  >
            [2/4] : >
            -> 0
            [3/4] :: >
            -> 0
            [4/4] : >
            -> 0
            [1/1]  >
            Apply permutations
            :>
            :>
            >
            Symmetric interreduction
            [1/1]  >
            Classical Groebner basis
            -> 1 generators
            Symmetric interreduction
            [1/1]  >
            Symmetrise 1 polynomials at level 4
            Apply permutations
            >
            :>
            :>
            >
            :>
            :>
            Symmetric interreduction
            [1/2]  >
            [2/2] : >
            -> 0
            [1/1]  >
            Symmetric interreduction
            [1/1]  >
            [x1]

        """
        # determine maximal generator index
        # and construct a common parent for the generators of self
        if algorithm is None:
            algorithm=''
        PARENT = self.ring()
        OUT = self.symmetrisation(tailreduce=tailreduce,report=report,use_full_group=use_full_group)
        if not (report is None):
            print "Symmetrisation done"
        VarList = set([])
        for P in OUT.gens():
            if P._p!=0:
                if P.lm()._p == P.lc(): # self generates all of PARENT
                    #return SymmetricIdeal(PARENT,[PARENT(1)], coerce=False)
                    return Sequence([PARENT(1)], PARENT, check=False)
                VarList = VarList.union([str(X) for X in P.variables()])
        VarList = list(VarList)
        if not VarList:
            #return SymmetricIdeal(PARENT,[0]) # it was already tested whether it is "1"
            return Sequence([PARENT(0)], PARENT, check=False)
        from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
        N = max([int(X[1:]) for X in VarList]+[1])

        #from sage.combinat.permutation import Permutations
        while (1):
            if hasattr(PARENT,'_P'):
                CommonR = PARENT._P
            else:
                VarList = set([])
                for P in OUT.gens():
                    if P._p!=0:
                        if P.lm()._p == P.lc(): # self generates all of PARENT
                            #return SymmetricIdeal(PARENT,[PARENT(1)], coerce=False)
                            return Sequence([PARENT(1)], PARENT, check=False)
                        VarList = VarList.union([str(X) for X in P.variables()])
                VarList = list(VarList)
                VarList.sort(cmp=PARENT.varname_cmp, reverse=True)
                CommonR = PolynomialRing(PARENT._base, VarList, order=PARENT._order)
            DenseIdeal = [P._p for P in OUT.gens()]*CommonR
            if hasattr(DenseIdeal,'groebner_basis'):
                if report != None:
                    print "Classical Groebner basis"
                    if algorithm!='':
                        print "(using %s)"%algorithm
                newOUT = (DenseIdeal.groebner_basis(algorithm)*PARENT)
                if report != None:
                    print "->",len(newOUT.gens()),'generators'
            else:
                if report != None:
                    print "GCD"
            # Symmetrise out to the next index:
            N += 1
            newOUT = newOUT.symmetrisation(N=N,tailreduce=tailreduce,report=report,use_full_group=use_full_group)
            if [X.lm() for X in OUT.gens()] == [X.lm() for X in newOUT.gens()]:
                if reduced:
                    if tailreduce:
                        return Sequence(newOUT.normalisation().gens(), PARENT, check=False)
                    return Sequence(newOUT.interreduction(tailreduce=True, report=report).normalisation().gens(), PARENT, check=False)
                return Sequence(newOUT.gens(), PARENT, check=False)
            OUT = newOUT
