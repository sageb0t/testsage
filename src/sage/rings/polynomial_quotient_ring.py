"""
Quotients of Univariate Polynomial Rings

EXAMPLES:
    sage: R = PolynomialRing(RationalField(), 'x'); x = R.gen()
    sage: S = R.quotient(x**3-3*x+1, 'alpha')
    sage: S.gen()**2 in S
    True
    sage: x in S
    True
    sage: S.gen() in R
    False
    sage: 1 in S
    True
"""

#*****************************************************************************
#       Copyright (C) 2005 William Stein <wstein@gmail.com>
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

import number_field.all
import polynomial_element
import polynomial_ring
import rational_field
import complex_field

import commutative_ring
import field
import integral_domain

import polynomial_quotient_ring_element

def PolynomialQuotientRing(ring, polynomial, names=None):
    r"""
    Create a quotient of a polynomial ring.

    INPUT:
        ring -- a univariate polynomial ring in one variable.
        polynomial -- element
        names -- (optional) name for the variable

    OUTPUT:
        Creates the quotient ring R/I, where R is the ring and I is
        the principal ideal generated by the polynomial.

    EXAMPLES:

    We create the quotient ring $\Z[x]/(x^3+7)$, and demonstrate many
    basic functions with it:

        sage: Z = IntegerRing()
        sage: R = PolynomialRing(Z,'x'); x = R.gen()
        sage: S = R.quotient(x^3 + 7, 'a'); a = S.gen()
        sage: S
        Univariate Quotient Polynomial Ring in a over Integer Ring with modulus x^3 + 7
        sage: a^3
        -7
        sage: S.is_field()
        False
        sage: a in S
        True
        sage: x in S
        True
        sage: a in R
        False
        sage: S.polynomial_ring()
        Univariate Polynomial Ring in x over Integer Ring
        sage: S.modulus()
        x^3 + 7
        sage: S.degree()
        3

    We create the ``iterated'' polynomial ring quotient
    $$
           R = (\F_2[y]/(y^{2}+y+1))[x]/(x^3 - 5).
    $$

        sage: A.<y> = PolynomialRing(GF(2)); A
        Univariate Polynomial Ring in y over Finite Field of size 2
        sage: B = A.quotient(y^2 + y + 1, 'y2'); print B
        Univariate Quotient Polynomial Ring in y2 over Finite Field of size 2 with modulus y^2 + y + 1
        sage: C = PolynomialRing(B, 'x'); x=C.gen(); print C
        Univariate Polynomial Ring in x over Univariate Quotient Polynomial Ring in y2 over Finite Field of size 2 with modulus y^2 + y + 1
        sage: R = C.quotient(x^3 - 5); print R
        Univariate Quotient Polynomial Ring in xbar over Univariate Quotient Polynomial Ring in y2 over Finite Field of size 2 with modulus y^2 + y + 1 with modulus x^3 + 1

    Next we create a number field, but viewed as a quotient of a
    polynomial ring over $\Q$:
        sage: R = PolynomialRing(RationalField(), 'x'); x = R.gen()
        sage: S = R.quotient(x^3 + 2*x - 5, 'a')
        sage: S
        Univariate Quotient Polynomial Ring in a over Rational Field with modulus x^3 + 2*x - 5
        sage: S.is_field()
        True
        sage: S.degree()
        3

    There are conversion functions for easily going back and forth
    between quotients of polynomial rings over $\Q$ and number
    fields:
        sage: K = S.number_field(); K
        Number Field in a with defining polynomial x^3 + 2*x - 5
        sage: K.polynomial_quotient_ring()
        Univariate Quotient Polynomial Ring in a over Rational Field with modulus x^3 + 2*x - 5

    The leading coefficient must be a unit (but need not be 1).
        sage: R = PolynomialRing(Integers(9), 'x'); x = R.gen()
        sage: S = R.quotient(2*x^4 + 2*x^3 + x + 2, 'a')
        sage: S = R.quotient(3*x^4 + 2*x^3 + x + 2, 'a')
        Traceback (most recent call last):
        ...
        TypeError: polynomial must have unit leading coefficient

    Another example:
        sage: R.<x> = PolynomialRing(IntegerRing())
        sage: f = x^2 + 1
        sage: R.quotient(f)
        Univariate Quotient Polynomial Ring in xbar over Integer Ring with modulus x^2 + 1
    """
    if not isinstance(ring, polynomial_ring.PolynomialRing_generic):
        raise TypeError, "ring must be a polynomial ring"
    if not isinstance(polynomial, polynomial_element.Polynomial):
        raise TypeError, "must be a polynomial"
    if not polynomial.parent() == ring:
        raise TypeError, "polynomial must be in ring"
    c = polynomial.leading_coefficient()
    if not c.is_unit():
        raise TypeError, "polynomial must have unit leading coefficient"
    R = ring.base_ring()
    if isinstance(R, integral_domain.IntegralDomain):
        try:
            if polynomial.is_irreducible():
                if isinstance(R, field.Field):
                    return PolynomialQuotientRing_field(ring, polynomial, names)
                else:
                    return PolynomialQuotientRing_domain(ring, polynomial, names)
        except NotImplementedError:   # is_irreducible sometimes not implemented
            pass
    return PolynomialQuotientRing_generic(ring, polynomial, names)

def is_PolynomialQuotientRing(x):
    return isinstance(x, PolynomialQuotientRing_generic)

class PolynomialQuotientRing_generic(commutative_ring.CommutativeRing):
    """
    Quotient of a univariate polynomial ring by an ideal.

    EXAMPLES:
        sage: R.<x> = PolynomialRing(Integers(8)); R
        Univariate Polynomial Ring in x over Ring of integers modulo 8
        sage: S.<xbar> = R.quotient(x^2 + 1); S
        Univariate Quotient Polynomial Ring in xbar over Ring of integers modulo 8 with modulus x^2 + 1

    We demonstrate object persistence.
        sage: loads(S.dumps()) == S
        True
        sage: loads(xbar.dumps()) == xbar
        True

    We create some sample homomorphisms;
        sage: R.<x> = PolynomialRing(ZZ)
        sage: S = R/(x^2-4)
        sage: f = S.hom([2])
        sage: f
        Ring morphism:
          From: Univariate Quotient Polynomial Ring in xbar over Integer Ring with modulus x^2 - 4
          To:   Integer Ring
          Defn: xbar |--> 2
        sage: f(x)
        2
        sage: f(x^2 - 4)
        0
        sage: f(x^2)
        4
    """
    def __init__(self, ring, polynomial, name=None):
        if not isinstance(ring, polynomial_ring.PolynomialRing_generic):
            raise TypeError, "R must be a univariate polynomial ring."

        if not isinstance(polynomial, polynomial_element.Polynomial):
            raise TypeError, "f must be a Polynomial"

        if polynomial.parent() != ring:
            raise TypeError, "f must have parent R"

        self.__ring = ring
        self.__polynomial = polynomial
        self._assign_names(name)

    def __reduce__(self):
        return PolynomialQuotientRing_generic, (self.__ring, self.__polynomial, self.variable_names())

    def __call__(self, x):
        """
        Coerce x into this quotient ring.  Anything that can be
        coerced into the polynomial ring can be coerced into the
        quotient.

        INPUT:
            x -- object to be coerced

        OUTPUT:
            an element obtained by coercing x into this ring.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(QQ)
            sage: S.<alpha> = R.quotient(x^3-3*x+1)
            sage: S(x)
            alpha
            sage: S(x^3)
            3*alpha - 1
            sage: S([1,2])
            2*alpha + 1
            sage: S([1,2,3,4,5])
            18*alpha^2 + 9*alpha - 3
            sage: S(S.gen()+1)
            alpha + 1
            sage: S(S.gen()^10+1)
            90*alpha^2 - 109*alpha + 28
        """
        if isinstance(x, polynomial_quotient_ring_element.PolynomialQuotientRingElement):
            if x.parent() == self:
                return x
        return polynomial_quotient_ring_element.PolynomialQuotientRingElement(
                        self, self.__ring(x) , check=True)

    def _is_valid_homomorphism_(self, codomain, im_gens):
        try:
            # We need that elements of the base ring of the polynomial
            # ring map canonically into codomain.

            codomain._coerce_(self.base_ring()(1))

            # We also need that the polynomial modulus maps to 0.
            f = self.modulus()
            return codomain(f(im_gens[0])) == 0
        except TypeError, ValueError:
            return False

    def _coerce_(self, x):
        """
        Return the coercion of x into this polynomial quotient ring.

        The rings that coerce into the quotient ring canonically, are:

           * this ring,
           * anything that coerces into the ring of which this is the quotient

        """
        try:
            P = x.parent()
            # this ring itself:
            if P is self: return x
            if P == self: return self(x)
        except AttributeError:
            pass

        # any ring that coerces to the base ring of this polynomial ring.
        return self._coerce_try(x, [self.polynomial_ring()])

    def __cmp__(self, other):
        """
        Compare self and other.

        EXAMPLES:
            sage: Rx.<x> = PolynomialRing(QQ)
            sage: Ry.<y> = PolynomialRing(QQ)
            sage: Rx == Ry
            False
            sage: Qx = Rx.quotient(x^2+1)
            sage: Qy = Ry.quotient(y^2+1)
            sage: Qx == Qy
            False
            sage: Qx == Qx
            True
            sage: Qz = Rx.quotient(x^2+1)
            sage: Qz == Qx
            True
        """
        if not isinstance(other, PolynomialQuotientRing_generic):
            return -1
        if self.polynomial_ring() != other.polynomial_ring():
            return -1
        return self.modulus().__cmp__(other.modulus())

    def __repr__(self):
        return "Univariate Quotient Polynomial Ring in %s over %s with modulus %s"%(
            self.variable_name(), self.base_ring(), self.modulus())

    def base_ring(self):
        r"""
        Return the base base ring of the polynomial ring, of which
        this ring is a quotient.

        EXAMPLES:
        The base ring of $\Z[z]/(z^3 + z^2 + z + 1)$ is $\Z$.
            sage: R.<z> = PolynomialRing(ZZ)
            sage: S.<beta> = R.quo(z^3 + z^2 + z + 1)
            sage: S.base_ring()
            Integer Ring

        Next we make a polynomial quotient ring over $S$ and ask for its basering.
            sage: T.<t> = PolynomialRing(S)
            sage: W = T.quotient(t^99 + 99)
            sage: W.base_ring()
            Univariate Quotient Polynomial Ring in beta over Integer Ring with modulus z^3 + z^2 + z + 1
        """
        return self.__ring.base_ring()

    def characteristic(self):
        """
        Return the characteristic of this quotient ring.

        This is always the same as the characteristic of the base ring.

        EXAMPLES:
            sage: R.<z> = PolynomialRing(ZZ)
            sage: S.<a> = R.quo(z - 19)
            sage: S.characteristic()
            0
            sage: R.<x> = PolynomialRing(GF(9,'a'))
            sage: S = R.quotient(x^3 + 1)
            sage: S.characteristic()
            3
        """
        return self.base_ring().characteristic()

    def degree(self):
        """
        Return the degree of this quotient ring.  The degree is the
        degree of the polynomial that we quotiented out by.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(GF(3))
            sage: S = R.quotient(x^2005 + 1)
            sage: S.degree()
            2005
        """
        return self.modulus().degree()

    def discriminant(self, v=None):
        """
        Return the discriminant of this ring over the base ring.  This
        is by definition the discriminant of the polynomial that we
        quotiented out by.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(QQ)
            sage: S = R.quotient(x^3 + x^2 + x + 1)
            sage: S.discriminant()
            -16
            sage: S = R.quotient((x + 1) * (x + 1))
            sage: S.discriminant()
            0

        The discriminant of the quotient polynomial ring need not
        equal the discriminant of the corresponding number field,
        since the discriminant of a number field is by definition the
        discriminant of the ring ring of integers of the number field:
            sage: S = R.quotient(x^2 - 8)
            sage: S.number_field().discriminant()
            8
            sage: S.discriminant()
            32
        """
        return self.modulus().discriminant()

    def gen(self, n=0):
        """
        Return the generator of this quotient ring.  This is the
        equivalence class of the image of the generator of the
        polynomial ring.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(QQ)
            sage: S = R.quotient(x^2 - 8, 'gamma')
            sage: S.gen()
            gamma
        """
        if n != 0:
            raise IndexError, "Only one generator."
        try:
            return self.__gen
        except AttributeError:
            self.__gen = self(self.polynomial_ring().gen())
            return self.__gen

    def is_field(self):
        """
        Return whether or not this quotient ring is a field.

        EXAMPLES:
            sage: R.<z> = PolynomialRing(ZZ)
            sage: S = R.quo(z^2-2)
            sage: S.is_field()
            False
            sage: R.<x> = PolynomialRing(QQ)
            sage: S = R.quotient(x^2 - 2)
            sage: S.is_field()
            True
        """
        return self.base_ring().is_field() and self.modulus().is_irreducible()

    def krull_dimension(self):
        return self.base_ring().krull_dimension()

    def modulus(self):
        """
        Return the polynomial modulus of this quotient ring.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(GF(3))
            sage: S = R.quotient(x^2 - 2)
            sage: S.modulus()
            x^2 + 1
        """
        return self.__polynomial

    def ngens(self):
        """
        Return the number of generators of this quotient ring over the
        base ring.  This function always returns 1.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(QQ)
            sage: S = PolynomialRing(R, 'y'); y = S.gen()
            sage: T = S.quotient(y + x, 'z')
            sage: T
            Univariate Quotient Polynomial Ring in z over Univariate Polynomial Ring in x over Rational Field with modulus y + x
            sage: T.ngens()
            1
        """
        return 1

    def number_field(self):
        """
        Return the number field isomorphic to this quotient polynomial
        ring, if possible.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(QQ)
            sage: S.<alpha> = R.quotient(x^29 - 17*x - 1)
            sage: K = S.number_field()
            sage: K
            Number Field in alpha with defining polynomial x^29 - 17*x - 1
            sage: alpha = K.gen()
            sage: alpha^29
            17*alpha + 1
        """
        if self.characteristic() != 0:
            raise ArithmeticError, "Polynomial quotient ring is not isomorphic to a number field (it has positive characteristic)."

        if not isinstance(self.base_ring(), rational_field.RationalField):
            raise NotImplementedError, "Computation of number field only implemented for quotients of the polynomial ring over the rational field."
        return number_field.all.NumberField(self.modulus(), self.variable_name())

    def polynomial_ring(self):
        """
        Return the polynomial ring of which this ring is the quotient.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(QQ)
            sage: S = R.quotient(x^2-2)
            sage: S.polynomial_ring()
            Univariate Polynomial Ring in x over Rational Field
        """
        return self.__ring

class PolynomialQuotientRing_domain(PolynomialQuotientRing_generic, integral_domain.IntegralDomain):
    """
    EXAMPLES:
        sage: R.<x> = PolynomialRing(ZZ)
        sage: S.<xbar> = R.quotient(x^2 + 1)
        sage: S
        Univariate Quotient Polynomial Ring in xbar over Integer Ring with modulus x^2 + 1
        sage: loads(S.dumps()) == S
        True
        sage: loads(xbar.dumps()) == xbar
        True
    """
    def __init__(self, ring, polynomial, name=None):
        PolynomialQuotientRing_generic.__init__(self, ring, polynomial, name)

    def __reduce__(self):
        return PolynomialQuotientRing_domain, (self.polynomial_ring(),
                                         self.modulus(), self.variable_names())

    def field_extension(self, names):
        r"""
        Takes a polynomial defined in a quotient ring, and returns
        a tuple with three elements: the NumberField defined by the
        same polynomial, a homomorphism from its parent to the
	NumberField sending the generators to one another, and the
	inverse isomorphism.

        For some reason, we first implemented this as a method
        for an element, instead of for the quotient ring.

        OUTPUT:
            -- field
            -- homomorphism from self to field
            -- homomorphism from field to self

        EXAMPLES:
            sage: R.<x> = PolynomialRing(Rationals())
            sage: S.<alpha> = R.quotient(x^3-2)
            sage: F.<b>, f, g = S.field_extension()
            sage: F
            Number Field in b with defining polynomial x^3 - 2
            sage: a = F.gen()
            sage: f(alpha)
            b
            sage: g(a)
            alpha

        We do another example over $\ZZ$.
            sage: R.<x> = ZZ['x']
            sage: S.<a> = R.quo(x^3 - 2)
            sage: F.<b>, g, h = S.field_extension()
            sage: h(F.0^2 + 3)
            a^2 + 3
            sage: g(x^2 + 2)
            b^2 + 2

        Note that the homomorphism is not defined on the entire
        ''domain''.   (Allowing creation of such functions may be
        disallowed in a future version of SAGE.):
            sage: h(1/3)
            Traceback (most recent call last):
            ...
            TypeError: Unable to coerce rational (=1/3) to an Integer.

        Note that the parent ring must be an integral domain:
            sage: R.<x> = GF(25,'f25')['x']
            sage: S.<a> = R.quo(x^3 - 2)
            sage: F, g, h = S.field_extension('b')
            Traceback (most recent call last):
            ...
            AttributeError: 'PolynomialQuotientRing_generic' object has no attribute 'field_extension'

        Over a finite field, the corresponding field extension is
        not a number field:

            sage: R.<x> = GF(25, 'a')['x']
            sage: S.<a> = R.quo(x^3 + 2*x + 1)
            sage: F, g, h = S.field_extension('b')
            sage: h(F.0^2 + 3)
            a^2 + 3
            sage: g(x^2 + 2)
            b^2 + 2

        We do an example involving a relative number field, which
        doesn't work since the relative extension generator doesn't
        generate the absolute extension.
            sage: R.<x> = QQ['x']
            sage: K.<a> = NumberField(x^3-2)
            sage: S.<X> = K['X']
            sage: Q.<b> = S.quo(X^3 + 2*X + 1)
            sage: F, g, h = Q.field_extension('b')
            Traceback (most recent call last):
            ...
            NotImplementedError: not implemented for relative extensions in which the relative generator is not an absolute generator, i.e., F.gen() != F.gen_relative()

        We slightly change the example above so it works.

            sage: R.<x> = QQ['x']
            sage: K.<a> = NumberField(x^3 - 2)
            sage: S.<X> = K['X']
            sage: f = (X+a)^3 + 2*(X+a) + 1
            sage: f
            X^3 + 3*a*X^2 + (3*a^2 + 2)*X + 2*a + 3
            sage: Q.<z> = S.quo(f)
            sage: F.<w>, g, h = Q.field_extension()
            sage: c = g(z)
            sage: f(c)
            0
            sage: h(g(z))
            z
            sage: g(h(w))
            w

        AUTHOR:
            -- Craig Citro 07 Aug 06
            -- William Stein 06 Aug 06
        """

        F = self.modulus().root_field(names)
        if isinstance(F, number_field.number_field.NumberField_extension):
            if F.gen() != F.gen_relative():
                # The issue is that there is no way to specify a homomorphism
                # from the relative number to the poly ring quotient that
                # is defined over Q.
                raise NotImplementedError, "not implemented for relative extensions in which the relative generator is not an absolute generator, i.e., F.gen() != F.gen_relative()"
            alpha = F.gen_relative()
        else:
            alpha = F.gen()
        x = self.gen()

        f = self.hom([alpha], F, check=False)
        g = F.hom([x], self, check=False)

        return F, f, g

class PolynomialQuotientRing_field(PolynomialQuotientRing_domain, field.Field):
    """
    EXAMPLES:
        sage: R.<x> = PolynomialRing(QQ)
        sage: S.<xbar> = R.quotient(x^2 + 1)
        sage: S
        Univariate Quotient Polynomial Ring in xbar over Rational Field with modulus x^2 + 1
        sage: loads(S.dumps()) == S
        True
        sage: loads(xbar.dumps()) == xbar
        True
    """
    def __init__(self, ring, polynomial, name=None):
        PolynomialQuotientRing_domain.__init__(self, ring, polynomial, name)

    def __reduce__(self):
        return PolynomialQuotientRing_field, (self.polynomial_ring(),
                                        self.modulus(), self.variable_names())

    def complex_embeddings(self, prec=53):
        r"""
        Return all homomorphisms of this ring into the approximate
        complex field with precision prec.

        EXAMPLES:
            sage: f = x^5 + x + 17
            sage: k = QQ['x']/(f)
            sage: v = k.complex_embeddings(100)
            sage: [phi(k.0^2) for phi in v]
            [2.9757207403766761469671194565, 0.92103906697304693634806949136 - 3.0755331188457794473265418086*I, 0.92103906697304693634806949136 + 3.0755331188457794473265418086*I, -2.4088994371613850098316292196 + 1.9025410530350528612407363802*I, -2.4088994371613850098316292196 - 1.9025410530350528612407363802*I]
        """
        CC = complex_field.ComplexField(prec)
        f = self.modulus().base_extend(CC)
        v = f.roots()
        return [self.hom([a], check=False) for a in v]
