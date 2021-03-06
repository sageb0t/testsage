"""
Long tests for libGAP

These stress test the garbage collection inside GAP
"""

from sage.libs.all import libgap

def test_loop_1():
    """
    EXAMPLES::

        sage: from sage.libs.gap.test_long import test_loop_1
        sage: test_loop_1()
    """
    libgap.collect()
    for i in range(10000):
        G = libgap.CyclicGroup(2)

def test_loop_2():
    """
    EXAMPLES::

        sage: from sage.libs.gap.test_long import test_loop_2
        sage: test_loop_2()
    """
    G =libgap.FreeGroup(2)
    a,b = G.GeneratorsOfGroup()
    for i in range(100):
        rel = libgap([a**2, b**2, a*b*a*b])
        H = G / rel
        H1 = H.GeneratorsOfGroup()[0]
        n = H1.Order()
        assert n.sage() == 2

    for i in range(300000):
        n = libgap.Order(H1)

def test_loop_3():
    """
    EXAMPLES::

        sage: from sage.libs.gap.test_long import test_loop_3
        sage: test_loop_3()
    """
    G = libgap.FreeGroup(2)
    (a,b) = G.GeneratorsOfGroup()
    for i in range(300000):
        lis=libgap([])
        lis.Add(a ** 2)
        lis.Add(b ** 2)
        lis.Add(b * a)
