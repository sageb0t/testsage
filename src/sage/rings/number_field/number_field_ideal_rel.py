"""
Relative Number Field Ideals

AUTHOR:
   -- Steven Sivek (2005-05-16)
   -- William Stein (2007-09-06)
   -- Nick Alexander (2009-01)

EXAMPLES:
    sage: K.<a,b> = NumberField([x^2 + 1, x^2 + 2])
    sage: A = K.absolute_field('z')
    sage: I = A.factor(3)[0][0]
    sage: from_A, to_A = A.structure()
    sage: G = [from_A(z) for z in I.gens()]; G
    [3, (-2*b - 1)*a + b - 1]
    sage: K.fractional_ideal(G)
    Fractional ideal ((-b + 1)*a - b - 2)
    sage: K.fractional_ideal(G).absolute_norm().factor()
    3^2
"""

#*****************************************************************************
#       Copyright (C) 2007 William Stein <wstein@gmail.com>
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

from number_field_ideal import NumberFieldFractionalIdeal, convert_from_zk_basis
from sage.structure.factorization import Factorization

import sage.rings.rational_field as rational_field
import sage.rings.integer_ring as integer_ring
QQ = rational_field.RationalField()
ZZ = integer_ring.IntegerRing()

class NumberFieldFractionalIdeal_rel(NumberFieldFractionalIdeal):
    """
    An ideal of a relative number field.

    EXAMPLES:
        sage: K.<a> = NumberField([x^2 + 1, x^2 + 2]); K
        Number Field in a0 with defining polynomial x^2 + 1 over its base field
        sage: i = K.ideal(38); i
        Fractional ideal (38)

    WARNING: Ideals in relative number fields are broken:
        sage: K.<a0, a1> = NumberField([x^2 + 1, x^2 + 2]); K
        Number Field in a0 with defining polynomial x^2 + 1 over its base field
        sage: i = K.ideal([a0+1]); i # random
        Fractional ideal (-a1*a0)
        sage: (g, ) = i.gens_reduced(); g # random
        -a1*a0
        sage: (g / (a0 + 1)).is_integral()
        True
        sage: ((a0 + 1) / g).is_integral()
        True
    """
    def __cmp__(self, other):
        """
        Compare an ideal of a relative number field to something else.

        EXAMPLES:
            sage: K.<a, b> = NumberField([x^2 + 23, x^2 - 7])
            sage: I = K.ideal(2, (a + 2*b + 3)/2)
            sage: J = K.ideal(2, a - b)
            sage: I == J
            False
        """
        if not isinstance(other, NumberFieldFractionalIdeal):
            return cmp(type(self), type(other))
        return cmp(self.pari_rhnf(), other.pari_rhnf())

    def _contains_(self, x):
        """
        Return True if x is an element of this ideal.

        This function is called (indirectly) when the \code{in}
        operator is used.

        EXAMPLES:
            sage: K.<a, b> = NumberField([x^2 + 23, x^2 - 7])
            sage: I = K.ideal(2, (a + 2*b + 3)/2)
            sage: [z in I for z in [a, b, 2, a + b]]
            [False, False, True, True]
        """
        abs_ideal = self.absolute_ideal()
        to_abs = abs_ideal.number_field().structure()[1]
        return to_abs(x) in abs_ideal

    def pari_rhnf(self):
        """
        Return PARI's representation of this relative ideal in Hermite
        normal form.

        EXAMPLES:

        """
        try:
            return self.__pari_rhnf
        except AttributeError:
            nf = self.number_field().absolute_field('a').pari_nf()
            rnf = self.number_field().pari_rnf()
            L_hnf = self.absolute_ideal().pari_hnf()
            self.__pari_rhnf = rnf.rnfidealabstorel(nf.getattr('zk')*L_hnf)
            return self.__pari_rhnf

    def absolute_ideal(self):
        """
        If this is an ideal in the extension L/K, return the ideal with
        the same generators in the absolute field L/Q.

        EXAMPLES:
            sage: x = ZZ['x'].0
            sage: K.<b> = NumberField(x^2 - 2)
            sage: L.<c> = K.extension(x^2 - b)
            sage: F = L.absolute_field('a')

            Let's check an inert ideal first:

            sage: P = F.factor(13)[0][0]; P
            Fractional ideal (13)
            sage: J = L.ideal(13)
            sage: J.absolute_ideal()
            Fractional ideal (13)

            Now how about a non-trivial ideal in L, but one that is
            actually principal in the subfield K:

            sage: J = L.ideal(b); J
            Fractional ideal (b)
            sage: J.absolute_ideal()
            Fractional ideal (a^2)
            sage: J.relative_norm()
            Fractional ideal (2)
            sage: J.absolute_norm()
            4
            sage: J.absolute_ideal().norm()
            4

            Now an ideal not generated by an element of K:

            sage: J = L.ideal(c); J
            Fractional ideal (c)
            sage: J.absolute_ideal()
            Fractional ideal (a)
            sage: J.absolute_norm()
            2
            sage: J.ideal_below()
            Fractional ideal (b)
            sage: J.ideal_below().norm()
            2
        """
        try:
            return self.__absolute_ideal
        except AttributeError:
            L = self.number_field().absolute_field('a')
            genlist = [ L( x.polynomial() ) for x in self.gens() ]
            self.__absolute_ideal = L.ideal(genlist)
            return self.__absolute_ideal

    def _from_absolute_ideal(self, id):
        r"""
        Convert the absolute ideal id to a relative number field ideal.

        Assumes id.number_field() == self.absolute_field('a').

        WARNING:  This is an internal helper function.

        TESTS:
            sage: L.<a, b> = QQ.extension([x^2 + 71, x^3 + 2*x + 1])
            sage: (2*a + b).norm()
            22584817
            sage: J = L.ideal(2*a + b); J
            Fractional ideal (22584817, a - b - 120132)
            sage: (2*a + b) in J
            True
            sage: J.absolute_norm()
            22584817
            sage: J.absolute_ideal()
            Fractional ideal (188/812911*a^5 - 1/812911*a^4 + 45120/812911*a^3 - 56/73901*a^2 + 3881638/812911*a + 50041/812911)
            sage: J.absolute_ideal().norm()
            22584817

            sage: J._from_absolute_ideal(J.absolute_ideal()) == J
            True
        """
        L = self.number_field()
        K = L.absolute_field('a')
        to_L = K.structure()[0]
        return L.ideal([to_L(g) for g in id.gens()])

    def free_module(self):
        return self.absolute_ideal().free_module()

    def gens_reduced(self):
        try:
            return self.__reduced_generators
        except AttributeError:
            L = self.number_field()
            K = L.base_field()
            R = L.relative_polynomial().parent()
            S = L['x']
            gens = L.pari_rnf().rnfidealtwoelt(self.pari_rhnf())
            gens = [ L(R(x.lift().lift())) for x in gens ]

            # pari always returns two elements, even if only one is needed!
            if gens[1] in L.ideal([ gens[0] ]):
                gens = [ gens[0] ]
            elif gens[0] in L.ideal([ gens[1] ]):
                gens = [ gens[1] ]
            self.__reduced_generators = tuple(gens)
            return self.__reduced_generators

    def __invert__(self):
        """
        Return the multiplicative inverse of self.  Call with ~self.

        EXAMPLES:
            sage: K.<a,b> = NumberField([x^2 + 1, x^2 + 2])
            sage: I = K.fractional_ideal(4)
            sage: I^(-1)
            Fractional ideal (1/4)
            sage: I * I^(-1)
            Fractional ideal (1)
        """
        if self.is_zero():
            raise ZeroDivisionError
        return self._from_absolute_ideal( self.absolute_ideal().__invert__() )

    def is_principal(self):
        return self.absolute_ideal().is_principal()

    def is_zero(self):
        zero = self.number_field().pari_rnf().rnfidealhnf(0)
        return self.pari_rhnf() == zero

    def absolute_norm(self):
        """
        Compute the absolute norm of this fractional ideal in a relative number
        field, returning a positive integer.

        EXAMPLES:
            sage: L.<a, b, c> = QQ.extension([x^2 - 23, x^2 - 5, x^2 - 7])
            sage: I = L.ideal(a + b)
            sage: I.absolute_norm()
            104976
            sage: I.relative_norm().relative_norm().relative_norm()
            104976
        """
        return self.absolute_ideal().norm()

    def relative_norm(self):
        """
        Compute the relative norm of this fractional ideal in a relative number
        field, returning an ideal in the base field.

        EXAMPLES:
            sage: R.<x> = QQ[]
            sage: K.<a> = NumberField(x^2+6)
            sage: L.<b> = K.extension(K['x'].gen()^4 + a)
            sage: N = L.ideal(b).relative_norm(); N
            Fractional ideal (-a)
            sage: N.parent()
            Monoid of ideals of Number Field in a with defining polynomial x^2 + 6
            sage: N.ring()
            Number Field in a with defining polynomial x^2 + 6
            sage: PQ.<X> = QQ[]
            sage: F.<a, b> = NumberField([X^2 - 2, X^2 - 3])
            sage: PF.<Y> = F[]
            sage: K.<c> = F.extension(Y^2 - (1 + a)*(a + b)*a*b)
            sage: K.ideal(1).relative_norm()
            Fractional ideal (1)
            sage: K.ideal(13).relative_norm().relative_norm()
            Fractional ideal (28561)
            sage: K.ideal(13).relative_norm().relative_norm().relative_norm()
            815730721
            sage: K.ideal(13).absolute_norm()
            815730721
        """
        L = self.number_field()
        K = L.base_field()
        K_abs = K.absolute_field('a')
        to_K = K_abs.structure()[0]
        R = K_abs.polynomial().parent()
        hnf = L.pari_rnf().rnfidealnormrel(self.pari_rhnf())
        return K.ideal([ to_K(K_abs(R(x))) for x in convert_from_zk_basis(K, hnf) ])

    def norm(self):
        """
        The norm of a fractional ideal in a relative number field is deliberately
        unimplemented, so that a user cannot mistake the absolute norm
        for the relative norm, or vice versa.
        """
        raise NotImplementedError, "For a fractional ideal in a relative number field you must use relative_norm or absolute_norm as appropriate"

    def ideal_below(self):
        """
        Compute the ideal of K below this ideal of L.

        EXAMPLES:
            sage: R.<x> = QQ[]
            sage: K.<a> = NumberField(x^2+6)
            sage: L.<b> = K.extension(K['x'].gen()^4 + a)
            sage: N = L.ideal(b)
            sage: M = N.ideal_below(); M == K.ideal([-a])
            True
            sage: Np = L.ideal( [ L(t) for t in M.gens() ])
            sage: Np.ideal_below() == M
            True
            sage: M.parent()
            Monoid of ideals of Number Field in a with defining polynomial x^2 + 6
            sage: M.ring()
            Number Field in a with defining polynomial x^2 + 6
            sage: M.ring() is K
            True

            This example concerns an inert ideal:

            sage: K = NumberField(x^4 + 6*x^2 + 24, 'a')
            sage: K.factor(7)
            Fractional ideal (7)
            sage: K0, K0_into_K, _ = K.subfields(2)[0]
            sage: K0
            Number Field in a0 with defining polynomial x^2 - 6*x + 24
            sage: L = K.relativize(K0_into_K, 'c'); L
            Number Field in c0 with defining polynomial x^2 + a0 over its base field
            sage: L.base_field() is K0
            True
            sage: L.ideal(7)
            Fractional ideal (7)
            sage: L.ideal(7).ideal_below()
            Fractional ideal (7)
            sage: L.ideal(7).ideal_below().number_field() is K0
            True

            This example concerns an ideal that splits in the quadratic field
            but each factor ideal remains inert in the extension:

            sage: len(K.factor(19))
            2
            sage: K0 = L.base_field(); a0 = K0.gen()
            sage: len(K0.factor(19))
            2
            sage: w1 = -a0 + 1; P1 = K0.ideal([w1])
            sage: P1.norm().factor(), P1.is_prime()
            (19, True)
            sage: L_into_K, K_into_L = L.structure()
            sage: L.ideal(K_into_L(K0_into_K(w1))).ideal_below() == P1
            True

            The choice of embedding of quadratic field into quartic field
            matters:

            sage: rho, tau = K0.embeddings(K)
            sage: L1 = K.relativize(rho, 'b')
            sage: L2 = K.relativize(tau, 'b')
            sage: L1_into_K, K_into_L1 = L1.structure()
            sage: L2_into_K, K_into_L2 = L2.structure()
            sage: a = K.gen()
            sage: P = K.ideal([a^2 + 5])
            sage: K_into_L1(P).ideal_below() == K0.ideal([-a0 + 1])
            True
            sage: K_into_L2(P).ideal_below() == K0.ideal([-a0 + 5])
            True
            sage: K0.ideal([-a0 + 1]) == K0.ideal([-a0 + 5])
            False

            It works when the base_field is itself a relative number field
            sage: PQ.<X> = QQ[]
            sage: F.<a, b> = NumberFieldTower([X^2 - 2, X^2 - 3])
            sage: PF.<Y> = F[]
            sage: K.<c> = F.extension(Y^2 - (1 + a)*(a + b)*a*b)
            sage: I = K.ideal(3, c)
            sage: J = I.ideal_below(); J
            Fractional ideal (-b*a + 3)
            sage: J.number_field() == F
            True
        """
        L = self.number_field()
        K = L.base_field()
        K_abs = K.absolute_field('a')
        to_K = K_abs.structure()[0]
        R = K_abs.polynomial().parent()
        hnf = L.pari_rnf().rnfidealdown(self.pari_rhnf())
        return K.ideal([ to_K(K_abs(R(x))) for x in convert_from_zk_basis(K, hnf) ])

    def factor(self):
        """
        Factor the ideal by factoring the corresponding ideal
        in the absolute number field.

        EXAMPLES:
            sage: K.<a, b> = QQ.extension([x^2 + 11, x^2 - 5])
            sage: K.factor(5)
            (Fractional ideal (5, 1/2*a - 1/2*b - 1))^2 * (Fractional ideal (5, 1/2*a - 1/2*b + 1))^2
            sage: K.ideal(5).factor()
            (Fractional ideal (5, 1/2*a - 1/2*b - 1))^2 * (Fractional ideal (5, 1/2*a - 1/2*b + 1))^2
            sage: K.ideal(5).prime_factors()
            [Fractional ideal (5, 1/2*a - 1/2*b - 1),
             Fractional ideal (5, 1/2*a - 1/2*b + 1)]

            sage: PQ.<X> = QQ[]
            sage: F.<a, b> = NumberFieldTower([X^2 - 2, X^2 - 3])
            sage: PF.<Y> = F[]
            sage: K.<c> = F.extension(Y^2 - (1 + a)*(a + b)*a*b)
            sage: K.ideal(c)
            Fractional ideal (6, -2*c + (171/2*b + 291/2)*a + 117*b + 216)
            sage: K.ideal(c).factor()
            (Fractional ideal (2, ((-13*b - 45/2)*a - 37/2*b - 63/2)*c + 1))^2 * (Fractional ideal (3, c))
        """
        F = self.number_field()
        abs_ideal = self.absolute_ideal()
        to_F = abs_ideal.number_field().structure()[0]
        factor_list = [(F.ideal([to_F(g) for g in p.gens()]), e) for p, e in abs_ideal.factor()]
        # sorting and simplification will already have been done
        return Factorization(factor_list, sort=False, simplify=False)

    def integral_basis(self):
        raise NotImplementedError

    def integral_split(self):
        """
        Return a tuple (I, d), where I is an integral ideal, and d is the
        smallest positive integer such that this ideal is equal to I/d.

        EXAMPLES:
            sage: K.<a, b> = NumberFieldTower([x^2 - 23, x^2 + 1])
            sage: I = K.ideal([a + b/3])
            sage: J, d = I.integral_split()
            sage: J.is_integral()
            True
            sage: J == d*I
            True

        """
        d = self.absolute_ideal().integral_split()[1]
        return (d*self, d)

    def is_prime(self):
        """
        Return True if this ideal of a relative number field is prime.

        EXAMPLES:
            sage: K.<a, b> = NumberField([x^2 - 17, x^3 - 2])
            sage: K.ideal(a + b).is_prime()
            True
            sage: K.ideal(13).is_prime()
            False
        """
        return self.absolute_ideal().is_prime()

    def is_integral(self):
        """
        Return True if this ideal is integral.

        EXAMPLES:
           sage: K.<a, b> = QQ.extension([x^2 + 11, x^2 - 5])
           sage: I = K.ideal(7).prime_factors()[0]
           sage: I.is_integral()
           True
           sage: (I/2).is_integral()
           False
        """
        return self.absolute_ideal().is_integral()

    def absolute_ramification_index(self):
        """
        Return the absolute ramification index of this fractional ideal,
        assuming it is prime.  Otherwise, raise a ValueError.

        The absolute ramification index is the power of this prime
        appearing in the factorization of the rational prime that
        this prime lies over.

        Use relative_ramification_index to obtain the power of this
        prime occurring in the factorization of the prime ideal
        of the  base field that this prime lies over.

        EXAMPLES:
            sage: PQ.<X> = QQ[]
            sage: F.<a, b> = NumberFieldTower([X^2 - 2, X^2 - 3])
            sage: PF.<Y> = F[]
            sage: K.<c> = F.extension(Y^2 - (1 + a)*(a + b)*a*b)
            sage: I = K.ideal(3, c)
            sage: I.absolute_ramification_index()
            4
            sage: I.smallest_integer()
            3
            sage: K.ideal(3) == I^4
            True
        """
        if self.is_prime():
            return self.absolute_ideal().ramification_index()
        raise ValueError, "the fractional ideal (= %s) is not prime"%self

    def relative_ramification_index(self):
        """
        Return the relative ramification index of this fractional ideal,
        assuming it is prime.  Otherwise, raise a ValueError.

        The relative ramification index is the power of this prime
        appearing in the factorization of the prime ideal of the
        base field that this prime lies over.

        Use absolute_ramification_index to obtain the power of this
        prime occurring in the factorization of the rational prime
        that this prime lies over.

        EXAMPLES:
            sage: PQ.<X> = QQ[]
            sage: F.<a, b> = NumberFieldTower([X^2 - 2, X^2 - 3])
            sage: PF.<Y> = F[]
            sage: K.<c> = F.extension(Y^2 - (1 + a)*(a + b)*a*b)
            sage: I = K.ideal(3, c)
            sage: I.relative_ramification_index()
            2
            sage: I.ideal_below()
            Fractional ideal (-b*a + 3)
            sage: K.ideal(-b*a + 3) == I^2
            True
        """
        if self.is_prime():
            abs_index = self.absolute_ramification_index()
            base_ideal = self.ideal_below()
            return ZZ(abs_index/base_ideal.absolute_ramification_index())
        raise ValueError, "the fractional ideal (= %s) is not prime"%self

    def ramification_index(self):
        """
        For ideals in relative number fields ramification_index is
        deliberately not implemented in order to avoid ambiguity.  Either
        relative_ramification_index or absolute_ramification_index should
        be used instead.
        """
        raise NotImplementedError, "For an ideal in a relative number field you must use relative_ramification_index or absolute_ramification_index as appropriate"

    def residue_class_degree(self):
        """
        EXAMPLES:
            sage: PQ.<X> = QQ[]
            sage: F.<a, b> = NumberFieldTower([X^2 - 2, X^2 - 3])
            sage: PF.<Y> = F[]
            sage: K.<c> = F.extension(Y^2 - (1 + a)*(a + b)*a*b)
            sage: [I.residue_class_degree() for I in K.ideal(c).prime_factors()]
            [1, 2]
         """
        if self.is_prime():
            return self.absolute_ideal().residue_class_degree()
        raise ValueError, "the ideal (= %s) is not prime"%self

    def residues(self):
        """
        Returns a iterator through a complete list of residues modulo this integral ideal.

        An error is raised if this fractional ideal is not integral.

        EXAMPLES:
            sage: K.<a, w> = NumberFieldTower([x^2 - 3, x^2 + x + 1])
            sage: I = K.ideal(6, -w*a - w + 4)
            sage: list(I.residues())[:5]
            [(-10/3*w - 8/3)*a,
             (-10/3*w - 8/3)*a + 1,
             (-10/3*w - 8/3)*a + 2,
             (-10/3*w - 8/3)*a + 3,
             (-10/3*w - 8/3)*a + 4]
        """
        abs_ideal = self.absolute_ideal()
        from_abs = abs_ideal.number_field().structure()[0]
        from sage.misc.mrange import xmrange_iter
        abs_residues = abs_ideal.residues()
        return xmrange_iter(abs_residues.iter_list, lambda c: from_abs(abs_residues.typ(c)))

    def element_1_mod(self, other):
        """
        Returns an element r in this ideal such that 1-r is in other.

        An error is raised if either ideal is not integral of if they
        are not coprime.

        INPUT:
            other -- another ideal of the same field, or generators of an ideal.
        OUTPUT:
            r -- an element of the ideal self such that 1-r is in the ideal other.

        EXAMPLES:
            sage: K.<a, b> = NumberFieldTower([x^2 - 23, x^2 + 1])
            sage: I = Ideal(2, (a - 3*b + 2)/2)
            sage: J = K.ideal(a)
            sage: z = I.element_1_mod(J); z
            -8*b*a + 24
            sage: z in I
            True
            sage: 1 - z in J
            True
        """
        # Catch invalid inputs by making sure that we can make an ideal out of other.
        K = self.number_field()
        if not self.is_integral():
            raise TypeError, "%s is not an integral ideal"%self

        other = K.ideal(other)
        if not other.is_integral():
            raise TypeError, "%s is not an integral ideal"%other

        if not self.is_coprime(other):
            raise TypeError, "%s and %s are not coprime ideals"%(self, other)

        to_K = K.absolute_field('a').structure()[0]
        return to_K(self.absolute_ideal().element_1_mod(other.absolute_ideal()))

    def smallest_integer(self):
        r"""
        Return the smallest non-negative integer in $I \cap \mathbb{Z}$,
        where $I$ is this ideal.  If $I = 0$, returns $0$.

        EXAMPLES:
            sage: K.<a, b> = NumberFieldTower([x^2 - 23, x^2 + 1])
            sage: I = K.ideal([a + b])
            sage: I.smallest_integer()
            12
            sage: [m for m in range(13) if m in I]
            [0, 12]
        """
        return self.absolute_ideal().smallest_integer()

    def valuation(self, p):
        r"""
        Return the valuation of this fractional ideal at the prime
        $\mathfrak{p}$.  If $\mathfrak{p}$ is not prime, raise a
        ValueError.

        INPUT:
            p -- a prime ideal of this relative number field.

        OUTPUT:
            integer

        EXAMPLES:
            sage: K.<a, b> = NumberField([x^2 - 17, x^3 - 2])
            sage: A = K.ideal(a + b)
            sage: A.is_prime()
            True
            sage: (A*K.ideal(3)).valuation(A)
            1
            sage: K.ideal(25).valuation(5)
            Traceback (most recent call last):
            ...
            ValueError: p (= Fractional ideal (5)) must be a prime
         """
        if p == 0:
            raise ValueError, "p (= %s) must be nonzero"%p
        if not isinstance(p, NumberFieldFractionalIdeal):
            p = self.number_field().ideal(p)
        if not p.is_prime():
            raise ValueError, "p (= %s) must be a prime"%p
        if p.ring() != self.number_field():
            raise ValueError, "p (= %s) must be an ideal in %s"%self.number_field()
        return self.absolute_ideal().valuation(p.absolute_ideal())

def is_NumberFieldFractionalIdeal_rel(x):
    """
    Return True if x is a fractional ideal of a relative number field.

    EXAMPLES:
        sage: from sage.rings.number_field.number_field_ideal_rel import is_NumberFieldFractionalIdeal_rel
        sage: from sage.rings.number_field.number_field_ideal import is_NumberFieldFractionalIdeal
        sage: is_NumberFieldFractionalIdeal_rel(2/3)
        False
        sage: is_NumberFieldFractionalIdeal_rel(ideal(5))
        False
        sage: k.<a> = NumberField(x^2 + 2)
        sage: I = k.ideal([a + 1]); I
        Fractional ideal (a + 1)
        sage: is_NumberFieldFractionalIdeal_rel(I)
        False
        sage: R.<x> = QQ[]
        sage: K.<a> = NumberField(x^2+6)
        sage: L.<b> = K.extension(K['x'].gen()^4 + a)
        sage: I = L.ideal(b); I
        Fractional ideal (b)
        sage: is_NumberFieldFractionalIdeal_rel(I)
        True
        sage: N = I.relative_norm(); N
        Fractional ideal (-a)
        sage: is_NumberFieldFractionalIdeal_rel(N)
        False
        sage: is_NumberFieldFractionalIdeal(N)
        True
    """
    return isinstance(x, NumberFieldFractionalIdeal_rel)
