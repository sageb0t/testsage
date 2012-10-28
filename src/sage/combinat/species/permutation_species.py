"""
Permutation species
"""
#*****************************************************************************
#       Copyright (C) 2008 Mike Hansen <mhansen@gmail.com>,
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
from species import GenericCombinatorialSpecies
from structure import GenericSpeciesStructure
from generating_series import _integers_from

from sage.rings.all import ZZ
from sage.misc.cachefunc import cached_function
from sage.combinat.permutation import Permutation, Permutations
from sage.combinat.species.misc import accept_size

class PermutationSpeciesStructure(GenericSpeciesStructure):
    def canonical_label(self):
        """
        EXAMPLES::

            sage: P = species.PermutationSpecies()
            sage: S = P.structures(["a", "b", "c"])
            sage: [s.canonical_label() for s in S]
            [['a', 'b', 'c'],
             ['b', 'a', 'c'],
             ['b', 'a', 'c'],
             ['b', 'c', 'a'],
             ['b', 'c', 'a'],
             ['b', 'a', 'c']]
        """
        P = self.parent()
        return P._canonical_rep_from_partition(self.__class__, self._labels, Permutation(self._list).cycle_type())

    def permutation_group_element(self):
        """
        Returns self as a permutation group element.

        EXAMPLES::

            sage: p = PermutationGroupElement((2,3,4))
            sage: P = species.PermutationSpecies()
            sage: a = P.structures(["a", "b", "c", "d"]).random_element(); a
            ['a', 'c', 'b', 'd']
            sage: a.permutation_group_element()
            (2,3)
        """
        from sage.groups.all import PermutationGroupElement
        return Permutation(self._list).to_permutation_group_element()

    def transport(self, perm):
        """
        Returns the transport of this structure along the permutation
        perm.

        EXAMPLES::

            sage: p = PermutationGroupElement((2,3,4))
            sage: P = species.PermutationSpecies()
            sage: a = P.structures(["a", "b", "c", "d"]).random_element(); a
            ['a', 'c', 'b', 'd']
            sage: a.transport(p)
            ['a', 'd', 'c', 'b']
        """
        p = self.permutation_group_element()
        p = perm*p*~perm
        return self.__class__(self.parent(), self._labels, p.list())

    def automorphism_group(self):
        """
        Returns the group of permutations whose action on this structure
        leave it fixed.

        EXAMPLES::

            sage: p = PermutationGroupElement((2,3,4))
            sage: P = species.PermutationSpecies()
            sage: a = P.structures(["a", "b", "c", "d"]).random_element(); a
            ['a', 'c', 'b', 'd']
            sage: a.automorphism_group()
            Permutation Group with generators [(2,3), (1,4)]

        ::

            sage: [a.transport(perm) for perm in a.automorphism_group()]
            [['a', 'c', 'b', 'd'],
             ['a', 'c', 'b', 'd'],
             ['a', 'c', 'b', 'd'],
             ['a', 'c', 'b', 'd']]
        """
        from sage.groups.all import SymmetricGroup, PermutationGroup
        S = SymmetricGroup(len(self._labels))
        p = self.permutation_group_element()
        return PermutationGroup(S.centralizer(p).gens())

@accept_size
@cached_function
def PermutationSpecies(*args, **kwds):
    """
    Returns the species of permutations.

    EXAMPLES::

        sage: P = species.PermutationSpecies()
        sage: P.generating_series().coefficients(5)
        [1, 1, 1, 1, 1]
        sage: P.isotype_generating_series().coefficients(5)
        [1, 1, 2, 3, 5]
    """
    return PermutationSpecies_class(*args, **kwds)

class PermutationSpecies_class(GenericCombinatorialSpecies):
    def __init__(self, min=None, max=None, weight=None):
        """
        EXAMPLES::

            sage: P = species.PermutationSpecies()
            sage: c = P.generating_series().coefficients(3)
            sage: P._check()
            True
            sage: P == loads(dumps(P))
            True
        """
        GenericCombinatorialSpecies.__init__(self, min=min, max=max, weight=weight)
        self._name = "Permutation species"

    _default_structure_class = PermutationSpeciesStructure

    _cached_constructor = staticmethod(PermutationSpecies)

    def _structures(self, structure_class, labels):
        """
        EXAMPLES::

            sage: P = species.PermutationSpecies()
            sage: P.structures([1,2,3]).list()
            [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
        """
        if labels == []:
            yield structure_class(self, labels, [])
        else:
            for p in Permutations(len(labels)):
                yield structure_class(self, labels, list(p))

    def _isotypes(self, structure_class, labels):
        """
        EXAMPLES::

            sage: P = species.PermutationSpecies()
            sage: P.isotypes([1,2,3]).list()
            [[2, 3, 1], [2, 1, 3], [1, 2, 3]]
        """
        from sage.combinat.partition import Partitions
        if labels == []:
            yield structure_class(self, labels, [])
            return

        for p in Partitions(len(labels)):
            yield self._canonical_rep_from_partition(structure_class, labels, p)

    def _canonical_rep_from_partition(self, structure_class, labels, p):
        """
        EXAMPLES::

            sage: P = species.PermutationSpecies()
            sage: P._canonical_rep_from_partition(P._default_structure_class, ["a","b","c"], [2,1])
            ['b', 'a', 'c']
        """
        indices = range(1, len(labels)+1)
        breaks = [sum(p[:i]) for i in range(len(p)+1)]
        cycles = tuple(tuple(indices[breaks[i]:breaks[i+1]]) for i in range(len(p)))
        perm = list(Permutation(cycles))
        return structure_class(self, labels, perm)

    def _gs_list(self, base_ring):
        r"""
        The generating series for the species of linear orders is
        `\frac{1}{1-x}`.

        EXAMPLES::

            sage: P = species.PermutationSpecies()
            sage: g = P.generating_series()
            sage: g.coefficients(10)
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        """
        return [base_ring(1)]

    def _itgs_iterator(self, base_ring):
        r"""
        The isomorphism type generating series is given by
        `\frac{1}{1-x}`.

        EXAMPLES::

            sage: P = species.PermutationSpecies()
            sage: g = P.isotype_generating_series()
            sage: g.coefficients(10)
            [1, 1, 2, 3, 5, 7, 11, 15, 22, 30]
        """
        from sage.combinat.partitions import number_of_partitions
        for n in _integers_from(0):
            yield base_ring(number_of_partitions(n))

    def _cis(self, series_ring, base_ring):
        r"""
        The cycle index series for the species of permutations is given by

        .. math::

             \prod{n=1}^\infty \frac{1}{1-x_n}.

        EXAMPLES::

            sage: P = species.PermutationSpecies()
            sage: g = P.cycle_index_series()
            sage: g.coefficients(5)
            [p[],
             p[1],
             p[1, 1] + p[2],
             p[1, 1, 1] + p[2, 1] + p[3],
             p[1, 1, 1, 1] + p[2, 1, 1] + p[2, 2] + p[3, 1] + p[4]]
        """
        CIS = series_ring
        return CIS.product_generator( CIS(self._cis_gen(base_ring, i)) for i in _integers_from(ZZ(1)) )

    def _cis_gen(self, base_ring, n):
        """
        EXAMPLES::

            sage: P = species.PermutationSpecies()
            sage: g = P._cis_gen(QQ, 2)
            sage: [g.next() for i in range(10)]
            [p[], 0, p[2], 0, p[2, 2], 0, p[2, 2, 2], 0, p[2, 2, 2, 2], 0]
        """
        from sage.combinat.sf.sf import SymmetricFunctions
        p = SymmetricFunctions(base_ring).power()

        pn = p([n])

        n = n - 1
        yield p(1)

        for k in _integers_from(1):
            for i in range(n):
                yield base_ring(0)
            yield pn**k