r"""
Multiplicative Abelian Groups

AUTHOR:
    -- David Joyner (2006-03) (based on free abelian monoids by David Kohel)

TODO:
   * additive abelian groups should also be supported

Background on elementary divisors, invariant factors and the Smith
normal form (according to section 4.1 of [C1]): An abelian group is a
group A for which there exists an exact sequence $\Z^k \rightarrow
\Z^\ell \rightarrow A \rightarrow 1$, for some positive integers
$k,\ell$ with $k\leq \ell$. For example, a finite abelian group has a
decomposition

\[
A = \langle a_1\rangle \times \dots \times  \langle a_\ell\rangle ,
\]
where $ord(a_i)=p_i^{c_i}$, for some primes $p_i$ and some
positive integers $c_i$, $i=1,...,\ell$. GAP calls the
list (ordered by size) of the $p_i^{c_i}$ the {\it abelian invariants}.
In \sage they will be called {\it invariants}.
In this situation,
$k=\ell$ and $\phi:  \Z^\ell \rightarrow A$ is the map
$\phi(x_1,...,x_\ell) = a_1^{x_1}...a_\ell^{x_\ell}$,
for $(x_1,...,x_\ell)\in \Z^\ell$. The matrix of relations
$M:\Z^k \rightarrow \Z^\ell$ is the matrix
whose rows generate the kernel of $\phi$ as a $\Z$-module.
In other words, $M=(M_{ij})$ is a $\ell\times \ell$
diagonal matrix with $M_{ii}=p_i^{c_i}$. Consider now the
subgroup $B\subset A$ generated by
$b_1 = a_1^{f_{1,1}}...a_\ell^{f_{\ell,1}}$, ...,
$b_m = a_1^{f_{1,m}}...a_\ell^{f_{\ell,m}}$.
The kernel of the map $\phi_B:  \Z^m \rightarrow B$ defined by
$\phi_B(y_1,...,y_m) = b_1^{y_1}...b_m^{y_m}$,
for $(y_1,...,y_m)\in \Z^m$, is the kernel of the matrix

\[
F=
\left(
\begin{array}{cccc}
f_{11} & f_{12} & \dots & f_{1m}\\
f_{21} & f_{22} & \dots & f_{2m}\\
\vdots &        & \ddots & \vdots \\
f_{\ell,1} & f_{\ell,2} & \dots & f_{\ell,m}
\end{array}
\right),
\]
regarded as a map
$Z^m\rightarrow (\Z/p_1^{c_1}\Z)\times ...\times (\Z/p_\ell^{c_\ell}\Z)$.
In particular, $B\cong \Z^m/ker(F)$. If $B=A$ then the
Smith normal form (SNF) of a generator matrix of
$ker(F)$ and the SNF of $M$ are the same. The diagonal entries $s_i$ of the
SNF $S = diag[s_1,s_2,s_3, ... s_r,0,0,...0]$,
are called {\it determinantal divisors} of $F$.
where $r$ is the rank. The {\it invariant factors} of  A  are:
\[
s_1, s_2/s_1, s_3/s_2, ... s_r/s_{r-1}.
\]
The {\it elementary divisors} use the highest (non-trivial) prime
powers occuring in the factorizations of the numbers $s_1, s_2,
... s_r$.

SAGE supports multiplicative abelian groups on any prescribed finite
number $n\geq 0$ of generators.  Use the \code{AbelianGroup} function
to create an abelian group, and the \code{gen} and \code{gens}
functions to obtain the corresponding generators.  You can print the
generators as arbitrary strings using the optional \code{names}
argument to the \code{AbelianGroup} function.

EXAMPLE 1:
We create an abelian group in zero or more variables; the syntax T(1)
creates the identity element even in the rank zero case.

    sage: T = AbelianGroup(0,[])
    sage: T
    Abelian group on 0 generators () with invariants []
    sage: T.gens()
    ()
    sage: T(1)
    1

EXAMPLE 2:
An abelian group uses a multiplicative representation of elements, but
the underlying representation is lists of integer exponents.

    sage: F = AbelianGroup(5,[3,4,5,5,7],names = list("abcde"))
    sage: F
    Abelian group on 5 generators (a, b, c, d, e) with invariants [3, 4, 5, 5, 7]
    sage: (a,b,c,d,e) = F.gens()
    sage: a*b^2*e*d
    a*b^2*d*e
    sage: x = b^2*e*d*a^7
    sage: x
    a*b^2*d*e
    sage: x.list()
    [1, 2, 0, 1, 1]

REFERENCES:
    [C1] H. Cohen Advanced topics in computational number
         theory, Springer, 2000.
    [C2] ------, A course in computational algebraic number
         theory, Springer, 1996.

"""

##########################################################################
#  Copyright (C) 2006 David Joyner and William Stein
#
#  Distributed under the terms of the GNU General Public License (GPL):
#
#                  http://www.gnu.org/licenses/
##########################################################################

# TODO: change the "invariants" terminology everywhere to elementary_divisors

import weakref

from sage.ext.integer import Integer

# TODO: get rid of the import *'s -- figure out exactly
# what you use below and include only that.

from sage.rings.infinity import *
from sage.rings.arith import *
from abelian_group_element import AbelianGroupElement,is_AbelianGroupElement
from sage.misc.misc import add, prod
import sage.groups.group as group

# TODO: this uses perm groups - the AbelianGroupElement instance method
# uses a different implementation.

def word_problem(words, g, verbose = False):
    r"""
    G and H are abelian, g in G, H is a subgroup of G generated by a
    list (words) of elements of G. If g is in H, return the expression
    for g as a word in the elements of (words).

    The 'word problem' for a finite abelian group G boils down to the following
    matrix-vector analog of the Chinese remainder theorem.

    Problem: Fix integers $1<n_1\leq n_2\leq ...\leq n_k$ (indeed,
    these $n_i$ will all be prime powers), fix a generating set
    $g_i=(a_{i1},...,a_{ik})$ (with $a_{ij}\in \Z/n_j\Z$),
    for $1\leq i\leq \ell$, for the group $G$, and let
    $d = (d_1,...,d_k)$ be an element of the direct product
    $\Z/n_1\Z \times ...\times \Z/n_k\Z$. Find, if they exist,
    integers $c_1,...,c_\ell$ such that
    $c_1g_1+...+c_\ell g_\ell = d$. In other words, solve the
    equation $cA=d$ for $c\in \Z^\ell$, where $A$ is the matrix whose
    rows are the $g_i$'s. Of course, it suffices to restrict the $c_i$'s
    to the range $0\leq c_i\leq N-1$, where $N$ denotes the least common
    multiple of the integers $n_1,...,n_k$.

    This function does not solve this directly, as perhaps it should. Rather
    (for both speed and as a model for a similar function valid for more
    general groups), it pushes it over to GAP, which has optimized algorithms for
    the word problem. Essentially, this function is a wrapper for the GAP
    function 'Factorization'.

    EXAMPLE:
        sage: G.<a,b,c> = AbelianGroup(3,[2,3,4]); G
        Abelian group on 3 generators (a, b, c) with invariants [2, 3, 4]
        sage: word_problem([a*b,a*c], b*c)
        [[a*b, 1], [a*c, 1]]
        sage: word_problem([a*b,a*c],b*c)
        [[a*b, 1], [a*c, 1]]

        sage: A.<a,b,c,d,e> = AbelianGroup(5,[4, 5, 5, 7, 8])
        sage: b1 = a^3*b*c*d^2*e^5
        sage: b2 = a^2*b*c^2*d^3*e^3
        sage: b3 = a^7*b^3*c^5*d^4*e^4
        sage: b4 = a^3*b^2*c^2*d^3*e^5
        sage: b5 = a^2*b^4*c^2*d^4*e^5
        sage: word_problem([b1,b2,b3,b4,b5],e)
        [[a^3*b*c*d^2*e^5, 1],
        [a^2*b*c^2*d^3*e^3, 1],
        [a^3*b^3*d^4*e^4, 3],
        [a^3*b^2*c^2*d^3*e^5, 1]]

    WARNINGS: (1) Might have unpleasant effect when the word problem
                 cannot be solved.

             (2) Uses permutation groups, so may be slow when group is
                 large. The instance method word_problem of the class
                 AbelianGroupElement is implemented differently
                 (wrapping GAP's"EpimorphismFromFreeGroup" and
                 "PreImagesRepresentative") and may be faster.

    """
    from sage.groups.permgroup import PermutationGroup
    from sage.interfaces.all import gap
    G = g.parent()
    invs = G.invariants()
    gap.eval("l:=One(Rationals)")
    s1 = 'A:=AbelianGroup(%s)'%invs
    gap.eval(s1)
    s2 = 'phi:=IsomorphismPermGroup(A)'
    gap.eval(s2)
    s3 = "gens := GeneratorsOfGroup(A)"
    gap.eval(s3)
    L = g.list()
    gap.eval("L1:="+str(L))
    s4 = "L2:=List([l..%s], i->gens[i]^L1[i]);"%len(L)
    gap.eval(s4)
    gap.eval("g:=Product(L2); gensH:=[]")
    for w in words:
         L = w.list()
         gap.eval("L1:="+str(L))
         s4 = "L2:=List([1..%s], i->gens[i]^L1[i]);"%len(L)
         gap.eval(s4)
         gap.eval("w:=Product(L2)")
         gap.eval("gensH:=Concatenation(gensH,[w])")
    s5 = 'H:=Group(gensH)'
    gap.eval(s5)
    gap.eval("x:=Factorization(H,g)")
    l3 = gap.eval("L3:=ExtRepOfObj(x)")
    nn = gap.eval("n:=Int(Length(L3)/2)")
    LL = eval(gap.eval("L4:=List([l..n],i->L3[2*i])"))
    if verbose:
        v = '*'.join(['(%s)^%s'%(words[i], LL[i]) for i in range(len(LL))])
        print '%s = %s'%(g, v)
    return [[words[i],LL[i]] for i in range(len(LL))]

def AbelianGroup(n, invfac=None, names="f"):
    r"""
    Create the multiplicative abelian group in $n$ generators with
    given invariants, which must be prime powers.

    INPUT:
        n -- integer
        invfac -- (the"invariant factors") a list of non-negative integers
                  in the form [a0, a1,...,a(n-1)], typically written in
                  increasing order.  This list is padded with zeros if
                  it has length less than n.
        names -- (optional) names of generators

    Alternatively, you can also give input in the following form:

        \code{AbelianGroup(invfac, names="f")},

    where names must be explicitly named.

    OUTPUT:
        Abelian group with generators and invariant type. The default name
        for generator A.i is fi, as in GAP.

    EXAMPLES:
        sage: F = AbelianGroup(5, [5,5,7,8,9], names='abcde')
        sage: F(1)
        1
        sage: (a, b, c, d, e) = F.gens()
        sage: mul([ a, b, a, c, b, d, c, d ])
        a^2*b^2*c^2*d^2
        sage: d * b**2 * c**3
        b^2*c^3*d
        sage: F = AbelianGroup(3,[2]*3); F
        Abelian group on 3 generators (f0, f1, f2) with invariants [2, 2, 2]
        sage: H = AbelianGroup([2,3], names="xy"); H
        Abelian group on 2 generators (x, y) with invariants [2, 3]

    Notice how $0$'s are padded on.
        sage: AbelianGroup(5, [2,3,4])
        Abelian group on 5 generators (f0, f1, f2, f3, f4) with invariants [2, 3, 4, 0, 0]

    The invariant list can't be longer than the number of generators.
        sage: AbelianGroup(2, [2,3,4])
        Traceback (most recent call last):
        ...
        ValueError: invfac (=[2, 3, 4]) must have length n (=2)
    """
    if invfac is None:
        if isinstance(n, (list, tuple)):
            invfac = n
            n = len(n)
        else:
            invfac = []
    if len(invfac) < n:
        invfac = invfac + [0] * (n - len(invfac))
    elif len(invfac) > n:
        raise ValueError, "invfac (=%s) must have length n (=%s)"%(invfac, n)
    M = AbelianGroup_class(n, invfac, names)
    return M

def is_AbelianGroup(x):
    """
    Return True if $x$ is an abelian group.

    EXAMPLES:
        sage: F = AbelianGroup(5,[5,5,7,8,9],names = list("abcde")); F
        Abelian group on 5 generators (a, b, c, d, e) with invariants [5, 5, 7, 8, 9]
        sage: is_AbelianGroup(F)
        True
        sage: is_AbelianGroup(AbelianGroup(7, [3]*7))
        True
    """
    return isinstance(x, AbelianGroup_class)

class AbelianGroup_class(group.AbelianGroup):
    """
    Free abelian group on $n$ generators. The invariant factors
    [a1,a2,...,ak] must be a list of prime powers.

    EXAMPLES:
        sage: F = AbelianGroup(5,[5,5,7,8,9],names = list("abcde")); F
        Abelian group on 5 generators (a, b, c, d, e) with invariants [5, 5, 7, 8, 9]
        sage: F = AbelianGroup(5,[2, 4, 12, 24, 120],names = list("abcde")); F
	Traceback (most recent call last):
        ...
        ValueError: each invariant factor (=[2, 4, 12, 24, 120])  must be a prime power.

    Thus we see that the "invariants" are not the invariant factors but
    the "elementary divisors" (in the terminology of Rotman).
    """
    def __init__(self, n, invfac, names="f"):
        #invfac.sort()
        n = Integer(n)
        if n < 0:
            raise ValueError, "n (=%s) must be nonnegative."%n
        self.__ngens = n
        self.assign_names(names)
        for i in range(len(invfac)):
           if invfac[i] > 1 and not is_prime_power(invfac[i]):
               raise ValueError, "each invariant factor (=%s)  must be a prime power."%invfac
        self.__invariants = invfac

    def invariants(self):
        return self.__invariants

##     def is_subgroup(self, other):
##         """
##         Return True if self is a subgroup of other.

##         EXAMPLES:
##             sage: G = AbelianGroup(3,[2,3,4], names="abc"); G
##             Abelian group on 3 generators (a, b, c) with invariants [2, 3, 4]
##             sage: a,b,c = G.gens()
##             sage: H = G.subgroup([a*b,a])
##             sage: H.is_subgroup(G)
##             True
##             sage: G.is_subgroup(H)
##             True
##             sage: K = AbelianGroup(4,[5,2,3,4], names="abcd"); G
##             Abelian group on 3 generators (a, b, c) with invariants [2, 3, 4]
##             sage: G.is_subgroup(K)
##             True
##         """
##         raise NotImplementedError
##         for x in self.gens():
##             if not x in other:
##                 return False
##         return True

    def exponent(self):
        """
        Return the exponent of this abelian group.

        EXAMPLES:
            G = AbelianGroup([2,3,7]); G
            Abelian group on 3 generators (f0, f1, f2) with invariants [2, 3, 7]
            sage: G.exponent()
            42
        """
        try:
            return self.__exponent
        except AttributeError:
            e = Integer(gap(self).Exponent())
            self.__exponent = e
            return e

    def _repr_(self):
        """
        Print method.

        EXAMPLES:
            sage: F = AbelianGroup(5,[5,64,729],names = list("abcde")); F
            Abelian group on 5 generators (a, b, c, d, e) with invariants [5, 64, 729, 0, 0]
	    sage: F = AbelianGroup(5,[1,1,5,64,729],names = list("abcde")); F
            Abelian group on 5 generators (a, b, c, d, e) with invariants [1, 1, 5, 64, 729]
            sage: F.rename('my group G')
            sage: F
            my group G
        """
        n = self.__ngens
        invs = self.invariants()
        m = len(invs)
        if m==n:
            return "Abelian group on %s generators %s with invariants %s"%(n,self.gens(),invs)
        else:
            invs = self.invariants()+[0]*(n-m)
            return "Abelian group on %s generators %s with invariants %s"%(n,self.gens(),invs)

    def __call__(self, x):
        """
        Create an element of this abelian group from $x$.

        EXAMPLES:
            sage: F = AbelianGroup(10, [2]*10)
            sage: F(F.2)
            f2
            sage: F(1)
            1
        """
        if isinstance(x, AbelianGroupElement) and x.parent() is self:
            return x
        return AbelianGroupElement(self, x)

    def __contains__(self, x):
        """
        Return True if $x$ is an element of this abelian group.

        EXAMPLES:
            sage: F = AbelianGroup(10,[2]*10)
            sage: F.2 * F.3 in F
            True
        """
        return isinstance(x, AbelianGroupElement) and x.parent() == self

    def random(self):
        """
        Return a random element of this group.
        """
        gens = self.gens()
        g = gens[0]^0
        for i in range(len(gens)):
            g = g*gens[i]^(random(gens[i].order()))
        return g

    def _gap_init_(self):
        r"""
        Return string that defines corresponding abelian group in GAP.

        EXAMPLES:
            sage: G = AbelianGroup([2,3,9])
            sage: G._gap_init_()
            'AbelianGroup([2, 3, 9])'
            sage: gap(G)
            <pc group of size 54 with 3 generators>

        Only works for finite groups.
            sage: G = AbelianGroup(3,[0,3,4],names="abc"); G
            Abelian group on 3 generators (a, b, c) with invariants [0, 3, 4]
            sage: G._gap_init_()
            Traceback (most recent call last):
            ...
            TypeError: abelian groups in GAP are finite, but self is infinite
        """
        # TODO: Use the package polycyclic has AbelianPcpGroup, which can handle
        # the infinite case but it is a GAP package not GPL'd.
        # Use this when the group is infinite...
        if (False and prod(self.invariants())==0):   # if False for now...
            return 'AbelianPcpGroup(%s)'%self.invariants()
        if not self.is_finite():
            raise TypeError, "abelian groups in GAP are finite, but self is infinite"
        return 'AbelianGroup(%s)'%self.invariants()

    def gen(self, i=0):
        """
        The $i$-th generator of the abelian group.

        EXAMPLES:
            sage: F = AbelianGroup(5,[],names='a')
            sage: F.0
            a0
            sage: F.2
            a2
            sage: F.invariants()
            [0, 0, 0, 0, 0]
        """
        n = self.__ngens
        if i < 0 or i >= n:
            raise IndexError, "Argument i (= %s) must be between 0 and %s."%(i, n-1)
        x = [0]*int(n)
        x[int(i)] = 1
        return AbelianGroupElement(self, x)

    def ngens(self):
        """
        The number of free generators of the abelian group.

        EXAMPLES:
            sage: F = AbelianGroup(10000)
            sage: F.ngens()
            10000
        """
        return self.__ngens

    def order(self):
        """
        Return the order of this group.

        EXAMPLES:
            sage: G = AbelianGroup(2,[2,3])
            sage: G.order()
            6
            sage: G = AbelianGroup(3,[2,3,0])
            sage: G.order()
            Infinity
        """
        import sage.rings.all
        try:
            return self.__len
        except AttributeError:
            if len(self.invariants()) < self.ngens():
                self.__len = sage.rings.all.infinity
            self.__len = sage.misc.misc.mul(self.invariants())
            if self.__len == 0:
                self.__len = sage.rings.all.infinity
        return self.__len

    def permutation_group(self):
        r"""
        Return the permutation group isomorphic to this abelian group.

        If the invariants are $q_1, \ldots, q_n$ then the generators
        of the permutation will be of order $q_1, \ldots, q_n$,
        respectively.

        EXAMPLES:
            sage: G = AbelianGroup(2,[2,3]); G
            Abelian group on 2 generators (f0, f1) with invariants [2, 3]
            sage: G.permutation_group()
            Permutation Group with generators [(1,4)(2,5)(3,6), (1,2,3)(4,5,6)]
        """
        from sage.groups.perm_gps.permgroup import PermutationGroup
        from sage.interfaces.all import gap
        invs = self.invariants()
        s = 'Image(IsomorphismPermGroup(%s))'%self._gap_init_()
        return PermutationGroup(s, from_group=True)

    def is_commutative(self):
        """
        Return True since this group is commutative.

        EXAMPLES:
            sage: G = AbelianGroup([2,3,9, 0])
            sage: G.is_commutative()
            True
            sage: G.is_abelian()
            True
        """
        return True

    def subgroup(self, gensH, names="f"):
         """
         Create a subgroup of this group.

         INPUT:
             gensH -- list of elements which are products of the
                      generators of the ambient abelian group G = self
         EXAMPLES:
             sage: G.<a,b,c> = AbelianGroup(3, [2,3,4]); G
             Abelian group on 3 generators (a, b, c) with invariants [2, 3, 4]
             sage: H = G.subgroup([a*b,a]); H
             Subgroup of Abelian group on 3 generators (a, b, c) with invariants [2, 3, 4] generated by [a*b, a]
             sage: H < G
             True
             sage: F = G.subgroup([a,b^2])
             sage: F
             Subgroup of Abelian group on 3 generators (a, b, c) with invariants [2, 3, 4] generated by [a, b^2]
             sage: F.gens()
             [a, b^2]

         """
         if not isinstance(gensH, (list, tuple)):
             raise TypeError, "gensH = (%s) must be a list or tuple"%(gensH)

         G = self
         for i in range(len(gensH)):
             if not(gensH[i] in G):
                 raise TypeError, "Subgroup generators must belong to the given group."
         return AbelianGroup_subgroup(self, gensH, names)

    def __cmp__(self, right):
       """
       Compare self and right.

       The ordering is the ordering induced by that on the invariant factors lists.

       EXAMPLES:
           sage: G1 = AbelianGroup([2,3,4,5])
           sage: G2 = AbelianGroup([2,3,4,5,1])
           sage: G1 < G2
           True
           sage: G1 > G2
           False
           sage: G1 == G2
           False
       """
       if not is_AbelianGroup(right):
           return -1
       return cmp(self.invariants(), right.invariants())

class AbelianGroup_subgroup(AbelianGroup_class):
    """
    Subgroup subclass of AbelianGroup_class, so instance methods are
    inherited.

    TODO: * There should be a way to coerce an element of a subgroup
            into the ambient group.
          * Does NOT work for infinite groups.
    """
    def __init__(self, ambient, gens, names="f"):
        """

        EXAMPLES:
            sage: A = AbelianGroup(5,[3, 5, 5, 7, 8], names="abcde")
            sage: a,b,c,d,e=A.gens()
            sage: A.subgroup([a,b])
            Subgroup of Abelian group on 5 generators (a, b, c, d, e) with invariants [3, 5, 5, 7, 8] generated by [a, b]
            sage: A.subgroup([a,b,c,d^2,e])
            Subgroup of Abelian group on 5 generators (a, b, c, d, e) with invariants [3, 5, 5, 7, 8] generated by [a, b, c, d^2, e]
            sage: A.subgroup([a,b,c,d^2,e^2])
            Subgroup of Abelian group on 5 generators (a, b, c, d, e) with invariants [3, 5, 5, 7, 8] generated by [a, b, c, d^2, e^2]
            sage: B = A.subgroup([a^3,b,c,d,e^2]); B
            Subgroup of Abelian group on 5 generators (a, b, c, d, e) with invariants [3, 5, 5, 7, 8] generated by [b, c, d, e^2]
            sage: B.invariants()
            [4, 5, 5, 7]
            sage: A=AbelianGroup(4,[1009, 2003, 3001, 4001], names="abcd")
            sage: a,b,c,d=A.gens()
            sage: B = A.subgroup([a^3,b,c,d])
            sage: B.invariants()
            [1009, 2003, 3001, 4001]
            sage: A.order()
            24266473210027
            sage: B.order()
            24266473210027

        Infinite groups can also be handled:
            sage: G = AbelianGroup([3,4,0], names="abc")
            sage: a,b,c = G.gens()
            sage: F = G.subgroup([a,b^2,c]); F
            Subgroup of Abelian group on 3 generators (a, b, c) with invariants [3, 4, 0] generated by [a, b^2, c]
            sage: F.invariants()
            [2, 3, 0]
            sage: F.gens()
            [a, b^2, c]
            sage: F.order()
            Infinity

        """
        if not isinstance(ambient, AbelianGroup_class):
            raise TypeError, "ambient (=%s) must be an abelian group."%ambient
        if not isinstance(gens, list):
            raise TypeError, "gens (=%s) must be a list"%gens

        self.__ambient_group = ambient
        Hgens = [x for x in gens if x!=ambient(1)]  ## in case someone puts 1 in the list of generators
        self.__gens = Hgens
        m = len(gens)
        ell = len(ambient.gens())
        ambient_invs = ambient.invariants()
        invsf = [x for x in ambient_invs if x>0]    ## fixes the problem with
        invs0 = [x for x in ambient_invs if x==0]   ## the infinite parts
        Ggens = list(ambient.variable_names())
        #print Ggens
        if invs0!=[]:
            Gfgens = [x for x in ambient.variable_names() if
                        ambient_invs[Ggens.index(x)]!=0]
            Ggens0 = [x for x in ambient.variable_names() if
                        ambient_invs[Ggens.index(x)]==0]
            #print invsf,Gfgens, Ggens0                ## ^^ only look at "finite" names
            Gf = AbelianGroup_class(len(invsf), invsf, names=Gfgens)
            #print Gf
            s1 = "G:= %s; gens := GeneratorsOfGroup(G)"%Gf._gap_init_()
            #print s1
            gap.eval(s1)
            Hgensf = [x for x in Hgens if len(set(Ggens0).intersection(set(list(str(x)))))==0]
            #print Hgensf
            for i in range(len(Gfgens)):
               cmd = ("%s := gens["+str(i+1)+"]")%Gfgens[i]
               #print i,"  \n",cmd
               gap.eval(cmd)
        if invs0==[]:
           Hgensf = Hgens
           G = ambient
           s1 = "G:= %s; gens := GeneratorsOfGroup(G)"%G._gap_init_()
           #print s1
           gap.eval(s1)
           for i in range(len(Ggens)):
               cmd = '%s := gens[%s]'%(Ggens[i], i+1)
               #print i,"  \n",cmd
               gap.eval(cmd)
        s2 = "gensH:=%s"%Hgensf #### remove from this the ones <--> 0 invar
        #print "s2 = ",s2
        gap.eval(s2)
        s3 = 'H:=Subgroup(G,gensH)'
        #print s3,"\n"
        gap.eval(s3)
        # a GAP command which returns the "invariants" of the
        # subgroup as an AbelianPcpGroup, RelativeOrdersOfPcp(Pcp(G)),
        # works if G is the subgroup declared as a AbelianPcpGroup
        self.__abinvs = eval(gap.eval("AbelianInvariants(H)"))
        invs = self.__abinvs
        if invs0!=[]:
            for x in invs0:
               invs.append(x)
        #print "invars: ",invs
        #print invs
        #eldivs = list(factor(invs[-1]))
        #print eldivs
        AbelianGroup_class.__init__(self, len(invs), invs, names)

    def __cmp__(self, right):
        r"""
        Compare self and other.  If self and other are in a common ambient group,
        then self <= other precisely if self is contained in other.

        EXAMPLES:
	    sage: G = AbelianGroup(3, [2,3,4], names="abc"); G
            Abelian group on 3 generators (a, b, c) with invariants [2, 3, 4]
	    sage: a,b,c = G.gens()
	    sage: F=G.subgroup([a,b^2])
	    sage: F<G
            True

        """
        if not is_AbelianGroup(right):
            return -1
        return cmp(self.invariants(), right.invariants())
        #other = right
        #if self is other:
        #    return 0
        #if not isinstance(other, AbelianGroup_class):
        #    return -1
        #c = cmp(self.ambient_group(), other.ambient_group())
        #if c: return c
        #if self.is_subgroup(other):
        #    return -1
        #else:
        #    return 1

    def _repr_(self):
        s = "Subgroup of %s generated by %s"%(self.ambient_group(), self.gens())
        return s

    def _latex_(self):
        r"""
        Return latex representation of this group.

        """
        return self._repr_()

    def ambient_group(self):
        """
        Return the ambient group related to self.

        """
        return self.__ambient_group

    def invs(self):
        """
        Return the invariants for this subgroup.

        """
        G = self.ambient_group()
        invsG = G.invariants()
        Hgap = self._gap_init_()

    def gens(self):
        """
        Return the generators for this subgroup.

        """
        return self.__gens
