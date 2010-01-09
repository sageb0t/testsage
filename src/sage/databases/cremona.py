"""
Cremona's tables of elliptic curves.

Sage includes John Cremona's tables of elliptic curves in an
easy-to-use format. The unique instance of the class
CremonaDatabase() gives access to the database.

If the optional full CremonaDatabase is not installed, a mini-version
is included by default with Sage.  It contains Weierstrass equations,
rank, and torsion for curves up to conductor 10000.

The large database includes all curves of conductor up to 130,000. It
also includes data related to the BSD conjecture and modular degrees
for all of these curves, and generators for the Mordell-Weil
groups. To install it type the following in Sage:

!sage -i database_cremona_ellcurve

This causes the latest version of the database to be downloaded from
the internet.  You can also install it from a local copy of the
database spkg file, using a command of the form

!sage -i database_cremona_ellcurve-20071019.spkg

"""

#*****************************************************************************
#
#       Sage: Copyright (C) 2005 William Stein <wstein@gmail.com>
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

import gzip, os
import sage.misc.prandom as random

import sage.schemes.elliptic_curves.constructor as elliptic
import sage.databases.db   # very important that this be fully qualified
from sage.misc.package import optional_packages
from sage.misc.all import xsrange
import sage.misc.misc

import re
import string

_map = {'allcurves':'a', 'degphi':'b', 'allbsd':'c', 'allgens':'d'}

def rebuild(data_tgz, largest_conductor, decompress=True):
    """
    Rebuild the LargeCremonaDatabase from scratch using the data_tgz
    tarball.
    """
    if os.path.exists("%s/cremona"%sage.databases.db.DB_HOME):
        raise RuntimeError, "Please (re)move %s/cremona before rebuilding database."%sage.databases.db.DB_HOME
    if not os.path.exists(data_tgz):
        raise IOError, "The data file is not at %s"%data_tgz
    t = sage.misc.misc.cputime()

    if decompress:
        cmd = "tar zxvf %s"%data_tgz
        n = os.system(cmd)
        if n:
            raise RuntimeError, "Error extracting tarball."

    c = LargeCremonaDatabase(False)
    c._init_from_ftpdata('ecdata', largest_conductor)
    print "Total time: ", sage.misc.misc.cputime(t)

def is_optimal_id(id):
    """
    Returns true if the Cremona id refers to an optimal curve, and
    false otherwise. The curve is optimal if the id, which is of the
    form [letter code][number] has number 1.

    .. note::

       990h3 is the optimal curve in that class, so doesn't obey
       this rule.

    INPUT:

    -  ``id`` - str of form letter code followed by an
       integer, e.g., a3, bb5, etc.

    OUTPUT: bool

    EXAMPLES::

        sage: from sage.databases.cremona import is_optimal_id
        sage: is_optimal_id('b1')
        True
        sage: is_optimal_id('bb1')
        True
        sage: is_optimal_id('c1')
        True
        sage: is_optimal_id('c2')
        False
    """
    return id[-1] == '1' and not id[-2].isdigit()

def cremona_letter_code(n):
    """
    Returns the Cremona letter code corresponding to an integer. For
    example, 0 - a 25 - z 26 - ba 51 - bz 52 - ca 53 - cb etc.

    .. note::

       This is just the base 26 representation of n, where a=0, b=1,
       ..., z=25. This extends the old Cremona notation (counting from
       0) for the first 26 classes, and is different for classes above
       26.

    INPUT:

    -  ``n`` (int) -- a non-negative integer

    OUTPUT: str

    EXAMPLES::

        sage: from sage.databases.cremona import cremona_letter_code
        sage: cremona_letter_code(0)
        'a'
        sage: cremona_letter_code(26)
        'ba'
        sage: cremona_letter_code(27)
        'bb'
        sage: cremona_letter_code(521)
        'ub'
        sage: cremona_letter_code(53)
        'cb'
        sage: cremona_letter_code(2005)
        'czd'

    TESTS::

        sage: cremona_letter_code(QQ)
        Traceback (most recent call last):
        ...
        ValueError: Cremona letter codes are only defined for non-negative integers
        sage: cremona_letter_code(x)
        Traceback (most recent call last):
        ...
        ValueError: Cremona letter codes are only defined for non-negative integers
        sage: cremona_letter_code(-1)
        Traceback (most recent call last):
        ...
        ValueError: Cremona letter codes are only defined for non-negative integers
        sage: cremona_letter_code(3.14159)
        Traceback (most recent call last):
        ...
        ValueError: Cremona letter codes are only defined for non-negative integers
    """
    try:
        m = int(n)
        if n == m:
            n = m
        else:
            n = -1
    except (ValueError, TypeError):
        n = -1

    if n<0:
        raise ValueError, "Cremona letter codes are only defined for non-negative integers"

    if n == 0:
        return "a"
    s = ""
    while n != 0:
        s = chr(n%26+97) + s
        n //= 26
    return s

def old_cremona_letter_code(n):
    r"""
    Returns the *old* Cremona letter code corresponding to an integer.
    integer.

    For example::

        1  --> A

        26 --> Z

        27 --> AA

        52 --> ZZ

        53 --> AAA

        etc.

    INPUT:

    -  ``n`` - int

    OUTPUT: str

    EXAMPLES::

        sage: from sage.databases.cremona import old_cremona_letter_code
        sage: old_cremona_letter_code(1)
        'A'
        sage: old_cremona_letter_code(26)
        'Z'
        sage: old_cremona_letter_code(27)
        'AA'
        sage: old_cremona_letter_code(521)
        'AAAAAAAAAAAAAAAAAAAAA'
        sage: old_cremona_letter_code(53)
        'AAA'
        sage: old_cremona_letter_code(2005)
        'CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC'
    """
    n -= 1
    k = n%26 + 65
    label = chr(k)*int(n//26 + 1)
    return label

## int codeletter_to_int(char* code)  // i counts from 0!
## {
##   int b = code[0]-'a';
##   if(code[1]=='\0')  return b;
##   int a = code[1]-'a';
##   return 26*(b+1)+a;
## }

## const char alphabet[] = "abcdefghijklmnopqrstuvwxyz";

## void new_codeletter(int i, char* code)  // i counts from 0!
## {
##   int b = i%26;
##   int a = (i-b)/26;
##   if (a==0) {code[0]=alphabet[b]; code[1]='\0';}
##   else {code[0]=alphabet[a-1]; code[1]=alphabet[b]; code[2]='\0';}
##   /*
##   int j = codeletter_to_int(code);
##   if(i==j) return;
##   cout<<i<<" -> "<<code<<" -> "<<j<<endl;
##   */
## }

def parse_cremona_label(label):
    """
    Given a Cremona label that defines an elliptic
    curve, e.g., 11A1 or 37B3, parse the label and return the
    conductor, isogeny class label, and number.

    The isogeny number may be omitted, in which case it defaults to 1.
    If the isogeny number and letter are both omitted, so label is just
    a string representing a conductor, then the label defaults to 'A'
    and the number to 1.

    INPUT:

    -  ``label`` - str

    OUTPUT:

    -  ``int`` - the conductor

    -  ``str`` - the isogeny class label

    -  ``int`` - the number

    EXAMPLES::

        sage: from sage.databases.cremona import parse_cremona_label
        sage: parse_cremona_label('37a2')
        (37, 'a', 2)
        sage: parse_cremona_label('37b1')
        (37, 'b', 1)
        sage: parse_cremona_label('10bb2')
        (10, 'bb', 2)
    """
    if not isinstance(label, str):
        label = str(label)
    i=0
    while i<len(label) and label[i]>='0' and label[i]<='9':
        i += 1
    j=i+1
    if j>len(label):
        label += "a"
    while j<len(label) and not (label[j]>='0' and label[j]<='9'):
        j += 1
    if j>=len(label):
        label += "1"
    conductor, iso, num = int(label[:i]), label[i:j], int(label[j:])
    #iso = iso.lower()
    return conductor, iso, num

def split_code(key):
    """
    Splits class+curve id string into its two parts.

    EXAMPLES::

        sage: import sage.databases.cremona as cremona
        sage: cremona.split_code('ba2')
        ('ba', '2')
    """
    cu = re.split("[a-z]*",key)[1]
    cl =  re.split("[0-9]*",key)[0]
    return (cl,cu)

def class_to_int(k):
    """
    Converts class id string into an integer. Note that this is the
    inverse of cremona_letter_code.

    EXAMPLES::

        sage: import sage.databases.cremona as cremona
        sage: cremona.class_to_int('ba')
        26
        sage: cremona.class_to_int('cremona')
        821863562
        sage: cremona.cremona_letter_code(821863562)
        'cremona'
    """
    kk = [string.ascii_lowercase.index(ch) for ch in list(k)]
    kk.reverse()
    return sum([kk[i]*26**i for i in range(len(kk))])

def cmp_code(key1,key2):
    """
    Comparison function for curve id strings.

    .. note::

       Not the same as standard lexicographic order!

    EXAMPLES::

        sage: import sage.databases.cremona as cremona
        sage: cremona.cmp_code('ba1','z1')
        1

    By contrast::

        sage: cmp('ba1','z1')
        -1
    """
    cl1,cu1 = split_code(key1)
    cl2,cu2 = split_code(key2)
    d = class_to_int(cl1)-class_to_int(cl2)
    if d!=0:  return d
    return cmp(cu1,cu2)

class LargeCremonaDatabase(sage.databases.db.Database):
    """
    The Cremona database of elliptic curves.

    EXAMPLES::

        sage: c = CremonaDatabase()
        sage: c.allcurves(11)
        {'a1': [[0, -1, 1, -10, -20], 0, 5], 'a3': [[0, -1, 1, 0, 0], 0, 5], 'a2': [[0, -1, 1, -7820, -263580], 0, 1]}
    """
    def __init__(self, read_only=True):
        """
        Initialize the database.

        INPUT:

        -  ``read_only`` - bool (default: True), if True, then
           the database is read_only and changes cannot be committed to
           disk.

        TESTS::

            sage: from sage.databases.cremona import LargeCremonaDatabase  # optional - database_cremona_ellcurves
            sage: c = LargeCremonaDatabase()                               # optional - database_cremona_ellcurves
            sage: c.read_only                                              # optional - database_cremona_ellcurves
            True
            sage: c.name                                                   # optional - database_cremona_ellcurves
            'cremona'
        """
        sage.databases.db.Database.__init__(self,
             name="cremona", read_only=read_only)

    def __iter__(self):
        """
        Returns an iterator through all EllipticCurve objects in the
        Cremona database.

        TESTS::

            sage: it = CremonaDatabase().__iter__()
            sage: it.next().label()
            '11a1'
            sage: it.next().label()
            '11a2'
            sage: it.next().label()
            '11a3'
            sage: it.next().label()
            '14a1'
            sage: skip = [it.next() for _ in range(100)]
            sage: it.next().label()
            '45a3'
        """
        return self.iter(xsrange(11,self.largest_conductor()+1))

    def __getitem__(self, N):
        """
        If N is an integer, return all data about level N in the database.
        If N is a string it must be a Cremona label, in which case return
        the corresponding elliptic curve, if it is in the database.

        INPUT:

        -  ``N`` - int or str

        OUTPUT: dict (if N is an int) or EllipticCurve (if N is a str)

        TESTS::

            sage: c = CremonaDatabase()
            sage: c[11]['a']['a2']
            [[0, -1, 1, -7820, -263580], 0, 1]
            sage: c['11a2']
            Elliptic Curve defined by y^2 + y = x^3 - x^2 - 7820*x - 263580 over Rational Field
        """
        if isinstance(N, str) and len(N) > 0:
            if N[0].isalpha():
                return sage.databases.db.Database.__getitem__(self, N)
            else:
                return self.elliptic_curve(N)
        try:
            N = int(N)
        except ValueError:
            raise KeyError, "N (=%s) must be a positive integer."

        if N <= 0:
            raise KeyError, "N (=%s) must be a positive integer."

        try:
            return sage.databases.db.Database.__getitem__(self, N)
        except KeyError:
            self[N] = {}
            return self[N]

    def __repr__(self):
        """
        String representation of this database.

        TESTS::

            sage: from sage.databases.cremona import LargeCremonaDatabase  # optional - database_cremona_ellcurves
            sage: c = LargeCremonaDatabase()                               # optional - database_cremona_ellcurves
            sage: c.__repr__()                                             # optional - database_cremona_ellcurves
            "Cremona's database of elliptic curves"
        """
        return "Cremona's database of elliptic curves"

    def allbsd(self, N):
        r"""
        Return the allbsd table for conductor N. The entries are::

            [id, tamagawa_product, Omega_E, L, Reg_E, Sha_an(E)],

        where id is the isogeny class (letter) followed by a number, e.g.,
        b3, and L is `L^r(E,1)/r!`, where E has rank r.

        INPUT:

        -  ``N`` - int, the conductor

        OUTPUT: dict containing the allbsd table for each isogeny class
        in conductor N

        EXAMPLES::

            sage: c = CremonaDatabase()
            sage: c.allbsd(12)
            {}
            sage: c.allbsd(19)['a3']      # optional - database_cremona_ellcurve
            ['1', '4.0792792004649324322', '0.45325324449610360358', '1', '1']
            sage: c.allbsd(12001)['a1']   # optional - database_cremona_ellcurve
            ['2', '3.2760813524872187381', '1.5491014309050596354', '0.23642597118795194508', '1']
        """
        try:
            return self[int(N)][_map['allbsd']]
        except KeyError:
            return {}

    def allcurves(self, N):
        """
        Returns the allcurves table of curves of conductor N.

        INPUT:

        -  ``N`` - int, the conductor

        OUTPUT:

        -  ``dict`` - id:[ainvs, rank, tor], ...

        EXAMPLES::

            sage: c = CremonaDatabase()
            sage: c.allcurves(11)['a3']
            [[0, -1, 1, 0, 0], 0, 5]
            sage: c.allcurves(12)
            {}
            sage: c.allcurves(12001)['a1']   # optional - database_cremona_ellcurve
            [[1, 0, 0, -101, 382], 1, 1]
        """
        try:
            return self[int(N)][_map['allcurves']]
        except KeyError:
            return {}

    def allgens(self, N):
        """
        Return the allgens table for conductor N.

        INPUT:

        -  ``N`` - int, the conductor

        OUTPUT:

        -  ``dict`` - id:[points, ...], ...

        EXAMPLES::

            sage: c = CremonaDatabase()
            sage: c.allgens(12)
            {}
            sage: c.allgens(1001)['a1']    # optional - database_cremona_ellcurve
            [[61, 181, 1]]
            sage: c.allgens(12001)['a1']   # optional - database_cremona_ellcurve
            [[7, 2, 1]]
        """
        try:
            return self[int(N)][_map['allgens']]
        except KeyError:
            return {}

    def curves(self, N):
        """
        Returns the curves table of all *optimal* curves of conductor N.

        INPUT:

        -  ``N`` - int, the conductor

        OUTPUT:

        -  ``dict`` - id:[ainvs, rank, tor], ...

        EXAMPLES:

        Optimal curves of conductor 37::

            sage: CremonaDatabase().curves(37)
            {'a1': [[0, 0, 1, -1, 0], 1, 1], 'b1': [[0, 1, 1, -23, -50], 0, 3]}

        Note the 'h3', which is the unique case in the tables where
        the optimal curve doesn't have label ending in 1::

            sage: list(sorted(CremonaDatabase().curves(990).keys()))
            ['a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h3', 'i1', 'j1', 'k1', 'l1']

        TESTS::

            sage: c = CremonaDatabase()
            sage: c.curves(12001)['a1']   # optional - database_cremona_ellcurve
            [[1, 0, 0, -101, 382], 1, 1]
        """
        A = self.allcurves(N)
        if N != 990:
            return dict([(id,val) for id,val in A.iteritems() if is_optimal_id(id)])
        return dict([(id,val) for id,val in A.iteritems() if id == 'h3' or (id[0]!='h' and is_optimal_id(id))])

    def degphi(self, N):
        """
        Return the degphi table for conductor N.

        INPUT:

        -  ``N`` - int, the conductor

        OUTPUT:

        -  ``dict`` - id:degphi, ...

        EXAMPLES::

            sage: c = CremonaDatabase()
            sage: c.degphi(11)      # optional - database_cremona_ellcurve
            {'a1': 1}
            sage: c.degphi(12001)['c1']   # optional - database_cremona_ellcurve
            1640
        """
        try:
            return self[int(N)][_map['degphi']]
        except KeyError:
            return {}

    def elliptic_curve_from_ainvs(self, N, ainvs):
        """
        Returns the elliptic curve in the database of conductor N with
        minimal ainvs, if it exists, or raises a RuntimeError exception
        otherwise.

        INPUT:

        -  ``N`` - int

        -  ``ainvs`` - list (5-tuple of int's); the minimal
           Weierstrass model for an elliptic curve of conductor N

        OUTPUT: EllipticCurve

        EXAMPLES::

            sage: c = CremonaDatabase()
            sage: c.elliptic_curve_from_ainvs(11, [0, -1, 1, -10, -20])
            Elliptic Curve defined by y^2 + y = x^3 - x^2 - 10*x - 20 over Rational Field
            sage: c.elliptic_curve_from_ainvs(12001, [1, 0, 0, -101, 382])  # optional - database_cremona_ellcurve
            Elliptic Curve defined by y^2 + x*y = x^3 - 101*x + 382 over Rational Field
        """
        for id, e in self.allcurves(N).iteritems():
            if e[0] == ainvs:
                return self.elliptic_curve(str(N)+id)
        raise RuntimeError, "No elliptic curve of conductor N (=%s) and ainvs (=%s) in the database."%(N,ainvs)

    def elliptic_curve(self, label):
        """
        Return an elliptic curve with given label with some data about it
        from the database pre-filled in.

        INPUT:

        -  ``label`` - str (Cremona label)

        OUTPUT: EllipticCurve

        EXAMPLES::

            sage: c = CremonaDatabase()
            sage: c.elliptic_curve('11a1')
            Elliptic Curve defined by y^2 + y = x^3 - x^2 - 10*x - 20 over Rational Field
            sage: c.elliptic_curve('12001a1')    # optional - database_cremona_ellcurve
            Elliptic Curve defined by y^2 + x*y = x^3 - 101*x + 382 over Rational Field
        """
        N, iso, num = parse_cremona_label(label)
        v = self[N]
        id = iso + str(num)
        try:
            e = v[_map['allcurves']][id]
        except KeyError:
            if N<10000:
                message =  "There is no elliptic curve with label "+label+" in the database (note: use lower case letters!)"
            elif N<130000:
                if 'database_cremona_ellcurve-20071019' in optional_packages()[0]:
                    message =  "There is no elliptic curve with label "+label+" in the database (note: use lower case letters!)"
                else:
                    message = "There is no elliptic curve with label "+label+" in the default database; try installing the optional package database_cremona_ellcurve-20071019 which contains all curves of conductor up to 130000"
            else:
                message = "There is no elliptic curve with label "+label+" in the currently available databases"
            raise RuntimeError, message

        F = elliptic.EllipticCurve(e[0])
        F._set_cremona_label("%s %s %s"%(N, iso, num))
        F._set_rank(e[1])
        F._set_torsion_order(e[2])
        F._set_conductor(N)

        try:
            F._set_modular_degree(v[_map['degphi']][id])
        except KeyError:
            pass

        try:
            F._set_gens(v[_map['allgens']][id])
        except KeyError:
            if e[1] == 0:
                F._set_gens([])

        try:
            F.db_extra = v[_map['allbsd']][id]
        except KeyError, msg:
            pass
        return F

    def iter(self, conductors):
        """
        Return an iterator through all curves in the database with given conductors.

        INPUT:

        -  ``conductors`` - list or generator of ints

        OUTPUT: generator that iterates over EllipticCurve objects.

        EXAMPLES::

            sage: [e.cremona_label() for e in CremonaDatabase().iter([11..15])]
            ['11a1', '11a2', '11a3', '14a1', '14a2', '14a3', '14a4', '14a5',
             '14a6', '15a1', '15a2', '15a3', '15a4', '15a5', '15a6', '15a7', '15a8']
        """
        for N in conductors:
            K = self.allcurves(N).keys()
            K.sort(cmp_code)
            for e in K:
                yield self.elliptic_curve(str(N) + e)

    def isogeny_classes(self, conductor):
        """
        Return the allcurves data (ainvariants, rank and torsion) for the
        elliptic curves in the database of given conductor as a list of
        lists, one for each isogeny class. The curve with number 1 is
        always listed first.

        EXAMPLES::

            sage: c = CremonaDatabase()
            sage: c.isogeny_classes(11)
            [[[[0, -1, 1, -10, -20], 0, 5],
             [[0, -1, 1, -7820, -263580], 0, 1],
             [[0, -1, 1, 0, 0], 0, 5]]]
            sage: c.isogeny_classes(12001)   # optional - database_cremona_ellcurve
            [[[[1, 0, 0, -101, 382], 1, 1]],
             [[[0, 0, 1, -247, 1494], 1, 1]],
             [[[0, 0, 1, -4, -18], 1, 1]],
             [[[0, 1, 1, -10, 18], 1, 1]]]
        """
        conductor=int(conductor)
        classes = []
        A = self.allcurves(conductor)
        K = A.keys()
        K.sort(cmp_code)
        for k in K:
            v = A[k]
            # test if not first curve in class
            if not (k[-1] == '1' and k[-2].isalpha()):
                classes[len(classes)-1].append(v)
            else:
                classes.append([v])
        return classes

    def isogeny_class(self, label):
        """
        Returns the isogeny class of elliptic curves that are
        isogenous to the curve with given Cremona label.

        INPUT:

        -  ``label`` - string

        OUTPUT:

        -  ``list`` - list of EllipticCurve objects.

        EXAMPLES::

            sage: c = CremonaDatabase()
            sage: c.isogeny_class('11a1')
            [Elliptic Curve defined by y^2 + y = x^3 - x^2 - 10*x - 20 over Rational Field,
             Elliptic Curve defined by y^2 + y = x^3 - x^2 over Rational Field,
             Elliptic Curve defined by y^2 + y = x^3 - x^2 - 7820*x - 263580 over Rational Field]
            sage: c.isogeny_class('12001a1')   # optional - database_cremona_ellcurve
            [Elliptic Curve defined by y^2 + x*y = x^3 - 101*x + 382 over Rational Field]
        """
        conductor, iso, num = parse_cremona_label(label)
        A = self.allcurves(conductor)
        K = [k for k in A.keys() if k[:len(iso)] == iso and k[len(iso)].isdigit()]
        return [self.elliptic_curve(str(conductor) + id) for id in K]

    def iter_optimal(self, conductors):
        """
        Return an iterator through all optimal curves in the database with given conductors.

        INPUT:

        - ``conductors`` - list or generator of ints

        OUTPUT:

        generator that iterates over EllipticCurve objects.

        EXAMPLES:

        We list optimal curves with conductor up to 20::

            sage: [e.cremona_label() for e in CremonaDatabase().iter_optimal([11..20])]
            ['11a1', '14a1', '15a1', '17a1', '19a1', '20a1']

        Note the unfortunate 990h3 special case::

            sage: [e.cremona_label() for e in CremonaDatabase().iter_optimal([990])]
            ['990a1', '990b1', '990c1', '990d1', '990e1', '990f1', '990g1', '990h3', '990i1', '990j1', '990k1', '990l1']

        """
        for N in conductors:
            K = self.curves(N).keys()
            K.sort(cmp_code)
            for id in K:
                if N == 990 and id == 'h1':   # the unfortunate ugly special case
                    yield self.elliptic_curve('990h3')
                else:
                    yield self.elliptic_curve(str(N) + id)

    def list(self, conductors):
        """
        Returns a list of all curves with given conductors.

        INPUT:

        - ``conductors`` - list or generator of ints

        OUTPUT:

        - list of EllipticCurve objects.

        EXAMPLES::

            sage: CremonaDatabase().list([37])
            [Elliptic Curve defined by y^2 + y = x^3 - x over Rational Field,
             Elliptic Curve defined by y^2 + y = x^3 + x^2 - 23*x - 50 over Rational Field,
             Elliptic Curve defined by y^2 + y = x^3 + x^2 - 1873*x - 31833 over Rational Field,
             Elliptic Curve defined by y^2 + y = x^3 + x^2 - 3*x + 1 over Rational Field]
        """
        return list(self.iter(conductors))

    def list_optimal(self, conductors):
        """
        Returns a list of all optimal curves with given conductors.

        INPUT:

        -  ``conductors`` - list or generator of ints
            list of EllipticCurve objects.

        OUTPUT:

        list of EllipticCurve objects.

        EXAMPLES::

            sage: CremonaDatabase().list_optimal([37])
            [Elliptic Curve defined by y^2 + y = x^3 - x over Rational Field,
             Elliptic Curve defined by y^2 + y = x^3 + x^2 - 23*x - 50 over Rational Field]
        """
        return list(self.iter_optimal(conductors))

    def largest_conductor(self):
        """
        The largest conductor for which the database is complete.

        OUTPUT:

        -  ``int`` - largest conductor

        EXAMPLES::

            sage: from sage.databases.cremona import LargeCremonaDatabase    # optional - database_cremona_ellcurve
            sage: c = LargeCremonaDatabase()                                # optional - database_cremona_ellcurve
            sage: c.largest_conductor()                                     # optional - database_cremona_ellcurve
            130000
        """
        try:
            return sage.databases.db.Database.__getitem__(self, 'largest_conductor')
        except KeyError:
            #print "Computing largest conductor."
            K = [k for k in self.keys() if isinstance(k, (int,long))]
            m = max(K)
            while len(self.allcurves(m).keys()) == 0:
                K.remove(m)
                m = max(K)
            self['largest_conductor'] = m
            try:
                self.commit()  # caching -- but only if possible
            except RuntimeError:
                pass
            return m

    def smallest_conductor(self):
        """
        The smallest conductor for which the database is complete: always 1.

        OUTPUT:

        -  ``int`` - smallest conductor

        .. note::

           This always returns the integer 1, since that is the
           smallest conductor for which the database is complete,
           although there are no elliptic curves of conductor 1.  The
           smallest conductor of a curve in the database is 11.

        EXAMPLES::

            sage: CremonaDatabase().smallest_conductor()
            1
        """
        return 1

    def conductor_range(self):
        """
        Return the range of conductors that are covered by the database.

        OUTPUT: tuple of ints (N1,N2+1) where N1 is the smallest and
        N2 the largest conductor for which the database is complete.

        EXAMPLES::

            sage: from sage.databases.cremona import LargeCremonaDatabase    # optional - database_cremona_ellcurve
            sage: c = LargeCremonaDatabase()                                 # optional - database_cremona_ellcurve
            sage: c.conductor_range()                                        # optional - database_cremona_ellcurve
            (1, 130001)
        """
        return 1, self.largest_conductor()+1

    def number_of_curves(self,  N=0, i=0):
        """
        Returns the number of curves stored in the database with conductor
        N. If N = 0, returns the total number of curves in the database.

        If i is nonzero, returns the number of curves in the i-th isogeny
        class. If i is a Cremona letter code, e.g., 'a' or 'bc', it is
        converted to the corresponding number.

        INPUT:

        -  ``N`` - int

        -  ``i`` - int or str

        OUTPUT: int

        EXAMPLES::

            sage: c = CremonaDatabase()
            sage: c.number_of_curves(11)
            3
            sage: c.number_of_curves(37)
            4
            sage: c.number_of_curves(990)
            42
            sage: num = c.number_of_curves()
        """
        if N == 0:
            try:
                # if the optional database is installed, the number is
                # easy to get
                return self['number_of_curves']
            except KeyError:
                # otherwise we need to do a bit of work
                num = 0
                for N in range(self.smallest_conductor(), self.largest_conductor()+1):
                    L = self.allcurves(N)
                    num = num + len(L)
                return num

        C = self.allcurves(N)
        if i == 0:
            return len(C)
        if not isinstance(i, str):
            i = old_cremona_letter_code(i)
        return len([k for k in C.keys() if k[:len(i)] == i and k[len(i)].isdigit()])

    def number_of_isogeny_classes(self, N=0):
        """
        Returns the number of isogeny classes of curves in the database of
        conductor N. If N is 0, return the total number of isogeny classes
        of curves in the database.

        INPUT:

        -  ``N`` - int

        OUTPUT: int

        EXAMPLES::

            sage: c = CremonaDatabase()
            sage: c.number_of_isogeny_classes(11)
            1
            sage: c.number_of_isogeny_classes(37)
            2
            sage: num = c.number_of_isogeny_classes()
        """
        if N == 0:
            try:
                # if the optional database is installed, the number is
                # easy to get
                return self['number_of_isogeny_classes']
            except KeyError:
                # otherwise we need to do a bit of work
                num = 0
                for N in range(self.smallest_conductor(), self.largest_conductor()+1):
                    L = self.curves(N)
                    num = num + len(L)
                return num

        return len(self.curves(N))

    def random(self):
        """
        Returns a random curve from the database.

        EXAMPLES::

            sage: CremonaDatabase().random() # random -- depends on database installed
            Elliptic Curve defined by y^2 + x*y  = x^3 - x^2 - 224*x + 3072 over Rational Field
        """
        N = random.randint(11, self.largest_conductor())
        A = self.allcurves(N)
        while len(A) == 0:
            N += 1
            if N > self.largest_conductor():
                N = 11
            A = self.allcurves(N)
        id = A.keys()[random.randrange(len(A))]
        return self.elliptic_curve(str(N) + id)

    ###############################################################################
    # Functions for loading data from Cremona's ftpdata directory.
    ###############################################################################
    def _init_from_ftpdata(self, ftpdata,  largest_conductor=0):
        """
        Create the ZODB Cremona Database from the Cremona data directory,
        which is available from Cremona's website. I.e., just wget
        Cremona's database to a local directory.

        .. note::

           For data up to level 130000, this function takes about 30
           minutes on a 1.8Ghz Opteron laptop. The resulting database
           occupies 36MB disk space. Creating the database uses a LOT
           of memory. Use a machine with at *least* 2GB RAM.

        To recreate the large database from the files in the current
        directory, do the following::

            sage: d = sage.databases.cremona.LargeCremonaDatabase(read_only=False)   # not tested
            sage: d._init_from_ftpdata('.')                                 # not tested
        """
        if self.read_only:
            raise RuntimeError, "The database must not be read_only."

        if not os.path.exists(ftpdata):
            raise RuntimeError, "The cremona ftpdata directory '%s' does not exist."%ftpdata

        if self.has_key('largest_conductor'):
            del self['largest_conductor']

        if largest_conductor:
            print "largest conductor = ", largest_conductor
            self['largest_conductor'] =  largest_conductor

        num_curves, num_iso_classes = self._init_allcurves(ftpdata, largest_conductor)
        self['number_of_curves'] = num_curves
        self['number_of_isogeny_classes'] = num_iso_classes
        self._init_degphi(ftpdata, largest_conductor)
        self._init_allbsd(ftpdata, largest_conductor)
        self._init_allgens(ftpdata, largest_conductor)
        self.commit()
        print "Doing a complete rebuild to improve compression."
        self.rebuild()

    def _init_allcurves(self, ftpdata, largest_conductor=0):
        """
        Initialize the allcurves table by reading the corresponding ftpdata
        files and importing them into the database.

        INPUT:

        -  ``largest_conductor`` - int (default: 0), if 0,
           then only include data up to that conductor.

        OUTPUT:

        -  ``int`` - number_of_curves

        -  ``int`` - number_of_isogeny_classes
        """
        if self.read_only:
            raise RuntimeError, "The database must not be read_only."
        files = os.listdir(ftpdata)
        files.sort()
        name = 'allcurves'
        c = _map['allcurves']
        num_curves = 0
        num_iso_classes = 0

        for F in files:
            if not F[:len(name)] == name:
                continue
            print F
            for L in gzip.GzipFile(ftpdata + "/" + F).readlines():
                print L
                N, iso, num, ainvs, r, tor = L.split()
                N = int(N)
                if largest_conductor and N > largest_conductor:
                    self.commit()
                    return num_curves, num_iso_classes
                id = iso + str(num)
                if num == "1":
                    num_iso_classes += 1
                dat = [eval(ainvs),int(r),int(tor)]
                num_curves += 1
                if not self[N].has_key(c):
                    self[N][c] = {}
                self[N][c][id] = dat
            print "Committing..."
            print "num_iso_classes = ", num_iso_classes
            self.commit()
        return num_curves, num_iso_classes

    def _init_degphi(self, ftpdata, largest_conductor=0):
        """
        Initialize the degphi table by reading the corresponding ftpdata
        files and importing them into the database.
        """
        if self.read_only:
            raise RuntimeError, "The database must not be read_only."
        files = os.listdir(ftpdata)
        files.sort()
        name = "degphi"
        c = _map[name]
        for F in files:
            if not F[:len(name)] == name:
                continue
            print F
            for L in gzip.GzipFile(ftpdata + "/" + F).readlines():
                print L
                v = L.split()
                if len(v) == 6:
                    N, iso, num, degree, primes, curve = v
                else:
                    N, iso, degree, primes, curve = v
                    num = '1'
                id = iso + num
                N = int(N)
                if largest_conductor and N > largest_conductor:
                    self.commit()
                    return
                degree = int(degree)
                if not self[N].has_key(c):
                    self[N][c] = {}
                self[N][c][id] = degree
                self[N] = self[N]  # so database knows that self[N] changed.
            self.commit()

    def _init_allbsd(self, ftpdata, largest_conductor=0):
        """
        Initialize the allbsd table by reading the corresponding ftpdata
        files and importing them into the database.
        """
        if self.read_only:
            raise RuntimeError, "The database must not be read_only."
        files = os.listdir(ftpdata)
        files.sort()
        name = "allbsd"
        c = _map[name]
        for F in files:
            if not F[:len(name)] == name:
                continue
            print F
            for L in gzip.GzipFile(ftpdata + "/" + F).readlines():
                print L
                v = L.split()
                N = int(v[0])
                if largest_conductor and N > largest_conductor:
                    self.commit()
                    return
                dat = v[6:]
                id = v[1] + v[2]
                if not self[N].has_key(c):
                    self[N][c] = {}
                self[N][c][id] = dat
                self[N] = self[N]
            self.commit()

    def _init_allgens(self, ftpdata, largest_conductor=0):
        """
        Initialize the allgens table by reading the corresponding ftpdata
        files and importing them into the database.
        """
        if self.read_only:
            raise RuntimeError, "The database must not be read_only."
        files = os.listdir(ftpdata)
        files.sort()
        name = "allgens"
        c = _map[name]
        print "Deleting old data"
        for N in range(1,largest_conductor+1):
            self[N][c] = {}
            self[N] = self[N]  # so database knows that self[N] changed.
        print "Reading new data"
        for F in files:
            if not F[:len(name)] == name:
                continue
            print F
            for L in gzip.GzipFile(ftpdata + "/" + F).readlines():
                print L
                v = L.split()
                N = int(v[0])
                if largest_conductor and N > largest_conductor:
                    self.commit()
                    return
                id = v[1] + v[2]
                dat = [eval(s.replace(':',',')) for s in v[5:]]
                if not self[N].has_key(c):
                    self[N][c] = {}
                self[N][c][id] = dat
                self[N] = self[N]  # so database knows that self[N] changed.

class MiniCremonaDatabase(LargeCremonaDatabase):
    """
    A mini version of the Cremona database that contains only the
    Weierstrass equations, rank and torsion of elliptic curves of
    conductor up to 10000 and nothing else.

    TESTS:

    Many of the following only work if the large Cremona database is
    installed.  Given only the mini version, we expect them to fail
    gracefully::

        sage: from sage.databases.cremona import MiniCremonaDatabase
        sage: c = MiniCremonaDatabase()
        sage: c.allbsd(11)
        {}
        sage: c.allbsd(12001)
        {}
        sage: c.allcurves(12001)
        {}
        sage: c.allgens(11)
        {}
        sage: c.allgens(12001)
        {}
        sage: c.curves(12001)
        {}
        sage: c.degphi(11)
        {}
        sage: c.degphi(12001)
        {}
        sage: c.elliptic_curve('12001a1')
        Traceback (most recent call last):
        ...
        RuntimeError: There is no elliptic curve with label 12001a1 in the default database; try installing the optional package database_cremona_ellcurve-20071019 which contains all curves of conductor up to 130000
        sage: c.elliptic_curve_from_ainvs(12001, [1, 0, 0, -101, 382])
        Traceback (most recent call last):
        ...
        RuntimeError: No elliptic curve of conductor N (=12001) and ainvs (=[1, 0, 0, -101, 382]) in the database.
        sage: c.isogeny_class('12001a1')
        []
        sage: c.isogeny_classes(12001)
        []
        sage: c.number_of_curves(12001)
        0
        sage: c.number_of_isogeny_classes(12001)
        0
    """
    def __init__(self, read_only=True):
        """
        Initialize the database.

        INPUT:

        -  ``read_only`` - bool (default: True), if True, then
           the database is read_only and changes cannot be committed to
           disk.

        TESTS::

            sage: from sage.databases.cremona import MiniCremonaDatabase
            sage: c = MiniCremonaDatabase()
            sage: c.read_only
            True
            sage: c.name
            'cremona_mini'
            sage: c.conductor_range()
            (1, 10000)
            sage: c.largest_conductor()
            9999
            sage: c.number_of_curves(0)
            64687
            sage: c.number_of_isogeny_classes(0)
            38042
        """
        sage.databases.db.Database.__init__(self,
             name="cremona_mini", read_only=read_only)

    def _init(self, ftpdata):
        if self.read_only:
            raise RuntimeError, "The database must not be read_only."
        self._init_allcurves(ftpdata, 10000)

    def __repr__(self):
        """
        Return a string description of this database.

        TESTS::

            sage: from sage.databases.cremona import MiniCremonaDatabase
            sage: c = MiniCremonaDatabase()
            sage: c.__repr__()
            'A mini version of the Cremona database'
        """
        return "A mini version of the Cremona database"

_db = None
def CremonaDatabase():
    """
    Initialize the large Cremona database, if available; otherwise initialize
    the default mini Cremona database.

    TESTS::

        sage: c = CremonaDatabase()
        sage: from sage.databases.cremona import LargeCremonaDatabase
        sage: c is LargeCremonaDatabase()    # optional - database_cremona_ellcurve
        True
    """
    global _db
    if _db != None:
        return _db
    if _db == None:
        try:
            _db = LargeCremonaDatabase()
        except RuntimeError:
            _db = MiniCremonaDatabase()
        return _db