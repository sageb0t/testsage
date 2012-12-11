r"""
Dyck Words

A class of an object enumerated by the :func:`Catalan numbers<sage.combinat.combinat.catalan_number>`, see [Sta1999]_, [Sta]_ for details.

AUTHORS:

- Mike Hansen

- Dan Drake (2008--05-30): DyckWordBacktracker support

- Florent Hivert (2009--02-01): Bijections with NonDecreasingParkingFunctions

- Christian Stump (2011--12): added combinatorial maps and statistics

- Mike Zabrocki (2012--10-15): added pretty print, characteristic function, more functions

REFERENCES:

.. [Sta1999] R. Stanley, Enumerative Combinatorics, Volume 2.
   Cambridge University Press, 2001.

.. [Sta] R. Stanley, electronic document containing the list
   of Catalan objects at http://www-math.mit.edu/~rstan/ec/catalan.pdf

.. [Hag2008] The `q,t` -- Catalan Numbers and the Space of Diagonal Harmonics:
   With an Appendix on the Combinatorics of Macdonald Polynomials, James Haglund,
   University of Pennsylvania, Philadelphia -- AMS, 2008, 167 pp.
"""

#*****************************************************************************
#       Copyright (C) 2007 Mike Hansen <mhansen@gmail.com>,
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

from combinat import CombinatorialClass, CombinatorialObject, catalan_number, InfiniteAbstractCombinatorialClass
from backtrack import GenericBacktracker

from sage.structure.parent import Parent
from sage.structure.unique_representation import UniqueRepresentation
from sage.categories.all import Posets

from sage.rings.all import ZZ, QQ
from sage.combinat.permutation import Permutation, Permutations
from sage.combinat.words.word import Word
from sage.misc.latex import latex

from sage.misc.superseded import deprecated_function_alias

open_symbol = 1
close_symbol = 0

def replace_parens(x):
    r"""
    A map from ``'('`` to ``open_symbol`` and ``')'`` to ``close_symbol`` and
    otherwise an error is raised. The values of the constants ``open_symbol``
    and ``close_symbol`` are subject to change. This is the inverse map of
    :func:`replace_symbols`.

    INPUT:

    - ``x`` -- either an opening or closing parenthesis.

    OUTPUT:

    - If ``x`` is an opening parenthesis, replace ``x`` with the constant ``open_symbol``.

    - If ``x`` is a closing parenthesis, replace ``x`` with the constant ``close_symbol``.

    - Raises a ``ValueError`` if ``x`` is neither an opening nor closing parenthesis.

    .. SEEALSO:: :func:`replace_symbols`

    EXAMPLES::

        sage: from sage.combinat.dyck_word import replace_parens
        sage: replace_parens('(')
        1
        sage: replace_parens(')')
        0
        sage: replace_parens(1)
        Traceback (most recent call last):
        ...
        ValueError
    """
    if x == '(':
        return open_symbol
    elif x == ')':
        return close_symbol
    else:
        raise ValueError

def replace_symbols(x):
    r"""
    A map from ``open_symbol`` to ``'('`` and ``close_symbol`` to ``')'`` and
    otherwise an error is raised. The values of the constants ``open_symbol``
    and ``close_symbol`` are subject to change. This is the inverse map of
    :func:`replace_parens`.

    INPUT:

    - ``x`` -- either ``open_symbol`` or ``close_symbol``.

    OUTPUT:

    - If ``x`` is ``open_symbol``, replace ``x`` with ``'('``.

    - If ``x`` is ``close_symbol``, replace ``x`` with ``')'``.

    - If ``x`` is neither ``open_symbol`` nor ``close_symbol``, a `ValueError`` is raised.

    .. SEEALSO:: :func:`replace_parens`

    EXAMPLES::

        sage: from sage.combinat.dyck_word import replace_symbols
        sage: replace_symbols(1)
        '('
        sage: replace_symbols(0)
        ')'
        sage: replace_symbols(3)
        Traceback (most recent call last):
        ...
        ValueError
    """
    if x == open_symbol:
        return '('
    elif x == close_symbol:
        return ')'
    else:
        raise ValueError

def DyckWord(dw=None, noncrossing_partition=None, area_sequence=None, heights_sequence=None, catalan_code=None):
    r"""
    Returns a complete or incomplete Dyck word.

    A Dyck word is a sequence of open and close symbols, such that every close symbol has
    a corresponding open symbol preceeding it.

    A Dyck word is complete if every open symbol moreover has a corresponding close symbol.

    A Dyck word may also be specified by either a noncrossing partition or by an area
    sequence or the sequence of heights.

    A Dyck word may also be thought of as a lattice path in the `\mathbb{Z}^2` grid,
    starting at the origin `(0,0)`, and with steps in the `N = (0,1)` and `E = (1,0)`,
    directions such that it does not pass below the `x=y` diagonal.
    The diagonal is referred to as the "main diagonal" in the documentation.
    Equivalently, the path may be represented with steps in the `NE = (1,1)`
    and the `SE = (1,-1)` direction such that it does not pass below the horizontal axis.

    EXAMPLES::

        sage: dw = DyckWord([1, 0, 1, 0]); dw
        [1, 0, 1, 0]
        sage: print dw
        ()()
        sage: print dw.height()
        1
        sage: dw.to_noncrossing_partition()
        [[1], [2]]

    ::

        sage: DyckWord('()()')
        [1, 0, 1, 0]
        sage: DyckWord('(())')
        [1, 1, 0, 0]
        sage: DyckWord('((')
        [1, 1]

    ::

        sage: DyckWord(noncrossing_partition=[[1],[2]])
        [1, 0, 1, 0]
        sage: DyckWord(noncrossing_partition=[[1,2]])
        [1, 1, 0, 0]

    ::

        sage: DyckWord(area_sequence=[0,0])
        [1, 0, 1, 0]
        sage: DyckWord(area_sequence=[0,1])
        [1, 1, 0, 0]
        sage: DyckWord(area_sequence=[0,1,2,2,0,1,1,2])
        [1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0]

    ::

        sage: DyckWord(heights_sequence=(0,1,0,1,0))
        [1, 0, 1, 0]
        sage: DyckWord(heights_sequence=(0,1,2,1,0))
        [1, 1, 0, 0]

    ::

        sage: print DyckWord([1,0,1,1,0,0]).to_path_string()
           /\
        /\/  \
        sage: DyckWord([1,0,1,1,0,0]).pretty_print()
           ___
          | x
         _|  .
        |  . .
    """
    if dw is None:
        if catalan_code is not None:
            return DyckWord_complete.from_Catalan_code(catalan_code)
        elif area_sequence is not None:
            return DyckWord_complete.from_area_sequence(area_sequence)
        elif noncrossing_partition is not None:
            return from_noncrossing_partition(noncrossing_partition)
        elif heights_sequence is not None:
            if heights_sequence[-1] == 0:
                cls = DyckWord_complete
            else:
                cls = DyckWord_class
            return cls.from_heights(heights_sequence)
        else:
            raise ValueError, "You have not specified a Dyck word."

    if isinstance(dw, str):
        l = map(replace_parens, dw)
    else:
        l = dw

    if isinstance(l, DyckWord_class):
        return l

    # CS: what happens here? there is a loop after a return (which is thus never used)
    #elif l in DyckWords() or is_a_prefix(l):
        #return DyckWord_class(l)
        #for opt in l._latex_options:
            #if opt not in latex_options:
                #latex_options[opt] = l._latex_options[opt]
        #return DyckWord_class(l,latex_options=latex_options)
    if l in DyckWords():
        return DyckWord_complete(l)
    if is_a_prefix(l):
        return DyckWord_class(l)
    else:
        raise ValueError, "invalid Dyck word"

class DyckWord_class(CombinatorialObject):
    r"""
    A class for representing a Dyck word.  A Dyck word of length `n` is a list with
    `n` entries 1 and and `n` entries 0 such that the first `k` entries
    always has at least as many 1s as 0s.  Alternatively, the alphabet
    1 and 0 can be replaced by other characters.

    A Dyck word is a representation of a Dyck path which is a lattice path in
    an `n \times n` rectangle from `(0,0)` to `(n,n)` using only North = `(0,1)`
    and East = `(1,0)` steps such that the path touches, but does not cross the
    `x=y` line.  A North step is represented by a 1 in the list and an East
    step is represented by a 0.
    """

    def __init__(self, l, latex_options={}):
        r"""
        TESTS::

            sage: from sage.combinat.dyck_word import DyckWord_class, DyckWord_complete
            sage: DW = DyckWord_class.from_heights((0,))
            sage: DW == loads(dumps(DW))
            True
            sage: DW = DyckWord_class.min_from_heights((0,))
            sage: DW == loads(dumps(DW))
            True
            sage: DW = DyckWord_complete.from_Catalan_code([])
            sage: DW == loads(dumps(DW))
            True
            sage: DW = DyckWord_complete.from_area_sequence([])
            sage: DW == loads(dumps(DW))
            True
        """
        CombinatorialObject.__init__(self, l)
        self._latex_options = dict(latex_options)
        if "tikz_scale" not in self._latex_options:
            self._latex_options["tikz_scale"] = 1
        if "diagonal" not in self._latex_options:
            self._latex_options["diagonal"] = False
        if "line width" not in self._latex_options:
            self._latex_options["line width"] = 2*self._latex_options["tikz_scale"]
        if "color" not in self._latex_options:
            self._latex_options["color"] = "black"
        if "bounce path" not in self._latex_options:
            self._latex_options["bounce path"] = False
        if "peaks" not in self._latex_options:
            self._latex_options["peaks"] = False
        if "valleys" not in self._latex_options:
            self._latex_options["valleys"] = False

    _has_2D_print = False

    def set_latex_options(self,D):
        r"""
        Sets the latex options for use in the ``_latex_`` function.  The default values
        are set in the ``__init__`` function.

        - ``tikz_scale`` -- (default:1) scale for use with the tikz package.

        - ``diagonal`` -- (default:False) boolean value to draw the diagonal or not.

        - ``line width`` -- (default:2*``tikz_scale``) value representing the line width.

        - ``color`` -- (default:black) the line color.

        - ``bounce path`` -- (default:False) boolean value to indicate if the bounce path should be drawn.

        - ``peaks`` -- (default:False) boolean value to indicate if the peaks should be displayed.

        - ``valleys`` -- (default:False) boolean value to indicate if the valleys should be displayed.

        INPUT:

        - ``D`` -- a dictionary with a list of latex parameters to change.

        EXAMPLES::

            sage: D = DyckWord([1,0,1,0,1,0])
            sage: D.set_latex_options({"tikz_scale":2})
            sage: D.set_latex_options({"valleys":True, "color":"blue"})
        """
        for opt in D:
            self._latex_options[opt] = D[opt]

    def latex_options(self):
        r"""
        Returns the latex options for use in the ``_latex_`` function as a dictionary.
        The default values are set in the ``__init__`` function.

        - ``tikz_scale`` -- (default:1) scale for use with the tikz package.

        - ``diagonal`` -- (default:False) boolean value to draw the diagonal or not.

        - ``line width`` -- (default:2*``tikz_scale``) value representing the line width.

        - ``color`` -- (default:black) the line color.

        - ``bounce path`` -- (default:False) boolean value to indicate if the bounce path should be drawn.

        - ``peaks`` -- (default:False) boolean value to indicate if the peaks should be displayed.

        - ``valleys`` -- (default:False) boolean value to indicate if the valleys should be displayed.

        EXAMPLES::

            sage: D = DyckWord([1,0,1,0,1,0])
            sage: D.latex_options()
            {'valleys': False, 'peaks': False, 'tikz_scale': 1, 'color': 'black', 'diagonal': False, 'bounce path': False, 'line width': 2}
        """
        return self._latex_options

    def __repr__(self):
        r"""
        TESTS::

            sage: DyckWord([1, 0, 1, 0])
            [1, 0, 1, 0]
            sage: DyckWord([1, 1, 0, 0])
            [1, 1, 0, 0]
            sage: type(DyckWord([]))._has_2D_print = True
            sage: DyckWord([1, 0, 1, 0])
            /\/\
            sage: DyckWord([1, 1, 0, 0])
             /\
            /  \
            sage: type(DyckWord([]))._has_2D_print = False
        """
        if self._has_2D_print:
            return self.to_path_string()
        else:
            return super(DyckWord_class, self).__repr__()

    def __str__(self):
        r"""
        Returns a string consisting of matched parentheses corresponding to
        the Dyck word.

        EXAMPLES::

            sage: print DyckWord([1, 0, 1, 0])
            ()()
            sage: print DyckWord([1, 1, 0, 0])
            (())
        """
        if self._has_2D_print:
            return self.to_path_string()
        else:
            return "".join(map(replace_symbols, [x for x in self]))

    def to_path_string(self):
        r"""
        A path representation of the Dyck word consisting of steps ``/`` and ``\`` .

        EXAMPLES::

            sage: DyckWord([1, 0, 1, 0]).to_path_string()
            '/\\/\\'
            sage: DyckWord([1, 1, 0, 0]).to_path_string()
            ' /\\ \n/  \\'
            sage: DyckWord([1,1,0,1,1,0,0,1,0,1,0,0]).to_path_string()
            '    /\\      \n /\\/  \\/\\/\\ \n/          \\'
        """
        res = [([" "]*len(self)) for _ in range(self.height())]
        h = 1
        for i, p in enumerate(self):
            if p == open_symbol:
                res[-h][i] = "/"
                h +=1
            else:
                h -=1
                res[-h][i] = "\\"
        return "\n".join("".join(l) for l in res)

    def pretty_print( self, type="N-E", labelling=None, underpath=True ):
        r"""
        Display a DyckWord as a lattice path in the `\mathbb{Z}^2` grid.

        If the ``type`` is "N-E", then the a cell below the diagonal is
        indicated by a period, a cell below the path, but above the
        diagonal are indicated by an x. If a list of labels is included,
        they are displayed along the vertical edges of the Dyck path.

        If the ``type`` is "NE-SE", then the path is simply printed
        as up steps and down steps.

        INPUT:

        - ``type`` -- can either be
                        - "N-E" to show ``self`` as a path of north and east steps, or
                        - "NE-SE" to show ``self`` as a path of north-east and south-east steps.

        - ``labelling`` -- (if type is "N-E") a list of labels assigned to the up steps in ``self``.

        - ``underpath`` -- (if type is "N-E", default:True)
                            - if True, the labelling is shown under the path
                            - otherwise, it is shown to the right of the path.

        EXAMPLES::

            sage: for D in DyckWords(3): D.pretty_print()
                 _
               _|
             _|  .
            |  . .
               ___
              | x
             _|  .
            |  . .
                 _
             ___|
            | x  .
            |  . .
               ___
             _| x
            | x  .
            |  . .
             _____
            | x x
            | x  .
            |  . .

        ::

            sage: for D in DyckWords(3): D.pretty_print(type="NE-SE")
            /\/\/\
               /\
            /\/  \
             /\
            /  \/\
             /\/\
            /    \
              /\
             /  \
            /    \

        ::

            sage: D = DyckWord([1,1,1,0,1,0,0,1,1])
            sage: D.pretty_print()
                  | x x
               ___| x  .
             _| x x  . .
            | x x  . . .
            | x  . . . .
            |  . . . . .

            sage: D = DyckWord([1,1,1,0,1,0,0,1,1,0])
            sage: D.pretty_print()
                   _
                  | x x
               ___| x  .
             _| x x  . .
            | x x  . . .
            | x  . . . .
            |  . . . . .

            sage: D = DyckWord([1,1,1,0,1,0,0,1,1,0,0])
            sage: D.pretty_print()
                   ___
                  | x x
               ___| x  .
             _| x x  . .
            | x x  . . .
            | x  . . . .
            |  . . . . .

        ::

            sage: DyckWord(area_sequence=[0,1,0]).pretty_print(labelling=[1,3,2])
                 _
             ___|2
            |3x  .
            |1 . .

            sage: DyckWord(area_sequence=[0,1,0]).pretty_print(labelling=[1,3,2],underpath=False)
                 _
             ___|  2
            | x  . 3
            |  . . 1

        ::

            sage: DyckWord(area_sequence=[0,1,1,2,3,2,3,3,2,0,1,1,2,3,4,2,3]).pretty_print()
                                       _______
                                      | x x x
                                 _____| x x  .
                                | x x x x  . .
                                | x x x  . . .
                                | x x  . . . .
                               _| x  . . . . .
                              | x  . . . . . .
                         _____|  . . . . . . .
                     ___| x x  . . . . . . . .
                   _| x x x  . . . . . . . . .
                  | x x x  . . . . . . . . . .
               ___| x x  . . . . . . . . . . .
              | x x x  . . . . . . . . . . . .
              | x x  . . . . . . . . . . . . .
             _| x  . . . . . . . . . . . . . .
            | x  . . . . . . . . . . . . . . .
            |  . . . . . . . . . . . . . . . .

            sage: DyckWord(area_sequence=[0,1,1,2,3,2,3,3,2,0,1,1,2,3,4,2,3]).pretty_print(labelling=range(17),underpath=False)
                                       _______
                                      | x x x  16
                                 _____| x x  . 15
                                | x x x x  . . 14
                                | x x x  . . . 13
                                | x x  . . . . 12
                               _| x  . . . . . 11
                              | x  . . . . . . 10
                         _____|  . . . . . . .  9
                     ___| x x  . . . . . . . .  8
                   _| x x x  . . . . . . . . .  7
                  | x x x  . . . . . . . . . .  6
               ___| x x  . . . . . . . . . . .  5
              | x x x  . . . . . . . . . . . .  4
              | x x  . . . . . . . . . . . . .  3
             _| x  . . . . . . . . . . . . . .  2
            | x  . . . . . . . . . . . . . . .  1
            |  . . . . . . . . . . . . . . . .  0

        ::

            sage: DyckWord([]).pretty_print()
            .

        """
        if type == "NE-SE":
            if labelling is not None or underpath is not True:
                raise ValueError, "The labelling cannot be shown with Northeast-Southeast paths."
            print self.to_path_string()+"\n"
            return None
        elif type == "N-E":
            alst = self.to_area_sequence()
            n = len(alst)
            if n == 0:
                print(".\n")
                return None
            if labelling is None:
                labels = [" "]*n
            else:
                if len(labelling) != n:
                    raise ValueError, "The given labelling has the wrong length."
                labels = [ str(label) for label in labelling ]
                if not underpath:
                    max_length = max( len(label) for label in labels )
                    labels = [ label.rjust(max_length+1) for label in labels ]

            length_of_final_fall = list(reversed(self)).index(open_symbol)
            if length_of_final_fall == 0:
                final_fall = " "
            else:
                final_fall = " _" + "__"*(length_of_final_fall-1)
            row = "  "*(n - alst[-1]-1) + final_fall + "\n"
            for i in range(n-1):
                c=0
                row = row + "  "*(n-i-2-alst[-i-2])
                c+=n-i-2-alst[-i-2]
                if alst[-i-2]+1!=alst[-i-1]:
                    row+=" _"
                c+=alst[-i-2]-alst[-i-1]
                if underpath:
                    row+="__"*(alst[-i-2]-alst[-i-1])+"|" + labels[-1] + "x "*(n-c-2-i)+ " ."*i + "\n"
                else:
                    row+="__"*(alst[-i-2]-alst[-i-1])+"| " + "x "*(n-c-2-i)+ " ."*i + labels[-1] + "\n"
                labels.pop()
            if underpath:
                row = row + "|" + labels[-1] + " ."*(n-1) + "\n"
            else:
                row = row + "| "+" ."*(n-1) + labels[-1] + "\n"
            print(row)
            return None
        else:
            raise ValueError, "The given type (=\s) is not valid."%type

    def _latex_(self):
        r"""
        A latex representation of ``self`` using the tikzpicture package.

        EXAMPLES:

            sage: DyckWord([1,0])._latex_()
            '\\vcenter{\\hbox{$\\begin{tikzpicture}[scale=1]\n  \\draw[dotted] (0, 0) grid (2, 1);\n  \\draw[rounded corners=1, color=black, line width=2 px] (0, 0) -- (1, 1) -- (2, 0);\n\\end{tikzpicture}$}}'
            sage: DyckWord([1,0,1,1,0,0])._latex_()
            '\\vcenter{\\hbox{$\\begin{tikzpicture}[scale=1]\n  \\draw[dotted] (0, 0) grid (6, 2);\n  \\draw[rounded corners=1, color=black, line width=2 px] (0, 0) -- (1, 1) -- (2, 0) -- (3, 1) -- (4, 2) -- (5, 1) -- (6, 0);\n\\end{tikzpicture}$}}'
        """
        latex.add_package_to_preamble_if_available("tikz")
        heights = self.heights()
        latex_options = self._latex_options
        diagonal = latex_options["diagonal"]
        ht = [(0,0)]
        valleys = []
        peaks = []
        for i in range(1,len(heights)):
            a,b = ht[-1]
            if heights[i] > heights[i-1]:
                if diagonal:
                    ht.append((a,b+1))
                else:
                    ht.append((a+1,b+1))
                if i < len(heights)-1 and heights[i+1] < heights[i]:
                    peaks.append(ht[-1])
            else:
                if diagonal:
                    ht.append((a+1,b))
                else:
                    ht.append((a+1,b-1))
                if i < len(heights)-1 and heights[i+1] > heights[i]:
                    valleys.append(ht[-1])
        ht = iter(ht)
        if diagonal:
            grid = [((0,i),(i,i+1)) for i in range(self.number_of_open_symbols())]
        else:
            grid = [((0,0),(len(self),self.height()))]
        res = "\\vcenter{\\hbox{$\\begin{tikzpicture}[scale="+str(latex_options['tikz_scale'])+"]\n"
        if latex_options["bounce path"]:
            D = self.bounce_path()
            D.set_latex_options(latex_options)
            D.set_latex_options({"color":"red","line width":2*latex_options['line width'],"bounce path":False})
            res += D._latex_().split("\n")[-2] + "\n"
        for v1,v2 in grid:
            res += "  \\draw[dotted] %s grid %s;\n"%(str(v1),str(v2))
        if diagonal:
            res += "  \\draw (0,0) -- %s;\n"%str((self.number_of_open_symbols(),self.number_of_open_symbols()))
        res += "  \\draw[rounded corners=1, color=%s, line width=%s px] (0, 0)"%(latex_options['color'],str(latex_options['line width']))
        ht.next()
        for i, j in ht:
            res += " -- (%s, %s)"%(i, j)
        res += ";\n"
        mark_points = []
        if latex_options['valleys']:
            mark_points.extend(valleys)
        if latex_options['peaks']:
            mark_points.extend(peaks)
        for v in mark_points:
            res += "  \\draw[line width=2px,color=red] %s circle (5px);\n"%str(v)
        res += "\\end{tikzpicture}$}}"
        return res

    def length(self):
        r"""
        Returns the length of ``self``.

        EXAMPLES::

            sage: DyckWord([1, 0, 1, 0]).length()
            4
            sage: DyckWord([1, 0, 1, 1, 0]).length()
            5

        TESTS::

            sage: DyckWord([]).length()
            0
        """
        return len(self)

    def number_of_open_symbols(self):
        r"""
        Returns the number of open symbols in ``self``.

        EXAMPLES::

            sage: DyckWord([1, 0, 1, 0]).number_of_open_symbols()
            2
            sage: DyckWord([1, 0, 1, 1, 0]).number_of_open_symbols()
            3

        TESTS::

            sage: DyckWord([]).number_of_open_symbols()
            0
        """
        return len(filter(lambda x: x == open_symbol, self))

    size = deprecated_function_alias(13550, number_of_open_symbols)

    def number_of_close_symbols(self):
        r"""
        Returns the number of close symbols in ``self``.

        EXAMPLES::

            sage: DyckWord([1, 0, 1, 0]).number_of_close_symbols()
            2
            sage: DyckWord([1, 0, 1, 1, 0]).number_of_close_symbols()
            2

        TESTS::

            sage: DyckWord([]).number_of_close_symbols()
            0
        """
        return len(filter(lambda x: x == close_symbol, self))

    def is_complete(self):
        r"""
        Returns True is ``self`` is complete.
        This is if self contains as many closers as openers.

        EXAMPLES::

            sage: DyckWord([1, 0, 1, 0]).is_complete()
            True
            sage: DyckWord([1, 0, 1, 1, 0]).is_complete()
            False

        TESTS::

            sage: DyckWord([]).is_complete()
            True
        """
        return self.number_of_open_symbols() == self.number_of_close_symbols()

    def height(self):
        r"""
        Returns the height of the Dyck word.

        We view the Dyck word as a Dyck path from `(0,0)` to
        `(2n,0)` in the first quadrant by letting ``1``'s represent
        steps in the direction `(1,1)` and ``0``'s represent steps in
        the direction `(1,-1)`.

        The height is the maximum `y`-coordinate reached.

        .. SEEALSO:: :meth:`heights`

        EXAMPLES::

            sage: DyckWord([]).height()
            0
            sage: DyckWord([1,0]).height()
            1
            sage: DyckWord([1, 1, 0, 0]).height()
            2
            sage: DyckWord([1, 1, 0, 1, 0]).height()
            2
            sage: DyckWord([1, 1, 0, 0, 1, 0]).height()
            2
            sage: DyckWord([1, 0, 1, 0]).height()
            1
            sage: DyckWord([1, 1, 0, 0, 1, 1, 1, 0, 0, 0]).height()
            3
        """
        # calling max(self.heights()) has a significant overhead (20%)
        height = 0
        height_max = 0
        for letter in self:
            if letter == open_symbol:
                height += 1
                height_max = max(height, height_max)
            elif letter == close_symbol:
                height -= 1
        return height_max

    def heights(self):
        r"""
        Returns the heights of the Dyck word.

        We view the Dyck word as a Dyck path from `(0,0)` to
        `(2n,0)` in the first quadrant by letting ``1``'s represent
        steps in the direction `(1,1)` and ``0``'s represent steps in
        the direction `(1,-1)`.

        The heights is the sequence of `y`-coordinate reached.

        .. SEEALSO:: :meth:`from_heights`, :meth:`min_from_heights`

        EXAMPLES::

            sage: DyckWord([]).heights()
            (0,)
            sage: DyckWord([1,0]).heights()
            (0, 1, 0)
            sage: DyckWord([1, 1, 0, 0]).heights()
            (0, 1, 2, 1, 0)
            sage: DyckWord([1, 1, 0, 1, 0]).heights()
            (0, 1, 2, 1, 2, 1)
            sage: DyckWord([1, 1, 0, 0, 1, 0]).heights()
            (0, 1, 2, 1, 0, 1, 0)
            sage: DyckWord([1, 0, 1, 0]).heights()
            (0, 1, 0, 1, 0)
            sage: DyckWord([1, 1, 0, 0, 1, 1, 1, 0, 0, 0]).heights()
            (0, 1, 2, 1, 0, 1, 2, 3, 2, 1, 0)
        """
        height  = 0
        heights = [0]*(len(self)+1)
        for i, letter in enumerate(self):
            if letter == open_symbol:
                height += 1
            elif letter == close_symbol:
                height -= 1
            heights[i+1] = height
        return tuple(heights)

    @classmethod
    def from_heights(cls, heights):
        r"""
        Compute a dyck word knowing its heights.

        We view the Dyck word as a Dyck path from `(0,0)` to
        `(2n,0)` in the first quadrant by letting ``1``'s represent
        steps in the direction `(1,1)` and ``0``'s represent steps in
        the direction `(1,-1)`.

        The :meth:`heights` is the sequence of `y`-coordinate reached.

        EXAMPLES::

            sage: from sage.combinat.dyck_word import DyckWord_class
            sage: DyckWord_class.from_heights((0,))
            []
            sage: DyckWord_class.from_heights((0, 1, 0))
            [1, 0]
            sage: DyckWord_class.from_heights((0, 1, 2, 1, 0))
            [1, 1, 0, 0]
            sage: DyckWord_class.from_heights((0, 1, 2, 1, 2, 1))
            [1, 1, 0, 1, 0]

        This also works for prefix of Dyck words::

            sage: DyckWord_class.from_heights((0, 1, 2, 1))
            [1, 1, 0]

        .. SEEALSO:: :meth:`heights`, :meth:`min_from_heights`

        TESTS::

            sage: all(dw == DyckWord_class.from_heights(dw.heights())
            ...       for i in range(7) for dw in DyckWords(i))
            True

            sage: DyckWord_class.from_heights((1, 2, 1))
            Traceback (most recent call last):
            ...
            ValueError: heights must start with 0: (1, 2, 1)
            sage: DyckWord_class.from_heights((0, 1, 4, 1))
            Traceback (most recent call last):
            ...
            ValueError: consecutive heights must differ by exactly 1: (0, 1, 4, 1)
            sage: DyckWord_class.from_heights(())
            Traceback (most recent call last):
            ...
            ValueError: heights must start with 0: ()
        """
        l1 = len(heights)-1
        res = [0]*(l1)
        if heights==() or heights[0] != 0:
            raise ValueError, "heights must start with 0: %s"%(heights,)
        for i in range(l1):
            if heights[i] == heights[i+1]-1:
                res[i] = 1
            elif heights[i] != heights[i+1]+1:
                raise ValueError, (
                    "consecutive heights must differ by exactly 1: %s"%(heights,))
        return cls(res)

    @classmethod
    def min_from_heights(cls, heights):
        r"""
        Compute the smallest dyck word which lies some heights.

        .. SEEALSO:: :meth:`heights` :meth:`from_heights`

        EXAMPLES::

            sage: from sage.combinat.dyck_word import DyckWord_class
            sage: DyckWord_class.min_from_heights((0,))
            []
            sage: DyckWord_class.min_from_heights((0, 1, 0))
            [1, 0]
            sage: DyckWord_class.min_from_heights((0, 0, 2, 0, 0))
            [1, 1, 0, 0]
            sage: DyckWord_class.min_from_heights((0, 0, 2, 0, 2, 0))
            [1, 1, 0, 1, 0]
            sage: DyckWord_class.min_from_heights((0, 0, 1, 0, 1, 0))
            [1, 1, 0, 1, 0]

        TESTS::

            sage: DyckWord_class.min_from_heights(())
            Traceback (most recent call last):
            ...
            ValueError: heights must start with 0: ()
        """
        if heights==() or heights[0] != 0:
            raise ValueError, "heights must start with 0: %s"%(heights,)
        # round heights to the smallest even-odd integer
        heights = list(heights)
        for i in range(0, len(heights), 2):
            if heights[i] % 2 == 1:
                heights[i]+=1
        for i in range(1, len(heights), 2):
            if heights[i] % 2 == 0:
                heights[i]+=1

        # smooth heights
        for i in range(len(heights)-1):
            if heights[i+1] < heights[i]:
                heights[i+1] = heights[i]-1
        for i in range(len(heights)-1, 0, -1):
            if heights[i] > heights[i-1]:
                heights[i-1] = heights[i]-1
        return cls.from_heights(heights)

    def associated_parenthesis(self, pos):
        r"""
        Report the position for the parenthesis that matches the one at
        position ``pos`` .

        INPUT:

        - ``pos`` -- the index of the parenthesis in the list.

        OUTPUT:

        - Integer representing the index of the matching parenthesis.  If no parenthesis matches, return ``None``.

        EXAMPLES::

            sage: DyckWord([1, 0]).associated_parenthesis(0)
            1
            sage: DyckWord([1, 0, 1, 0]).associated_parenthesis(0)
            1
            sage: DyckWord([1, 0, 1, 0]).associated_parenthesis(1)
            0
            sage: DyckWord([1, 0, 1, 0]).associated_parenthesis(2)
            3
            sage: DyckWord([1, 0, 1, 0]).associated_parenthesis(3)
            2
            sage: DyckWord([1, 1, 0, 0]).associated_parenthesis(0)
            3
            sage: DyckWord([1, 1, 0, 0]).associated_parenthesis(2)
            1
            sage: DyckWord([1, 1, 0]).associated_parenthesis(1)
            2
            sage: DyckWord([1, 1]).associated_parenthesis(0)
        """
        d = 0
        height = 0
        if pos >= len(self):
            raise ValueError, "invalid index"

        if self[pos] == open_symbol:
            d += 1
            height += 1
        elif self[pos] == close_symbol:
            d -= 1
            height -= 1
        else:
            raise ValueError, "unknown symbol %s"%self[pos-1]

        while height != 0:
            pos += d
            if pos < 0 or pos >= len(self):
                return None
            if self[pos] == open_symbol:
                height += 1
            elif self[pos] == close_symbol:
                height -= 1
        return pos

    def number_of_initial_rises(self):
        r"""
        Return the length of the initial run of ``self``

        OUPUT:

            - a non--negative integer indicating the length of the initial rise

        EXAMPLES::

            sage: DyckWord([1, 0, 1, 0]).number_of_initial_rises()
            1
            sage: DyckWord([1, 1, 0, 0]).number_of_initial_rises()
            2
            sage: DyckWord([1, 1, 0, 0, 1, 0]).number_of_initial_rises()
            2
            sage: DyckWord([1, 0, 1, 1, 0, 0]).number_of_initial_rises()
            1

        TESTS::

            sage: DyckWord([]).number_of_initial_rises()
            0
            sage: DyckWord([1, 0]).number_of_initial_rises()
            1
        """
        if not self:
            return 0
        i = 1
        while self[i] == open_symbol:
            i+=1
        return i

    def peaks(self):
        r"""
        Returns a list of the positions of the peaks of a Dyck word. A peak
        is 1 followed by a 0.  Note that this does not agree with the
        definition given in [Hag2008]_.

        EXAMPLES::

            sage: DyckWord([1, 0, 1, 0]).peaks()
            [0, 2]
            sage: DyckWord([1, 1, 0, 0]).peaks()
            [1]
            sage: DyckWord([1,1,0,1,0,1,0,0]).peaks() # Haglund's def gives 2
            [1, 3, 5]
        """
        return [i for i in range(len(self)-1) if self[i] == open_symbol and self[i+1] == close_symbol]

    def number_of_peaks(self):
        r"""
        The number of peaks of the Dyck path associated to ``self`` .

        .. SEEALSO:: :meth:`peaks`

        EXAMPLES::

            sage: DyckWord([1, 0, 1, 0]).number_of_peaks()
            2
            sage: DyckWord([1, 1, 0, 0]).number_of_peaks()
            1
            sage: DyckWord([1,1,0,1,0,1,0,0]).number_of_peaks()
            3
            sage: DyckWord([]).number_of_peaks()
            0
        """
        return len(self.peaks())

    def valleys(self):
        r"""
        Returns a list of the positions of the valleys of a Dyck
        word. A valley is 0 followed by a 1.

        EXAMPLES::

            sage: DyckWord([1, 0, 1, 0]).valleys()
            [1]
            sage: DyckWord([1, 1, 0, 0]).valleys()
            []
            sage: DyckWord([1,1,0,1,0,1,0,0]).valleys()
            [2, 4]
        """
        return [i for i in xrange(len(self)-1) if self[i] == close_symbol and self[i+1] == open_symbol]

    def number_of_valleys(self):
        r"""
        Returns the number of valleys of ``self`` .

        EXAMPLES::

            sage: DyckWord([1, 0, 1, 0]).number_of_valleys()
            1
            sage: DyckWord([1, 1, 0, 0]).number_of_valleys()
            0
            sage: DyckWord([1, 1, 0, 0, 1, 0]).number_of_valleys()
            1
            sage: DyckWord([1, 0, 1, 1, 0, 0]).number_of_valleys()
            1

        TESTS::

            sage: DyckWord([]).number_of_valleys()
            0
            sage: DyckWord([1, 0]).number_of_valleys()
            0
        """
        return len(self.valleys())

    def position_of_first_return(self):
        r"""
        Return the number of vertical steps before the Dyck path returns to the main
        diagonal.

        EXAMPLES::

            sage: DyckWord([1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0]).position_of_first_return()
            1
            sage: DyckWord([1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0]).position_of_first_return()
            7
            sage: DyckWord([1, 1, 0, 0]).position_of_first_return()
            2
            sage: DyckWord([1, 0, 1, 0]).position_of_first_return()
            1
            sage: DyckWord([]).position_of_first_return()
            0
        """
        touches = self.touch_points()
        if touches == []:
            return 0
        else:
            return touches[0]

    def positions_of_double_rises(self):
        r"""
        returns a list of positions in the Dyck word where there are two
        consecutive 1s.

        EXAMPLES::

            sage: DyckWord([1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0]).positions_of_double_rises()
            [2, 5]
            sage: DyckWord([1, 1, 0, 0]).positions_of_double_rises()
            [0]
            sage: DyckWord([1, 0, 1, 0]).positions_of_double_rises()
            []
        """
        return [ i for i in xrange(len(self)-1) if self[i] == self[i+1] == open_symbol ]

    def number_of_double_rises(self):
        r"""
        returns a the number of positions in the Dyck word where there are two
        consecutive 1s.

        EXAMPLES::

            sage: DyckWord([1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0]).number_of_double_rises()
            2
            sage: DyckWord([1, 1, 0, 0]).number_of_double_rises()
            1
            sage: DyckWord([1, 0, 1, 0]).number_of_double_rises()
            0
        """
        return len(self.positions_of_double_rises())

    def returns_to_zero(self):
        r"""
        Return a list of positions where the Dyck word has height `0`.

        EXAMPLES::

            sage: DyckWord([]).returns_to_zero()
            []
            sage: DyckWord([1, 0]).returns_to_zero()
            [2]
            sage: DyckWord([1, 0, 1, 0]).returns_to_zero()
            [2, 4]
            sage: DyckWord([1, 1, 0, 0]).returns_to_zero()
            [4]
        """
        h = self.heights()
        return [i for i in xrange(2, len(h), 2) if h[i] == 0]

    return_to_zero = deprecated_function_alias(13550, returns_to_zero)

    def touch_points(self):
        r"""
        Returns the positions greater than `0` and less than or equal to the length of
        ``self`` of the points where the Dyck path touches the main diagonal.

        OUTPUT:

        - a list of integers indicating where the path touches the diagonal

        EXAMPLES::

            sage: DyckWord([1, 0, 1, 0]).touch_points()
            [1, 2]
            sage: DyckWord([1, 1, 0, 0]).touch_points()
            [2]
            sage: DyckWord([1, 1, 0, 0, 1, 0]).touch_points()
            [2, 3]
            sage: DyckWord([1, 0, 1, 1, 0, 0]).touch_points()
            [1, 3]
        """
        return [ i/2 for i in self.returns_to_zero() ]

    def touch_composition(self):
        r"""
        Returns a composition which indicates the positions where the
        Dyck path returns to the diagonal.

        OUTPUT:

        - a composition of length equal to the length of the Dyck word.

        EXAMPLES::

            sage: DyckWord([1, 0, 1, 0]).touch_composition()
            [1, 1]
            sage: DyckWord([1, 1, 0, 0]).touch_composition()
            [2]
            sage: DyckWord([1, 1, 0, 0, 1, 0]).touch_composition()
            [2, 1]
            sage: DyckWord([1, 0, 1, 1, 0, 0]).touch_composition()
            [1, 2]
            sage: DyckWord([]).touch_composition()
            []
        """
        from sage.combinat.composition import Composition
        if self.length()==0:
            return Composition([])
        return Composition( descents=[i-1 for i in self.touch_points()] )

    def number_of_touch_points(self):
        r"""
        Returns the number of touches of ``self`` at the main diagonal.

        OUTPUT:

        - a non--negative integer

        EXAMPLES::

            sage: DyckWord([1, 0, 1, 0]).number_of_touch_points()
            2
            sage: DyckWord([1, 1, 0, 0]).number_of_touch_points()
            1
            sage: DyckWord([1, 1, 0, 0, 1, 0]).number_of_touch_points()
            2
            sage: DyckWord([1, 0, 1, 1, 0, 0]).number_of_touch_points()
            2

        TESTS::

            sage: DyckWord([]).number_of_touch_points()
            0
        """
        return len(self.touch_points())

    def rise_composition(self):
        r"""
        The sequences of lengths of runs of 1s in the Dyck word.  Also equal to the
        sequence of lengths of vertical segments in the Dyck path.

        EXAMPLES::

            sage: DyckWord([1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0]).pretty_print()
                       ___
                      | x
               _______|  .
              | x x x  . .
              | x x  . . .
             _| x  . . . .
            | x  . . . . .
            |  . . . . . .

            sage: DyckWord([1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0]).rise_composition()
            [2, 3, 2]
            sage: DyckWord([1,1,0,0]).rise_composition()
            [2]
            sage: DyckWord([1,0,1,0]).rise_composition()
            [1, 1]
        """
        from sage.combinat.composition import Composition
        L = list(self)
        rise_comp = []
        while L:
            i = L.index(0)
            L = L[i+1:]
            if i > 0:
                rise_comp.append(i)
        return Composition(rise_comp)

    def to_standard_tableau(self):
        r"""
        Returns a standard tableau of shape `(a,b)` where
        `a` is the number of open symbols and `b` is the number of
        close symbols in ``self``.

        EXAMPLES::

            sage: DyckWord([]).to_standard_tableau()
            []
            sage: DyckWord([1, 0]).to_standard_tableau()
            [[1], [2]]
            sage: DyckWord([1, 1, 0, 0]).to_standard_tableau()
            [[1, 2], [3, 4]]
            sage: DyckWord([1, 0, 1, 0]).to_standard_tableau()
            [[1, 3], [2, 4]]
            sage: DyckWord([1]).to_standard_tableau()
            [[1]]
            sage: DyckWord([1, 0, 1]).to_standard_tableau()
            [[1, 3], [2]]
        """
        open_positions = []
        close_positions = []
        from sage.combinat.tableau import Tableau
        for i in range(len(self)):
            if self[i] == open_symbol:
                open_positions.append(i+1)
            else:
                close_positions.append(i+1)
        return Tableau(filter(lambda x: x != [],  [ open_positions, close_positions ]))

    def to_area_sequence(self):
        r"""
        Return the sequence of numbers representing of full cells below the
        Dyck path but above the diagonal in the successive rows.

        A area sequence is a list of integer l such that `l_0 = 0` and
        `0 \leq l_{i+1} \leq l_i + 1` for `i > 0`.
        This sequence is equal to the number of full cells below the
        path but above the diagonal in the corresponding Dyck path.

        EXAMPLES::

            sage: DyckWord([]).to_area_sequence()
            []
            sage: DyckWord([1, 0]).to_area_sequence()
            [0]
            sage: DyckWord([1, 1, 0, 0]).to_area_sequence()
            [0, 1]
            sage: DyckWord([1, 0, 1, 0]).to_area_sequence()
            [0, 0]
            sage: from sage.combinat.dyck_word import DyckWord_complete
            sage: all(dw ==
            ...       DyckWord_complete.from_area_sequence(dw.to_area_sequence())
            ...       for i in range(6) for dw in DyckWords(i))
            True
            sage: DyckWord([1,0,1,0,1,0,1,0,1,0]).to_area_sequence()
            [0, 0, 0, 0, 0]
            sage: DyckWord([1,1,1,1,1,0,0,0,0,0]).to_area_sequence()
            [0, 1, 2, 3, 4]
            sage: DyckWord([1,1,1,1,0,1,0,0,0,0]).to_area_sequence()
            [0, 1, 2, 3, 3]
            sage: DyckWord([1,1,0,1,0,0,1,1,0,1,0,1,0,0]).to_area_sequence()
            [0, 1, 1, 0, 1, 1, 1]
        """
        seq = []
        a = 0
        for move in self:
            if move == open_symbol:
                seq.append(a)
                a += 1
            elif move == close_symbol:
                a -= 1
        return seq

class DyckWord_complete(DyckWord_class):
    r"""
    The class of complete :class:`Dyck words<sage.combinat.dyck_word.DyckWord_class>`.
    A Dyck word is complete, if it contains as many closers as openers.

    For further information on Dyck words, see :class:`DyckWords_class<sage.combinat.dyck_word.DyckWord_class>`.
    """

    def semilength(self):
        r"""
        Returns the semilength of ``self``. This is the number of openers
        and the number of closers of a complete Dyck word.

        EXAMPLES::

            sage: DyckWord([1, 0, 1, 0]).semilength()
            2

        TESTS::

            sage: DyckWord([]).semilength()
            0
        """
        return len(self) / 2

    def to_partition(self):
        r"""
        Returns the partition associated to ``self`` .
        This partition is determined by thinking of ``self`` as a lattice path
        and considering the cells which are above the path but within the
        `n \times n`  grid and the partition is formed by reading the sequence of
        the number of cells in this collection in each row.

        OUTPUT:

        - a partition representing the rows of cells in the square lattice and above the path

        EXAMPLES::

            sage: DyckWord([]).to_partition()
            []
            sage: DyckWord([1,0]).to_partition()
            []
            sage: DyckWord([1,1,0,0]).to_partition()
            []
            sage: DyckWord([1,0,1,0]).to_partition()
            [1]
            sage: DyckWord([1,0,1,0,1,0]).to_partition()
            [2, 1]
            sage: DyckWord([1,1,0,0,1,0]).to_partition()
            [2]
            sage: DyckWord([1,0,1,1,0,0]).to_partition()
            [1, 1]
        """
        from sage.combinat.partition import Partition
        n = len(self) // 2
        res = []
        for c in reversed(self):
            if c == close_symbol:
                n -= 1
            else:
                res.append(n)
        return Partition(res)

    def number_of_parking_functions(self):
        r"""
        Returns the number of parking functions with ``self`` as the supporting
        Dyck path.  One representation of a parking function is as a pair
        consisting of a Dyck path and a permutation such that if `[a_0, a_1, \ldots, a_{n-1}]`
        is the area_sequence (see :meth:`to_area_sequence<DyckWord_class.to_area_sequence>`) then the
        permutation `\pi` such that if `a_{i} < a_{i+1}` then `\pi_i < \pi_{i+1}`.
        This function counts the number of permutations `\pi` which satisfy this
        condition.

        EXAMPLES::

            sage: DyckWord(area_sequence=[0,1,2]).number_of_parking_functions()
            1
            sage: DyckWord(area_sequence=[0,1,1]).number_of_parking_functions()
            3
            sage: DyckWord(area_sequence=[0,1,0]).number_of_parking_functions()
            3
            sage: DyckWord(area_sequence=[0,0,0]).number_of_parking_functions()
            6
        """
        from sage.rings.arith import multinomial
        return multinomial( list(self.rise_composition()) )

    def list_parking_functions( self ):
        r"""
        Returns all parking functions whose supporting Dyck path is ``self`` .

        EXAMPLES::

            sage: DyckWord([1,1,0,0,1,0]).list_parking_functions()
            Permutations of the multi-set [1, 1, 3]
            sage: DyckWord([1,1,1,0,0,0]).list_parking_functions()
            Permutations of the multi-set [1, 1, 1]
            sage: DyckWord([1,0,1,0,1,0]).list_parking_functions()
            Permutations of the set [1, 2, 3]
        """
        alist = self.to_area_sequence()
        return Permutations([i - alist[i]+1 for i in range(len(alist))])
        # TODO: upon implementation of ParkingFunction class
        # map(ParkingFunction, Permutations([i - alist[i]+1 for i in range(len(alist))]))

    def reading_permutation(self):
        r"""
        The permutation formed by taking the reading word of the Dyck path if the
        vertical edges of the Dyck path are labeled from bottom to top with 1 through
        n and the diagonals are read from top to bottom starting with the diagonal
        furthest from the main diagonal.

        EXAMPLES::

            sage: DyckWord([1,0,1,0]).reading_permutation()
            [2, 1]
            sage: DyckWord([1,1,0,0]).reading_permutation()
            [2, 1]
            sage: DyckWord([1,1,0,1,0,0]).reading_permutation()
            [3, 2, 1]
            sage: DyckWord([1,1,0,0,1,0]).reading_permutation()
            [2, 3, 1]
            sage: DyckWord([1,0,1,1,0,0,1,0]).reading_permutation()
            [3, 4, 2, 1]
        """
        alist = self.to_area_sequence()
        if alist==[]:
            return Permutation([])
        m = max(alist)
        p1 =Word([m-alist[-i-1] for i in range(len(alist))]).standard_permutation()
        return p1.inverse().complement()

    def characteristic_symmetric_function(self, q=None, R=QQ['q','t'].fraction_field()):
        r"""
        The characteristic function of the Dyck path is the sum over all permutation
        fillings of the Dyck path `q^{dinv(D,F)} Q_{ides(read(D,F))}` where `ides(read(D,F))`
        is the descent composition of the inverse of the reading word of the filling.

        INPUT:

        - ``q`` -- (default: ``q = R('q')``) a parameter for the generating function power.

        - ``R`` -- (default : ``R = QQ['q','t'].fraction_field()``) the base ring to do the calculations over.

        OUTPUT:

        - an element of the symmetric functions over the ring ``R``.

        EXAMPLES::

            sage: R = QQ['q','t'].fraction_field()
            sage: (q,t) = R.gens()
            sage: f = sum(t**D.area()*D.characteristic_symmetric_function() for D in DyckWords(3)); f
            (q^3+q^2*t+q*t^2+t^3+q*t)*s[1, 1, 1] + (q^2+q*t+t^2+q+t)*s[2, 1] + s[3]
            sage: f.nabla(power=-1)
            s[1, 1, 1]
        """
        from sage.combinat.ncsf_qsym.qsym import QuasiSymmetricFunctions
        from sage.combinat.sf.sf import SymmetricFunctions
        if q is None:
            q=R('q')
        else:
            if not q in R:
                raise ValueError,"q=%s must be an element of the base ring %s"%(q,R)
        F = QuasiSymmetricFunctions(R).Fundamental()
        p = self.reading_permutation()
        perms = [Word(perm).standard_permutation().inverse() for perm in self.list_parking_functions()]
        QSexpr = sum( q**self.dinv(pv)*F((p*pv).inverse().descents_composition()) for pv in perms)
        s = SymmetricFunctions(R).s()
        return s(QSexpr.to_symmetric_function())

    def to_pair_of_standard_tableaux(self):
        r"""
        Converts a Dyck word to a pair of standard tableaux of the same shape and of
        length less than or equal to two.

        EXAMPLES::

            sage: DyckWord([1,0,1,0]).to_pair_of_standard_tableaux()
            ([[1], [2]], [[1], [2]])
            sage: DyckWord([1,1,0,0]).to_pair_of_standard_tableaux()
            ([[1, 2]], [[1, 2]])
            sage: DyckWord([1,1,0,1,0,0,1,1,0,1,0,1,0,0]).to_pair_of_standard_tableaux()
            ([[1, 2, 4, 7], [3, 5, 6]], [[1, 2, 4, 6], [3, 5, 7]])
        """
        from sage.combinat.tableau import Tableau
        n = self.semilength()
        if n==0:
            return (Tableau([]), Tableau([]))
        elif self.height()==n:
            return (Tableau([range(1,n+1)]),Tableau([range(1,n+1)]))
        else:
            left = [[],[]]
            right = [[], []]
            for pos in range(n):
                if self[pos] == open_symbol:
                    left[0].append(pos+1)
                else:
                    left[1].append(pos+1)
                if self[-pos-1] == close_symbol:
                    right[0].append(pos+1)
                else:
                    right[1].append(pos+1)
            return (Tableau(left), Tableau(right))

    def to_312_avoiding_permutation(self):
        r"""
        Converts the Dyck word to a `312`-avoiding permutation using the bijection by
        Bandlow and Killpatrick in [BK2001]_.  Sends the area to the inversion number.

        REFERENCES:

        .. [BK2001] J. Bandlow, K. Killpatrick -- An area-to_inv bijection between
            Dyck paths and 312-avoiding permutations, Electronic Journal
            of Combinatorics, Volume 8, Issue 1 (2001).

        EXAMPLES::

            sage: DyckWord([1,1,0,0]).to_312_avoiding_permutation()
            [2, 1]
            sage: DyckWord([1,0,1,0]).to_312_avoiding_permutation()
            [1, 2]
            sage: p = DyckWord([1,1,0,1,0,0,1,1,0,1,0,1,0,0]).to_312_avoiding_permutation(); p
            [2, 3, 1, 5, 6, 7, 4]
            sage: DyckWord([1,1,0,1,0,0,1,1,0,1,0,1,0,0]).area()
            5
            sage: p.length()
            5

        TESTS::

            sage: PD = [D.to_312_avoiding_permutation() for D in DyckWords(5)]
            sage: all(pi.avoids([3,1,2]) for pi in PD)
            True
            sage: all(D.area()==D.to_312_avoiding_permutation().length() for D in DyckWords(5))
            True
        """
        n = self.semilength()
        area = self.to_area_sequence()
        from sage.groups.perm_gps.permgroup_named import SymmetricGroup
        pi = SymmetricGroup(n).one()
        for j in range(n):
            for i in range(area[j]):
                pi = pi.apply_simple_reflection(j-i)
        return Permutation(~pi)

    def to_noncrossing_permutation(self):
        r"""
        Uses the bijection by C. Stump in [Stu2008]_ to non-crossing permutations.
        A non-crossing permutation when written in cyclic notation has cycles which
        are strictly increasing.  Sends the area to the inversion number and ``self.major_index()``
        is sent to `n(n-1) - maj(\sigma) - maj(\sigma^{-1})`.
        Uses the function :func:`~sage.combinat.dyck_word.pealing`

        REFERENCES:

        .. [Stu2008] C. Stump -- More bijective Catalan combinatorics on permutations
            and on colored permutations, Preprint. arXiv:0808.2822.

        EXAMPLES::

            sage: DyckWord([1,1,0,0]).to_noncrossing_permutation()
            [2, 1]
            sage: DyckWord([1,0,1,0]).to_noncrossing_permutation()
            [1, 2]
            sage: p = DyckWord([1,1,0,1,0,0,1,1,0,1,0,1,0,0]).to_noncrossing_permutation(); p
            [2, 3, 1, 5, 6, 7, 4]
            sage: DyckWord([1,1,0,1,0,0,1,1,0,1,0,1,0,0]).area()
            5
            sage: p.length()
            5

        TESTS::

            sage: all(D.area()==D.to_noncrossing_permutation().length() for D in DyckWords(5))
            True
            sage: all(20-D.major_index()==D.to_noncrossing_permutation().major_index()
            ...       +D.to_noncrossing_permutation().imajor_index() for D in DyckWords(5))
            True
        """
        n = self.semilength()
        if n==0:
            return Permutation([])
        D,touch_sequence = pealing(self, return_touches=True)
        from sage.groups.perm_gps.permgroup_named import SymmetricGroup
        S = SymmetricGroup(n)
        pi = S.one()
        while touch_sequence:
            for touches in touch_sequence:
                pi = pi * S( tuple(touches) )
            D,touch_sequence = pealing(D, return_touches=True)
        return Permutation(pi)

    def to_321_avoiding_permutation(self):
        r"""
        Uses the bijection [Knu1973]_ to `321`-avoiding permutations. It is shown in
        [EP2004]_ that it sends the number of centered tunnels to the number of fixed
        points, the number of right tunnels to the number of exceedences, and the semilength
        plus the height of the middle point to 2 times the length of the longest
        increasing subsequence.

        REFERENCES:

        .. [EP2004] S. Elizalde, I. Pak -- Bijections for refined restricted
            permutations, JCTA 105(2) 2004.
        .. [Knu1973] D. Knuth -- The Art of Computer Programming, Vol. III,
            Addison-Wesley, Reading, MA, 1973.

        EXAMPLES::

            sage: DyckWord([1,0,1,0]).to_321_avoiding_permutation()
            [2, 1]
            sage: DyckWord([1,1,0,0]).to_321_avoiding_permutation()
            [1, 2]
            sage: D = DyckWord([1,1,0,1,0,0,1,1,0,1,0,1,0,0])
            sage: p = D.to_321_avoiding_permutation()
            sage: p
            [3, 5, 1, 6, 2, 7, 4]
            sage: D.number_of_tunnels()
            0
            sage: p.number_of_fixed_points()
            0
            sage: D.number_of_tunnels('right')
            4
            sage: len(p.weak_excedences())-p.number_of_fixed_points()
            4
            sage: n = D.semilength()
            sage: D.heights()[n] + n
            8
            sage: 2*p.longest_increasing_subsequence_length()
            8

        TESTS::

            sage: PD = [D.to_321_avoiding_permutation() for D in DyckWords(5)]
            sage: all(pi.avoids([3,2,1]) for pi in PD)
            True
            sage: to_perm = lambda x: x.to_321_avoiding_permutation()
            sage: all(D.number_of_tunnels() == to_perm(D).number_of_fixed_points()
            ...       for D in DyckWords(5))
            True
            sage: all(D.number_of_tunnels('right') == len(to_perm(D).weak_excedences())
            ...       -to_perm(D).number_of_fixed_points() for D in DyckWords(5))
            True
            sage: all(D.heights()[5]+5 == 2*to_perm(D).longest_increasing_subsequence_length()
            ...       for D in DyckWords(5))
            True
        """
        from sage.combinat.permutation import robinson_schensted_inverse
        A,B = self.to_pair_of_standard_tableaux()
        return robinson_schensted_inverse(A,B)

    def to_132_avoiding_permutation(self):
        r"""
        Uses the bijection by C. Krattenthaler in [Kra2001]_ to `132`-avoiding permutations.

        REFERENCES:

        .. [Kra2001] C. Krattenthaler -- Permutations with restricted patterns and Dyck
            paths, Adv. Appl. Math. 27 (2001), 510--530.

        EXAMPLES::

            sage: DyckWord([1,1,0,0]).to_132_avoiding_permutation()
            [1, 2]
            sage: DyckWord([1,0,1,0]).to_132_avoiding_permutation()
            [2, 1]
            sage: DyckWord([1,1,0,1,0,0,1,1,0,1,0,1,0,0]).to_132_avoiding_permutation()
            [6, 5, 4, 7, 2, 1, 3]

        TESTS::

            sage: PD = [D.to_132_avoiding_permutation() for D in DyckWords(5)]
            sage: all(pi.avoids([1,3,2]) for pi in PD)
            True
        """
        n = self.semilength()
        area = self.to_area_sequence()
        area.append(0)
        pi = []
        values = range(1,n+1)
        for i in range(n):
            if area[n-i-1]+1 > area[n-i]:
                pi.append(n-i-area[n-i-1])
                values.remove(n-i-area[n-i-1])
            else:
                v = min( v for v in values if v > n-i-area[n-i-1] )
                pi.append(v)
                values.remove(v)
        return Permutation(pi)

    def to_permutation(self,map):
        r"""
        This is simply a method collecting all implemented maps from Dyck words to permutations.

        INPUT:

            - ``map`` -- defines the map from Dyck words to permutations. These are currently
                        - ``Bandlow-Killpatrick``: :func:`to_312_avoiding_permutation`
                        - ``Knuth``: :func:`to_321_avoiding_permutation`
                        - ``Krattenthaler``: :func:`to_132_avoiding_permutation`
                        - ``Stump``: :func:`to_noncrossing_permutation`

        EXAMPLES::

            sage: D = DyckWord([1,1,1,0,1,0,0,0])
            sage: D.pretty_print()
               _____
             _| x x
            | x x  .
            | x  . .
            |  . . .

            sage: D.to_permutation(map="Bandlow-Killpatrick")
            [3, 4, 2, 1]
            sage: D.to_permutation(map="Stump")
            [4, 2, 3, 1]
            sage: D.to_permutation(map="Knuth")
            [1, 2, 4, 3]
            sage: D.to_permutation(map="Krattenthaler")
            [2, 1, 3, 4]
        """
        if   map=="Bandlow-Killpatrick":
            return self.to_312_avoiding_permutation()
        elif map=="Knuth":
            return self.to_321_avoiding_permutation()
        elif map=="Krattenthaler":
            return self.to_132_avoiding_permutation()
        elif map=="Stump":
            return self.to_noncrossing_permutation()
        else:
            raise ValueError, "The given map is not valid."

    def to_noncrossing_partition(self, bijection=None):
        r"""
        Bijection of Biane from Dyck words to noncrossing partitions. Thanks to
        Mathieu Dutour for describing the bijection.  See also
        :func:`from_noncrossing_partition`.

        There is an optional parameter ``bijection`` that indicates if a different bijection
        from Dyck words to non-crossing partitions should be used (since there are
        potentially many).

        If the parameter ``bijection`` is "Stump" then the bijection used is from
        a paper by C. Stump, see also the method :meth:`to_noncrossing_permutation`.

        EXAMPLES::

            sage: DyckWord([]).to_noncrossing_partition()
            []
            sage: DyckWord([1, 0]).to_noncrossing_partition()
            [[1]]
            sage: DyckWord([1, 1, 0, 0]).to_noncrossing_partition()
            [[1, 2]]
            sage: DyckWord([1, 1, 1, 0, 0, 0]).to_noncrossing_partition()
            [[1, 2, 3]]
            sage: DyckWord([1, 0, 1, 0, 1, 0]).to_noncrossing_partition()
            [[1], [2], [3]]
            sage: DyckWord([1, 1, 0, 1, 0, 0]).to_noncrossing_partition()
            [[2], [1, 3]]
            sage: DyckWord([]).to_noncrossing_partition("Stump")
            []
            sage: DyckWord([1, 0]).to_noncrossing_partition("Stump")
            [[1]]
            sage: DyckWord([1, 1, 0, 0]).to_noncrossing_partition("Stump")
            [[1, 2]]
            sage: DyckWord([1, 1, 1, 0, 0, 0]).to_noncrossing_partition("Stump")
            [[1, 3], [2]]
            sage: DyckWord([1, 0, 1, 0, 1, 0]).to_noncrossing_partition("Stump")
            [[1], [2], [3]]
            sage: DyckWord([1, 1, 0, 1, 0, 0]).to_noncrossing_partition("Stump")
            [[1, 2, 3]]
        """
        if bijection=="Stump":
            return [[v for v in c] for c in self.to_noncrossing_permutation().cycle_tuples()]
        partition = []
        stack = []
        i = 0
        p = 1

        #Invariants:
        # - self[i] = 0
        # - p is the number of opening parens at position i

        while i < len(self):
            stack.append(p)
            j = i + 1
            while j < len(self) and self[j] == close_symbol:
                j += 1

            #Now j points to the next 1 or past the end of self
            nz = j - (i+1) # the number of )'s between i and j
            if nz > 0:
                # Remove the nz last elements of stack and
                # make a new part in partition
                if nz > len(stack):
                    raise ValueError, "incorrect Dyck word"

                partition.append( stack[-nz:] )

                stack = stack[: -nz]
            i = j
            p += 1

        if len(stack) > 0:
            raise ValueError, "incorrect Dyck word"

        return partition

    def to_Catalan_code(self):
        r"""
        Return the Catalan code associated to ``self`` .  The Catalan code is a
        sequence of non--negative integers `a_i` such that if `i<j` and `a_i > 0`
        and `a_j>0` and `a_{i+1} =a_{i+1} = \cdots = a_{j-1} = 0` then `a_i - a_j < j-i`.

        The Catalan code of a Dyck word is example (x) in Richard Stanley's
        exercises on combinatorial interpretations for Catalan objects.
        The code in this example is the reverse of the description provided
        there. See [Sta1999]_ and [Sta]_.

        EXAMPLES::

            sage: DyckWord([]).to_Catalan_code()
            []
            sage: DyckWord([1, 0]).to_Catalan_code()
            [0]
            sage: DyckWord([1, 1, 0, 0]).to_Catalan_code()
            [0, 1]
            sage: DyckWord([1, 0, 1, 0]).to_Catalan_code()
            [0, 0]
            sage: from sage.combinat.dyck_word import DyckWord_complete
            sage: all(dw ==
            ...       DyckWord_complete.from_Catalan_code(dw.to_Catalan_code())
            ...       for i in range(6) for dw in DyckWords(i))
            True
        """
        if not self:
            return []
        cut = self.associated_parenthesis(0)
        recdw = DyckWord(self[1:cut]+self[cut+1:])
        returns = [0]+recdw.returns_to_zero()
        res = recdw.to_Catalan_code()
        res.append(returns.index(cut-1))
        return res

    @classmethod
    def from_Catalan_code(cls, code):
        r"""
        Return the Dyck words associated to the given Catalan code

        The Catalan code is a sequence of non--negative integers `a_i` such that
        if `i<j` and `a_i > 0` and `a_j>0` and `a_{i+1} = a_{i+1} = \cdots = a_{j-1} = 0`
        then `a_i - a_j < j-i`.

        The Catalan code of a Dyck word is example (x) in Richard Stanley's
        exercises on combinatorial interpretations for Catalan objects.
        The code in this example is the reverse of the description provided
        there. See [Sta1999]_ and [Sta]_.

        EXAMPLES::

            sage: from sage.combinat.dyck_word import DyckWord_complete
            sage: DyckWord_complete.from_Catalan_code([])
            []
            sage: DyckWord_complete.from_Catalan_code([0])
            [1, 0]
            sage: DyckWord_complete.from_Catalan_code([0, 1])
            [1, 1, 0, 0]
            sage: DyckWord_complete.from_Catalan_code([0, 0])
            [1, 0, 1, 0]
        """
        code = list(code)
        if not code: return cls([])
        res = cls.from_Catalan_code(code[:-1])
        cuts = [0]+res.returns_to_zero()
        return cls([1]+res[:cuts[code[-1]]]+[0]+res[cuts[code[-1]]:])

    @classmethod
    def from_area_sequence(cls, code):
        r"""
        Return the Dyck words associated to the given area sequence.

        The area sequence is a list of integers `l` such that `l_0 = 0` and
        `0 \leq l_{i+1} \leq l_i + 1` for `i > 0`.
        This sequence is equal to the number of full cells below the
        path but above the diagonal in the corresponding Dyck path.

        .. SEEALSO:: :meth:`area`

        INPUT:

            - ``code`` -- a list of integers satisfying ``0 <= code[i+1] <= code[i]+1``.

        EXAMPLES::

            sage: from sage.combinat.dyck_word import DyckWord_complete
            sage: DyckWord_complete.from_area_sequence([])
            []
            sage: DyckWord_complete.from_area_sequence([0])
            [1, 0]
            sage: DyckWord_complete.from_area_sequence([0, 1])
            [1, 1, 0, 0]
            sage: DyckWord_complete.from_area_sequence([0, 0])
            [1, 0, 1, 0]
        """
        if not is_area_sequence(code):
            raise ValueError, "The given sequence is not a sequence giving the number of cells between the Dyck path and the diagonal."
        dyck_word = []
        for i in xrange(len(code)):
            if i > 0:
                dyck_word.extend([close_symbol]*(code[i-1]-code[i]+1))
            dyck_word.append(open_symbol)
        dyck_word.extend([close_symbol]*(2*len(code)-len(dyck_word)))
        return cls(dyck_word)

    def to_ordered_tree(self):
        r"""
        TESTS::

            sage: DyckWord([1, 1, 0, 0]).to_ordered_tree()
            Traceback (most recent call last):
            ...
            NotImplementedError: TODO
        """
        raise NotImplementedError, "TODO"

    def to_triangulation(self):
        r"""

        This method is not yet implemented.

        TESTS::

            sage: DyckWord([1, 1, 0, 0]).to_triangulation()
            Traceback (most recent call last):
            ...
            NotImplementedError: TODO
        """
        raise NotImplementedError, "TODO"

    def to_non_decreasing_parking_function(self):
        r"""
        Bijection to :class:`non-decreasing parking
        functions<sage.combinat.non_decreasing_parking_function.NonDecreasingParkingFunctions>`. See
        there the method
        :meth:`~sage.combinat.non_decreasing_parking_function.NonDecreasingParkingFunction.to_dyck_word`
        for more information.

        EXAMPLES::

            sage: DyckWord([]).to_non_decreasing_parking_function()
            []
            sage: DyckWord([1,0]).to_non_decreasing_parking_function()
            [1]
            sage: DyckWord([1,1,0,0]).to_non_decreasing_parking_function()
            [1, 1]
            sage: DyckWord([1,0,1,0]).to_non_decreasing_parking_function()
            [1, 2]
            sage: DyckWord([1,0,1,1,0,1,0,0,1,0]).to_non_decreasing_parking_function()
            [1, 2, 2, 3, 5]

        TESTS::

            sage: ld=DyckWords(5);
            sage: list(ld) == [dw.to_non_decreasing_parking_function().to_dyck_word() for dw in ld]
            True
        """
        from sage.combinat.non_decreasing_parking_function import NonDecreasingParkingFunction
        return NonDecreasingParkingFunction.from_dyck_word(self)

    @classmethod
    def from_non_decreasing_parking_function(cls, pf):
        r"""
        Bijection from :class:`non-decreasing parking
        functions<sage.combinat.non_decreasing_parking_function.NonDecreasingParkingFunctions>`. See
        there the method
        :meth:`~sage.combinat.non_decreasing_parking_function.NonDecreasingParkingFunction.to_dyck_word`
        for more information.

        EXAMPLES::

            sage: from sage.combinat.dyck_word import DyckWord_complete
            sage: DyckWord_complete.from_non_decreasing_parking_function([])
            []
            sage: DyckWord_complete.from_non_decreasing_parking_function([1])
            [1, 0]
            sage: DyckWord_complete.from_non_decreasing_parking_function([1,1])
            [1, 1, 0, 0]
            sage: DyckWord_complete.from_non_decreasing_parking_function([1,2])
            [1, 0, 1, 0]
            sage: DyckWord_complete.from_non_decreasing_parking_function([1,1,1])
            [1, 1, 1, 0, 0, 0]
            sage: DyckWord_complete.from_non_decreasing_parking_function([1,2,3])
            [1, 0, 1, 0, 1, 0]
            sage: DyckWord_complete.from_non_decreasing_parking_function([1,1,3,3,4,6,6])
            [1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0]

        TESTS::

            sage: DyckWord_complete.from_non_decreasing_parking_function(NonDecreasingParkingFunction([]))
            []
            sage: DyckWord_complete.from_non_decreasing_parking_function(NonDecreasingParkingFunction([1,1,3,3,4,6,6]))
            [1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0]
        """
        return cls.from_area_sequence([ i - pf[i] + 1 for i in range(len(pf)) ])

    def major_index(self):
        r"""
        Returns the major index of ``self`` . This is
        the sum of the positions of the valleys of ``self``
        (when started counting at position ``1``).

        EXAMPLES::

            sage: DyckWord([1, 0, 1, 0]).major_index()
            2
            sage: DyckWord([1, 1, 0, 0]).major_index()
            0
            sage: DyckWord([1, 1, 0, 0, 1, 0]).major_index()
            4
            sage: DyckWord([1, 0, 1, 1, 0, 0]).major_index()
            2

        TESTS::

            sage: DyckWord([]).major_index()
            0
            sage: DyckWord([1, 0]).major_index()
            0
        """
        valleys = self.valleys()
        return sum(valleys) + len(valleys)

    def pyramid_weight( self ):
        r"""
        A pyramid of the Dyck word is a subsequence of the form
        `1^h 0^h`, a pyramid is maximal if it is not preceeded my a `1`
        and followed by a `0`.
        The pyramid weight is the sums of the lengths of the maximal
        pyramids and was defined in [DS1992]_.

        EXAMPLES::

            sage: DyckWord([1,1,0,1,1,1,0,0,1,0,0,0,1,1,0,0]).pyramid_weight()
            6
            sage: DyckWord([1,1,1,0,0,0]).pyramid_weight()
            3
            sage: DyckWord([1,0,1,0,1,0]).pyramid_weight()
            3
            sage: DyckWord([1,1,0,1,0,0]).pyramid_weight()
            2

        REFERENCES:

        .. [DS1992] A. Denise, R. Simion, Two combinatorial statistics on Dyck paths,
                 Discrete Math 137 (1992), 155-176.
        """
        aseq = self.to_area_sequence() + [0]
        bseq = self.reverse().to_area_sequence() + [0]
        apeak = []
        bpeak = []
        for i in range(len(aseq)-1):
            if aseq[i+1]<=aseq[i]:
                apeak += [i]
            if bseq[i+1]<=bseq[i]:
                bpeak += [i]
        out = 0
        for i in range(len(apeak)):
            out += min(aseq[apeak[i]]-aseq[apeak[i]+1]+1,bseq[bpeak[-i-1]]-bseq[bpeak[-i-1]+1]+1)
        return out

    def tunnels(self):
        r"""
        Returns the list of ranges of the matching parentheses in the Dyck word.
        That is, if ``(a,b)`` is in ``self.tunnels()``, then the matching parenthesis
        to ``self[a]`` is ``self[b-1]`` .

        EXAMPLES::

            sage: DyckWord([1, 1, 0, 1, 1, 0, 0, 1, 0, 0]).tunnels()
            [(0, 10), (1, 3), (3, 7), (4, 6), (7, 9)]
        """
        heights = self.heights()
        tunnels = []
        for i in range(len(heights)-1):
            height = heights[i]
            if height < heights[i+1]:
                tunnels.append( (i,i+1+heights[i+1:].index(height)) )
        return tunnels

    def number_of_tunnels(self,tunnel_type='centered'):
        r"""
        A tunnel is a pair ``(a,b)`` where ``a`` is the position of an open
        parenthesis and ``b`` is the position of the matching close parenthesis.
        If ``a+b==n`` then the tunnel is called ``centered`` .  If ``a+b<n`` then
        the tunnel is called ``left`` and if ``a+b>n``, then the tunnel is called
        ``right`` .

        INPUT:

        - ``self`` -- a Dyck word.

        - ``tunnel_type`` -- (default: ``'centered'``) an optional parameter specifying ``'left'``, ``'right'``, ``'centered'``, ``'all'``.

        EXAMPLES::

            sage: DyckWord([1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0]).number_of_tunnels()
            0
            sage: DyckWord([1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0]).number_of_tunnels('left')
            5
            sage: DyckWord([1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0]).number_of_tunnels('right')
            2
            sage: DyckWord([1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0]).number_of_tunnels('all')
            7
            sage: DyckWord([1, 1, 0, 0]).number_of_tunnels('centered')
            2
        """
        n = len(self)
        tunnels = self.tunnels()
        if tunnel_type == 'left':
            return len( [ i for (i,j) in tunnels if i+j < n ] )
        elif tunnel_type == 'centered':
            return len( [ i for (i,j) in tunnels if i+j == n ] )
        elif tunnel_type == 'right':
            return len( [ i for (i,j) in tunnels if i+j > n ] )
        elif tunnel_type == 'all':
            return len(tunnels)
        else:
            raise ValueError, "The given tunnel_type is not valid."

    def reverse(self):
        r"""
        Returns the reverse and complement of the Dyck word ``self`` .
        This operation corresponds to flipping the Dyck path across the `y=-x` line.

        EXAMPLES::

            sage: DyckWord([1,1,0,0,1,0]).reverse()
            [1, 0, 1, 1, 0, 0]
            sage: DyckWord([1,1,1,0,0,0]).reverse()
            [1, 1, 1, 0, 0, 0]
            sage: DyckWords(5).filter(lambda D: D.reverse()==D).cardinality()
            10

        TESTS::

            sage: DyckWord([]).reverse()
            []
        """
        list = []
        for i in range(len(self)):
            if self[i] == open_symbol:
                list.append(close_symbol)
            else:
                list.append(open_symbol)
        list.reverse()
        return DyckWord(list)

    def first_return_decomposition(self):
        r"""
        Decompose a Dyck word into a pair of Dyck words (potentially empty) where
        the first word consists of the word after the first up step and the corresponding
        matching closing parenthesis.

        EXAMPLES::

            sage: DyckWord([1,1,0,1,0,0,1,1,0,1,0,1,0,0]).first_return_decomposition()
            ([1, 0, 1, 0], [1, 1, 0, 1, 0, 1, 0, 0])
            sage: DyckWord([1,1,0,0]).first_return_decomposition()
            ([1, 0], [])
            sage: DyckWord([1,0,1,0]).first_return_decomposition()
            ([], [1, 0])
        """
        k = self.position_of_first_return()*2
        return DyckWord(self[1:k-1]),DyckWord(self[k:])

    def decomposition_reverse(self):
        r"""
        An involution on Dyck words with a recursive definition.  If ``self`` decomposes
        as 1, ``D1`` , 0, ``D2`` where ``D1`` and ``D2`` are complete Dyck words then the
        decomposition reverse is 1, `\phi(` ``D2`` `)`, 0, `\phi(` ``D1`` `)`.

        EXAMPLES::

            sage: DyckWord([1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0]).decomposition_reverse()
            [1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0]
            sage: DyckWord([1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0]).decomposition_reverse()
            [1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0]
            sage: DyckWord([1,1,0,0]).decomposition_reverse()
            [1, 0, 1, 0]
            sage: DyckWord([1,0,1,0]).decomposition_reverse()
            [1, 1, 0, 0]
        """
        if self.semilength() == 0:
            return self
        else:
            D1,D2 = self.first_return_decomposition()
            return DyckWord([1]+list(D2.decomposition_reverse())+[0]+list(D1.decomposition_reverse()))

    def area_dinv_to_bounce_area_map(self):
        r"""
        Returns the image of the Dyck word under the map which sends a
        Dyck word with ``area`` equal to `r` and ``dinv`` equal to `s` to a Dyck
        word with ``bounce`` equal to `r` and ``area`` equal to `s` .

        For a definition of this map, see [Hag2008]_.

        EXAMPLES::

            sage: DyckWord([1,1,0,1,0,0,1,1,0,1,0,1,0,0]).area_dinv_to_bounce_area_map()
            [1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0]
            sage: DyckWord([1,1,0,1,0,0,1,1,0,1,0,1,0,0]).area()
            5
            sage: DyckWord([1,1,0,1,0,0,1,1,0,1,0,1,0,0]).dinv()
            13
            sage: DyckWord([1,1,1,1,1,0,0,0,1,0,0,1,0,0]).area()
            13
            sage: DyckWord([1,1,1,1,1,0,0,0,1,0,0,1,0,0]).bounce()
            5
            sage: DyckWord([1,1,1,1,1,0,0,0,1,0,0,1,0,0]).area_dinv_to_bounce_area_map()
            [1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0]
            sage: DyckWord([1,1,0,0]).area_dinv_to_bounce_area_map()
            [1, 0, 1, 0]
            sage: DyckWord([1,0,1,0]).area_dinv_to_bounce_area_map()
            [1, 1, 0, 0]
        """
        a = self.to_area_sequence()
        if a==[]:
            return self
        a.reverse()
        image = []
        for i in range(max(a),-2,-1):
            for j in a:
                if j == i:
                    image.append(1)
                elif j == i + 1:
                    image.append(0)
        return DyckWord(image)

    def area(self):
        r"""
        Returns the area for the Dyck word corresponding to the area
        of the Dyck path.

        One can view a balanced Dyck word as a lattice path from
        `(0,0)` to `(n,n)` in the first quadrant by letting
        '1's represent steps in the direction `(1,0)` and '0's
        represent steps in the direction `(0,1)`. The resulting
        path will remain weakly above the diagonal `y = x`.

        The area statistic is the number of complete
        squares in the integer lattice which are below the path and above
        the line `y = x`. The 'half-squares' directly above the
        line `y=x` do not contribute to this statistic.

        EXAMPLES::

            sage: dw = DyckWord([1,0,1,0])
            sage: dw.area() # 2 half-squares, 0 complete squares
            0

        ::

            sage: dw = DyckWord([1,1,1,0,1,1,1,0,0,0,1,1,0,0,1,0,0,0])
            sage: dw.area()
            19

        ::

            sage: DyckWord([1,1,1,1,0,0,0,0]).area()
            6
            sage: DyckWord([1,1,1,0,1,0,0,0]).area()
            5
            sage: DyckWord([1,1,1,0,0,1,0,0]).area()
            4
            sage: DyckWord([1,1,1,0,0,0,1,0]).area()
            3
            sage: DyckWord([1,0,1,1,0,1,0,0]).area()
            2
            sage: DyckWord([1,1,0,1,1,0,0,0]).area()
            4
            sage: DyckWord([1,1,0,0,1,1,0,0]).area()
            2
            sage: DyckWord([1,0,1,1,1,0,0,0]).area()
            3
            sage: DyckWord([1,0,1,1,0,0,1,0]).area()
            1
            sage: DyckWord([1,0,1,0,1,1,0,0]).area()
            1
            sage: DyckWord([1,1,0,0,1,0,1,0]).area()
            1
            sage: DyckWord([1,1,0,1,0,0,1,0]).area()
            2
            sage: DyckWord([1,1,0,1,0,1,0,0]).area()
            3
            sage: DyckWord([1,0,1,0,1,0,1,0]).area()
            0
        """
        above = 0
        diagonal = 0
        a = 0
        for move in self:
            if move == open_symbol:
                above += 1
            elif move == close_symbol:
                diagonal += 1
                a += above - diagonal
        return a

    a_statistic = deprecated_function_alias(13550, area)

    def bounce_path(self):
        r"""
        Returns the bounce path of the Dyck path formed by starting at `(n,n)` and
        traveling West until encountering the first vertical step of ``self``,
        then South until encountering the diagonal, then West again to hit the path,
        etc. until the `(0,0)` point is reached.  The path followed by this walk
        is the bounce path.

        .. SEEALSO:: :meth:`bounce`

        EXAMPLES::

            sage: DyckWord([1,1,0,1,0,0]).bounce_path()
            [1, 0, 1, 1, 0, 0]
            sage: DyckWord([1,1,1,0,0,0]).bounce_path()
            [1, 1, 1, 0, 0, 0]
            sage: DyckWord([1,0,1,0,1,0]).bounce_path()
            [1, 0, 1, 0, 1, 0]
            sage: DyckWord([1,1,1,1,0,0,1,0,0,0]).bounce_path()
            [1, 1, 0, 0, 1, 1, 1, 0, 0, 0]

        TESTS::

            sage: DyckWord([]).bounce_path()
            []
            sage: DyckWord([1,0]).bounce_path()
            [1, 0]

        """
        area_seq = self.to_area_sequence()
        i = len(area_seq)-1
        n = 5
        while i > 0:
            n -= 1
            a = area_seq[i]
            i_new = i - a
            while i > i_new:
                i -= 1
                area_seq[i] = area_seq[i+1] - 1
            i -= 1
        return DyckWord(area_sequence = area_seq)

    def bounce(self):
        r"""
        Returns the bounce statistic of ``self`` due to J. Haglund, see [Hag2008]_.

        One can view a balanced Dyck word as a lattice path from `(0,0)` to
        `(n,n)` in the first quadrant by letting '1's represent steps in
        the direction `(0,1)` and '0's represent steps in the direction
        `(1,0)`.  The resulting path will remain weakly above the diagonal
        `y = x`.

        We describe the bounce statistic of such a path in terms of what is
        known as the "bounce path".

        We can think of our bounce path as describing the trail of a billiard
        ball shot West from (n, n), which "bounces" down whenever it
        encounters a vertical step and "bounces" left when it encounters the
        line y = x.

        The bouncing ball will strike the diagonal at places

        .. MATH::

            (0, 0), (j_1, j_1), (j_2, j_2), \dots , (j_r-1, j_r-1), (j_r, j_r)
            =
            (n, n).

        We define the bounce to be the sum `\sum_{i=1}^{r-1} j_i`.

        EXAMPLES::

            sage: DyckWord([1,1,1,0,1,1,1,0,0,0,1,1,0,0,1,0,0,0]).bounce()
            7
            sage: DyckWord([1,1,1,1,0,0,0,0]).bounce()
            0
            sage: DyckWord([1,1,1,0,1,0,0,0]).bounce()
            1
            sage: DyckWord([1,1,1,0,0,1,0,0]).bounce()
            2
            sage: DyckWord([1,1,1,0,0,0,1,0]).bounce()
            3
            sage: DyckWord([1,0,1,1,0,1,0,0]).bounce()
            3
            sage: DyckWord([1,1,0,1,1,0,0,0]).bounce()
            1
            sage: DyckWord([1,1,0,0,1,1,0,0]).bounce()
            2
            sage: DyckWord([1,0,1,1,1,0,0,0]).bounce()
            1
            sage: DyckWord([1,0,1,1,0,0,1,0]).bounce()
            4
            sage: DyckWord([1,0,1,0,1,1,0,0]).bounce()
            3
            sage: DyckWord([1,1,0,0,1,0,1,0]).bounce()
            5
            sage: DyckWord([1,1,0,1,0,0,1,0]).bounce()
            4
            sage: DyckWord([1,1,0,1,0,1,0,0]).bounce()
            2
            sage: DyckWord([1,0,1,0,1,0,1,0]).bounce()
            6

        """
        x_pos = len(self)/2
        y_pos = len(self)/2

        b = 0

        mode = "left"
        makeup_steps = 0
        l = self._list[:]
        l.reverse()

        for move in l:
            #print x_pos, y_pos, mode, move
            if mode == "left":
                if move == close_symbol:
                    x_pos -= 1
                elif move == open_symbol:
                    y_pos -= 1
                    if x_pos == y_pos:
                        b += x_pos
                    else:
                        mode = "drop"
            elif mode == "drop":
                if move == close_symbol:
                    makeup_steps += 1
                elif move == open_symbol:
                    y_pos -= 1
                    if x_pos == y_pos:
                        b += x_pos
                        mode = "left"
                        x_pos -= makeup_steps
                        makeup_steps = 0

        return b

    b_statistic = deprecated_function_alias(13550, bounce)

    def dinv(self, labeling = None):
        r"""
        Returns the dinv statistic of ``self`` due to M. Haiman, see [Hag2008]_.
        If a labeling is provided then this function returns the dinv of the labeled
        Dyck word.

        INPUT:

        - ``self`` -- a Dyck word.

        - ``labeling`` -- an optional argument to be viewed as the labelings of the vertical edges of the Dyck path.

        OUTPUT:

        - an integer -- representing the ``dinv`` statistic of the Dyck path or the labelled Dyck path.

        EXAMPLES::

            sage: DyckWord([1,0,1,0,1,0,1,0,1,0]).dinv()
            10
            sage: DyckWord([1,1,1,1,1,0,0,0,0,0]).dinv()
            0
            sage: DyckWord([1,1,1,1,0,1,0,0,0,0]).dinv()
            1
            sage: DyckWord([1,1,0,1,0,0,1,1,0,1,0,1,0,0]).dinv()
            13
            sage: DyckWord([1,1,0,1,0,0,1,1,0,1,0,1,0,0]).dinv([1,2,3,4,5,6,7])
            11
            sage: DyckWord([1,1,0,1,0,0,1,1,0,1,0,1,0,0]).dinv([6,7,5,3,4,2,1])
            2
        """
        alist = self.to_area_sequence()
        cnt = 0
        for j in range(len(alist)):
            for i in range(j):
                if (alist[i]-alist[j] == 0 and (labeling is None or labeling[i]<labeling[j])) or (alist[i]-alist[j]==1 and (labeling is None or labeling[i]>labeling[j])):
                    cnt+=1
        return cnt

def DyckWords(k1=None, k2=None):
    r"""
    Returns the combinatorial class of Dyck words. A Dyck word is a
    sequence `(w_1, ..., w_n)` consisting of 1 s and 0 s, with the property that for any
    `i` with `1 \le i \le n`, the sequence `(w_1,...,w_i)` contains at least as many 1 s as 0 .

    A Dyck word is balanced if the total number of 1 s is equal to the total number of
    0 s. The number of balanced Dyck words of length `2k` is given by the :func:`Catalan number<sage.combinat.combinat.catalan_number>` `C_k`.

    EXAMPLES: If neither ``k1`` nor ``k2`` are specified, then DyckWords
    returns the combinatorial class of all balanced Dyck words.

    ::

        sage: DW = DyckWords(); DW
        Dyck words
        sage: [] in DW
        True
        sage: [1, 0, 1, 0] in DW
        True
        sage: [1, 1, 0] in DW
        False

    If just ``k1`` is specified, then it returns the combinatorial class of
    balanced Dyck words with ``k1`` opening parentheses and ``k1`` closing
    parentheses.

    ::

        sage: DW2 = DyckWords(2); DW2
        Dyck words with 2 opening parentheses and 2 closing parentheses
        sage: DW2.first()
        [1, 0, 1, 0]
        sage: DW2.last()
        [1, 1, 0, 0]
        sage: DW2.cardinality()
        2
        sage: DyckWords(100).cardinality() == catalan_number(100)
        True

    If ``k2`` is specified in addition to ``k1``, then it returns the
    combinatorial class of Dyck words with ``k1`` opening parentheses and
    ``k2`` closing parentheses.

    ::

        sage: DW32 = DyckWords(3,2); DW32
        Dyck words with 3 opening parentheses and 2 closing parentheses
        sage: DW32.list()
        [[1, 0, 1, 0, 1],
         [1, 0, 1, 1, 0],
         [1, 1, 0, 0, 1],
         [1, 1, 0, 1, 0],
         [1, 1, 1, 0, 0]]
    """
    if k1 is None and k2 is None:
        return DyckWords_all()
    else:
        if k1 < 0 or (k2 is not None and k2 < 0):
            raise ValueError, "k1 (= %s) and k2 (= %s) must be nonnegative, with k1 >= k2."%(k1, k2)
        if k2 is not None and k1 < k2:
            raise ValueError, "k1 (= %s) must be >= k2 (= %s)"%(k1, k2)
        if k2 is None:
            return DyckWords_size(k1, k1)
        else:
            return DyckWords_size(k1, k2)

class DyckWords_all(InfiniteAbstractCombinatorialClass):
    def __init__(self):
        r"""
        TESTS::

            sage: DW = DyckWords()
            sage: DW == loads(dumps(DW))
            True
        """
        pass

    def __repr__(self):
        r"""
        TESTS::

            sage: repr(DyckWords())
            'Dyck words'
        """
        return "Dyck words"

    def __contains__(self, x):
        r"""
        TESTS::

            sage: [] in DyckWords()
            True
            sage: [1] in DyckWords()
            False
            sage: [0] in DyckWords()
            False
            sage: [1, 0] in DyckWords()
            True
        """
        if isinstance(x, DyckWord_class):
            return True

        if not isinstance(x, list):
            return False

        if len(x) % 2 != 0:
            return False

        return is_a(x)

    def _infinite_cclass_slice(self, n):
        r"""
        Needed by InfiniteAbstractCombinatorialClass to build __iter__.

        TESTS::

            sage: DyckWords()._infinite_cclass_slice(4) == DyckWords(4)
            True
            sage: it = iter(DyckWords())    # indirect doctest
            sage: [it.next() for i in range(10)]
            [[], [1, 0], [1, 0, 1, 0], [1, 1, 0, 0], [1, 0, 1, 0, 1, 0], [1, 0, 1, 1, 0, 0], [1, 1, 0, 0, 1, 0], [1, 1, 0, 1, 0, 0], [1, 1, 1, 0, 0, 0], [1, 0, 1, 0, 1, 0, 1, 0]]
         """
        return DyckWords_size(n, n)

    def _an_element_(self):
        r"""
        TESTS::

            sage: DyckWords().an_element()
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        """
        return self._infinite_cclass_slice(5).an_element()

    class height_poset(UniqueRepresentation, Parent):
        r"""
        The poset of complete Dyck word compared componentwise by ``heights``.
        This is, ``D`` is smaller than or equal to ``D'`` if it is weakly below ``D'``.
        """
        def __init__(self):
            r"""
            TESTS::

                sage: poset = DyckWords().height_poset()
                sage: TestSuite(poset).run()
            """
            Parent.__init__(self,
                            facade = DyckWords_all(),
                            category = Posets())

        def _an_element_(self):
            r"""
            TESTS::

                sage: DyckWords().height_poset().an_element()   # indirect doctest
                [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]

            """
            return DyckWords_all().an_element()

        def __call__(self, obj):
            r"""
            TESTS::

                sage: poset = DyckWords().height_poset()
                sage: poset([1,0,1,0])
                [1, 0, 1, 0]
            """
            return DyckWords_all()(obj)

        def le(self, dw1, dw2):
            r"""
            Compare two Dyck words and return ``True`` if all of the heights
            of ``dw1`` are less than or equal to the heights of ``dw2`` .

            .. SEEALSO:: :meth:`heights<sage.combinat.dyck_word.DyckWord_class.heights>`

            EXAMPLES::

                sage: poset = DyckWords().height_poset()
                sage: poset.le(DyckWord([]), DyckWord([]))
                True
                sage: poset.le(DyckWord([1,0]), DyckWord([1,0]))
                True
                sage: poset.le(DyckWord([1,0,1,0]), DyckWord([1,1,0,0]))
                True
                sage: poset.le(DyckWord([1,1,0,0]), DyckWord([1,0,1,0]))
                False
                sage: [poset.le(dw1, dw2)
                ...       for dw1 in DyckWords(3) for dw2 in DyckWords(3)]
                [True, True, True, True, True, False, True, False, True, True, False, False, True, True, True, False, False, False, True, True, False, False, False, False, True]
            """
            assert len(dw1)==len(dw2), "Length mismatch: %s and %s"%(dw1, dw2)
            sh = dw1.heights()
            oh = dw2.heights()
            return all(sh[i] <= oh[i] for i in range(len(dw1)))

class DyckWordBacktracker(GenericBacktracker):
    r"""
    DyckWordBacktracker: this class is an iterator for all Dyck words
    with n opening parentheses and n - endht closing parentheses using
    the backtracker class. It is used by the DyckWords_size class.

    This is not really meant to be called directly, partially because
    it fails in a couple corner cases: DWB(0) yields [0], not the
    empty word, and DWB(k, k+1) yields something (it shouldn't yield
    anything). This could be fixed with a sanity check in _rec(), but
    then we'd be doing the sanity check *every time* we generate new
    objects; instead, we do *one* sanity check in DyckWords and assume
    here that the sanity check has already been made.

    AUTHOR:

    - Dan Drake (2008-05-30)
    """
    def __init__(self, k1, k2):
        r"""
        TESTS::

            sage: from sage.combinat.dyck_word import DyckWordBacktracker
            sage: len(list(DyckWordBacktracker(5, 5)))
            42
            sage: len(list(DyckWordBacktracker(6,4)))
            90
            sage: len(list(DyckWordBacktracker(7,0)))
            1
        """
        GenericBacktracker.__init__(self, [], (0, 0))
        # note that the comments in this class think of our objects as
        # Dyck paths, not words; having k1 opening parens and k2 closing
        # parens corresponds to paths of length k1 + k2 ending at height
        # k1 - k2.
        self.n = k1 + k2
        self.endht = k1 - k2

    def _rec(self, path, state):
        r"""
        TESTS::

            sage: from sage.combinat.dyck_word import DyckWordBacktracker
            sage: dwb = DyckWordBacktracker(3, 3)
            sage: list(dwb._rec([1,1,0],(3, 2)))
            [([1, 1, 0, 0], (4, 1), False), ([1, 1, 0, 1], (4, 3), False)]
            sage: list(dwb._rec([1,1,0,0],(4, 0)))
            [([1, 1, 0, 0, 1], (5, 1), False)]
            sage: list(DyckWordBacktracker(4, 4)._rec([1,1,1,1],(4, 4)))
            [([1, 1, 1, 1, 0], (5, 3), False)]
        """
        len, ht = state

        if len < self.n - 1:
            # if length is less than n-1, new path won't have length n, so
            # don't yield it, and keep building paths

            # if the path isn't too low and is not touching the x-axis, we can
            # yield a path with a downstep at the end
            if ht > (self.endht - (self.n - len)) and ht > 0:
                yield path + [0], (len + 1, ht - 1), False

            # if the path isn't too high, it can also take an upstep
            if ht < (self.endht + (self.n - len)):
                yield path + [1], (len + 1, ht + 1), False
        else:
            # length is n - 1, so add a single step (up or down,
            # according to current height and endht), don't try to
            # construct more paths, and yield the path
            if ht < self.endht:
                yield path + [1], None, True
            else:
                yield path + [0], None, True

class DyckWords_size(CombinatorialClass):
    def __init__(self, k1, k2=None):
        r"""
        TESTS::

            sage: DW4 = DyckWords(4)
            sage: DW4 == loads(dumps(DW4))
            True
            sage: DW42 = DyckWords(4,2)
            sage: DW42 == loads(dumps(DW42))
            True
        """
        self.k1 = k1
        self.k2 = k2

    def __repr__(self):
        r"""
        TESTS::

            sage: repr(DyckWords(4))
            'Dyck words with 4 opening parentheses and 4 closing parentheses'
        """
        return "Dyck words with %s opening parentheses and %s closing parentheses"%(self.k1, self.k2)

    def cardinality(self):
        r"""
        Returns the number of complete Dyck words of semilength `n`, i.e. the `n`-th :func:`Catalan number<sage.combinat.combinat.catalan_number>`.

        EXAMPLES::

            sage: DyckWords(4).cardinality()
            14
            sage: ns = range(9)
            sage: dws = [DyckWords(n) for n in ns]
            sage: all([ dw.cardinality() == len(dw.list()) for dw in dws])
            True
        """
        if self.k2 == self.k1:
            return catalan_number(self.k1)
        else:
            return len(self.list())

    def __contains__(self, x):
        r"""
        EXAMPLES::

            sage: [1, 0] in DyckWords(1)
            True
            sage: [1, 0] in DyckWords(2)
            False
            sage: [1, 1, 0, 0] in DyckWords(2)
            True
            sage: [1, 0, 0, 1] in DyckWords(2)
            False
            sage: [1, 0, 0, 1] in DyckWords(2,2)
            False
            sage: [1, 0, 1, 0] in DyckWords(2,2)
            True
            sage: [1, 0, 1, 0, 1] in DyckWords(3,2)
            True
            sage: [1, 0, 1, 1, 0] in DyckWords(3,2)
            True
            sage: [1, 0, 1, 1] in DyckWords(3,1)
            True
        """
        return is_a(x, self.k1, self.k2)

    def list(self):
        r"""
        Returns a list of all the Dyck words with ``k1`` opening and ``k2``
        closing parentheses.

        EXAMPLES::

            sage: DyckWords(0).list()
            [[]]
            sage: DyckWords(1).list()
            [[1, 0]]
            sage: DyckWords(2).list()
            [[1, 0, 1, 0], [1, 1, 0, 0]]
        """
        return list(self)

    def __iter__(self):
        r"""
        Returns an iterator for Dyck words with ``k1`` opening and ``k2``
        closing parentheses.

        EXAMPLES::

            sage: [ w for w in DyckWords(0) ]
            [[]]
            sage: [ w for w in DyckWords(1) ]
            [[1, 0]]
            sage: [ w for w in DyckWords(2) ]
            [[1, 0, 1, 0], [1, 1, 0, 0]]
            sage: len([ 'x' for _ in DyckWords(5) ])
            42
        """
        if self.k1 == 0:
            yield DyckWord_complete([])
        elif self.k2 == 0:
            yield DyckWord_class([ open_symbol for _ in range(self.k1) ])
        else:
            if self.k2 is None or self.k2 == self.k1:
                is_complete = True
            else:
                is_complete = False
            for w in DyckWordBacktracker(self.k1, self.k2):
                if not is_complete:
                    yield DyckWord_class(w)
                else:
                    yield DyckWord_complete(w)

    def _an_element_(self):
        r"""
        TESTS::

            sage: DyckWords(0).an_element()    # indirect doctest
            []
            sage: DyckWords(1).an_element()    # indirect doctest
            [1, 0]
            sage: DyckWords(2).an_element()    # indirect doctest
            [1, 0, 1, 0]
        """
        return iter(self).next()

def is_a_prefix(obj, k1 = None, k2 = None):
    r"""
    If ``k1`` is specified, then the object must have exactly ``k1`` open
    symbols. If ``k2`` is also specified, then obj must have exactly ``k2``
    close symbols.

    EXAMPLES::

        sage: from sage.combinat.dyck_word import is_a_prefix
        sage: is_a_prefix([1,1,0])
        True
        sage: is_a_prefix([0,1,0])
        False
        sage: is_a_prefix([1,1,0],2,1)
        True
        sage: is_a_prefix([1,1,0],1,1)
        False
    """
    if k1 is not None and k2 is None:
        k2 = k1
    if k1 is not None and k1 < k2:
        raise ValueError, "k1 (= %s) must be >= k2 (= %s)"%(k1, k2)

    n_opens = 0
    n_closes = 0

    for p in obj:
        if p == open_symbol:
            n_opens += 1
        elif p == close_symbol:
            n_closes += 1
        else:
            return False

        if n_opens < n_closes:
            return False

    if k1 is None and k2 is None:
        return True
    elif k2 is None:
        return n_opens == k1
    else:
        return n_opens == k1 and n_closes == k2

def is_area_sequence(seq):
    r"""
    Tests if a sequence `l` of integers satisfies `l_0 = 0` and
    `0 \leq l_{i+1} \leq l_i + 1` for `i > 0`.

    EXAMPLES::

        sage: from sage.combinat.dyck_word import is_area_sequence
        sage: is_area_sequence([0,2,0])
        False
        sage: is_area_sequence([1,2,3])
        False
        sage: is_area_sequence([0,1,0])
        True
        sage: is_area_sequence([0,1,2])
        True
        sage: is_area_sequence([])
        True
    """
    if seq==[]:
        return True
    return seq[0] == 0 and all( 0 <= seq[i+1] and seq[i+1] <= seq[i]+1 for i in xrange(len(seq)-1) )

def is_a(obj, k1 = None, k2 = None):
    r"""
    If ``k1`` is specified, then the object must have exactly ``k1`` open
    symbols. If ``k2`` is also specified, then ``obj`` must have exactly ``k2``
    close symbols.

    EXAMPLES::

        sage: from sage.combinat.dyck_word import is_a
        sage: is_a([1,1,0,0])
        True
        sage: is_a([1,0,1,0])
        True
        sage: is_a([1,1,0,0],2)
        True
        sage: is_a([1,1,0,0],3)
        False
    """
    if k1 is not None and k2 is None:
        k2 = k1
    if k1 is not None and k1 < k2:
        raise ValueError, "k1 (= %s) must be >= k2 (= %s)"%(k1, k2)

    n_opens = 0
    n_closes = 0

    for p in obj:
        if p == open_symbol:
            n_opens += 1
        elif p == close_symbol:
            n_closes += 1
        else:
            return False

        if n_opens < n_closes:
            return False

    if k1 is None and k2 is None:
        return n_opens == n_closes
    elif k2 is None:
        return n_opens == n_closes and n_opens == k1
    else:
        return n_opens == k1 and n_closes == k2

def from_noncrossing_partition(ncp):
    r"""
    Converts a noncrossing partition to a Dyck word.

    TESTS::

        sage: DyckWord(noncrossing_partition=[[1,2]]) # indirect doctest
        [1, 1, 0, 0]
        sage: DyckWord(noncrossing_partition=[[1],[2]])
        [1, 0, 1, 0]

    ::

        sage: dws = DyckWords(5).list()
        sage: ncps = map( lambda x: x.to_noncrossing_partition(), dws)
        sage: dws2 = map( lambda x: DyckWord(noncrossing_partition=x), ncps)
        sage: dws == dws2
        True
    """
    l = [ 0 ] * int( sum( [ len(v) for v in ncp ] ) )
    for v in ncp:
        l[v[-1]-1] = len(v)

    res = []
    for i in l:
        res += [ open_symbol ] + [close_symbol]*int(i)
    return DyckWord(res)

def from_ordered_tree(tree):
    r"""
    TESTS::

        sage: sage.combinat.dyck_word.from_ordered_tree(1)
        Traceback (most recent call last):
        ...
        NotImplementedError: TODO
    """
    raise NotImplementedError, "TODO"

def pealing(D,return_touches=False):
    r"""
    A helper function for computing the bijection from a Dyck word to a 231-avoiding
    permutations using the bijection "Stump".  For details see [Stu2008]_.

    .. SEEALSO:: :meth:`~sage.combinat.dyck_word.DyckWord_complete.to_noncrossing_partition`

    EXAMPLES::

        sage: from sage.combinat.dyck_word import pealing
        sage: pealing(DyckWord([1,1,0,0]))
        [1, 0, 1, 0]
        sage: pealing(DyckWord([1,0,1,0]))
        [1, 0, 1, 0]
        sage: pealing(DyckWord([1, 1, 0, 0, 1, 1, 1, 0, 0, 0]))
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        sage: pealing(DyckWord([1,1,0,0]),return_touches=True)
        ([1, 0, 1, 0], [[1, 2]])
        sage: pealing(DyckWord([1,0,1,0]),return_touches=True)
        ([1, 0, 1, 0], [])
        sage: pealing(DyckWord([1, 1, 0, 0, 1, 1, 1, 0, 0, 0]),return_touches=True)
        ([1, 0, 1, 0, 1, 0, 1, 0, 1, 0], [[1, 2], [3, 5]])
    """
    n = D.semilength()
    area = D.to_area_sequence()
    new_area = []
    touch_sequences = []
    touches = []
    for i in range(n-1):
        if area[i+1] == 0:
            touches.append(i+1)
            if len(touches) > 1:
                touch_sequences.append(touches)
                touches = []
            elif area[i] == 0:
                touches = []
            new_area.append(0)
        elif area[i+1] == 1:
            new_area.append(0)
            touches.append(i+1)
        else:
            new_area.append(area[i+1]-2)
    new_area.append(0)
    if area[n-1] != 0:
        touches.append(n)
        if len(touches) > 1:
            touch_sequences.append(touches)
    D = DyckWord_complete.from_area_sequence( new_area )
    if return_touches:
        return (D,touch_sequences)
    else:
        return D