#!/usr/bin/env python

import os, sys
from distutils.core import setup
from distutils.extension import Extension

#########################################################
### Configure SAGE_ROOT
#########################################################

if not os.environ.has_key('SAGE_ROOT'):
    print "    ERROR: The environment variable SAGE_ROOT must be defined."
    sys.exit(1)
else:
    SAGE_ROOT  = os.environ['SAGE_ROOT']
    SAGE_LOCAL = SAGE_ROOT + '/local/'
    SAGE_DEVEL = SAGE_ROOT + '/devel/'

#########################################################
### BLAS setup
#########################################################

## Choose cblas library -- note -- make sure to update sage/misc/cython.py
## if you change this!!
if os.environ.has_key('SAGE_BLAS'):
    BLAS=os.environ['SAGE_BLAS']
    BLAS2=os.environ['SAGE_BLAS']
elif os.path.exists('%s/lib/libatlas.so'%os.environ['SAGE_LOCAL']):
    BLAS='cblas'
    BLAS2='atlas'
elif os.path.exists('/usr/lib/libcblas.dylib') or \
     os.path.exists('/usr/lib/libcblas.so'):
    BLAS='cblas'
    BLAS2='atlas'
elif os.path.exists('/usr/lib/libblas.dll.a'):
    BLAS='gslcblas'
    BLAS2='gslcblas'
else:
    # This is very slow  (?), but *guaranteed* to be available.
    BLAS='gslcblas'
    BLAS2='gslcblas'

#########################################################
### Debian-related stuff
#########################################################

if os.environ.has_key('SAGE_DEBIAN'):
    debian_include_dirs=["/usr/include",
                         "/usr/include/cudd",
                         "/usr/include/eclib",
                         "/usr/include/FLINT",
                         "/usr/include/fplll",
                         "/usr/include/givaro",
                         "/usr/include/gmp++",
                         "/usr/include/gsl",
                         "/usr/include/linbox",
                         "/usr/include/NTL",
                         "/usr/include/numpy",
                         "/usr/include/pari",
                         "/usr/include/polybori",
                         "/usr/include/polybori/groebner",
                         "/usr/include/singular",
                         "/usr/include/singular/singular",
                         "/usr/include/symmetrica",
                         "/usr/include/zn_poly"]
    include_dirs = include_dirs + debian_include_dirs
else:
    debian_include_dirs=[]

#########################################################
### Commonly used include directories
#########################################################

numpy_include_dirs = [SAGE_ROOT+'/local/lib/python/site-packages/numpy/core/include']

#########################################################
### PolyBoRi defines
#########################################################

import ast
polybori_extra_compile_args = []
for line in open(SAGE_LOCAL + "/share/polybori/flags.conf"):
    if not line.startswith("CPPDEFINES"):
        continue
    polybori_extra_compile_args = ["-D"+e for e in ast.literal_eval(line[len("CPPDEFINES = "):])]
    break

#############################################################
### List of modules
###
### Note that the list of modules is sorted alphabetically
### by extension name. Please keep this list sorted when
### adding new modules!
###
#############################################################

def uname_specific(name, value, alternative):
    if name in os.uname()[0]:
        return value
    else:
        return alternative

ext_modules = [

    ################################
    ##
    ## sage.algebras
    ##
    ################################

    Extension('sage.algebras.quatalg.quaternion_algebra_element',
               sources = ['sage/algebras/quatalg/quaternion_algebra_element.pyx'],
               extra_compile_args=["-std=c99"],
               language='c++',
               libraries = ["csage", "flint", "gmp", "gmpxx", "m", "stdc++", "ntl"],
               include_dirs = [SAGE_ROOT+'/local/include/FLINT/'],
               depends = [SAGE_ROOT + "/local/include/FLINT/flint.h"]),

    Extension('sage.algebras.quatalg.quaternion_algebra_cython',
               sources = ['sage/algebras/quatalg/quaternion_algebra_cython.pyx'],
               language='c++',
               libraries = ["csage", "flint", "gmp", "gmpxx", "m", "stdc++", "ntl"]),

    ################################
    ##
    ## sage.calculus
    ##
    ################################

    Extension('sage.calculus.var',
              sources = ['sage/calculus/var.pyx']),

    Extension('sage.calculus.riemann',
              sources = ['sage/calculus/riemann.pyx'],
              include_dirs = numpy_include_dirs),

    Extension('sage.calculus.interpolators',
              sources = ['sage/calculus/interpolators.pyx'],
              include_dirs = numpy_include_dirs),

    ################################
    ##
    ## sage.categories
    ##
    ################################

    Extension('sage.categories.action',
              sources = ['sage/categories/action.pyx']),

    Extension('sage.categories.functor',
              sources = ['sage/categories/functor.pyx']),

    Extension('sage.categories.map',
              sources = ['sage/categories/map.pyx']),

    Extension('sage.categories.morphism',
              sources = ['sage/categories/morphism.pyx']),

    Extension('sage.categories.examples.semigroups_cython',
              sources = ['sage/categories/examples/semigroups_cython.pyx']),

    ################################
    ##
    ## sage.coding
    ##
    ################################

    Extension('sage.coding.binary_code',
              sources = ['sage/coding/binary_code.pyx']),

    ################################
    ##
    ## sage.combinat
    ##
    ################################

    Extension('sage.combinat.expnums',
              sources = ['sage/combinat/expnums.pyx'],
              libraries = ['gmp']),

    Extension('sage.combinat.matrices.dancing_links',
              sources = ['sage/combinat/matrices/dancing_links.pyx'],
              libraries = ["stdc++"],
              language='c++'),

    Extension('sage.combinat.partitions',
              sources = ['sage/combinat/partitions.pyx',
                         'sage/combinat/partitions_c.cc'],
              libraries = ['gmp', 'mpfr'],
              depends = ['sage/combinat/partitions_c.h'],
              language='c++'),

    Extension('sage.combinat.words.word_datatypes',
            sources=['sage/combinat/words/word_datatypes.pyx'],
            include_dirs = ['sage/combinat/words'],
            libraries = ['stdc++'],
            language='c++'),

    Extension('sage.combinat.permutation_cython',
              sources=['sage/combinat/permutation_cython.pyx']),

    ################################
    ##
    ## sage.crypto
    ##
    ################################

    Extension('sage.crypto.boolean_function',
              sources = ['sage/crypto/boolean_function.pyx']),

    ################################
    ##
    ## sage.ext
    ##
    ################################

    Extension('sage.ext.fast_callable',
              sources = ['sage/ext/fast_callable.pyx']),

    Extension('sage.ext.fast_eval',
              sources = ['sage/ext/fast_eval.pyx']),

    Extension('sage.ext.interactive_constructors_c',
              sources = ['sage/ext/interactive_constructors_c.pyx']),

    Extension('sage.ext.multi_modular',
              sources = ['sage/ext/multi_modular.pyx'],
              libraries=['gmp']),

    Extension('sage.ext.sig',
              sources = ['sage/ext/sig.pyx']),

    ################################
    ##
    ## sage.finance
    ##
    ################################

    Extension('sage.finance.fractal',
              sources = ['sage/finance/fractal.pyx']),

    Extension('sage.finance.markov_multifractal_cython',
              sources = ['sage/finance/markov_multifractal_cython.pyx']),

    Extension('sage.finance.time_series',
              sources = ['sage/finance/time_series.pyx'],
              include_dirs = numpy_include_dirs),

    ################################
    ##
    ## sage.functions
    ##
    ################################

    Extension('sage.functions.prime_pi',
        sources = ['sage/functions/prime_pi.pyx']),

     ################################
     ##
     ## sage.games
     ##
     ################################

     Extension('sage.games.sudoku_backtrack',
               sources = ['sage/games/sudoku_backtrack.pyx']),

     ################################
     ##
     ## sage.geometry
     ##
     ################################

     Extension('sage.geometry.toric_lattice_element',
               sources = ['sage/geometry/toric_lattice_element.pyx']),

    ################################
    ##
    ## sage.graphs
    ##
    ################################

    Extension('sage.graphs.chrompoly',
              sources = ['sage/graphs/chrompoly.pyx'],
              libraries = ['gmp']),

    Extension('sage.graphs.cliquer',
              sources = ['sage/graphs/cliquer.pyx'],
              libraries = ['cliquer']),

    Extension('sage.graphs.generic_graph_pyx',
              sources = ['sage/graphs/generic_graph_pyx.pyx'],
              libraries = ['gmp']),

    Extension('sage.graphs.modular_decomposition.modular_decomposition',
              sources = ['sage/graphs/modular_decomposition/modular_decomposition.pyx'],
              depends = ['sage/graphs/modular_decomposition/src/dm.c',
                         'sage/graphs/modular_decomposition/src/dm_english.h']),

    Extension('sage.graphs.planarity',
              sources = ['sage/graphs/planarity/graphColorVertices.c',
                         'sage/graphs/planarity/graphColorVertices_Extensions.c',
                         'sage/graphs/planarity/graphDrawPlanar.c',
                         'sage/graphs/planarity/graphDrawPlanar_Extensions.c',
                         'sage/graphs/planarity/graphEmbed.c',
                         'sage/graphs/planarity/graphExtensions.c',
                         'sage/graphs/planarity/graphIO.c',
                         'sage/graphs/planarity/graphIsolator.c',
                         'sage/graphs/planarity/graphK23Search.c',
                         'sage/graphs/planarity/graphK23Search_Extensions.c',
                         'sage/graphs/planarity/graphK33Search.c',
                         'sage/graphs/planarity/graphK33Search_Extensions.c',
                         'sage/graphs/planarity/graphK4Search.c',
                         'sage/graphs/planarity/graphK4Search_Extensions.c',
                         'sage/graphs/planarity/graphNonplanar.c',
                         'sage/graphs/planarity/graphOuterplanarObstruction.c',
                         'sage/graphs/planarity/graphPreprocess.c',
                         'sage/graphs/planarity/graphTests.c',
                         'sage/graphs/planarity/graphUtils.c',
                         'sage/graphs/planarity/listcoll.c',
                         'sage/graphs/planarity/planarity.c',
                         'sage/graphs/planarity/planarityCommandLine.c',
                         'sage/graphs/planarity/planarityRandomGraphs.c',
                         'sage/graphs/planarity/planaritySpecificGraph.c',
                         'sage/graphs/planarity/planarityUtils.c',
                         'sage/graphs/planarity/stack.c',
                         'sage/graphs/planarity.pyx'],
              depends = ['sage/graphs/planarity/appconst.h',
                         'sage/graphs/planarity/graphColorVertices.h',
                         'sage/graphs/planarity/graphColorVertices.private.h',
                         'sage/graphs/planarity/graphDrawPlanar.h',
                         'sage/graphs/planarity/graphDrawPlanar.private.h',
                         'sage/graphs/planarity/graphExtensions.h',
                         'sage/graphs/planarity/graphExtensions.private.h',
                         'sage/graphs/planarity/graphFunctionTable.h',
                         'sage/graphs/planarity/graph.h',
                         'sage/graphs/planarity/graphK23Search.h',
                         'sage/graphs/planarity/graphK23Search.private.h',
                         'sage/graphs/planarity/graphK33Search.h',
                         'sage/graphs/planarity/graphK33Search.private.h',
                         'sage/graphs/planarity/graphK4Search.h',
                         'sage/graphs/planarity/graphK4Search.private.h',
                         'sage/graphs/planarity/graphStructures.h',
                         'sage/graphs/planarity/listcoll.h',
                         'sage/graphs/planarity/planarity.h',
                         'sage/graphs/planarity/platformTime.h',
                         'sage/graphs/planarity/stack.h']),

    Extension('sage.graphs.trees',
              sources = ['sage/graphs/trees.pyx']),

    Extension('sage.graphs.genus',
              sources = ['sage/graphs/genus.pyx']),

        ################################
        ##
        ## sage.graphs.base
        ##
        ################################

    Extension('sage.graphs.base.c_graph',
              sources = ['sage/graphs/base/c_graph.pyx']),

    Extension('sage.graphs.base.sparse_graph',
              sources = ['sage/graphs/base/sparse_graph.pyx']),

    Extension('sage.graphs.base.dense_graph',
              sources = ['sage/graphs/base/dense_graph.pyx']),

    ################################
    ##
    ## sage.groups
    ##
    ################################

    Extension('sage.groups.group',
              sources = ['sage/groups/group.pyx']),

    Extension('sage.groups.perm_gps.permgroup_element',
              sources = ['sage/groups/perm_gps/permgroup_element.pyx']),

        ###################################
        ##
        ## sage.groups.perm_gps.partn_ref
        ##
        ###################################

    Extension('sage.groups.perm_gps.partn_ref.automorphism_group_canonical_label',
              sources = ['sage/groups/perm_gps/partn_ref/automorphism_group_canonical_label.pyx'],
              libraries = ['gmp']),

    Extension('sage.groups.perm_gps.partn_ref.double_coset',
              sources = ['sage/groups/perm_gps/partn_ref/double_coset.pyx']),

    Extension('sage.groups.perm_gps.partn_ref.refinement_binary',
              sources = ['sage/groups/perm_gps/partn_ref/refinement_binary.pyx'],
              libraries = ['gmp']),

    Extension('sage.groups.perm_gps.partn_ref.refinement_graphs',
              sources = ['sage/groups/perm_gps/partn_ref/refinement_graphs.pyx'],
              libraries = ['gmp']),

    Extension('sage.groups.perm_gps.partn_ref.refinement_lists',
              sources = ['sage/groups/perm_gps/partn_ref/refinement_lists.pyx'],
              libraries = ['gmp']),

    Extension('sage.groups.perm_gps.partn_ref.refinement_matrices',
              sources = ['sage/groups/perm_gps/partn_ref/refinement_matrices.pyx'],
              libraries = ['gmp']),

    Extension('sage.groups.perm_gps.partn_ref.refinement_python',
              sources = ['sage/groups/perm_gps/partn_ref/refinement_python.pyx'],
              libraries = ['gmp']),

    ################################
    ##
    ## sage.gsl
    ##
    ################################

    Extension('sage.gsl.callback',
              sources = ['sage/gsl/callback.pyx'],
              libraries = ['gsl', BLAS, BLAS2],
              define_macros=[('GSL_DISABLE_DEPRECATED','1')]),

    Extension('sage.gsl.dwt',
              sources = ['sage/gsl/dwt.pyx'],
              libraries=['gsl',BLAS],
              define_macros=[('GSL_DISABLE_DEPRECATED','1')]),

    Extension('sage.gsl.fft',
              sources = ['sage/gsl/fft.pyx'],
              libraries = ['gsl', BLAS, BLAS2],
              define_macros=[('GSL_DISABLE_DEPRECATED','1')]),

    Extension('sage.gsl.gsl_array',
              sources = ['sage/gsl/gsl_array.pyx'],
              libraries=['gsl', BLAS, BLAS2],
              define_macros=[('GSL_DISABLE_DEPRECATED','1')]),

    Extension('sage.gsl.integration',
              sources = ['sage/gsl/integration.pyx'],
              define_macros=[('GSL_DISABLE_DEPRECATED','1')],
              libraries=['gsl',BLAS, BLAS2]),

    Extension('sage.gsl.interpolation',
              sources = ['sage/gsl/interpolation.pyx'],
              libraries = ['gsl', BLAS, BLAS2],
              define_macros=[('GSL_DISABLE_DEPRECATED','1')]),

    Extension('sage.gsl.ode',
              sources = ['sage/gsl/ode.pyx'],
              libraries=['gsl',BLAS, BLAS2],
              define_macros=[('GSL_DISABLE_DEPRECATED','1')]),

    Extension('sage.gsl.probability_distribution',
              sources = ['sage/gsl/probability_distribution.pyx'],
              libraries=['gsl', BLAS, BLAS2],
              define_macros=[('GSL_DISABLE_DEPRECATED','1')]),

    ################################
    ##
    ## sage.libs
    ##
    ################################

    Extension('sage.libs.ecl',
              sources = ["sage/libs/ecl.pyx"],
              libraries = ["ecl"],
              include_dirs = [SAGE_ROOT+'/local/include/ecl/'],
              depends = [SAGE_ROOT + '/local/include/ecl/ecl.h']),

    Extension('sage.libs.flint.flint',
              sources = ["sage/libs/flint/flint.pyx"],
              libraries = ["csage", "flint", "gmp", "gmpxx", "m", "stdc++"],
              include_dirs = [SAGE_ROOT+'/local/include/FLINT/'],
              extra_compile_args=["-std=c99", "-D_XPG6"],
              depends = [SAGE_ROOT + "/local/include/FLINT/flint.h"]),

    Extension('sage.libs.flint.fmpz_poly',
              sources = ["sage/libs/flint/fmpz_poly.pyx"],
              libraries = ["csage", "flint", "gmp", "gmpxx", "m", "stdc++"],
              include_dirs = [SAGE_ROOT+'/local/include/FLINT/'],
              extra_compile_args=["-std=c99", "-D_XPG6"],
              depends = [SAGE_ROOT + "/local/include/FLINT/flint.h"]),

    Extension('sage.libs.fplll.fplll',
              sources = ['sage/libs/fplll/fplll.pyx'],
              libraries = ['gmp', 'mpfr', 'stdc++', 'fplll'],
              language="c++",
              include_dirs = [SAGE_ROOT +'/local/include/fplll'],
              depends = [SAGE_ROOT + "/local/include/fplll/fplll.h"]),

    Extension('sage.libs.linbox.linbox',
              sources = ['sage/libs/linbox/linbox.pyx'],
              # For this to work on cygwin, linboxwrap *must* be
              # before ntl.
              libraries = ['linboxsage', 'ntl', 'linbox',
                           'stdc++', 'givaro', 'gmp', 'gmpxx', BLAS, BLAS2],
              language = 'c++'),

    Extension('sage.libs.lcalc.lcalc_Lfunction',
              sources = ['sage/libs/lcalc/lcalc_Lfunction.pyx'],
              libraries = ['m', 'ntl', 'mpfr', 'gmp', 'gmpxx',
                           'Lfunction', 'stdc++'],
              include_dirs = [SAGE_ROOT + "/local/include/lcalc/"],
              extra_compile_args=["-O3", "-ffast-math"],
              language = 'c++'),

    Extension('sage.libs.libecm',
              sources = ['sage/libs/libecm.pyx'],
              libraries = ['ecm', 'gmp'],
              depends = [SAGE_ROOT + "/local/include/ecm.h"]),

    Extension('sage.libs.mwrank.mwrank',
              sources = ["sage/libs/mwrank/mwrank.pyx",
                         "sage/libs/mwrank/wrap.cc"],
              define_macros = [("NTL_ALL",None)],
              depends = ["sage/libs/mwrank/wrap.h"],
              libraries = ["curvesntl", "g0nntl", "jcntl", "rankntl",
                           "ntl", "gmp", "gmpxx", "stdc++", "m", "pari"]),

    Extension('sage.libs.pari.gen',
              sources = ["sage/libs/pari/gen.pyx"],
              libraries = ['pari', 'gmp']),

    Extension('sage.libs.ratpoints',
              sources = ["sage/libs/ratpoints.pyx"],
              depends = [SAGE_ROOT + '/local/include/ratpoints.h'],
              libraries = ["ratpoints", "gmp"]),

    Extension('sage.libs.singular.singular',
              sources = ['sage/libs/singular/singular.pyx'],
              libraries = ['m', 'readline', 'singular', 'givaro', 'ntl', 'gmpxx', 'gmp'],
              language="c++",
              include_dirs = [SAGE_ROOT +'/local/include/singular'],
              depends = [SAGE_ROOT + "/local/include/libsingular.h"]),

    Extension('sage.libs.singular.polynomial',
              sources = ['sage/libs/singular/polynomial.pyx'],
              libraries = ['m', 'readline', 'singular', 'givaro', 'gmpxx', 'gmp'],
              language="c++",
              include_dirs = [SAGE_ROOT +'/local/include/singular'],
              depends = [SAGE_ROOT + "/local/include/libsingular.h"]),

    Extension('sage.libs.singular.ring',
              sources = ['sage/libs/singular/ring.pyx'],
              libraries = ['m', 'readline', 'singular', 'givaro', 'gmpxx', 'gmp'],
              language="c++",
              include_dirs = [SAGE_ROOT +'/local/include/singular'],
              depends = [SAGE_ROOT + "/local/include/libsingular.h"]),

    Extension('sage.libs.singular.groebner_strategy',
              sources = ['sage/libs/singular/groebner_strategy.pyx'],
              libraries = ['m', 'readline', 'singular', 'givaro', 'gmpxx', 'gmp'],
              language="c++",
              include_dirs = [SAGE_ROOT +'/local/include/singular'],
              depends = [SAGE_ROOT + "/local/include/libsingular.h"]),

    Extension('sage.libs.singular.function',
              sources = ['sage/libs/singular/function.pyx'],
              libraries = ['m', 'readline', 'singular', 'givaro', 'gmpxx', 'gmp'],
              language="c++",
              include_dirs = [SAGE_ROOT +'/local/include/singular'],
              depends = [SAGE_ROOT + "/local/include/libsingular.h"]),

    Extension('sage.libs.singular.option',
              sources = ['sage/libs/singular/option.pyx'],
              libraries = ['m', 'readline', 'singular', 'givaro', 'gmpxx', 'gmp'],
              language="c++",
              include_dirs = [SAGE_ROOT +'/local/include/singular'],
              depends = [SAGE_ROOT + "/local/include/libsingular.h"]),

    Extension('sage.libs.symmetrica.symmetrica',
              sources = ["sage/libs/symmetrica/%s"%s for s in ["symmetrica.pyx"]],
              include_dirs = ['/usr/include/malloc/'],
              libraries = ["symmetrica"],
              depends = [SAGE_ROOT + "/local/include/symmetrica/def.h"]),

    Extension('sage.libs.mpmath.utils',
              sources = ["sage/libs/mpmath/utils.pyx"],
              libraries = ['mpfr', 'gmp']),

    Extension('sage.libs.mpmath.ext_impl',
              sources = ["sage/libs/mpmath/ext_impl.pyx"],
              libraries = ['gmp']),

    Extension('sage.libs.mpmath.ext_main',
              sources = ["sage/libs/mpmath/ext_main.pyx"],
              libraries = ['gmp']),

    Extension('sage.libs.mpmath.ext_libmp',
              sources = ["sage/libs/mpmath/ext_libmp.pyx"],
              libraries = ['gmp']),

        ###################################
        ##
        ## sage.libs.cremona
        ##
        ###################################

    Extension('sage.libs.cremona.homspace',
              sources = ["sage/libs/cremona/homspace.pyx"],
              libraries = ['g0nntl', 'jcntl', 'gmpxx', 'ntl', 'gmp',
                           'm', 'stdc++', 'pari', 'curvesntl'],
              language='c++',
              define_macros = [("NTL_ALL",None)]),

    Extension('sage.libs.cremona.mat',
              sources = ["sage/libs/cremona/mat.pyx"],
              libraries = ['g0nntl', 'jcntl', 'gmpxx', 'ntl',
                           'gmp', 'm', 'stdc++', ],
              language='c++',
              define_macros = [("NTL_ALL",None)]),

    Extension('sage.libs.cremona.newforms',
              sources = ["sage/libs/cremona/newforms.pyx"],
              libraries = ['g0nntl', 'jcntl', 'gmpxx', 'ntl', 'gmp',
                           'm', 'stdc++', 'pari', 'curvesntl'],
              language='c++',
              define_macros = [("NTL_ALL",None)]),

        ###################################
        ##
        ## sage.libs.ntl
        ##
        ###################################

    # NOTE: It is *very* important (for cygwin) that csage be the
    # first library listed for all ntl extensions below.

    Extension('sage.libs.ntl.ntl_GF2',
              sources = ["sage/libs/ntl/ntl_GF2.pyx"],
              libraries = ["csage", "ntl", "gmp", "gmpxx", "stdc++"],
              language='c++'),

    Extension('sage.libs.ntl.ntl_GF2E',
              sources = ["sage/libs/ntl/ntl_GF2E.pyx"],
              libraries = ["csage", "ntl", "gmp", "gmpxx", "m", "stdc++"],
              language='c++'),

    Extension('sage.libs.ntl.ntl_GF2EContext',
              sources = ["sage/libs/ntl/ntl_GF2EContext.pyx"],
              libraries = ["csage", "ntl", "gmp", "gmpxx", "m", "stdc++"],
              language='c++'),

    Extension('sage.libs.ntl.ntl_GF2EX',
              sources = ["sage/libs/ntl/ntl_GF2EX.pyx"],
              libraries = ["csage", "ntl", "gmp", "gmpxx", "m", "stdc++"],
              language='c++'),

    Extension('sage.libs.ntl.ntl_GF2X',
              sources = ["sage/libs/ntl/ntl_GF2X.pyx"],
              libraries = ["csage", "ntl", "gmp", "gmpxx", "m", "stdc++"],
              language='c++'),

    Extension('sage.libs.ntl.ntl_lzz_p',
              sources = ["sage/libs/ntl/ntl_lzz_p.pyx"],
              libraries = ["csage", "ntl", "gmp", "gmpxx", "m", "stdc++"],
              language='c++'),

    Extension('sage.libs.ntl.ntl_lzz_pContext',
              sources = ["sage/libs/ntl/ntl_lzz_pContext.pyx"],
              libraries = ["csage", "ntl", "gmp", "gmpxx", "m", "stdc++"],
              language='c++'),

    Extension('sage.libs.ntl.ntl_lzz_pX',
              sources = ["sage/libs/ntl/ntl_lzz_pX.pyx"],
              libraries = ["csage", "ntl", "gmp", "gmpxx", "m", "stdc++"],
              language='c++'),

    Extension('sage.libs.ntl.ntl_mat_GF2',
              sources = ["sage/libs/ntl/ntl_mat_GF2.pyx"],
              libraries = ["csage", "ntl", "gmp", "gmpxx", "m", "stdc++"],
              language='c++'),

    Extension('sage.libs.ntl.ntl_mat_GF2E',
              sources = ["sage/libs/ntl/ntl_mat_GF2E.pyx"],
              libraries = ["csage", "ntl", "gmp", "gmpxx", "m", "stdc++"],
              language='c++'),

    Extension('sage.libs.ntl.ntl_mat_ZZ',
              sources = ["sage/libs/ntl/ntl_mat_ZZ.pyx"],
              libraries = ["csage", "ntl", "gmp", "gmpxx", "m", "stdc++"],
              language='c++'),

    Extension('sage.libs.ntl.ntl_ZZ',
              sources = ["sage/libs/ntl/ntl_ZZ.pyx"],
              libraries = ["csage", "ntl", "gmp", "gmpxx", "m", "stdc++"],
              language='c++'),

    Extension('sage.libs.ntl.ntl_ZZX',
              sources = ["sage/libs/ntl/ntl_ZZX.pyx"],
              libraries = ["csage", "ntl", "gmp", "gmpxx", "m", "stdc++"],
              language='c++'),

    Extension('sage.libs.ntl.ntl_ZZ_p',
              sources = ["sage/libs/ntl/ntl_ZZ_p.pyx"],
              libraries = ["csage", "ntl", "gmp", "gmpxx", "m", "stdc++"],
              language='c++'),

    Extension('sage.libs.ntl.ntl_ZZ_pContext',
              sources = ["sage/libs/ntl/ntl_ZZ_pContext.pyx"],
              libraries = ["csage", "ntl", "gmp", "gmpxx", "m", "stdc++"],
              language='c++'),

    Extension('sage.libs.ntl.ntl_ZZ_pE',
              sources = ["sage/libs/ntl/ntl_ZZ_pE.pyx"],
              libraries = ["csage", "ntl", "gmp", "gmpxx", "m", "stdc++"],
              language='c++'),

    Extension('sage.libs.ntl.ntl_ZZ_pEContext',
              sources = ["sage/libs/ntl/ntl_ZZ_pEContext.pyx"],
              libraries = ["csage", "ntl", "gmp", "gmpxx", "m", "stdc++"],
              language='c++'),

    Extension('sage.libs.ntl.ntl_ZZ_pEX',
              sources = ["sage/libs/ntl/ntl_ZZ_pEX.pyx"],
              libraries = ["csage", "ntl", "gmp", "gmpxx", "m", "stdc++"],
              language='c++'),

    Extension('sage.libs.ntl.ntl_ZZ_pX',
              sources = ["sage/libs/ntl/ntl_ZZ_pX.pyx"],
              libraries = ["csage", "ntl", "gmp", "gmpxx", "m", "stdc++"],
              language='c++'),

    ################################
    ##
    ## sage.matrix
    ##
    ################################

    Extension('sage.matrix.action',
              sources = ['sage/matrix/action.pyx']),

    Extension('sage.matrix.change_ring',
              sources = ['sage/matrix/change_ring.pyx'],
              libraries=[BLAS, BLAS2, 'gmp'],
              include_dirs = numpy_include_dirs),

    Extension('sage.matrix.matrix',
              sources = ['sage/matrix/matrix.pyx']),

    Extension('sage.matrix.matrix0',
              sources = ['sage/matrix/matrix0.pyx']),

    Extension('sage.matrix.matrix1',
              sources = ['sage/matrix/matrix1.pyx']),

    Extension('sage.matrix.matrix2',
              sources = ['sage/matrix/matrix2.pyx']),

    Extension('sage.matrix.matrix_complex_double_dense',
              sources = ['sage/matrix/matrix_complex_double_dense.pyx'],
              libraries=[BLAS, BLAS2],
              include_dirs = numpy_include_dirs),

    Extension('sage.matrix.matrix_cyclo_dense',
              sources = ['sage/matrix/matrix_cyclo_dense.pyx'],
              language = "c++",
              libraries=['ntl', 'gmp']),

    #Extension('sage.matrix.matrix_cyclo_sparse',
    #          sources = ['sage/matrix/matrix_cyclo_sparse.pyx']),

    Extension('sage.matrix.matrix_dense',
              sources = ['sage/matrix/matrix_dense.pyx']),

    #Extension('sage.matrix.matrix_domain_dense',
    #          sources = ['sage/matrix/matrix_domain_dense.pyx']),

    #Extension('sage.matrix.matrix_domain_sparse',
    #          sources = ['sage/matrix/matrix_domain_sparse.pyx']),

    Extension('sage.matrix.matrix_double_dense',
              sources = ['sage/matrix/matrix_double_dense.pyx'],
              libraries=[BLAS, BLAS2],
              include_dirs = numpy_include_dirs),

    Extension('sage.matrix.matrix_generic_dense',
              sources = ['sage/matrix/matrix_generic_dense.pyx']),

    Extension('sage.matrix.matrix_generic_sparse',
              sources = ['sage/matrix/matrix_generic_sparse.pyx']),

    Extension('sage.matrix.matrix_integer_2x2',
              sources = ['sage/matrix/matrix_integer_2x2.pyx'],
              libraries = ['gmp']),

    # TODO -- change to use BLAS at some point.
    Extension('sage.matrix.matrix_integer_dense',
              sources = ['sage/matrix/matrix_integer_dense.pyx'],
              # order matters for cygwin!!
              libraries = ['iml', 'gmp', 'm', 'pari', BLAS, BLAS2]),

    Extension('sage.matrix.matrix_integer_sparse',
              sources = ['sage/matrix/matrix_integer_sparse.pyx'],
              libraries = ['gmp']),

    Extension('sage.matrix.matrix_mod2_dense',
              sources = ['sage/matrix/matrix_mod2_dense.pyx'],
              libraries = ['gmp','m4ri', 'gd', 'png12', 'z'],
              depends = [SAGE_ROOT + "/local/include/png.h", SAGE_ROOT + "/local/include/m4ri/m4ri.h"]),

    Extension('sage.matrix.matrix_modn_dense',
              sources = ['sage/matrix/matrix_modn_dense.pyx'],
              libraries = ['gmp']),

    Extension('sage.matrix.matrix_modn_sparse',
              sources = ['sage/matrix/matrix_modn_sparse.pyx'],
              libraries = ['gmp']),

    Extension('sage.matrix.matrix_mpolynomial_dense',
              sources = ['sage/matrix/matrix_mpolynomial_dense.pyx'],
              libraries = ['m', 'readline', 'singular', 'givaro', 'gmpxx', 'gmp'],
              language="c++",
              include_dirs = [SAGE_ROOT +'/local/include/singular'],
              depends = [SAGE_ROOT + "/local/include/libsingular.h"]),

    #Extension('sage.matrix.matrix_pid_dense',
    #          sources = ['sage/matrix/matrix_pid_dense.pyx']),

    #Extension('sage.matrix.matrix_pid_sparse',
    #          sources = ['sage/matrix/matrix_pid_sparse.pyx']),

    Extension('sage.matrix.matrix_rational_dense',
              sources = ['sage/matrix/matrix_rational_dense.pyx'],
              libraries = ['gmp', 'pari']),

    Extension('sage.matrix.matrix_rational_sparse',
              sources = ['sage/matrix/matrix_rational_sparse.pyx'],
              libraries = ['gmp']),

    Extension('sage.matrix.matrix_real_double_dense',
              sources = ['sage/matrix/matrix_real_double_dense.pyx'],
              libraries=[BLAS, BLAS2],
              include_dirs = numpy_include_dirs),

    Extension('sage.matrix.matrix_sparse',
              sources = ['sage/matrix/matrix_sparse.pyx']),

    Extension('sage.matrix.matrix_symbolic_dense',
              sources = ['sage/matrix/matrix_symbolic_dense.pyx']),

    Extension('sage.matrix.matrix_window',
              sources = ['sage/matrix/matrix_window.pyx']),

    Extension('sage.matrix.matrix_window_modn_dense',
              sources = ['sage/matrix/matrix_window_modn_dense.pyx']),

    Extension('sage.matrix.misc',
              sources = ['sage/matrix/misc.pyx'],
              libraries=['mpfr','gmp']),

    Extension('sage.matrix.strassen',
              sources = ['sage/matrix/strassen.pyx']),

    #Extension('sage.matrix.padics.matrix_padic_capped_relative_dense',
    #          sources = ['sage/matrix/padics/matrix_padic_capped_relative_dense.pyx']),

    ################################
    ##
    ## sage.media
    ##
    ################################

    Extension('sage.media.channels',
              sources = ['sage/media/channels.pyx']),

    ################################
    ##
    ## sage.misc
    ##
    ################################

    Extension('sage.misc.allocator',
              sources = ['sage/misc/allocator.pyx']),

    Extension('sage.misc.bitset',
              sources = ['sage/misc/bitset.pyx']),

    Extension('sage.misc.citation',
              sources = ['sage/misc/citation.pyx']),

    Extension('sage.misc.cython_c',
              sources = ['sage/misc/cython_c.pyx']),

    Extension('sage.misc.derivative',
              sources = ['sage/misc/derivative.pyx']),

    Extension('sage.misc.fpickle',
              sources = ['sage/misc/fpickle.pyx']),

    Extension('sage.misc.misc_c',
              sources = ['sage/misc/misc_c.pyx']),

    Extension('sage.misc.parser',
              sources = ['sage/misc/parser.pyx']),

    Extension('sage.misc.pickle_old',
              sources = ['sage/misc/pickle_old.pyx']),

    Extension('sage.misc.randstate',
              sources = ['sage/misc/randstate.pyx'],
              libraries = ['gmp']),

    Extension('sage.misc.refcount',
              sources = ['sage/misc/refcount.pyx']),

    Extension('sage.misc.reset',
              sources = ['sage/misc/reset.pyx']),

    Extension('sage.misc.sage_timeit_class',
              sources = ['sage/misc/sage_timeit_class.pyx']),

    Extension('sage.misc.sagex_ds',
              sources = ['sage/misc/sagex_ds.pyx']),

    Extension('sage.misc.search',
              sources = ['sage/misc/search.pyx']),

    Extension('sage.misc.session',
              sources = ['sage/misc/session.pyx']),

    ################################
    ##
    ## sage.modular
    ##
    ################################

    Extension('sage.modular.arithgroup.congroup_pyx',
              sources = ['sage/modular/arithgroup/congroup_pyx.pyx']),

    Extension('sage.modular.modform.eis_series_cython',
              sources = ['sage/modular/modform/eis_series_cython.pyx'],
              libraries = ["gmp", "flint"],
              include_dirs = [SAGE_ROOT + '/local/include/FLINT/'],
              extra_compile_args = ['-std=c99'],
              depends = [SAGE_ROOT + "/local/include/FLINT/flint.h"]),

    Extension('sage.modular.modsym.apply',
              sources = ['sage/modular/modsym/apply.pyx'],
              libraries = ["csage", "flint", "gmp", "gmpxx", "m", "stdc++"],
              include_dirs = [SAGE_ROOT+'/local/include/FLINT/'],
              extra_compile_args=["-std=c99",  "-D_XPG6"],
              depends = [SAGE_ROOT + "/local/include/FLINT/flint.h"]),

    Extension('sage.modular.modsym.heilbronn',
              sources = ['sage/modular/modsym/heilbronn.pyx'],
              libraries = ["csage", "flint", "gmp", "gmpxx", "m", "stdc++"],
              include_dirs = [SAGE_ROOT+'/local/include/FLINT/'],
              extra_compile_args=["-std=c99", "-D_XPG6"],
              depends = [SAGE_ROOT + "/local/include/FLINT/flint.h"]),

    Extension('sage.modular.modsym.p1list',
              sources = ['sage/modular/modsym/p1list.pyx'],
              libraries = ['gmp']),

    ################################
    ##
    ## sage.modules
    ##
    ################################

    Extension('sage.modules.free_module_element',
              sources = ['sage/modules/free_module_element.pyx']),

    Extension('sage.modules.module',
              sources = ['sage/modules/module.pyx']),

    Extension('sage.modules.vector_complex_double_dense',
              ['sage/modules/vector_complex_double_dense.pyx'],
              libraries = [BLAS, BLAS2],
              include_dirs = numpy_include_dirs),

    Extension('sage.modules.vector_double_dense',
              ['sage/modules/vector_double_dense.pyx'],
              libraries = [BLAS, BLAS2],
              include_dirs = numpy_include_dirs),

    Extension('sage.modules.vector_integer_dense',
              sources = ['sage/modules/vector_integer_dense.pyx'],
              libraries = ['gmp']),

    Extension('sage.modules.vector_modn_dense',
              sources = ['sage/modules/vector_modn_dense.pyx']),

    Extension('sage.modules.vector_mod2_dense',
              sources = ['sage/modules/vector_mod2_dense.pyx'],
              libraries = ['gmp','m4ri', 'png12', 'gd'],
              depends = [SAGE_ROOT + "/local/include/png.h", SAGE_ROOT + "/local/include/m4ri/m4ri.h"]),

    Extension('sage.modules.vector_rational_dense',
              sources = ['sage/modules/vector_rational_dense.pyx'],
              libraries = ['gmp']),

    Extension('sage.modules.vector_real_double_dense',
              ['sage/modules/vector_real_double_dense.pyx'],
              libraries = [BLAS, BLAS2],
              include_dirs = numpy_include_dirs),

    # Extension('sage.modules.vector_rational_sparse',
    #           sources = ['sage/modules/vector_rational_sparse.pyx'],
    #           libraries = ['gmp']),

    ################################
    ##
    ## sage.numerical
    ##
    ################################

    Extension("sage.numerical.mip",
              ["sage/numerical/mip.pyx"],
            include_dirs=["local/include/"],
            libraries=["csage","stdc++"]),

    ################################
    ##
    ## sage.plot
    ##
    ################################

    Extension('sage.plot.complex_plot',
              sources = ['sage/plot/complex_plot.pyx'],
              include_dirs = numpy_include_dirs),

    Extension('sage.plot.plot3d.base',
              sources = ['sage/plot/plot3d/base.pyx'],
              extra_compile_args=["-std=c99"]),

    Extension('sage.plot.plot3d.implicit_surface',
              sources = ['sage/plot/plot3d/implicit_surface.pyx'],
              libraries = ['gsl'],
              include_dirs = numpy_include_dirs),

    Extension('sage.plot.plot3d.index_face_set',
              sources = ['sage/plot/plot3d/index_face_set.pyx'],
              extra_compile_args=["-std=c99"]),

    Extension('sage.plot.plot3d.parametric_surface',
              sources = ['sage/plot/plot3d/parametric_surface.pyx']),

    Extension('sage.plot.plot3d.shapes',
              sources = ['sage/plot/plot3d/shapes.pyx']),

    Extension('sage.plot.plot3d.transform',
              sources = ['sage/plot/plot3d/transform.pyx']),

    ################################
    ##
    ## sage.quadratic_forms
    ##
    ################################

    Extension('sage.quadratic_forms.count_local_2',
              sources = ['sage/quadratic_forms/count_local_2.pyx'],
              libraries = ['gmp']),

    Extension('sage.quadratic_forms.quadratic_form__evaluate',
              sources = ['sage/quadratic_forms/quadratic_form__evaluate.pyx']),

    ################################
    ##
    ## sage.rings
    ##
    ################################

    Extension('sage.rings.bernmm',
              sources = ['sage/rings/bernmm.pyx',
                         'sage/rings/bernmm/bern_modp.cpp',
                         'sage/rings/bernmm/bern_modp_util.cpp',
                         'sage/rings/bernmm/bern_rat.cpp'],
              libraries = ['ntl', 'gmp', 'stdc++', 'pthread'],
              depends = ['sage/rings/bernmm/bern_modp.h',
                         'sage/rings/bernmm/bern_modp_util.h',
                         'sage/rings/bernmm/bern_rat.h'],
              language = 'c++',
              define_macros=[('USE_THREADS', '1'),
                             ('THREAD_STACK_SIZE', '4096')]),

    Extension('sage.rings.bernoulli_mod_p',
              sources = ['sage/rings/bernoulli_mod_p.pyx'],
              libraries=['ntl','stdc++'],
              language = 'c++',
              include_dirs = ['sage/libs/ntl/']),

    Extension('sage.rings.complex_double',
              sources = ['sage/rings/complex_double.pyx'],
              extra_compile_args=["-std=c99",  "-D_XPG6"],
              libraries = (['gsl', BLAS, BLAS2, 'pari', 'gmp'] +
                           uname_specific('CYGWIN', ['mc', 'md'], []) +
                           ['m'])),

    Extension('sage.rings.complex_interval',
              sources = ['sage/rings/complex_interval.pyx'],
              libraries = ['mpfi', 'mpfr', 'gmp']),

    Extension('sage.rings.complex_number',
              sources = ['sage/rings/complex_number.pyx'],
              libraries = ['mpfr', 'gmp']),

    Extension('sage.rings.integer',
              sources = ['sage/rings/integer.pyx'],
              libraries=['ntl', 'gmp', 'pari']),

    Extension('sage.rings.integer_ring',
              sources = ['sage/rings/integer_ring.pyx'],
              libraries=['ntl', 'gmp']),

    Extension('sage.rings.fast_arith',
              sources = ['sage/rings/fast_arith.pyx'],
              libraries=['gmp','pari','csage']),

    Extension('sage.rings.fraction_field_element',
              sources = ['sage/rings/fraction_field_element.pyx']),

    Extension('sage.rings.fraction_field_FpT',
              sources = ['sage/rings/fraction_field_FpT.pyx'],
              libraries = ["csage", "flint", "gmp", "gmpxx", "ntl", "zn_poly"],
              extra_compile_args=["-std=c99", "-D_XPG6"],
              include_dirs = [SAGE_ROOT+'/local/include/FLINT/'],
              depends = [SAGE_ROOT + "/local/include/FLINT/flint.h"]),

    Extension('sage.rings.laurent_series_ring_element',
              sources = ['sage/rings/laurent_series_ring_element.pyx']),

    Extension('sage.rings.memory',
              sources = ['sage/rings/memory.pyx'],
              libraries=['gmp','stdc++']),

    Extension('sage.rings.morphism',
              sources = ['sage/rings/morphism.pyx']),

    Extension('sage.rings.power_series_mpoly',
              sources = ['sage/rings/power_series_mpoly.pyx']),

    Extension('sage.rings.power_series_poly',
              sources = ['sage/rings/power_series_poly.pyx']),

    Extension('sage.rings.power_series_ring_element',
              sources = ['sage/rings/power_series_ring_element.pyx']),

    Extension('sage.rings.rational',
              sources = ['sage/rings/rational.pyx'],
              libraries=['ntl', 'gmp']),

    Extension('sage.rings.real_double',
              sources = ['sage/rings/real_double.pyx'],
              libraries = ['gsl', 'gmp', BLAS, BLAS2],
              define_macros=[('GSL_DISABLE_DEPRECATED','1')]),

    Extension('sage.rings.real_lazy',
              sources = ['sage/rings/real_lazy.pyx']),

    Extension('sage.rings.real_mpfi',
              sources = ['sage/rings/real_mpfi.pyx'],
              libraries = ['mpfi', 'mpfr', 'gmp']),

    Extension('sage.rings.real_mpfr',
              sources = ['sage/rings/real_mpfr.pyx'],
              libraries = ['mpfr', 'pari', 'gmp']),

    #Extension('sage.rings.real_rqdf',
    #          sources = ["sage/rings/real_rqdf.pyx"],
    #          libraries = ['qd', 'm', 'stdc++','gmp','mpfr' ],
    #          language='c++'),

    Extension('sage.rings.residue_field',
              sources = ['sage/rings/residue_field.pyx']),

    Extension('sage.rings.ring',
              sources = ['sage/rings/ring.pyx']),

        ################################
        ##
        ## sage.rings.finite_rings
        ##
        ################################

    Extension('sage.rings.finite_rings.finite_field_base',
              sources = ['sage/rings/finite_rings/finite_field_base.pyx']),

    Extension('sage.rings.finite_rings.element_base',
              sources = ['sage/rings/finite_rings/element_base.pyx']),

    Extension('sage.rings.finite_rings.integer_mod',
              sources = ['sage/rings/finite_rings/integer_mod.pyx'],
              libraries = ['gmp']),

    Extension('sage.rings.finite_rings.element_givaro',
              sources = ["sage/rings/finite_rings/element_givaro.pyx"],
              # this order is needed to compile under windows.
              libraries = ['givaro', 'ntl', 'gmpxx', 'gmp', 'm', 'stdc++', ],
              language='c++'),

    Extension('sage.rings.finite_rings.element_ntl_gf2e',
              sources = ['sage/rings/finite_rings/element_ntl_gf2e.pyx'],
              libraries = ['ntl', 'gmp'],
              language = 'c++'),

        ################################
        ##
        ## sage.rings.number_field
        ##
        ################################

    Extension('sage.rings.number_field.number_field_base',
              sources = ['sage/rings/number_field/number_field_base.pyx']),

    Extension('sage.rings.number_field.number_field_element',
              sources = ['sage/rings/number_field/number_field_element.pyx'],
              libraries=['ntl','gmp'],
              language = 'c++'),

    Extension('sage.rings.number_field.number_field_element_quadratic',
              sources = ['sage/rings/number_field/number_field_element_quadratic.pyx'],
              libraries=['ntl', 'gmp'],
              language = 'c++'),

    Extension('sage.rings.number_field.number_field_morphisms',
              sources = ['sage/rings/number_field/number_field_morphisms.pyx']),

    Extension('sage.rings.number_field.totallyreal',
              sources = ['sage/rings/number_field/totallyreal.pyx'],
              libraries = ['gmp', 'pari']),

    Extension('sage.rings.number_field.totallyreal_data',
              sources = ['sage/rings/number_field/totallyreal_data.pyx'],
              libraries = ['gmp']),

        ################################
        ##
        ## sage.rings.padics
        ##
        ################################

    Extension('sage.rings.padics.local_generic_element',
              sources = ['sage/rings/padics/local_generic_element.pyx']),

    #Extension('sage.rings.padics.morphism',
    #          sources = ['sage/rings/padics/morphism.pyx'],
    #          libraries=['gmp', 'ntl', 'csage', 'gmpxx', 'm', 'stdc++'],
    #          language='c++'),

    Extension('sage.rings.padics.padic_base_generic_element',
              sources = ['sage/rings/padics/padic_base_generic_element.pyx'],
              libraries=['gmp']),

    Extension('sage.rings.padics.padic_capped_absolute_element',
              sources = ['sage/rings/padics/padic_capped_absolute_element.pyx'],
              libraries=['gmp']),

    Extension('sage.rings.padics.padic_capped_relative_element',
              sources = ['sage/rings/padics/padic_capped_relative_element.pyx'],
              libraries=['gmp', 'csage']),

    Extension('sage.rings.padics.padic_ext_element',
              sources = ['sage/rings/padics/padic_ext_element.pyx'],
              libraries=['ntl', 'gmp', 'csage', 'gmpxx', 'm', 'stdc++'],
              language='c++'),

    Extension('sage.rings.padics.padic_fixed_mod_element',
              sources = ['sage/rings/padics/padic_fixed_mod_element.pyx'],
              libraries=['gmp']),

    Extension('sage.rings.padics.padic_generic_element',
              sources = ['sage/rings/padics/padic_generic_element.pyx'],
              libraries=['gmp']),

    Extension('sage.rings.padics.padic_printing',
              sources = ['sage/rings/padics/padic_printing.pyx'],
              libraries=['gmp', 'ntl', 'csage', 'gmpxx', 'm', 'stdc++'],
              language='c++'),

    Extension('sage.rings.padics.padic_ZZ_pX_CA_element',
              sources = ['sage/rings/padics/padic_ZZ_pX_CA_element.pyx'],
              libraries = ['ntl', 'gmp', 'csage','gmpxx','m','stdc++'],
              language='c++'),

    Extension('sage.rings.padics.padic_ZZ_pX_CR_element',
              sources = ['sage/rings/padics/padic_ZZ_pX_CR_element.pyx'],
              libraries=['ntl', 'gmp', 'csage','gmpxx','m','stdc++'],
              language='c++'),

    Extension('sage.rings.padics.padic_ZZ_pX_element',
              sources = ['sage/rings/padics/padic_ZZ_pX_element.pyx'],
              libraries=['ntl', 'gmp', 'csage', 'gmpxx', 'm', 'stdc++'],
              language='c++'),

    Extension('sage.rings.padics.padic_ZZ_pX_FM_element',
              sources = ['sage/rings/padics/padic_ZZ_pX_FM_element.pyx'],
              libraries=['ntl', 'gmp', 'csage', 'gmpxx', 'm', 'stdc++'],
              language='c++'),

    Extension('sage.rings.padics.pow_computer',
              sources = ['sage/rings/padics/pow_computer.pyx'],
              libraries = ["csage", "ntl", "gmp", "gmpxx", "m", "stdc++"],
              language='c++'),

    Extension('sage.rings.padics.pow_computer_ext',
              sources = ['sage/rings/padics/pow_computer_ext.pyx'],
              libraries = ["csage", "ntl", "gmp", "gmpxx", "m", "stdc++"],
              language='c++'),

        ################################
        ##
        ## sage.rings.polynomial
        ##
        ################################

    Extension('sage.rings.polynomial.cyclotomic',
              sources = ['sage/rings/polynomial/cyclotomic.pyx']),

    Extension('sage.rings.polynomial.laurent_polynomial',
              sources = ['sage/rings/polynomial/laurent_polynomial.pyx']),

    Extension('sage.rings.polynomial.multi_polynomial',
              sources = ['sage/rings/polynomial/multi_polynomial.pyx']),

    Extension('sage.rings.polynomial.multi_polynomial_ideal_libsingular',
              sources = ['sage/rings/polynomial/multi_polynomial_ideal_libsingular.pyx'],
              libraries = ['m', 'readline', 'singular', 'givaro', 'gmpxx', 'gmp'],
              language="c++",
              include_dirs = [SAGE_ROOT +'/local/include/singular'],
              depends = [SAGE_ROOT + "/local/include/libsingular.h"]),

    Extension('sage.rings.polynomial.multi_polynomial_libsingular',
              sources = ['sage/rings/polynomial/multi_polynomial_libsingular.pyx'],
              libraries = ['m', 'readline', 'singular', 'givaro', 'gmpxx', 'gmp'],
              language="c++",
              include_dirs = [SAGE_ROOT +'/local/include/singular'],
              depends = [SAGE_ROOT + "/local/include/libsingular.h"]),

    Extension('sage.rings.polynomial.multi_polynomial_ring_generic',
              sources = ['sage/rings/polynomial/multi_polynomial_ring_generic.pyx']),

    Extension('sage.rings.polynomial.polydict',
              sources = ['sage/rings/polynomial/polydict.pyx']),

    Extension('sage.rings.polynomial.polynomial_compiled',
               sources = ['sage/rings/polynomial/polynomial_compiled.pyx']),

    Extension('sage.rings.polynomial.polynomial_element',
              sources = ['sage/rings/polynomial/polynomial_element.pyx']),

    Extension('sage.rings.polynomial.polynomial_gf2x',
              sources = ['sage/rings/polynomial/polynomial_gf2x.pyx'],
              libraries = ['ntl', 'stdc++', 'gmp'],
              language = 'c++',
              include_dirs = ['sage/libs/ntl/']),

    Extension('sage.rings.polynomial.polynomial_zz_pex',
              sources = ['sage/rings/polynomial/polynomial_zz_pex.pyx'],
              libraries = ['ntl', 'stdc++', 'gmp'],
              language = 'c++',
              include_dirs = ['sage/libs/ntl/']),

    Extension('sage.rings.polynomial.polynomial_zmod_flint',
              sources = ['sage/rings/polynomial/polynomial_zmod_flint.pyx'],
              libraries = ["csage", "flint", "gmp", "gmpxx", "ntl", "zn_poly"],
              extra_compile_args=["-std=c99", "-D_XPG6"],
              include_dirs = [SAGE_ROOT+'/local/include/FLINT/'],
              depends = [SAGE_ROOT + "/local/include/FLINT/flint.h"]),

    Extension('sage.rings.polynomial.polynomial_integer_dense_flint',
              sources = ['sage/rings/polynomial/polynomial_integer_dense_flint.pyx'],
              language = 'c++',
              libraries = ["csage", "flint", "ntl", "gmpxx", "gmp"],
              include_dirs = [SAGE_ROOT+'/local/include/FLINT/'],
              depends = [SAGE_ROOT + "/local/include/FLINT/flint.h"]),

    Extension('sage.rings.polynomial.polynomial_integer_dense_ntl',
              sources = ['sage/rings/polynomial/polynomial_integer_dense_ntl.pyx'],
              libraries = ['ntl', 'stdc++', 'gmp'],
              language = 'c++',
              include_dirs = ['sage/libs/ntl/']),

    Extension('sage.rings.polynomial.polynomial_modn_dense_ntl',
              sources = ['sage/rings/polynomial/polynomial_modn_dense_ntl.pyx'],
              libraries = ['ntl', 'stdc++', 'gmp'],
              language = 'c++',
              include_dirs = ['sage/libs/ntl/']),

    Extension('sage.rings.polynomial.pbori',
              sources = ['sage/rings/polynomial/pbori.pyx'],
              libraries=(['polybori','pboriCudd', 'groebner', 'gd'] +
                           uname_specific('CYGWIN', ['png'], ['png12']) +
                           ['m4ri']),
              include_dirs = [SAGE_ROOT+'/local/include/cudd',
                              SAGE_ROOT+'/local/include/polybori',
                              SAGE_ROOT+'/local/include/polybori/groebner',
                              "sage/libs/polybori"],
              depends = [SAGE_ROOT + "/local/include/polybori/polybori.h"],
              extra_compile_args = polybori_extra_compile_args,
              language = 'c++'),

    Extension('sage.rings.polynomial.polynomial_real_mpfr_dense',
              sources = ['sage/rings/polynomial/polynomial_real_mpfr_dense.pyx'],
              libraries = ['mpfr', 'gmp']),

    Extension('sage.rings.polynomial.real_roots',
              sources = ['sage/rings/polynomial/real_roots.pyx'],
              #libraries=['mpfr', 'qd],
              libraries=['mpfr', 'gmp'],
              include_dirs = numpy_include_dirs),

    Extension('sage.rings.polynomial.symmetric_reduction',
              sources = ['sage/rings/polynomial/symmetric_reduction.pyx']),

    ################################
    ##
    ## sage.schemes
    ##
    ################################

    Extension('sage.schemes.elliptic_curves.descent_two_isogeny',
              sources = ['sage/schemes/elliptic_curves/descent_two_isogeny.pyx'],
              extra_compile_args=["-std=c99"],
              depends = [SAGE_ROOT + '/local/include/ratpoints.h',
                         SAGE_ROOT + '/local/include/gmp.h',
                         SAGE_ROOT + '/local/include/FLINT/flint.h'],
              include_dirs = [SAGE_ROOT+'/local/include/FLINT/'],
              libraries = ['flint', 'gmp', 'ratpoints']),

    Extension('sage.schemes.hyperelliptic_curves.hypellfrob',
              sources = ['sage/schemes/hyperelliptic_curves/hypellfrob.pyx',
                         'sage/schemes/hyperelliptic_curves/hypellfrob/hypellfrob.cpp',
                         'sage/schemes/hyperelliptic_curves/hypellfrob/recurrences_ntl.cpp',
                         'sage/schemes/hyperelliptic_curves/hypellfrob/recurrences_zn_poly.cpp'],
              libraries = ['ntl', 'stdc++', 'gmp', 'zn_poly'],
              depends = ['sage/schemes/hyperelliptic_curves/hypellfrob/hypellfrob.h',
                         'sage/schemes/hyperelliptic_curves/hypellfrob/recurrences_ntl.h',
                         'sage/schemes/hyperelliptic_curves/hypellfrob/recurrences_zn_poly.h'],
              language = 'c++',
              include_dirs = ['sage/libs/ntl/',
                              'sage/schemes/hyperelliptic_curves/hypellfrob/']),

    ################################
    ##
    ## sage.sets
    ##
    ################################

    Extension('sage.sets.disjoint_set',
              sources = ['sage/sets/disjoint_set.pyx']),

    ################################
    ##
    ## sage.stats
    ##
    ################################

    Extension('sage.stats.hmm.util',
              sources = ['sage/stats/hmm/util.pyx']),

    Extension('sage.stats.hmm.distributions',
              sources = ['sage/stats/hmm/distributions.pyx']),

    Extension('sage.stats.hmm.hmm',
              sources = ['sage/stats/hmm/hmm.pyx']),

    Extension('sage.stats.hmm.chmm',
              sources = ['sage/stats/hmm/chmm.pyx'],
              extra_compile_args=["-std=c99"]),

    Extension('sage.stats.intlist',
              sources = ['sage/stats/intlist.pyx']),

    ################################
    ##
    ## sage.structure
    ##
    ################################

    Extension('sage.structure.category_object',
              sources = ['sage/structure/category_object.pyx']),

    Extension('sage.structure.coerce',
              sources = ['sage/structure/coerce.pyx']),

    Extension('sage.structure.coerce_actions',
              sources = ['sage/structure/coerce_actions.pyx']),

    Extension('sage.structure.coerce_dict',
              sources = ['sage/structure/coerce_dict.pyx']),

    Extension('sage.structure.coerce_maps',
              sources = ['sage/structure/coerce_maps.pyx']),

    Extension('sage.structure.element',
              sources = ['sage/structure/element.pyx']),

    Extension('sage.structure.factory',
              sources = ['sage/structure/factory.pyx']),

    Extension('sage.structure.generators',
              sources = ['sage/structure/generators.pyx']),

    Extension('sage.structure.mutability',
              sources = ['sage/structure/mutability.pyx']),

    Extension('sage.structure.parent',
              sources = ['sage/structure/parent.pyx']),

    Extension('sage.structure.parent_base',
              sources = ['sage/structure/parent_base.pyx']),

    Extension('sage.structure.parent_gens',
              sources = ['sage/structure/parent_gens.pyx']),

    Extension('sage.structure.parent_old',
              sources = ['sage/structure/parent_old.pyx']),

    Extension('sage.structure.sage_object',
              sources = ['sage/structure/sage_object.pyx']),

    Extension('sage.structure.wrapper_parent',
              sources = ['sage/structure/wrapper_parent.pyx']),

    ################################
    ##
    ## sage.symbolic
    ##
    ################################
    Extension('sage.symbolic.constants_c',
              sources = ['sage/symbolic/constants_c.pyx'],
              language = 'c++',
              depends = [SAGE_ROOT + "/local/include/pynac/ginac.h"],
              libraries = ["pynac", "gmp"]),

    Extension('sage.symbolic.expression',
              sources = ['sage/symbolic/expression.pyx'],
              language = 'c++',
              depends = [SAGE_ROOT + "/local/include/pynac/ginac.h"],
              libraries = ["pynac", "gmp"]),

    Extension('sage.symbolic.function',
              sources = ['sage/symbolic/function.pyx'],
              language = 'c++',
              depends = [SAGE_ROOT + "/local/include/pynac/ginac.h"],
              libraries = ["pynac", "gmp"]),

    Extension('sage.symbolic.power_helper',
              sources = ['sage/symbolic/power_helper.pyx'],
              depends = [SAGE_ROOT + "/local/include/pynac/ginac.h"],
              language = 'c++'),

    Extension('sage.symbolic.pynac',
              sources = ['sage/symbolic/pynac.pyx'],
              language = 'c++',
              depends = [SAGE_ROOT + "/local/include/pynac/ginac.h"],
              libraries = ["pynac", "gmp", "gsl"]),

    Extension('sage.symbolic.ring',
              sources = ['sage/symbolic/ring.pyx'],
              language = 'c++',
              depends = [SAGE_ROOT + "/local/include/pynac/ginac.h"],
              libraries = ["pynac", "gmp"]),

    ]

# Optional extensions :
# These extensions are to be compiled only if the
# corresponding packages have been installed

from sage.misc.package import is_package_installed

if is_package_installed('glpk'):
    ext_modules.append(
        Extension("sage.numerical.mip_glpk",
                  ["sage/numerical/mip_glpk.pyx"],
                  include_dirs = [SAGE_ROOT+"/local/include/", "sage/c_lib/include/"],
                  language = 'c++',
                  libraries=["csage", "stdc++", "glpk"])
        )

if is_package_installed('cbc'):

    ext_modules.append(
        Extension("sage.numerical.osi_interface",
                  ["sage/numerical/osi_interface.pyx"],
                  include_dirs = [SAGE_ROOT+"/local/include/","sage/c_lib/include/"],
                  language = 'c++',
                  libraries = ["csage", "stdc++", "Cbc", "CbcSolver", "Cgl", "Clp", "CoinUtils", "OsiCbc", "OsiClp", "Osi", "OsiVol", "Vol"])
        )

    if os.path.isfile(SAGE_ROOT+"/local/include/coin/OsiCpxSolverInterface.hpp"):
    # if Cplex is installed too
        ext_modules.append(
            Extension("sage.numerical.mip_coin",
                      ["sage/numerical/mip_coin.pyx"],
                      include_dirs = [SAGE_ROOT+"/local/include/","sage/c_lib/include/"],
                      language = 'c++',
                      define_macros=[('BOB','1')],
                      libraries = ["csage", "stdc++", "Cbc", "CbcSolver", "Cgl", "Clp", "CoinUtils", "OsiCbc", "OsiClp", "Osi", "OsiVol", "Vol", "OsiCpx"])

            )
        ext_modules.append(
            Extension("sage.numerical.mip_cplex",
                      ["sage/numerical/mip_cplex.pyx"],
                      include_dirs = [SAGE_ROOT+"/local/include/","/sage/c_lib/include/"],
                      language = 'c++',
                      libraries = ["csage", "stdc++", "Cbc", "CbcSolver", "Cgl", "Clp", "CoinUtils", "OsiCbc", "OsiClp", "Osi", "OsiVol", "Vol", "OsiCpx"])
            )

    # otherwise
    else:
        ext_modules.append(
            Extension("sage.numerical.mip_coin",
                      ["sage/numerical/mip_coin.pyx"],
                      include_dirs = [SAGE_ROOT+"/local/include/","sage/c_lib/include/"],
                      language = 'c++',
                      libraries = ["csage", "stdc++", "Cbc", "CbcSolver", "Cgl", "Clp", "CoinUtils", "OsiCbc", "OsiClp", "Osi", "OsiVol", "Vol"])
            )

# Only include darwin_utilities on OS_X >= 10.5
UNAME = os.uname()
if UNAME[0] == "Darwin" and not UNAME[2].startswith('8.'):
    ext_modules.append(
        Extension('sage.misc.darwin_utilities',
            sources = ['sage/misc/darwin_memory_usage.c',
                       'sage/misc/darwin_utilities.pyx'],
            depends = ['sage/misc/darwin_memory_usage.h'])
        )
